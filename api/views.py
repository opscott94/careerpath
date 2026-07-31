from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from careers.models import Career, Subject
from eligibility.models import University, Program
import json
import re

@csrf_exempt
@require_http_methods(["POST"])
def career_search(request):
    data = json.loads(request.body)
    query = data.get('query', '').lower().strip()
    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)
    careers = Career.objects.select_related('learning_area').all()
    matches = []
    for career in careers:
        keywords = career.keywords_list()
        score = sum(1 for k in keywords if k in query)
        if score > 0:
            matches.append((score, career))
    matches.sort(key=lambda x: x[0], reverse=True)
    if not matches:
        return JsonResponse({'results': [], 'message': 'No careers found'})
    results = []
    for score, career in matches[:5]:
        results.append({
            'id': career.id,
            'name': career.name,
            'icon': career.icon,
            'learning_area': career.learning_area.name if career.learning_area else '',
            'why_text': career.why_text,
            'score': score,
        })
    return JsonResponse({'results': results})


@csrf_exempt
@require_http_methods(["POST"])
def ai_career_match(request):
    """
    AI-powered career matching endpoint (two-step approach).
    Step 1: Check if frontend pre-generated Firebase AI results. If not, use local LLM.
    Step 2: Programmatic database search using SQL filtering via Q objects.
    """
    data = json.loads(request.body)
    from django.db.models import Q
    from django.conf import settings
    from google.oauth2 import service_account
    import google.auth.transport.requests
    import urllib.request
    import os

    key_path = os.path.join(settings.BASE_DIR, 'gcp-key.json')

    # If the key is not set, we cannot run Vertex AI, so fallback to keyword search
    if not os.path.exists(key_path):
        return JsonResponse({'ai_match': False, 'message': 'GCP service account key not found, fallback to keyword search'})

    query = data.get('query', '').lower().strip()
    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)

    # Ask Gemini to determine career and search keywords
    system_prompt = """You are a career counselor for Ghanaian students. Analyze the student's interest and respond ONLY with a JSON object in this format:
{
  "career_name": "determined career title (e.g. Aerospace Engineer, Medical Doctor, Software Developer)",
  "career_description": "1 sentence describing the career and its main activities",
  "primary_keywords": ["keyword1", "keyword2"],
  "secondary_keywords": ["keyword3", "keyword4"],
  "explanations": {
    "keyword1": "1-sentence explanation of how this direct subject relates to the career",
    "keyword2": "1-sentence explanation of how this direct subject relates to the career",
    "keyword3": "1-sentence explanation of how this secondary subject relates to the career",
    "keyword4": "1-sentence explanation of how this secondary subject relates to the career"
  }
}

CRITICAL RULES:
1. The keywords MUST be academic subjects, degree fields, or department terms.
2. "primary_keywords" MUST ONLY contain the most specific, direct specialized field name for the career (e.g. ["Optometry"] for Optometrist, ["Aerospace", "Aeronautical"] for Aerospace Engineer, ["Marine"] for Marine Engineer, ["Law", "LLB"] for Lawyer).
3. "secondary_keywords" MUST contain related, general, or broader fields that can also lead to the career (e.g. ["Medicine", "Biology", "Medical"] for Optometrist, ["Mechanical", "Engineering"] for Aerospace/Marine Engineer).
4. "explanations" MUST contain a key-value mapping for EACH keyword in both primary_keywords and secondary_keywords, explaining in a brief sentence how studying that subject prepares someone for the determined career.
5. NEVER use job titles (like "Lawyer", "Accountant", "Software Developer", "Doctor") as keywords.
6. Respond ONLY with the JSON object. Do NOT output any thinking process, reasoning, explanations, or introductory text. Skip any thinking phase and generate the JSON directly."""

    user_prompt = f"Student Stated Interest: \"{query}\""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    # Try calling the Gemini developer API
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": full_prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    parsed = None
    models_to_try = ["gemini-2.5-flash", "gemini-2.5-pro"]
    
    try:
        # Load credentials and refresh token
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        creds = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        token = creds.token
        project_id = creds.project_id
        
        for model_name in models_to_try:
            url = f"https://firebasevertexai.googleapis.com/v1beta/projects/{project_id}/locations/us-central1/publishers/google/models/{model_name}:generateContent"
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_data = json.loads(response.read().decode())
                    candidates = res_data.get("candidates", [])
                    if candidates:
                        text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        parsed = json.loads(text_content)
                        break
            except Exception as e:
                print(f"DEBUG: Backend Vertex AI call for model {model_name} failed: {e}")
                continue
    except Exception as e:
        print(f"DEBUG: Backend Vertex AI authentication failed: {e}")

    if not parsed:
        return JsonResponse({'ai_match': False, 'message': 'Gemini call failed, fallback to keyword search'})

    career_name = parsed.get("career_name", "")
    career_description = parsed.get("career_description", "")
    primary_keywords = parsed.get("primary_keywords", [])
    secondary_keywords = parsed.get("secondary_keywords", [])
    explanations = parsed.get("explanations", {})

    if not career_name or (not primary_keywords and not secondary_keywords):
        return JsonResponse({'ai_match': False, 'message': 'Incomplete response, fallback to keyword search'})

    # Step 2: SQL-level filtering for candidate programs using AI keywords
    try:
        all_keywords = primary_keywords + secondary_keywords
        query_filter = Q()
        for kw in all_keywords:
            kw = kw.strip()
            if kw:
                query_filter |= Q(name__icontains=kw) | Q(faculty__icontains=kw) | Q(requirements__learning_area__name__icontains=kw)

        # Only fetch matching programs from the database (distinct candidate set)
        programs = Program.objects.filter(query_filter).select_related('university').prefetch_related(
            'requirements__learning_area',
        ).distinct()

        # Group candidate programs by base name (removing campus suffix e.g. "(Obuasi Campus)") to avoid duplicate recommendations
        grouped_programs = {}
        for p in programs:
            score = 0
            base_name = re.sub(r'\s*\([^)]*campus\)', '', p.name, flags=re.IGNORECASE).strip()
            name_lower = base_name.lower()
            name_key = base_name
            faculty_lower = (p.faculty or '').lower()
            la_names = [req.learning_area.name.lower() for req in p.requirements.all() if req.learning_area]

            # Score primary keywords
            for kw in primary_keywords:
                kw_lower = kw.lower()
                if kw_lower in name_lower:
                    score += 10
                if kw_lower in faculty_lower:
                    score += 5
                for la in la_names:
                    if kw_lower in la:
                        score += 5

            # Score secondary keywords
            for kw in secondary_keywords:
                kw_lower = kw.lower()
                if kw_lower in name_lower:
                    score += 3
                if kw_lower in faculty_lower:
                    score += 1
                for la in la_names:
                    if kw_lower in la:
                        score += 1

            if score > 0:
                is_direct = any(kw.lower() in base_name.lower() for kw in primary_keywords)
                key = base_name.lower()
                
                # Track matched keywords for this specific program offering
                current_kws = set()
                for kw in primary_keywords:
                    if kw.lower() in name_lower or kw.lower() in faculty_lower or any(kw.lower() in la for la in la_names):
                        current_kws.add(kw)
                for kw in secondary_keywords:
                    if kw.lower() in name_lower or kw.lower() in faculty_lower or any(kw.lower() in la for la in la_names):
                        current_kws.add(kw)

                if key not in grouped_programs:
                    grouped_programs[key] = {
                        'name': base_name,
                        'score': score,
                        'is_direct': is_direct,
                        'min_cutoff': p.aggregate,
                        'universities': {p.university.short_name},
                        'matched_kws': current_kws,
                    }
                else:
                    g = grouped_programs[key]
                    if score > g['score']:
                        g['score'] = score
                    if is_direct:
                        g['is_direct'] = True
                    if p.aggregate is not None:
                        if g['min_cutoff'] is None or p.aggregate < g['min_cutoff']:
                            g['min_cutoff'] = p.aggregate
                    g['universities'].add(p.university.short_name)
                    g['matched_kws'].update(current_kws)

        groups = list(grouped_programs.values())

        # Separate into primary and secondary groups
        primary_groups = []
        secondary_groups = []
        for g in groups:
            p_type = "Direct Program" if g['is_direct'] else "Secondary Pathway"
            
            # Find the best matching explanation from explanations dict
            explanation = ""
            # Try primary keywords first (if any matched)
            for m_kw in primary_keywords:
                if m_kw in g['matched_kws']:
                    explanation = explanations.get(m_kw, "")
                    if not explanation:
                        # Case-insensitive lookup fallback
                        for k, v in explanations.items():
                            if k.lower() == m_kw.lower():
                                explanation = v
                                break
                    if explanation:
                        break
            
            if not explanation:
                # Try secondary keywords
                for m_kw in secondary_keywords:
                    if m_kw in g['matched_kws']:
                        explanation = explanations.get(m_kw, "")
                        if not explanation:
                            # Case-insensitive lookup fallback
                            for k, v in explanations.items():
                                if k.lower() == m_kw.lower():
                                    explanation = v
                                    break
                        if explanation:
                            break

            if not explanation:
                explanation = f"Provides relevant academic foundations for a career in this field."

            g['reason'] = f"[{p_type}] {explanation}"
            if g['is_direct']:
                primary_groups.append(g)
            else:
                secondary_groups.append(g)

        # Sort both groups: min_cutoff ascending (None/null goes last)
        primary_groups.sort(key=lambda x: (x['min_cutoff'] is None, x['min_cutoff'] or 999))
        secondary_groups.sort(key=lambda x: (x['min_cutoff'] is None, x['min_cutoff'] or 999))

        combined_groups = primary_groups + secondary_groups
        top_groups = combined_groups[:5]

        if top_groups:
            matched = []
            for g in top_groups:
                matched.append({
                    'program_name': g['name'],
                    'universities': ", ".join(sorted(list(g['universities']))),
                    'reason': g['reason'],
                })
            return JsonResponse({
                'ai_match': True,
                'career_name': career_name,
                'career_description': career_description,
                'matched_programs': matched,
            })

    except Exception:
        # Fall back to keyword search if AI is unavailable
        pass

    # If AI fails, return an indicator so frontend can fall back
    return JsonResponse({'ai_match': False, 'message': 'AI unavailable, use keyword search'})


@csrf_exempt
@require_http_methods(["POST"])
def program_details(request):
    """
    Returns the requirements and details of all university offerings matching a program name.
    Groups offerings by university so that a university with multiple campuses shows 
    a single card with all campus cutoffs & notes.
    """
    data = json.loads(request.body)
    program_name = data.get('program_name', '').strip()
    if not program_name:
        return JsonResponse({'error': 'No program_name provided'}, status=400)

    base_name = re.sub(r'\s*\([^)]*campus\)', '', program_name, flags=re.IGNORECASE).strip()

    programs = Program.objects.filter(
        Q(name__iexact=program_name) | Q(name__icontains=base_name)
    ).select_related('university').prefetch_related(
        'core_subjects',
        'requirements__learning_area',
        'requirements__mandatory_subjects',
        'requirements__elective_subjects'
    ).all()

    if not programs:
        return JsonResponse({'error': 'Program not found'}, status=404)

    grouped_by_uni = {}
    for p in programs:
        uni = p.university
        uni_key = uni.short_name
        if uni_key not in grouped_by_uni:
            grouped_by_uni[uni_key] = {
                'university': uni.name,
                'university_short': uni.short_name,
                'faculty': p.faculty,
                'duration_years': p.duration_years,
                'min_cutoff': p.aggregate,
                'campuses': [],
                'core_subjects': [{'name': s.name} for s in p.core_subjects.all()],
                'requirements': []
            }
            for req in p.requirements.all():
                la_name = req.learning_area.name if req.learning_area else "General Entry"
                mandatory = [{'name': s.name} for s in req.mandatory_subjects.all()]
                electives = [{'name': s.name} for s in req.elective_subjects.all()]
                grouped_by_uni[uni_key]['requirements'].append({
                    'learning_area': la_name,
                    'mandatory_subjects': mandatory,
                    'elective_subjects': electives,
                })

        g = grouped_by_uni[uni_key]
        if p.aggregate is not None:
            if g['min_cutoff'] is None or p.aggregate < g['min_cutoff']:
                g['min_cutoff'] = p.aggregate

        g['campuses'].append({
            'campus_name': p.campus or 'Main Campus',
            'cutoff': p.aggregate,
            'note': p.note or '',
            'faculty': p.faculty,
        })

    offerings = list(grouped_by_uni.values())
    offerings.sort(key=lambda x: (x['min_cutoff'] is None, x['min_cutoff'] or 999))

    return JsonResponse({
        'program_name': base_name or program_name,
        'offerings': offerings
    })


@csrf_exempt
@require_http_methods(["POST"])
def subject_recommendation(request):
    data = json.loads(request.body)
    career_id = data.get('career_id')
    if not career_id:
        return JsonResponse({'error': 'No career_id provided'}, status=400)
    try:
        career = Career.objects.select_related('learning_area').prefetch_related(
            'core_subjects', 'mandatory_electives', 'recommended_electives',
            'recommendation_reasons__subject'
        ).get(id=career_id)
    except Career.DoesNotExist:
        return JsonResponse({'error': 'Career not found'}, status=404)
    reasons = {r.subject_id: r.reason for r in career.recommendation_reasons.all()}
    def fmt(subjects, badge):
        return [{'name': s.name, 'badge': badge, 'reason': reasons.get(s.id, '')} for s in subjects]
    return JsonResponse({
        'career': career.name,
        'icon': career.icon,
        'learning_area': career.learning_area.name if career.learning_area else '',
        'why_text': career.why_text,
        'core_subjects': fmt(career.core_subjects.all(), 'core'),
        'mandatory_electives': fmt(career.mandatory_electives.all(), 'required'),
        'recommended_electives': fmt(career.recommended_electives.all(), 'recommended'),
    })


@csrf_exempt
@require_http_methods(["POST"])
def wassce_check(request):
    data = json.loads(request.body)
    aggregate = data.get('aggregate')
    program_id = data.get('program_id')
    if not aggregate or not program_id:
        return JsonResponse({'error': 'aggregate and program_id required'}, status=400)
    try:
        program = Program.objects.select_related('university').get(id=program_id)
    except Program.DoesNotExist:
        return JsonResponse({'error': 'Program not found'}, status=404)
    if program.aggregate is None:
        return JsonResponse({'error': 'No cutoff data available'}, status=404)
    eligible = int(aggregate) <= program.aggregate
    return JsonResponse({
        'program': program.name,
        'university': program.university.name,
        'cutoff': program.aggregate,
        'your_aggregate': aggregate,
        'eligible': eligible,
        'message': 'Congratulations! You qualify.' if eligible else f'You need aggregate {program.aggregate} or better.',
    })


@require_http_methods(["GET"])
def universities_list(request):
    universities = University.objects.prefetch_related('programs').all()
    data = []
    for uni in universities:
        programs = []
        for prog in uni.programs.all():
            programs.append({
                'id': prog.id,
                'name': prog.name,
                'faculty': prog.faculty,
                'cutoff': prog.aggregate,
                'campus': prog.campus or 'Main Campus',
                'note': prog.note or '',
            })
        data.append({
            'id': uni.id,
            'name': uni.name,
            'short_name': uni.short_name,
            'location': uni.location,
            'programs': programs,
        })
    return JsonResponse({'universities': data})


@csrf_exempt
@require_http_methods(["POST"])
def evaluate_eligibility(request):
    """
    Takes a student's core and elective subjects + WASSCE grades,
    calculates their Best 6 aggregate, and evaluates program eligibility
    across all 172 university degree programs in the database.
    """
    data = json.loads(request.body)
    core_grades = data.get('core_grades', {})
    elective_inputs = data.get('electives', [])

    eng = int(core_grades.get('English Language', 9))
    math = int(core_grades.get('Core Mathematics', 9))
    sci = int(core_grades.get('Integrated Science', 9))
    soc = int(core_grades.get('Social Studies', 9))

    best_3rd_core = min(sci, soc)
    core_sum = eng + math + best_3rd_core

    valid_electives = []
    for e in elective_inputs:
        name = e.get('name', '').strip()
        grade = e.get('grade')
        if name and grade and int(grade) <= 6:
            valid_electives.append({'name': name, 'grade': int(grade)})

    sorted_elec_grades = sorted([e['grade'] for e in valid_electives])

    if len(sorted_elec_grades) < 3:
        return JsonResponse({'error': 'At least 3 passing elective grades (A1 to C6) are required for aggregate calculation.'}, status=400)

    aggregate = core_sum + sum(sorted_elec_grades[:3])
    user_elective_names = [e['name'].lower() for e in valid_electives]

    science_subs = {'biology', 'chemistry', 'physics', 'additional mathematics', 'agricultural science'}
    business_subs = {'business management', 'accounting', 'business economics'}
    computing_subs = {'computer science', 'ict'}
    arts_subs = {'economics', 'geography', 'government', 'history', 'literature in english', 'christian religious studies', 'islamic religious studies', 'rme'}
    tech_subs = {'design and communication technology', 'electrical and electronic technology', 'building construction and wood technology', 'automobile and metal technology'}

    has_science = any(s in user_elective_names for s in science_subs)
    has_business = any(s in user_elective_names for s in business_subs)
    has_computing = any(s in user_elective_names for s in computing_subs)
    has_arts = any(s in user_elective_names for s in arts_subs)
    has_tech = any(s in user_elective_names for s in tech_subs)

    cores_passed = (eng <= 6 and math <= 6 and best_3rd_core <= 6)

    all_programs = Program.objects.select_related('university').prefetch_related(
        'core_subjects',
        'requirements__learning_area',
        'requirements__mandatory_subjects',
        'requirements__elective_subjects'
    ).all()

    grouped = {}
    for p in all_programs:
        p_name = p.name.strip()
        key = p_name.lower()

        if not cores_passed:
            continue

        requirements = p.requirements.all()
        is_qualified = False

        if not requirements.exists():
            is_qualified = True
        else:
            for req in requirements:
                la_name = (req.learning_area.name.lower() if req.learning_area else '').strip()
                m_subs = [s.name.strip().lower() for s in req.mandatory_subjects.all()]
                e_subs = [s.name.strip().lower() for s in req.elective_subjects.all()]

                if m_subs and not all(m in user_elective_names for m in m_subs):
                    continue

                if e_subs:
                    if any(e in user_elective_names for e in e_subs):
                        is_qualified = True
                        break
                elif la_name:
                    if la_name == 'science' and has_science:
                        is_qualified = True
                        break
                    elif la_name == 'business' and has_business:
                        is_qualified = True
                        break
                    elif 'arts' in la_name and (has_arts or has_business):
                        is_qualified = True
                        break
                    elif la_name == 'computing' and (has_computing or has_science):
                        is_qualified = True
                        break
                    elif 'technology' in la_name and (has_tech or has_science):
                        is_qualified = True
                        break
                    else:
                        if not m_subs:
                            is_qualified = True
                            break
                else:
                    is_qualified = True
                    break

        if is_qualified:
            cutoff = p.aggregate
            is_eligible = (cutoff is not None and aggregate <= cutoff)
            is_borderline = (cutoff is not None and not is_eligible and aggregate <= cutoff + 3)

            category = 'all'
            lower_pname = base_pname.lower()
            if any(k in lower_pname for k in ['medicine', 'surgery', 'pharmacy', 'nursing', 'midwifery', 'medical', 'dental', 'health', 'optometry', 'herbal', 'physiotherapy', 'dietetics']):
                category = 'health'
            elif 'engineering' in lower_pname or 'architecture' in lower_pname:
                category = 'engineering'
            elif any(k in lower_pname for k in ['computer', 'information technology', 'software', 'ict', 'data']):
                category = 'computing'
            elif any(k in lower_pname for k in ['business', 'accounting', 'marketing', 'banking', 'finance', 'management', 'agribusiness', 'administration']):
                category = 'business'
            elif any(k in lower_pname for k in ['law', 'llb', 'political', 'sociology', 'social', 'history']):
                category = 'law'
            elif any(k in lower_pname for k in ['agriculture', 'crop', 'animal', 'soil', 'agric']):
                category = 'agric'
            elif any(k in lower_pname for k in ['biology', 'chemistry', 'physics', 'mathematics', 'biochemistry', 'science']):
                category = 'science'

            if key not in grouped:
                grouped[key] = {
                    'program_name': base_pname,
                    'category': category,
                    'faculty': p.faculty,
                    'min_cutoff': cutoff,
                    'is_eligible': is_eligible,
                    'is_borderline': is_borderline,
                    'universities_dict': {},
                    'core_subjects': [s.name for s in p.core_subjects.all()],
                }

            g = grouped[key]
            if cutoff is not None:
                if g['min_cutoff'] is None or cutoff < g['min_cutoff']:
                    g['min_cutoff'] = cutoff
            if is_eligible:
                g['is_eligible'] = True
            elif is_borderline and not g['is_eligible']:
                g['is_borderline'] = True

            u_code = p.university.short_name
            if u_code not in g['universities_dict']:
                g['universities_dict'][u_code] = {
                    'short_name': u_code,
                    'full_name': p.university.name,
                    'location': p.university.location,
                    'cutoff': cutoff,
                    'eligible': is_eligible,
                    'borderline': is_borderline,
                    'campuses': []
                }

            ud = g['universities_dict'][u_code]
            if cutoff is not None:
                if ud['cutoff'] is None or cutoff < ud['cutoff']:
                    ud['cutoff'] = cutoff
            if is_eligible:
                ud['eligible'] = True
            elif is_borderline and not ud['eligible']:
                ud['borderline'] = True

            ud['campuses'].append({
                'campus_name': p.campus or 'Main Campus',
                'cutoff': cutoff,
                'eligible': is_eligible,
                'borderline': is_borderline,
                'margin': (cutoff - aggregate) if cutoff else None,
                'note': p.note or ''
            })

    results = []
    for g_data in grouped.values():
        unis_list = list(g_data['universities_dict'].values())
        unis_list.sort(key=lambda u: (not u['eligible'], not u['borderline'], u['cutoff'] or 999))
        g_data['universities'] = unis_list
        del g_data['universities_dict']
        results.append(g_data)

    results.sort(key=lambda x: (not x['is_eligible'], not x['is_borderline'], x['min_cutoff'] or 999))

    label = 'Outstanding' if aggregate <= 8 else 'Excellent' if aggregate <= 12 else 'Very Good' if aggregate <= 18 else 'Good' if aggregate <= 24 else 'Fair'

    return JsonResponse({
        'aggregate': aggregate,
        'label': label,
        'total_qualified_programs': len(results),
        'eligible_count': sum(1 for r in results if r['is_eligible']),
        'borderline_count': sum(1 for r in results if r['is_borderline']),
        'results': results
    })

