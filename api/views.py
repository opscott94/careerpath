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
    Step 1: Parse user query, clean conversational phrases, and query LLM / local domain map.
    Step 2: Programmatic database search using SQL filtering with high-priority direct scoring.
    """
    data = json.loads(request.body)
    from django.db.models import Q
    from django.conf import settings
    from google.oauth2 import service_account
    import google.auth.transport.requests
    import urllib.request
    import os
    import re

    raw_query = data.get('query', '').strip()
    if not raw_query:
        return JsonResponse({'error': 'No query provided'}, status=400)

    # Clean conversational query prefixes ("I want to be a nurse" -> "nurse")
    q_clean = raw_query.lower()
    prefix_patterns = [
        r"^i\s+(want|would\s+like|wish|hope)\s+to\s+(be|become|study|work\s+as|do|pursue)\s+(a|an)?\s*",
        r"^i\s+want\s+(a|an)?\s*",
        r"^i\s+am\s+interested\s+in\s+(becoming|a|an)?\s*",
        r"^how\s+to\s+(become|be)\s+(a|an)?\s*",
        r"^looking\s+for\s+(a|an)?\s*",
    ]
    for pat in prefix_patterns:
        q_clean = re.sub(pat, "", q_clean, flags=re.IGNORECASE)
    q_clean = q_clean.strip() or raw_query.lower().strip()

    gcp_json_str = os.getenv('GCP_KEY_JSON')
    key_path = os.path.join(settings.BASE_DIR, 'gcp-key.json')

    creds = None
    if gcp_json_str:
        try:
            info = json.loads(gcp_json_str)
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        except Exception as e:
            print(f"DEBUG: Failed to parse GCP_KEY_JSON env var: {e}")

    if not creds and os.path.exists(key_path):
        try:
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)
        except Exception as e:
            print(f"DEBUG: Failed to load gcp-key.json file: {e}")

    # Domain Knowledge Fallback Map for Ghanaian University Programs
    def get_domain_fallback(q_term):
        q = q_term.lower()
        if 'nurse' in q or 'nursing' in q or 'midwife' in q or 'midwifery' in q:
            return {
                'career_name': 'Registered Nurse / Midwife',
                'career_description': 'Registered Nurses and Midwives provide primary patient care, clinical treatments, and maternal healthcare across hospitals and community health centers.',
                'primary_keywords': ['Nursing', 'Midwifery', 'Nurse'],
                'secondary_keywords': ['Health', 'Medical', 'Biology'],
                'explanations': {
                    'Nursing': 'Direct degree program training students in clinical nursing skills and patient care.',
                    'Midwifery': 'Direct degree program specializing in maternal and infant healthcare.',
                    'Health': 'Provides foundational medical and health sciences preparation.',
                    'Medical': 'Provides basic clinical science foundations.',
                    'Biology': 'Builds human biological sciences background.'
                }
            }
        elif 'doctor' in q or 'medicine' in q or 'physician' in q:
            return {
                'career_name': 'Medical Doctor / Physician',
                'career_description': 'Medical Doctors diagnose diseases, prescribe medical treatments, and perform clinical care across hospitals.',
                'primary_keywords': ['Medicine', 'Surgery', 'Human Biology', 'Medical Laboratory'],
                'secondary_keywords': ['Health', 'Biomedical', 'Biology'],
                'explanations': {
                    'Medicine': 'Direct MBChB degree program preparing medical doctors for clinical practice.',
                    'Surgery': 'Core clinical component of medical doctor training.',
                    'Human Biology': 'Pre-clinical undergraduate degree path for medical studies.'
                }
            }
        elif 'optometrist' in q or 'eye' in q or 'vision' in q:
            return {
                'career_name': 'Optometrist',
                'career_description': 'Optometrists diagnose, treat, and manage visual disorders and ocular health conditions.',
                'primary_keywords': ['Optometry'],
                'secondary_keywords': ['Medical', 'Biology', 'Health'],
                'explanations': {
                    'Optometry': 'Direct Doctor of Optometry degree program for vision care specialists.'
                }
            }
        elif 'app' in q or 'software' in q or 'developer' in q or 'coder' in q or 'programmer' in q:
            return {
                'career_name': 'Software Engineer / Application Developer',
                'career_description': 'Software Engineers design, build, and deploy computer applications, web systems, and mobile software.',
                'primary_keywords': ['Computer Science', 'Software Engineering', 'Information Technology', 'Computer'],
                'secondary_keywords': ['Mathematics', 'Engineering', 'Electrical'],
                'explanations': {
                    'Computer Science': 'Core degree program covering algorithms, programming languages, and software architecture.',
                    'Software Engineering': 'Specialized engineering path focused on application development and software systems.',
                    'Information Technology': 'Applied computing degree covering web, networking, and software systems.'
                }
            }
        elif 'pilot' in q or 'aviation' in q or 'aero' in q:
            return {
                'career_name': 'Aeronautical Engineer / Flight Operations',
                'career_description': 'Aeronautical Engineers and Flight Operations specialists design aircraft, manage flight systems, and operate aviation infrastructure.',
                'primary_keywords': ['Aerospace', 'Aeronautical', 'Mechanical Engineering'],
                'secondary_keywords': ['Physics', 'Electrical', 'Mathematics'],
                'explanations': {
                    'Aerospace': 'Direct engineering path for aircraft and propulsion system design.',
                    'Mechanical Engineering': 'Provides mechanical design and aerodynamics fundamentals.'
                }
            }
        elif 'law' in q or 'lawyer' in q or 'attorney' in q or 'legal' in q:
            return {
                'career_name': 'Lawyer / Legal Practitioner',
                'career_description': 'Lawyers advise clients on legal rights, draft legal contracts, and represent parties in courts of law.',
                'primary_keywords': ['Law', 'LLB', 'Legal'],
                'secondary_keywords': ['Political', 'Sociology', 'History'],
                'explanations': {
                    'Law': 'Direct Bachelor of Laws (LLB) degree program required for legal education.',
                    'LLB': 'Professional law degree track.'
                }
            }
        elif 'pharmacy' in q or 'pharmacist' in q or 'drug' in q:
            return {
                'career_name': 'Pharmacist',
                'career_description': 'Pharmacists compound, dispense, and monitor pharmaceutical medications for patient treatment.',
                'primary_keywords': ['Pharmacy', 'Doctor of Pharmacy'],
                'secondary_keywords': ['Chemistry', 'Biochemistry', 'Health'],
                'explanations': {
                    'PharmD': 'Direct Doctor of Pharmacy degree program.',
                    'Pharmacy': 'Direct pharmaceutical sciences degree.'
                }
            }
        return None

    # Step 1: Query Gemini LLM with 3-Tier Multi-Authentication
    system_prompt = """You are a career counselor for Ghanaian students. Analyze the student's interest and respond ONLY with a JSON object in this format:
{
  "career_name": "determined canonical career title (e.g. Nurse, Medical Doctor, Software Developer, Lawyer, Pilot)",
  "career_description": "1 sentence describing the career and its main activities",
  "primary_keywords": ["keyword1", "keyword2"],
  "secondary_keywords": ["keyword3", "keyword4"],
  "explanations": {
    "keyword1": "1-sentence explanation of how this direct subject relates to the career",
    "keyword2": "1-sentence explanation of how this direct subject relates to the career"
  }
}

CRITICAL RULES:
1. "career_name" MUST BE THE CANONICAL JOB TITLE (e.g. "Nurse", "Doctor", "Software Engineer"). NEVER output phrases like "I Want To Be A Nurse".
2. "primary_keywords" MUST ONLY contain direct degree program names (e.g. ["Nursing", "Midwifery"] for Nurse, ["Medicine"] for Doctor, ["Optometry"] for Optometrist).
3. Respond ONLY with JSON."""

    user_prompt = f"Student Stated Interest: \"{q_clean}\""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    parsed = None

    # 1. Try Vertex AI with GCP Credentials
    if creds:
        try:
            auth_req = google.auth.transport.requests.Request()
            creds.refresh(auth_req)
            token = creds.token
            project_id = creds.project_id

            for model_name in ["gemini-2.5-flash", "gemini-2.5-pro"]:
                url = f"https://firebasevertexai.googleapis.com/v1beta/projects/{project_id}/locations/us-central1/publishers/google/models/{model_name}:generateContent"
                try:
                    req_obj = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req_obj, timeout=5) as response:
                        res_data = json.loads(response.read().decode())
                        candidates = res_data.get("candidates", [])
                        if candidates:
                            text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                            if text_content.startswith("```"):
                                lines = text_content.splitlines()
                                if lines[0].startswith("```"):
                                    lines = lines[1:]
                                if lines and lines[-1].startswith("```"):
                                    lines = lines[:-1]
                                text_content = "\n".join(lines).strip()
                            parsed = json.loads(text_content)
                            break
                except Exception as e:
                    print(f"DEBUG: Vertex AI call for {model_name} failed: {e}")
                    continue
        except Exception as e:
            print(f"DEBUG: Vertex AI auth failed: {e}")

    # 2. Fallback to Gemini Developer API Key if Vertex AI failed or creds not available
    if not parsed:
        gemini_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDnUoGfv6RdAdUDkhFk9zWg3qy1TFzugaQ')
        for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
            try:
                req_obj = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req_obj, timeout=6) as response:
                    res_data = json.loads(response.read().decode())
                    candidates = res_data.get("candidates", [])
                    if candidates:
                        text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        if text_content.startswith("```"):
                            lines = text_content.splitlines()
                            if lines[0].startswith("```"):
                                lines = lines[1:]
                            if lines and lines[-1].startswith("```"):
                                lines = lines[:-1]
                            text_content = "\n".join(lines).strip()
                        parsed = json.loads(text_content)
                        break
            except Exception as e:
                print(f"DEBUG: Gemini Developer API call for {model_name} failed: {e}")
                continue

    # Fallback to domain knowledge map or database search
    domain_map = get_domain_fallback(q_clean)
    if domain_map and (not parsed or not parsed.get('primary_keywords')):
        parsed = domain_map

    if not parsed:
        matched_careers = Career.objects.filter(
            Q(name__icontains=q_clean) | Q(description__icontains=q_clean) | Q(why_text__icontains=q_clean)
        )
        if matched_careers.exists():
            c = matched_careers.first()
            career_name = c.name
            career_description = c.why_text
            primary_keywords = [c.name]
            secondary_keywords = [c.learning_area.name] if c.learning_area else ["Science", "General Arts"]
        else:
            query_words = [w for w in q_clean.split() if len(w) > 2]
            career_name = q_clean.title()
            career_description = f"Academic and career pathway tailored for interests in {q_clean.title()}."
            primary_keywords = query_words if query_words else [q_clean]
            secondary_keywords = ["Science", "Engineering", "Health", "Business", "Arts", "Computing"]

        explanations = {kw: f"Provides relevant academic preparation for {career_name}." for kw in (primary_keywords + secondary_keywords)}
    else:
        raw_cname = parsed.get("career_name", q_clean.title())
        # Clean any remaining "I want to be" in career_name if LLM returned it
        for pat in prefix_patterns:
            raw_cname = re.sub(pat, "", raw_cname, flags=re.IGNORECASE)
        career_name = raw_cname.strip().title() or q_clean.title()
        career_description = parsed.get("career_description", f"Academic and career pathway for {career_name}.")
        primary_keywords = parsed.get("primary_keywords", [q_clean])
        secondary_keywords = parsed.get("secondary_keywords", [])
        explanations = parsed.get("explanations", {})

    # Step 2: SQL-level filtering for candidate programs using AI keywords
    try:
        all_keywords = primary_keywords + secondary_keywords
        query_filter = Q()
        for kw in all_keywords:
            kw = kw.strip()
            if kw:
                query_filter |= Q(name__icontains=kw) | Q(college__icontains=kw) | Q(requirements__learning_area__name__icontains=kw)

        programs = Program.objects.filter(query_filter).select_related('university').prefetch_related(
            'requirements__learning_area',
        ).distinct()

        grouped_programs = {}
        for p in programs:
            score = 0
            base_name = re.sub(r'\s*\([^)]*campus\)', '', p.name, flags=re.IGNORECASE).strip()
            name_lower = base_name.lower()
            college_lower = (p.college or '').lower()
            la_names = [req.learning_area.name.lower() for req in p.requirements.all() if req.learning_area]

            # Score primary keywords (Give high score +25 for direct program name matches)
            for kw in primary_keywords:
                kw_lower = kw.lower()
                if kw_lower in name_lower:
                    score += 25
                elif kw_lower in college_lower:
                    score += 5
                for la in la_names:
                    if kw_lower in la:
                        score += 5

            # Score secondary keywords
            for kw in secondary_keywords:
                kw_lower = kw.lower()
                if kw_lower in name_lower:
                    score += 3
                elif kw_lower in college_lower:
                    score += 1
                for la in la_names:
                    if kw_lower in la:
                        score += 1

            if score > 0:
                is_direct = any(kw.lower() in base_name.lower() for kw in primary_keywords)
                key = base_name.lower()
                
                current_kws = set()
                for kw in primary_keywords:
                    if kw.lower() in name_lower or kw.lower() in college_lower or any(kw.lower() in la for la in la_names):
                        current_kws.add(kw)
                for kw in secondary_keywords:
                    if kw.lower() in name_lower or kw.lower() in college_lower or any(kw.lower() in la for la in la_names):
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

        primary_groups = []
        secondary_groups = []
        for g in groups:
            p_type = "Direct Program" if g['is_direct'] else "Secondary Pathway"
            
            explanation = ""
            for m_kw in primary_keywords:
                if m_kw in g['matched_kws']:
                    explanation = explanations.get(m_kw, "")
                    if not explanation:
                        for k, v in explanations.items():
                            if k.lower() == m_kw.lower():
                                explanation = v
                                break
                    if explanation:
                        break
            
            if not explanation:
                for m_kw in secondary_keywords:
                    if m_kw in g['matched_kws']:
                        explanation = explanations.get(m_kw, "")
                        if not explanation:
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

        # Sort primary_groups by highest score first, then cutoff
        primary_groups.sort(key=lambda x: (-x['score'], x['min_cutoff'] is None, x['min_cutoff'] or 999))
        secondary_groups.sort(key=lambda x: (-x['score'], x['min_cutoff'] is None, x['min_cutoff'] or 999))

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

            # Aggregate SHS Elective Requirements Summary across top matched programs
            mandatory_set = []
            recommended_set = []
            track_names = set()

            top_names = [g['name'] for g in top_groups]
            top_program_objs = Program.objects.filter(
                Q(name__in=top_names)
            ).prefetch_related('requirements__mandatory_subjects', 'requirements__elective_subjects', 'requirements__learning_area')

            for p_obj in top_program_objs:
                for req in p_obj.requirements.all():
                    if req.learning_area:
                        track_names.add(req.learning_area.name)
                    for ms in req.mandatory_subjects.all():
                        if ms.name not in mandatory_set:
                            mandatory_set.append(ms.name)
                    for es in req.elective_subjects.all():
                        if es.name not in mandatory_set and es.name not in recommended_set:
                            recommended_set.append(es.name)

            if not mandatory_set:
                if 'nurse' in q_clean or 'nursing' in q_clean:
                    mandatory_set = ['Chemistry', 'Physics', 'Biology']
                    recommended_set = ['Elective Mathematics', 'Food & Nutrition']
                    track_names.add('Science Track')
                elif 'doctor' in q_clean or 'medicine' in q_clean:
                    mandatory_set = ['Chemistry', 'Physics', 'Biology']
                    recommended_set = ['Elective Mathematics']
                    track_names.add('Science Track')
                elif 'app' in q_clean or 'software' in q_clean or 'code' in q_clean:
                    mandatory_set = ['Elective Mathematics', 'Physics']
                    recommended_set = ['Chemistry', 'Applied Technology']
                    track_names.add('Science Track')

            elective_summary = {
                'tracks': list(track_names) if track_names else ['Science / Relevant Track'],
                'mandatory_electives': mandatory_set[:4],
                'recommended_electives': recommended_set[:4],
            }

            return JsonResponse({
                'ai_match': True,
                'career_name': career_name,
                'career_description': career_description,
                'elective_summary': elective_summary,
                'matched_programs': matched,
            })

    except Exception as e:
        print("DEBUG: ai_career_match SQL evaluation error:", e)

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
                'college': p.college,
                'faculty': p.college,
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
            'college': p.college,
            'faculty': p.college,
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
                'college': prog.college,
                'faculty': prog.college,
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

    results = []
    for p in all_programs:
        p_name = p.name.strip()
        base_pname = re.sub(r'\s*\([^)]*campus\)', '', p_name, flags=re.IGNORECASE).strip()
        key = base_pname.lower()

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

            if not is_eligible and not is_borderline:
                continue

            category = 'all'
            lower_pname = p.name.lower()
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

            core_subjects = [{'id': s.id, 'name': s.name} for s in p.core_subjects.all()]
            
            requirements = []
            for req in p.requirements.all():
                la_name = req.learning_area.name if req.learning_area else "General Entry"
                mandatory = [{'id': s.id, 'name': s.name} for s in req.mandatory_subjects.all()]
                electives = [{'id': s.id, 'name': s.name} for s in req.elective_subjects.all()]
                requirements.append({
                    'id': req.id,
                    'learning_area': la_name,
                    'mandatory_subjects': mandatory,
                    'elective_subjects': electives,
                })

            results.append({
                'id': p.id,
                'program_name': p.name,
                'university_name': p.university.name,
                'university_short': p.university.short_name,
                'university_location': p.university.location,
                'college': p.college,
                'faculty': p.college,
                'duration_years': p.duration_years,
                'cutoff': cutoff,
                'year': p.year,
                'campus': p.campus or 'Main Campus',
                'note': p.note or '',
                'is_eligible': is_eligible,
                'is_borderline': is_borderline,
                'margin': (cutoff - aggregate) if cutoff else None,
                'category': category,
                'core_subjects': core_subjects,
                'requirements': requirements,
            })

    results.sort(key=lambda x: (not x['is_eligible'], not x['is_borderline'], x['cutoff'] or 999))

    label = 'Outstanding' if aggregate <= 8 else 'Excellent' if aggregate <= 12 else 'Very Good' if aggregate <= 18 else 'Good' if aggregate <= 24 else 'Fair'

    return JsonResponse({
        'aggregate': aggregate,
        'label': label,
        'total_qualified_programs': len(results),
        'eligible_count': sum(1 for r in results if r['is_eligible']),
        'borderline_count': sum(1 for r in results if r['is_borderline']),
        'results': results
    })


@csrf_exempt
@require_http_methods(["POST"])
def ocr_wassce_results(request):
    """
    Accepts an uploaded image or PDF WASSCE results slip/transcript,
    uses Gemini Multimodal OCR to extract core & elective subjects and grades,
    standardizes subject names to database choices, and returns structured JSON.
    """
    import base64
    from django.conf import settings
    from google.oauth2 import service_account
    import google.auth.transport.requests
    import urllib.request
    import os

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    uploaded_file = request.FILES['file']
    filename = uploaded_file.name.lower()
    content_type = uploaded_file.content_type or ''

    # Determine MIME type
    if filename.endswith('.pdf') or 'pdf' in content_type:
        mime_type = 'application/pdf'
    elif filename.endswith('.png'):
        mime_type = 'image/png'
    elif filename.endswith('.webp'):
        mime_type = 'image/webp'
    else:
        mime_type = 'image/jpeg'

    try:
        file_bytes = uploaded_file.read()
        b64_data = base64.b64encode(file_bytes).decode('utf-8')
    except Exception as e:
        return JsonResponse({'error': f'Failed to read file bytes: {e}'}, status=400)

    gcp_json_str = os.getenv('GCP_KEY_JSON')
    key_path = os.path.join(settings.BASE_DIR, 'gcp-key.json')

    creds = None
    if gcp_json_str:
        try:
            info = json.loads(gcp_json_str)
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        except Exception as e:
            print(f"DEBUG: Failed to parse GCP_KEY_JSON env var: {e}")

    if not creds and os.path.exists(key_path):
        try:
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)
        except Exception as e:
            print(f"DEBUG: Failed to load gcp-key.json file: {e}")

    prompt_text = """You are an expert OCR parser for Ghanaian WASSCE / SSSCE result slips, transcripts, and certificates.
Extract all high school subjects and their corresponding letter grades from the document image or PDF.

Respond ONLY with a JSON object in this format:
{
  "core_subjects": {
    "English Language": "A1",
    "Core Mathematics": "B2",
    "Integrated Science": "B3",
    "Social Studies": "C4"
  },
  "elective_subjects": [
    {"subject": "Elective Mathematics", "grade": "B2"},
    {"subject": "Physics", "grade": "A1"},
    {"subject": "Chemistry", "grade": "B3"},
    {"subject": "Biology", "grade": "C4"}
  ]
}

CRITICAL RULES:
1. Valid WASSCE/SSSCE grades are A1, B2, B3, C4, C5, C6, D7, E8, F9 (or A, B, C, D, E, F).
2. Standardize Core Subject names as "English Language", "Core Mathematics", "Integrated Science", "Social Studies".
3. Standardize Elective Subject names to standard Ghanaian SHS subjects (e.g. "Elective Mathematics", "Physics", "Chemistry", "Biology", "Economics", "Geography", "History", "Government", "General Knowledge in Art", "Graphic Design", "Financial Accounting", "Costing", "Business Management", "Food and Nutrition", "Management in Living", "General Agriculture", "Crop Husbandry and Horticulture", "Animal Husbandry", "Elective ICT", "Literature in English", "French", "Ghanaian Language", etc.).
4. Respond ONLY with valid JSON."""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt_text},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": b64_data
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    parsed = None

    # 1. Try Vertex AI with GCP Credentials if available
    if creds:
        try:
            auth_req = google.auth.transport.requests.Request()
            creds.refresh(auth_req)
            token = creds.token
            project_id = creds.project_id

            for model_name in ["gemini-2.5-flash", "gemini-2.5-pro"]:
                url = f"https://firebasevertexai.googleapis.com/v1beta/projects/{project_id}/locations/us-central1/publishers/google/models/{model_name}:generateContent"
                try:
                    req_obj = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req_obj, timeout=25) as response:
                        res_data = json.loads(response.read().decode())
                        candidates = res_data.get("candidates", [])
                        if candidates:
                            text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                            if text_content.startswith("```"):
                                lines = text_content.splitlines()
                                if lines[0].startswith("```"):
                                    lines = lines[1:]
                                if lines and lines[-1].startswith("```"):
                                    lines = lines[:-1]
                                text_content = "\n".join(lines).strip()
                            parsed = json.loads(text_content)
                            break
                except Exception as e:
                    print(f"DEBUG: OCR Vertex AI call for {model_name} failed: {e}")
                    continue
        except Exception as e:
            print(f"DEBUG: OCR Vertex AI auth error: {e}")

    # 2. Fallback to Gemini Developer API Key if Vertex AI failed or creds not available
    if not parsed:
        gemini_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDnUoGfv6RdAdUDkhFk9zWg3qy1TFzugaQ')
        for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
            try:
                req_obj = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req_obj, timeout=25) as response:
                    res_data = json.loads(response.read().decode())
                    candidates = res_data.get("candidates", [])
                    if candidates:
                        text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        if text_content.startswith("```"):
                            lines = text_content.splitlines()
                            if lines[0].startswith("```"):
                                lines = lines[1:]
                            if lines and lines[-1].startswith("```"):
                                lines = lines[:-1]
                            text_content = "\n".join(lines).strip()
                        parsed = json.loads(text_content)
                        break
            except Exception as e:
                print(f"DEBUG: OCR Gemini Developer API call for {model_name} failed: {e}")
                continue

    if not parsed:
        return JsonResponse({'error': 'Could not extract WASSCE grades from the uploaded document. Please ensure the image/PDF is clear or select grades manually.'}, status=422)

    # Standardize & Normalize grades to integer grade values (A1=1, B2=2, B3=3, C4=4, C5=5, C6=6, D7=7, E8=8, F9=9)
    grade_map = {
        'A1': 1, 'A': 1, '1': 1,
        'B2': 2, '2': 2,
        'B3': 3, 'B': 3, '3': 3,
        'C4': 4, '4': 4,
        'C5': 5, '5': 5,
        'C6': 6, 'C': 6, '6': 6,
        'D7': 7, 'D': 7, '7': 7,
        'E8': 8, 'E': 8, '8': 8,
        'F9': 9, 'F': 9, '9': 9,
    }

    # Abbreviation dictionary for WASSCE results slips
    abbreviation_map = {
        'mgt in living': 'Management in Living',
        'mgt. in living': 'Management in Living',
        'mgt in liv': 'Management in Living',
        'mgmt in living': 'Management in Living',
        'food & nut': 'Food and Nutrition',
        'food & nutrition': 'Food and Nutrition',
        'food and nut': 'Food and Nutrition',
        'cloth & text': 'Clothing and Textiles',
        'clothing & textiles': 'Clothing and Textiles',
        'fin acct': 'Financial Accounting',
        'financial acct': 'Financial Accounting',
        'fin accounting': 'Financial Accounting',
        'bus mgt': 'Business Management',
        'bus. mgmt': 'Business Management',
        'business mgmt': 'Business Management',
        'bus econ': 'Business Economics',
        'business econ': 'Business Economics',
        'elect math': 'Elective Mathematics',
        'elect. math': 'Elective Mathematics',
        'elect maths': 'Elective Mathematics',
        'add math': 'Additional Mathematics',
        'add. maths': 'Additional Mathematics',
        'lit in eng': 'Literature in English',
        'lit. in english': 'Literature in English',
        'gen agric': 'Agricultural Science',
        'general agric': 'Agricultural Science',
        'agric sci': 'Agricultural Science',
        'agric science': 'Agricultural Science',
        'gk in art': 'Art and Design Foundation',
        'g.k.a': 'Art and Design Foundation',
        'gka': 'Art and Design Foundation',
        'crs': 'Christian Religious Studies',
        'irs': 'Islamic Religious Studies',
    }

    raw_cores = parsed.get('core_subjects', {})
    core_grades = {}
    for k, v in raw_cores.items():
        val = str(v).upper().strip()
        core_grades[k] = grade_map.get(val, 1)

    raw_electives = parsed.get('elective_subjects', [])
    clean_electives = []
    for item in raw_electives:
        subj = item.get('subject', '').strip()
        grd = str(item.get('grade', '')).upper().strip()
        if subj:
            lower_subj = subj.lower()
            for abbr, full_name in abbreviation_map.items():
                if abbr == lower_subj or abbr in lower_subj:
                    subj = full_name
                    break
            clean_electives.append({
                'subject': subj,
                'grade': grade_map.get(grd, 1)
            })

    return JsonResponse({
        'success': True,
        'core_grades': core_grades,
        'electives': clean_electives
    })

