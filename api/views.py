from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db.models import Q
from careers.models import Career, Subject
from eligibility.models import University, Program
from careers.domain_matcher import get_domain_fallback
from api.services.gemini_service import call_gemini
from api.services.pdf_service import generate_eligibility_report_pdf
import json
import re
import base64
import os


def safe_int(val, default=9):
    """Safely converts input to int, handling empty strings, None, and invalid formats."""
    try:
        if val is None:
            return default
        s = str(val).strip()
        if not s:
            return default
        return int(float(s))
    except (ValueError, TypeError):
        return default


def parse_json_body(request):
    """Safely parses JSON request body, returning empty dict if missing or malformed."""
    try:
        if not request.body:
            return {}
        return json.loads(request.body)
    except Exception:
        return {}


@csrf_exempt
@require_http_methods(["POST"])
def career_search(request):
    data = parse_json_body(request)
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
    data = parse_json_body(request)
    raw_query = data.get('query', '').strip()
    if not raw_query:
        return JsonResponse({'error': 'No query provided'}, status=400)

    # Clean conversational query prefixes ("I want to be a nurse" -> "nurse")
    q_clean = raw_query.lower()
    prefix_patterns = [
        r"^i\s+(want|would\s+like|wish|hope)\s+to\s+(be|become|study|work\s+as|do|pursue|build|design|create|make|fly)\s+(a|an)?\s*",
        r"^i\s+(want|would\s+like|wish|hope)\s+to\s*",
        r"^i\s+(want|would\s+like|wish|hope)\s+(a|an)?\s*",
        r"^i\s+am\s+interested\s+in\s+(becoming|a|an)?\s*",
        r"^how\s+to\s+(become|be|study|build|make)\s+(a|an)?\s*",
        r"^looking\s+for\s+(a|an)?\s*",
        r"^to\s+(be|become|study|work\s+as|do|pursue|build|design|create|make|fly)\s+(a|an)?\s*",
        r"^to\s*",
    ]
    for pat in prefix_patterns:
        q_clean = re.sub(pat, "", q_clean, flags=re.IGNORECASE)
    q_clean = q_clean.strip() or raw_query.lower().strip()

    # Performance Caching Check (1-day TTL)
    cache_safe_key = f"ai_career_match_{re.sub(r'[^a-zA-Z0-9_]', '_', q_clean)[:64]}"
    cached_response = cache.get(cache_safe_key)
    if cached_response:
        return JsonResponse(cached_response)

    # Check Domain Knowledge Fallback Map first for instant, high-accuracy response
    parsed = None
    domain_map = get_domain_fallback(q_clean)
    if domain_map and domain_map.get('primary_keywords'):
        parsed = domain_map

    # If not in domain map, query Gemini LLM
    if not parsed:
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

        parsed = call_gemini(
            payload,
            timeout=8,
            expect_json=True
        )

    # Defensively normalize parsed response (handle LLM wrapping in a list)
    if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
        parsed = parsed[0]
    elif not isinstance(parsed, dict):
        parsed = None

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
            STOP_WORDS = {'to', 'a', 'an', 'the', 'in', 'on', 'at', 'for', 'of', 'and', 'or', 'is', 'be', 'want', 'build', 'building', 'make', 'do', 'study', 'work', 'become', 'like', 'how', 'looking'}
            query_words = [w for w in q_clean.split() if len(w) > 2 and w.lower() not in STOP_WORDS]
            career_name = q_clean.title()
            career_description = f"Academic and career pathway tailored for interests in {q_clean.title()}."
            primary_keywords = query_words if query_words else [q_clean]
            secondary_keywords = ["Science", "Engineering", "Health", "Business", "Arts", "Computing"]

        explanations = {kw: f"Provides relevant academic preparation for {career_name}." for kw in (primary_keywords + secondary_keywords)}
    else:
        raw_cname = parsed.get("career_name", q_clean.title())
        for pat in prefix_patterns:
            raw_cname = re.sub(pat, "", str(raw_cname), flags=re.IGNORECASE)
        career_name = str(raw_cname).strip().title() or q_clean.title()
        career_description = parsed.get("career_description", f"Academic and career pathway for {career_name}.")
        primary_keywords = parsed.get("primary_keywords", [q_clean])
        if not isinstance(primary_keywords, list):
            primary_keywords = [str(primary_keywords)]
        secondary_keywords = parsed.get("secondary_keywords", [])
        if not isinstance(secondary_keywords, list):
            secondary_keywords = []
        explanations = parsed.get("explanations", {})
        if not isinstance(explanations, dict):
            explanations = {}

    # Step 2: SQL-level filtering for candidate programs using AI keywords
    try:
        all_keywords = primary_keywords + secondary_keywords
        query_filter = Q()
        for kw in all_keywords:
            kw = str(kw).strip()
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
                kw_lower = str(kw).lower()
                if kw_lower in name_lower:
                    score += 25
                elif kw_lower in college_lower:
                    score += 5
                for la in la_names:
                    if kw_lower in la:
                        score += 5

            # Score secondary keywords
            for kw in secondary_keywords:
                kw_lower = str(kw).lower()
                if kw_lower in name_lower:
                    score += 3
                elif kw_lower in college_lower:
                    score += 1
                for la in la_names:
                    if kw_lower in la:
                        score += 1

            if score > 0:
                is_direct = any(str(kw).lower() in base_name.lower() for kw in primary_keywords)
                key = base_name.lower()
                
                current_kws = set()
                for kw in primary_keywords:
                    kstr = str(kw)
                    if kstr.lower() in name_lower or kstr.lower() in college_lower or any(kstr.lower() in la for la in la_names):
                        current_kws.add(kstr)
                for kw in secondary_keywords:
                    kstr = str(kw)
                    if kstr.lower() in name_lower or kstr.lower() in college_lower or any(kstr.lower() in la for la in la_names):
                        current_kws.add(kstr)

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
                            if k.lower() == str(m_kw).lower():
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
                                if k.lower() == str(m_kw).lower():
                                    explanation = v
                                    break
                        if explanation:
                            break

            if not explanation:
                explanation = "Provides relevant academic foundations for a career in this field."

            g['reason'] = f"[{p_type}] {explanation}"
            if g['is_direct']:
                primary_groups.append(g)
            else:
                secondary_groups.append(g)

        primary_groups.sort(key=lambda x: (-x['score'], x['min_cutoff'] is None, x['min_cutoff'] or 999))
        secondary_groups.sort(key=lambda x: (-x['score'], x['min_cutoff'] is None, x['min_cutoff'] or 999))

        top_groups = (primary_groups[:15] + secondary_groups[:5])[:15]

        if top_groups:
            matched = []
            for g in top_groups:
                matched.append({
                    'program_name': g['name'],
                    'universities': ", ".join(sorted(list(g['universities']))),
                    'reason': g['reason'],
                })

            mandatory_set = []
            recommended_set = []
            track_names = set()

            summary_target_groups = primary_groups if primary_groups else secondary_groups
            summary_names = [g['name'] for g in summary_target_groups]

            summary_program_objs = Program.objects.filter(
                Q(name__in=summary_names)
            ).prefetch_related('requirements__mandatory_subjects', 'requirements__elective_subjects', 'requirements__learning_area')

            for p_obj in summary_program_objs:
                for req in p_obj.requirements.all():
                    if req.learning_area:
                        track_names.add(req.learning_area.name)
                    for ms in req.mandatory_subjects.all():
                        if ms.name not in mandatory_set:
                            mandatory_set.append(ms.name)
                    for es in req.elective_subjects.all():
                        if es.name not in mandatory_set and es.name not in recommended_set:
                            recommended_set.append(es.name)

            elective_summary = {
                'tracks': list(track_names) if track_names else ['General Track'],
                'mandatory_electives': mandatory_set[:5],
                'recommended_electives': recommended_set[:5],
            }

            res_payload = {
                'ai_match': True,
                'career_name': career_name,
                'career_description': career_description,
                'elective_summary': elective_summary,
                'matched_programs': matched,
            }

            cache.set(cache_safe_key, res_payload, timeout=86400)
            return JsonResponse(res_payload)

    except Exception as e:
        import traceback
        traceback.print_exc()
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
    data = parse_json_body(request)
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
def career_outlook(request):
    """
    AI-generated career outlook for a specific university degree program.
    Returns a 2-3 sentence Ghana-specific career description covering job roles,
    key employers, and relevant industries. Caches response for 7 days.
    """
    data = parse_json_body(request)
    program_name = data.get('program_name', '').strip()
    if not program_name:
        return JsonResponse({'error': 'No program_name provided'}, status=400)

    # 7-day Cache Check
    cache_key = f"career_outlook_{re.sub(r'[^a-zA-Z0-9_]', '_', program_name.lower())[:64]}"
    cached_text = cache.get(cache_key)
    if cached_text:
        return JsonResponse({'career_outlook': cached_text})

    # Build AI prompt
    system_prompt = f"""You are a career counselor for Ghanaian university students. Given the degree program name below, write exactly 2-3 sentences describing:
1. The specific professional roles a graduate can pursue.
2. Key employers or institutions in Ghana (and internationally where relevant) that hire these graduates.
3. The industry sectors this degree serves.

CRITICAL RULES:
- Be specific to Ghana where possible (mention real Ghanaian institutions like GSA, FDA, GHS, GRA, Bank of Ghana, Cocoa Processing Company, Volta River Authority, Ghana Education Service, etc. where relevant).
- Do NOT use bullet points or numbered lists. Write in flowing paragraph form.
- Do NOT start with "Graduating with a..." — start directly with the career outlook content.
- Keep it concise: exactly 2-3 sentences, no more.
- Do NOT use emojis.

Degree Program: {program_name}"""

    payload = {
        "contents": [{"role": "user", "parts": [{"text": system_prompt}]}],
        "generationConfig": {"temperature": 0.7}
    }

    result_text = call_gemini(
        payload,
        timeout=8,
        expect_json=False
    )

    if not result_text:
        result_text = f"Graduates of {program_name} are well-positioned for professional roles across both public and private sectors in Ghana and internationally. Career opportunities span government agencies, corporate organizations, research institutions, and NGOs that align with this field of study."

    cache.set(cache_key, result_text, timeout=604800)
    return JsonResponse({'career_outlook': result_text})


@csrf_exempt
@require_http_methods(["POST"])
def subject_recommendation(request):
    data = parse_json_body(request)
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
    data = parse_json_body(request)
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
    
    user_agg = safe_int(aggregate, default=None)
    if user_agg is None:
        return JsonResponse({'error': 'Invalid aggregate value provided'}, status=400)

    eligible = user_agg <= program.aggregate
    return JsonResponse({
        'program': program.name,
        'university': program.university.name,
        'cutoff': program.aggregate,
        'your_aggregate': user_agg,
        'eligible': eligible,
        'message': 'Congratulations! You qualify.' if eligible else f'You need aggregate {program.aggregate} or better.',
    })


@require_http_methods(["GET"])
def universities_list(request):
    """Returns all universities and their program offerings. Cached for 1 day."""
    cache_key = "universities_list_all_v1"
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse({'universities': cached_data})

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
    cache.set(cache_key, data, timeout=86400)
    return JsonResponse({'universities': data})


@csrf_exempt
@require_http_methods(["POST"])
def evaluate_eligibility(request):
    """
    Takes a student's core and elective subjects + WASSCE grades (or is_awaiting flag),
    calculates Best 6 aggregate (if graded) or evaluates subject track eligibility
    (if awaiting results) across all university degree programs.
    """
    data = parse_json_body(request)
    is_awaiting = data.get('is_awaiting', False)
    core_grades = data.get('core_grades', {})
    if not isinstance(core_grades, dict):
        core_grades = {}
    elective_inputs = data.get('electives', [])
    if not isinstance(elective_inputs, list):
        elective_inputs = []

    if is_awaiting:
        user_elective_names = [str(e.get('name', '')).strip().lower() for e in elective_inputs if isinstance(e, dict) and e.get('name')]
        if len(user_elective_names) < 3:
            return JsonResponse({'error': 'Please select at least 3 elective subjects for subject eligibility checking.'}, status=400)
        
        raw_eng = 1
        raw_math = 1
        raw_sci = 1
        raw_soc = 1
        raw_electives = []
        aggregate = None
    else:
        raw_eng = safe_int(core_grades.get('English Language'), default=9)
        raw_math = safe_int(core_grades.get('Core Mathematics'), default=9)
        raw_sci = safe_int(core_grades.get('Integrated Science'), default=9)
        raw_soc = safe_int(core_grades.get('Social Studies'), default=9)

        raw_electives = []
        for e in elective_inputs:
            if isinstance(e, dict):
                name = str(e.get('name', '')).strip()
                grade = e.get('grade')
                if name and grade is not None:
                    raw_electives.append({'name': name, 'grade': safe_int(grade, default=9)})

        best_3rd_core = min(raw_sci, raw_soc)
        sorted_all_grades = sorted([el['grade'] for el in raw_electives])
        if len(sorted_all_grades) >= 3:
            aggregate = raw_eng + raw_math + best_3rd_core + sum(sorted_all_grades[:3])
        elif len(sorted_all_grades) > 0:
            aggregate = raw_eng + raw_math + best_3rd_core + sum(sorted_all_grades)
        else:
            aggregate = raw_eng + raw_math + best_3rd_core
        user_elective_names = [e['name'].lower() for e in raw_electives]

    def norm_sub(name):
        n = (name or '').strip().lower()
        n = re.sub(r'[\(\)]', '', n).strip()
        if 'math' in n and ('elec' in n or 'add' in n or 'furth' in n):
            return 'elective mathematics'
        if 'math' in n and ('core' in n or 'gen' in n):
            return 'core mathematics'
        if 'science' in n and ('integ' in n or 'gen' in n):
            return 'integrated science'
        if 'physics' in n:
            return 'physics'
        if 'chem' in n:
            return 'chemistry'
        if 'bio' in n and 'med' not in n:
            return 'biology'
        return n

    user_elec_dict = {}
    if not is_awaiting:
        for e in raw_electives:
            user_elec_dict[norm_sub(e['name'])] = e['grade']

    science_subs = {'biology', 'chemistry', 'physics', 'elective mathematics', 'agricultural science'}
    business_subs = {'business management', 'accounting', 'business economics', 'cost accounting'}
    computing_subs = {'computer science', 'ict', 'information technology'}
    arts_subs = {'economics', 'geography', 'government', 'history', 'literature in english', 'christian religious studies', 'islamic religious studies', 'rme'}
    tech_subs = {'design and communication technology', 'electrical and electronic technology', 'building construction and wood technology', 'automobile and metal technology', 'technical drawing', 'applied electricity', 'electronics'}

    norm_user_elective_names = [norm_sub(name) for name in user_elective_names]
    has_science = any(s in norm_user_elective_names for s in science_subs)
    has_business = any(s in norm_user_elective_names for s in business_subs)
    has_computing = any(s in norm_user_elective_names for s in computing_subs)
    has_arts = any(s in norm_user_elective_names for s in arts_subs)
    has_tech = any(s in norm_user_elective_names for s in tech_subs)

    all_programs = Program.objects.select_related('university').prefetch_related(
        'core_subjects',
        'requirements__learning_area',
        'requirements__mandatory_subjects',
        'requirements__elective_subjects'
    ).all()

    results = []
    for p in all_programs:
        uni = p.university
        min_pass = p.min_passing_grade or 6

        if not is_awaiting:
            cores_passed = (raw_eng <= min_pass and raw_math <= min_pass and min(raw_sci, raw_soc) <= min_pass)
        else:
            cores_passed = True

        if not cores_passed:
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

        requirements = p.requirements.all()
        is_qualified = False
        best_prog_aggregate = None

        if is_awaiting:
            if not requirements.exists():
                is_qualified = True
            else:
                for req in requirements:
                    la_name = (req.learning_area.name.lower() if req.learning_area else '').strip()
                    m_subs = [norm_sub(s.name) for s in req.mandatory_subjects.all()]
                    e_subs = [norm_sub(s.name) for s in req.elective_subjects.all()]

                    if m_subs and not all(m in norm_user_elective_names for m in m_subs):
                        continue

                    if e_subs:
                        if any(e in norm_user_elective_names for e in e_subs):
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
        else:
            u_eng = uni.get_point(raw_eng)
            u_math = uni.get_point(raw_math)
            u_sci = uni.get_point(raw_sci)
            u_soc = uni.get_point(raw_soc)

            requires_science_core = (category in ['science', 'health', 'engineering', 'computing']) or \
                                    any(c.name.strip().lower() == 'integrated science' for c in p.core_subjects.all())
            
            if requires_science_core:
                if raw_sci > min_pass:
                    continue
                u_3rd_core = u_sci
            else:
                u_3rd_core = min(u_sci, u_soc)

            core_sum = u_eng + u_math + u_3rd_core

            if not requirements.exists():
                passing_grades = sorted([uni.get_point(g) for g in user_elec_dict.values() if g <= min_pass])
                if len(passing_grades) >= 3:
                    best_prog_aggregate = core_sum + sum(passing_grades[:3])
                    is_qualified = True
            else:
                for req in requirements:
                    la_name = (req.learning_area.name.lower() if req.learning_area else '').strip()
                    m_subs = [norm_sub(s.name) for s in req.mandatory_subjects.all()]
                    e_subs = [norm_sub(s.name) for s in req.elective_subjects.all()]

                    m_points = []
                    m_missing = False
                    used_subs = set()
                    for m in m_subs:
                        if m in user_elec_dict and user_elec_dict[m] <= min_pass:
                            m_points.append(uni.get_point(user_elec_dict[m]))
                            used_subs.add(m)
                        else:
                            m_missing = True
                            break

                    if m_missing:
                        continue

                    needed = max(0, 3 - len(m_points))
                    rem_candidates = []
                    for sub_name, grade in user_elec_dict.items():
                        if sub_name not in used_subs and grade <= min_pass:
                            priority = 0
                            if e_subs and sub_name in e_subs:
                                priority = -1
                            rem_candidates.append((priority, uni.get_point(grade), sub_name))

                    rem_candidates.sort(key=lambda x: (x[0], x[1]))

                    if len(m_points) + len(rem_candidates) < 3:
                        continue

                    extra_points = [x[1] for x in rem_candidates[:needed]]
                    route_elec_sum = sum(m_points) + sum(extra_points)
                    route_aggregate = core_sum + route_elec_sum

                    is_qualified = True
                    if best_prog_aggregate is None or route_aggregate < best_prog_aggregate:
                        best_prog_aggregate = route_aggregate

        if is_qualified:
            cutoff = p.aggregate
            if is_awaiting:
                is_eligible = True
                is_borderline = False
                prog_aggregate = None
            else:
                prog_aggregate = best_prog_aggregate
                if prog_aggregate is None:
                    continue

                is_eligible = (cutoff is not None and prog_aggregate <= cutoff)
                is_borderline = (cutoff is not None and not is_eligible and prog_aggregate <= cutoff + 3)

            if not is_awaiting and not is_eligible and not is_borderline:
                continue

            core_subjects = [{'id': s.id, 'name': s.name} for s in p.core_subjects.all()]
            
            req_list = []
            for req in p.requirements.all():
                la_name = req.learning_area.name if req.learning_area else "General Entry"
                mandatory = [{'id': s.id, 'name': s.name} for s in req.mandatory_subjects.all()]
                electives = [{'id': s.id, 'name': s.name} for s in req.elective_subjects.all()]
                req_list.append({
                    'id': req.id,
                    'learning_area': la_name,
                    'mandatory_subjects': mandatory,
                    'elective_subjects': electives,
                })

            margin = (cutoff - prog_aggregate) if (cutoff is not None and prog_aggregate is not None) else None

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
                'user_aggregate': prog_aggregate,
                'is_eligible': is_eligible,
                'is_borderline': is_borderline,
                'margin': margin,
                'category': category,
                'core_subjects': core_subjects,
                'requirements': req_list,
            })

    results.sort(key=lambda x: (not x['is_eligible'], not x['is_borderline'], x['cutoff'] or 999))

    label = 'Awaiting WASSCE Results' if is_awaiting else ('Outstanding' if (aggregate is not None and aggregate <= 8) else 'Excellent' if (aggregate is not None and aggregate <= 12) else 'Very Good' if (aggregate is not None and aggregate <= 18) else 'Good' if (aggregate is not None and aggregate <= 24) else 'Fair')

    return JsonResponse({
        'is_awaiting': is_awaiting,
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
    if 'file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)

    uploaded_file = request.FILES['file']
    filename = uploaded_file.name.lower()
    content_type = uploaded_file.content_type or ''

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
        return JsonResponse({'success': False, 'error': f'Failed to read file bytes: {e}'}, status=400)

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
3. Standardize Elective Subject names to standard Ghanaian SHS subjects (e.g. "Additional Mathematics" / "Elective Mathematics", "Physics", "Chemistry", "Biology", "Economics", "Geography", "History", "Government", "Art and Design Foundation" / "General Knowledge in Art", "Art and Design Studio" / "Graphic Design", "Accounting", "Business Management", "Food and Nutrition", "Management in Living", "Clothing and Textiles", "Agricultural Science", "Computer Science", "Literature in English", "Christian Religious Studies", "Islamic Religious Studies", "French", "Ghanaian Language", "Design and Communication Technology", etc.).
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

    parsed = call_gemini(
        payload,
        timeout=25,
        expect_json=True
    )

    if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
        parsed = parsed[0]
    elif not isinstance(parsed, dict):
        parsed = None

    if not parsed:
        return JsonResponse({'success': False, 'error': 'Could not extract WASSCE grades from the uploaded document. Please ensure the image/PDF is clear or select grades manually.'}, status=422)

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
        'fin acct': 'Accounting',
        'financial acct': 'Accounting',
        'fin accounting': 'Accounting',
        'financial accounting': 'Accounting',
        'bus mgt': 'Business Management',
        'bus. mgmt': 'Business Management',
        'business mgmt': 'Business Management',
        'bus econ': 'Business Economics',
        'business econ': 'Business Economics',
        'elect math': 'Additional Mathematics',
        'elect. math': 'Additional Mathematics',
        'elect maths': 'Additional Mathematics',
        'elective math': 'Additional Mathematics',
        'elective mathematics': 'Additional Mathematics',
        'add math': 'Additional Mathematics',
        'add. maths': 'Additional Mathematics',
        'additional math': 'Additional Mathematics',
        'additional maths': 'Additional Mathematics',
        'further math': 'Additional Mathematics',
        'lit in eng': 'Literature in English',
        'lit. in english': 'Literature in English',
        'gen agric': 'Agricultural Science',
        'general agric': 'Agricultural Science',
        'general agriculture': 'Agricultural Science',
        'agric sci': 'Agricultural Science',
        'agric science': 'Agricultural Science',
        'gen know in art': 'Art and Design Foundation',
        'gen. know. in art': 'Art and Design Foundation',
        'gen know in arts': 'Art and Design Foundation',
        'gen. know. in arts': 'Art and Design Foundation',
        'general knowledge in art': 'Art and Design Foundation',
        'general knowledge in arts': 'Art and Design Foundation',
        'gen knowledge in art': 'Art and Design Foundation',
        'gen know art': 'Art and Design Foundation',
        'general know in art': 'Art and Design Foundation',
        'gk in art': 'Art and Design Foundation',
        'g.k.a': 'Art and Design Foundation',
        'gka': 'Art and Design Foundation',
        'graphic design': 'Art and Design Studio',
        'picture making': 'Art and Design Studio',
        'sculpture': 'Art and Design Studio',
        'ceramics': 'Art and Design Studio',
        'leatherwork': 'Art and Design Studio',
        'crs': 'Christian Religious Studies',
        'c.r.s': 'Christian Religious Studies',
        'irs': 'Islamic Religious Studies',
        'i.r.s': 'Islamic Religious Studies',
        'rme': 'RME',
        'r.m.e': 'RME',
        'tech draw': 'Design and Communication Technology',
        'technical drawing': 'Design and Communication Technology',
        'applied electricity': 'Electrical and Electronic Technology',
        'electronics': 'Electrical and Electronic Technology',
        'building construction': 'Building Construction and Wood Technology',
        'woodwork': 'Building Construction and Wood Technology',
        'metalwork': 'Automobile and Metal Technology',
        'auto mechanics': 'Automobile and Metal Technology',
    }

    raw_cores = parsed.get('core_subjects', {})
    if not isinstance(raw_cores, dict):
        raw_cores = {}
    core_grades = {}
    for k, v in raw_cores.items():
        val = str(v).upper().strip()
        core_grades[str(k).strip()] = grade_map.get(val, 4)

    raw_electives = parsed.get('elective_subjects', [])
    if not isinstance(raw_electives, list):
        raw_electives = []
    clean_electives = []
    for item in raw_electives:
        if isinstance(item, dict):
            subj = str(item.get('subject', '')).strip()
            grd = str(item.get('grade', '')).upper().strip()
            if subj:
                lower_subj = subj.lower()
                for abbr, full_name in abbreviation_map.items():
                    if abbr == lower_subj or abbr in lower_subj:
                        subj = full_name
                        break
                clean_electives.append({
                    'subject': subj,
                    'grade': grade_map.get(grd, 4)
                })

    return JsonResponse({
        'success': True,
        'core_grades': core_grades,
        'electives': clean_electives
    })


# =========================================================================
# PHASE 3: STUDENT FEATURES (PDF Report & What-If Grade Simulator)
# =========================================================================

@csrf_exempt
@require_http_methods(["POST"])
def generate_eligibility_pdf(request):
    """
    Generates and returns an official PDF Academic Eligibility Report
    using ReportLab.
    """
    data = parse_json_body(request)
    if not data:
        return JsonResponse({'error': 'Invalid or empty JSON payload'}, status=400)

    pdf_bytes = generate_eligibility_report_pdf(data)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = "CareerPath_Ghana_Eligibility_Report.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@csrf_exempt
@require_http_methods(["POST"])
def grade_simulator(request):
    """
    'What If' Grade Simulator:
    Given a student's current grades and borderline/target programs, calculates
    the minimum grade improvements needed in specific subjects to qualify.
    """
    data = parse_json_body(request)
    core_grades = data.get('core_grades', {})
    if not isinstance(core_grades, dict):
        core_grades = {}
    elective_inputs = data.get('electives', [])
    if not isinstance(elective_inputs, list):
        elective_inputs = []
    target_program_ids = data.get('program_ids', [])
    if not isinstance(target_program_ids, list):
        target_program_ids = []

    programs = Program.objects.filter(id__in=target_program_ids).select_related('university') if target_program_ids else Program.objects.select_related('university').all()[:20]

    simulations = []
    grade_letters = {1: 'A1', 2: 'B2', 3: 'B3', 4: 'C4', 5: 'C5', 6: 'C6', 7: 'D7', 8: 'E8', 9: 'F9'}

    for prog in programs:
        cutoff = prog.aggregate
        if not cutoff:
            continue

        raw_eng = safe_int(core_grades.get('English Language'), default=4)
        raw_math = safe_int(core_grades.get('Core Mathematics'), default=4)
        raw_sci = safe_int(core_grades.get('Integrated Science'), default=4)
        raw_soc = safe_int(core_grades.get('Social Studies'), default=4)
        best_core = min(raw_sci, raw_soc)

        raw_elecs = [safe_int(e.get('grade'), default=4) for e in elective_inputs if isinstance(e, dict) and e.get('grade') is not None]
        sorted_elecs = sorted(raw_elecs) if raw_elecs else [4, 4, 4]
        current_agg = raw_eng + raw_math + best_core + sum(sorted_elecs[:3])

        diff = current_agg - cutoff
        if diff > 0 and diff <= 6:
            recommendations = []
            if raw_math > 1:
                needed_boost = min(diff, raw_math - 1)
                new_grade = raw_math - needed_boost
                recommendations.append({
                    'subject': 'Core Mathematics',
                    'current_grade': grade_letters.get(raw_math, str(raw_math)),
                    'target_grade': grade_letters.get(new_grade, str(new_grade)),
                    'points_saved': needed_boost
                })
            if raw_eng > 1:
                needed_boost = min(diff, raw_eng - 1)
                new_grade = raw_eng - needed_boost
                recommendations.append({
                    'subject': 'English Language',
                    'current_grade': grade_letters.get(raw_eng, str(raw_eng)),
                    'target_grade': grade_letters.get(new_grade, str(new_grade)),
                    'points_saved': needed_boost
                })
            for idx, el in enumerate(elective_inputs[:3]):
                if isinstance(el, dict):
                    g = safe_int(el.get('grade'), default=4)
                    if g > 1:
                        needed_boost = min(diff, g - 1)
                        new_g = g - needed_boost
                        recommendations.append({
                            'subject': el.get('name', f'Elective {idx+1}'),
                            'current_grade': grade_letters.get(g, str(g)),
                            'target_grade': grade_letters.get(new_g, str(new_g)),
                            'points_saved': needed_boost
                        })

            simulations.append({
                'program_id': prog.id,
                'program_name': prog.name,
                'university': prog.university.short_name,
                'cutoff': cutoff,
                'current_aggregate': current_agg,
                'points_needed': diff,
                'recommendations': recommendations[:3]
            })

    return JsonResponse({'simulations': simulations})


# =========================================================================
# PHASE 4: UI MODERNIZATION (Global Search & Program Comparison Matrix)
# =========================================================================

@require_http_methods(["GET"])
def global_search(request):
    """
    Instant search / autocomplete endpoint across programs, universities, and careers.
    """
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'programs': [], 'universities': [], 'careers': []})

    programs = list(Program.objects.filter(
        Q(name__icontains=q) | Q(college__icontains=q)
    ).select_related('university').values(
        'id', 'name', 'university__short_name', 'aggregate', 'campus'
    )[:8])

    universities = list(University.objects.filter(
        Q(name__icontains=q) | Q(short_name__icontains=q) | Q(location__icontains=q)
    ).values('id', 'name', 'short_name', 'location')[:4])

    careers = list(Career.objects.filter(
        Q(name__icontains=q) | Q(description__icontains=q)
    ).values('id', 'name', 'icon')[:4])

    return JsonResponse({
        'programs': programs,
        'universities': universities,
        'careers': careers,
    })


@csrf_exempt
@require_http_methods(["POST"])
def compare_programs(request):
    """
    Returns side-by-side comparison data for 2 to 4 selected programs.
    """
    data = parse_json_body(request)
    program_ids = data.get('program_ids', [])
    if not program_ids or not isinstance(program_ids, list) or len(program_ids) > 5:
        return JsonResponse({'error': 'Please provide between 1 and 5 program IDs to compare.'}, status=400)

    clean_ids = [safe_int(pid, default=None) for pid in program_ids if safe_int(pid, default=None) is not None]
    programs = Program.objects.filter(id__in=clean_ids).select_related('university').prefetch_related(
        'core_subjects',
        'requirements__learning_area',
        'requirements__mandatory_subjects',
        'requirements__elective_subjects'
    )

    comparison = []
    for p in programs:
        req_list = []
        for req in p.requirements.all():
            req_list.append({
                'track': req.learning_area.name if req.learning_area else 'General',
                'mandatory': [s.name for s in req.mandatory_subjects.all()],
                'electives': [s.name for s in req.elective_subjects.all()],
            })

        comparison.append({
            'id': p.id,
            'name': p.name,
            'university': p.university.name,
            'university_short': p.university.short_name,
            'location': p.university.location,
            'duration_years': p.duration_years,
            'cutoff': p.aggregate,
            'campus': p.campus or 'Main Campus',
            'college': p.college or '',
            'min_passing_grade': p.min_passing_grade or 6,
            'core_subjects': [s.name for s in p.core_subjects.all()],
            'requirements': req_list,
            'note': p.note or '',
        })

    return JsonResponse({'comparison': comparison})


@require_http_methods(["GET"])
def health_check(request):
    """
    Lightweight health-check endpoint.
    Performs a simple query against PostgreSQL to keep the connection
    and cloud database instance warm, preventing auto-suspension.
    """
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        return JsonResponse({'status': 'ok', 'database': 'connected'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'database': str(e)}, status=503)
