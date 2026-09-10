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
    try:
        data = json.loads(request.body)
    except Exception:
        data = {}

    from django.db.models import Q
    from django.conf import settings
    import urllib.request
    import os
    import re

    try:
        from google.oauth2 import service_account
        import google.auth.transport.requests
        has_google_auth = True
    except ImportError:
        has_google_auth = False
        service_account = None

    raw_query = data.get('query', '').strip()
    if not raw_query:
        return JsonResponse({'error': 'No query provided'}, status=400)

    # Clean conversational query prefixes ("I want to be a nurse" -> "nurse", "I want to build airplanes" -> "airplanes")
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

    gcp_json_str = os.getenv('GCP_KEY_JSON')
    key_path = os.path.join(settings.BASE_DIR, 'gcp-key.json')

    creds = None
    if has_google_auth and gcp_json_str:
        try:
            info = json.loads(gcp_json_str)
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        except Exception as e:
            print(f"DEBUG: Failed to parse GCP_KEY_JSON env var: {e}")

    if has_google_auth and not creds and os.path.exists(key_path):
        try:
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)
        except Exception as e:
            print(f"DEBUG: Failed to load gcp-key.json file: {e}")

    # Domain Knowledge Fallback Map for Ghanaian University Programs
    def get_domain_fallback(q_term):
        q = q_term.lower()
        if any(k in q for k in ['health field', 'healthcare', 'health care', 'health sector', 'allied health', 'health science', 'health sciences', 'health career', 'medical field']):
            return {
                'career_name': 'Healthcare & Allied Health Practitioner',
                'career_description': 'Healthcare and Allied Health specialists deliver clinical nursing, rehabilitation therapy, medical diagnostics, nutritional guidance, healthcare data systems, and public health disease prevention across hospitals and community health centres.',
                'primary_keywords': ['Nursing', 'Midwifery', 'Physiotherapy', 'Dietetics', 'Health Information', 'Public Health', 'Water and Public Health Engineering', 'Medical Laboratory', 'Medical Imaging', 'Public Health Nursing'],
                'secondary_keywords': ['Biology', 'Chemistry', 'Health', 'General Science'],
                'explanations': {
                    'Nursing': 'Direct degree program training students in clinical nursing skills and hospital patient care.',
                    'Midwifery': 'Direct degree specializing in maternal, prenatal, and infant healthcare.',
                    'Physiotherapy': 'Specialized clinical path in physical rehabilitation and movement recovery therapy.',
                    'Dietetics': 'Specialized clinical path focusing on human nutrition, dietary planning, and metabolic health.',
                    'Health Information': 'Covers medical records informatics, health statistics, and healthcare data systems.',
                    'Public Health': 'Focuses on epidemiology, community hygiene, sanitation, and disease prevention programs.',
                    'Water and Public Health Engineering': 'Direct engineering degree for potable water supply, environmental health, and municipal sanitation.',
                    'Medical Laboratory': 'Direct clinical diagnostic pathology and laboratory disease analysis.'
                }
            }
        elif 'physiotherap' in q or 'physical therap' in q:
            return {
                'career_name': 'Physiotherapist / Physical Rehabilitation Specialist',
                'career_description': 'Physiotherapists assess, treat, and rehabilitate patients with movement disorders, sports injuries, neurological conditions, and physical disabilities.',
                'primary_keywords': ['Physiotherapy', 'Physical Therapy'],
                'secondary_keywords': ['Biology', 'Physics', 'Health', 'Medical'],
                'explanations': {
                    'Physiotherapy': 'Direct clinical degree preparing physical rehabilitation and movement specialists.',
                    'Physical Therapy': 'Direct degree path in physical rehabilitation.'
                }
            }
        elif 'dietetic' in q or 'dietitian' in q or 'nutritionist' in q or 'nutrition' in q:
            return {
                'career_name': 'Clinical Dietitian / Nutrition Specialist',
                'career_description': 'Dietitians and Nutritionists assess nutritional needs, formulate clinical diets, manage metabolic disorders, and promote public nutritional wellness.',
                'primary_keywords': ['Dietetics', 'Food Science and Technology', 'Human Nutrition', 'Nutrition'],
                'secondary_keywords': ['Chemistry', 'Biology', 'Health'],
                'explanations': {
                    'Dietetics': 'Direct clinical degree in therapeutic nutrition and clinical dietetics.',
                    'Food Science and Technology': 'Covers food chemistry, nutritional processing, and food safety.'
                }
            }
        elif 'nurse' in q or 'nursing' in q or 'midwife' in q or 'midwifery' in q:
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
        elif any(k in q for k in ['pilot', 'aviation', 'aero', 'airplane', 'airplanes', 'aeroplane', 'aeroplanes', 'aircraft', 'aircrafts', 'flight', 'plane', 'planes', 'aerospace', 'rocket']):
            return {
                'career_name': 'Aerospace / Aeronautical Engineer',
                'career_description': 'Aerospace and Aeronautical Engineers design, test, build, and maintain aircraft, spacecraft, avionics systems, and flight hardware.',
                'primary_keywords': ['Aerospace', 'Aeronautical', 'Mechanical Engineering'],
                'secondary_keywords': ['Physics', 'Electrical', 'Mathematics'],
                'explanations': {
                    'Aerospace': 'Direct engineering path for aircraft and propulsion system design.',
                    'Aeronautical': 'Specialized engineering field focused on flight and aircraft design.',
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
        elif any(k in q for k in ['account', 'accounting', 'accountant', 'finance', 'business', 'banking', 'auditor']):
            return {
                'career_name': 'Accountant / Financial Auditor',
                'career_description': 'Accountants and Financial Auditors manage financial records, prepare balance sheets, perform audit verifications, and analyze business financial performance.',
                'primary_keywords': ['Accounting', 'Business Administration', 'Finance'],
                'secondary_keywords': ['Economics', 'Management', 'Business'],
                'explanations': {
                    'Accounting': 'Direct degree program preparing students for chartered accounting and financial management.',
                    'Business Administration': 'Provides broad business, management, and financial education.',
                    'Finance': 'Focuses on financial markets, corporate finance, and investment analysis.'
                }
            }
        elif any(k in q for k in ['journalism', 'journalist', 'reporter', 'media', 'broadcasting', 'broadcast', 'news', 'communication', 'writer']):
            return {
                'career_name': 'Journalist / Media & Communications Specialist',
                'career_description': 'Journalists and Media Specialists research stories, write news articles, produce broadcast programs, and communicate critical information across digital, television, radio, and print platforms.',
                'primary_keywords': ['Communication Studies', 'Journalism', 'Media', 'English', 'Public Relations'],
                'secondary_keywords': ['Political Science', 'Sociology', 'History', 'Theatre Arts', 'Information Studies'],
                'explanations': {
                    'Communication Studies': 'Direct degree pathway covering news broadcasting, media writing, and public communication.',
                    'Journalism': 'Direct degree track specializing in news reporting, photojournalism, and investigative media.',
                    'English': 'Builds advanced writing, grammar, and literary communication fundamentals essential for journalism.',
                    'Political Science': 'Provides deep understanding of government, policy, and public affairs reporting.'
                }
            }
        elif any(k in q for k in ['civil', 'bridge', 'structural', 'construction engineer', 'roads', 'infrastructure']):
            return {
                'career_name': 'Civil & Structural Engineer',
                'career_description': 'Civil and Structural Engineers plan, design, and oversee construction of essential infrastructure including roads, bridges, water supply systems, and tall buildings.',
                'primary_keywords': ['Civil Engineering', 'Geomatic', 'Construction Technology'],
                'secondary_keywords': ['Physics', 'Mathematics', 'Engineering'],
                'explanations': {
                    'Civil Engineering': 'Direct engineering degree for infrastructure, structural design, and urban works.',
                    'Geomatic': 'Specialized survey engineering for land spatial analysis and construction.',
                    'Construction Technology': 'Provides management and construction science foundations.'
                }
            }
        elif any(k in q for k in ['plant', 'crop', 'farm', 'farming', 'agriculture', 'agronomy', 'soil', 'agric', 'animal science', 'horticulture']):
            return {
                'career_name': 'Agricultural Scientist / Agronomist',
                'career_description': 'Agricultural Scientists and Agronomists improve crop yields, manage livestock health, innovate sustainable farming techniques, and safeguard food security.',
                'primary_keywords': ['Agriculture', 'Agricultural', 'Agribusiness', 'Post Harvest', 'Forest Resources'],
                'secondary_keywords': ['Biology', 'Chemistry', 'General Science'],
                'explanations': {
                    'Agriculture': 'Comprehensive degree covering crop science, soil fertility, and agricultural systems.',
                    'Agricultural': 'Applied agricultural technology and production sciences.',
                    'Agribusiness': 'Combines agricultural knowledge with business management and economics.'
                }
            }
        elif any(k in q for k in ['cyber', 'security', 'hack', 'network', 'information security', 'malware', 'firewall']):
            return {
                'career_name': 'Cybersecurity Analyst / Network Engineer',
                'career_description': 'Cybersecurity Analysts protect networks, cloud systems, and data infrastructure against cyber threats, security breaches, and unauthorized intrusion.',
                'primary_keywords': ['Computer Science', 'Information Technology', 'Telecommunication Engineering', 'Computer Engineering'],
                'secondary_keywords': ['Mathematics', 'Physics', 'Computing'],
                'explanations': {
                    'Computer Science': 'Core degree providing programming, network architecture, and cryptography algorithms.',
                    'Information Technology': 'Covers systems administration, network security, and enterprise database infrastructure.',
                    'Telecommunication Engineering': 'Focuses on network hardware, data communications, and signal transmission security.'
                }
            }
        elif any(k in q for k in ['robot', 'robotics', 'automation', 'mechatronics', 'automated machine']):
            return {
                'career_name': 'Robotics & Automation Engineer',
                'career_description': 'Robotics and Automation Engineers design, program, and build robotic devices, autonomous systems, and industrial automated machinery.',
                'primary_keywords': ['Mechanical Engineering', 'Electrical/Electronic Engineering', 'Computer Engineering', 'Biomedical Engineering'],
                'secondary_keywords': ['Physics', 'Mathematics', 'Computer Science'],
                'explanations': {
                    'Mechanical Engineering': 'Provides mechanical design, kinematics, and dynamic systems engineering foundations.',
                    'Electrical/Electronic Engineering': 'Covers microcontrollers, sensors, power electronics, and robotic motor control.',
                    'Computer Engineering': 'Bridges hardware and software for embedded system robotics programming.'
                }
            }
        elif any(k in q for k in ['dna', 'genetics', 'medical laboratory', 'biomedical', 'laboratory disease', 'clinical lab', 'pathology']):
            return {
                'career_name': 'Biomedical Scientist / Medical Lab Specialist',
                'career_description': 'Biomedical Scientists conduct clinical diagnostic laboratory tests, investigate disease mechanisms, analyze genetic markers, and develop medical therapies.',
                'primary_keywords': ['Medical Laboratory', 'Biomedical Science', 'Biochemistry', 'Biological Science', 'Molecular'],
                'secondary_keywords': ['Chemistry', 'Biology', 'Health'],
                'explanations': {
                    'Medical Laboratory': 'Direct clinical degree for diagnostic testing, pathology analysis, and lab practice.',
                    'Biomedical Science': 'Prepares students for advanced biomedical research and therapeutic development.',
                    'Biochemistry': 'Provides deep chemical and molecular understanding of biological systems.'
                }
            }
        elif any(k in q for k in ['hotel', 'hospitality', 'tourism', 'events', 'resort', 'travel']):
            return {
                'career_name': 'Hospitality & Tourism Manager',
                'career_description': 'Hospitality and Tourism Managers oversee international hotel operations, resort destinations, event planning, and guest experience logistics.',
                'primary_keywords': ['Hospitality', 'Tourism', 'Business Administration', 'Marketing', 'Management'],
                'secondary_keywords': ['Economics', 'Languages', 'French'],
                'explanations': {
                    'Hospitality': 'Direct degree covering hotel management, food service operations, and customer experience.',
                    'Tourism': 'Specialized program in ecotourism, travel agency operations, and destination management.',
                    'Business Administration': 'Provides strategic management, finance, and marketing foundations.'
                }
            }
        elif any(k in q for k in ['electric', 'electrical', 'solar', 'renewable energy', 'power', 'grid', 'energy']):
            return {
                'career_name': 'Electrical & Renewable Energy Engineer',
                'career_description': 'Electrical and Renewable Energy Engineers design power generation facilities, solar energy systems, national electric grids, and electronic devices.',
                'primary_keywords': ['Electrical/Electronic Engineering', 'Renewable Energy', 'Energy Systems', 'Physics'],
                'secondary_keywords': ['Mathematics', 'Mechanical Engineering'],
                'explanations': {
                    'Electrical/Electronic Engineering': 'Direct engineering degree covering power systems, circuit design, and electromagnetics.',
                    'Renewable Energy': 'Specialized path focused on solar, wind, biomass, and sustainable power grids.',
                    'Physics': 'Provides deep theoretical electromagnetic and quantum foundations.'
                }
            }
        elif any(k in q for k in ['teach', 'teacher', 'teaching', 'education', 'lecturer', 'tutor']):
            return {
                'career_name': 'Professional Educator / High School Teacher',
                'career_description': 'Professional Educators deliver instruction, inspire students in specialized subjects, design curricula, and foster academic development.',
                'primary_keywords': ['Education', 'B.Ed.', 'Teacher'],
                'secondary_keywords': ['Arts', 'Science', 'Mathematics', 'English'],
                'explanations': {
                    'Education': 'Direct Bachelor of Education degree equipping teachers with pedagogy and subject mastery.',
                    'B.Ed.': 'Official teaching qualification in Ghana.'
                }
            }
        return None

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

        # 1. Try Vertex AI with GCP Credentials
        if creds:
            try:
                auth_req = google.auth.transport.requests.Request()
                creds.refresh(auth_req)
                token = creds.token
                project_id = creds.project_id

                for model_name in ["gemini-1.5-flash", "gemini-1.5-pro"]:
                    url = f"https://firebasevertexai.googleapis.com/v1beta/projects/{project_id}/locations/us-central1/publishers/google/models/{model_name}:generateContent"
                    try:
                        req_obj = urllib.request.Request(
                            url,
                            data=json.dumps(payload).encode("utf-8"),
                            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                            method="POST"
                        )
                        with urllib.request.urlopen(req_obj, timeout=3) as response:
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
                        continue
            except Exception as e:
                pass

        # 2. Fallback to Gemini Developer API Key if Vertex AI failed or creds not available
        if not parsed:
            gemini_key = os.getenv('GEMINI_API_KEY')
            for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                try:
                    req_obj = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req_obj, timeout=3) as response:
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
                    continue

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
        top_groups = (primary_groups[:15] + secondary_groups[:5])[:15]

        if top_groups:
            matched = []
            for g in top_groups:
                matched.append({
                    'program_name': g['name'],
                    'universities': ", ".join(sorted(list(g['universities']))),
                    'reason': g['reason'],
                })

            # Aggregate SHS Elective Requirements Summary
            # If direct pathways exist, pick exclusively from direct pathways; else fallback to secondary pathways
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

            return JsonResponse({
                'ai_match': True,
                'career_name': career_name,
                'career_description': career_description,
                'elective_summary': elective_summary,
                'matched_programs': matched,
            })

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
def career_outlook(request):
    """
    AI-generated career outlook for a specific university degree program.
    Returns a 2-3 sentence Ghana-specific career description covering job roles,
    key employers, and relevant industries.
    """
    from django.conf import settings
    import urllib.request
    import os

    try:
        from google.oauth2 import service_account
        import google.auth.transport.requests
        has_google_auth = True
    except ImportError:
        has_google_auth = False
        service_account = None

    data = json.loads(request.body)
    program_name = data.get('program_name', '').strip()
    if not program_name:
        return JsonResponse({'error': 'No program_name provided'}, status=400)

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

    result_text = None

    # 1. Try GCP credentials (Vertex AI)
    gcp_json_str = os.getenv('GCP_KEY_JSON')
    key_path = os.path.join(settings.BASE_DIR, 'gcp-key.json')
    creds = None

    if has_google_auth and gcp_json_str:
        try:
            info = json.loads(gcp_json_str)
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        except Exception:
            pass

    if has_google_auth and not creds and os.path.exists(key_path):
        try:
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)
        except Exception:
            pass

    if creds:
        try:
            auth_req = google.auth.transport.requests.Request()
            creds.refresh(auth_req)
            token = creds.token
            project_id = creds.project_id
            url = f"https://firebasevertexai.googleapis.com/v1beta/projects/{project_id}/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent"
            req_obj = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                method="POST"
            )
            with urllib.request.urlopen(req_obj, timeout=8) as response:
                res_data = json.loads(response.read().decode())
                candidates = res_data.get("candidates", [])
                if candidates:
                    result_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        except Exception as e:
            print(f"DEBUG: career_outlook Vertex AI failed: {e}")

    # 2. Fallback to Gemini Developer API
    if not result_text:
        gemini_key = os.getenv('GEMINI_API_KEY')
        for model_name in ["gemini-2.5-flash", "gemini-3.6-flash", "gemini-flash-latest", "gemini-3.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash"]:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
            try:
                req_obj = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req_obj, timeout=8) as response:
                    res_data = json.loads(response.read().decode())
                    candidates = res_data.get("candidates", [])
                    if candidates:
                        result_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        if result_text:
                            break
            except Exception as e:
                print(f"DEBUG: career_outlook Gemini API {model_name} failed: {e}")
                continue

    # 3. Fallback to generic template
    if not result_text:
        result_text = f"Graduates of {program_name} are well-positioned for professional roles across both public and private sectors in Ghana and internationally. Career opportunities span government agencies, corporate organizations, research institutions, and NGOs that align with this field of study."

    return JsonResponse({'career_outlook': result_text})

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
    Takes a student's core and elective subjects + WASSCE grades (or is_awaiting flag),
    calculates Best 6 aggregate (if graded) or evaluates subject track eligibility
    (if awaiting results) across all university degree programs.

    Grading is university-specific: e.g. KNUST treats C4, C5, C6 all as 4 points.
    Passing threshold is program-specific: most require C6 (6), some accept D7 (7).
    """
    data = json.loads(request.body)
    is_awaiting = data.get('is_awaiting', False)
    core_grades = data.get('core_grades', {})
    elective_inputs = data.get('electives', [])

    if is_awaiting:
        user_elective_names = [e.get('name', '').strip().lower() for e in elective_inputs if e.get('name')]
        if len(user_elective_names) < 3:
            return JsonResponse({'error': 'Please select at least 3 elective subjects for subject eligibility checking.'}, status=400)
        
        # Placeholder values for awaiting mode (no grades to evaluate)
        raw_eng = 1
        raw_math = 1
        raw_sci = 1
        raw_soc = 1
        raw_electives = []
        aggregate = None
    else:
        raw_eng = int(core_grades.get('English Language', 9))
        raw_math = int(core_grades.get('Core Mathematics', 9))
        raw_sci = int(core_grades.get('Integrated Science', 9))
        raw_soc = int(core_grades.get('Social Studies', 9))

        # Collect ALL electives with their raw grades (filter per-program later)
        raw_electives = []
        for e in elective_inputs:
            name = e.get('name', '').strip()
            grade = e.get('grade')
            if name and grade:
                raw_electives.append({'name': name, 'grade': int(grade)})

        # Standard aggregate for display purposes (uses standard grading scale)
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

    # Map normalized user electives
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

        # Check core passing using this program's minimum passing grade
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
            # Evaluate subject track matching for awaiting mode
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
            # Graded mode: calculate core points
            u_eng = uni.get_point(raw_eng)
            u_math = uni.get_point(raw_math)
            u_sci = uni.get_point(raw_sci)
            u_soc = uni.get_point(raw_soc)

            # Science, Health, Engineering & IT programs strictly require Integrated Science
            requires_science_core = (category in ['science', 'health', 'engineering', 'computing']) or \
                                    any(c.name.strip().lower() == 'integrated science' for c in p.core_subjects.all())
            
            if requires_science_core:
                if raw_sci > min_pass:
                    continue  # Integrated Science pass is mandatory for science-based degree programs
                u_3rd_core = u_sci
            else:
                u_3rd_core = min(u_sci, u_soc)

            core_sum = u_eng + u_math + u_3rd_core

            if not requirements.exists():
                # General entry without specific requirement routes
                passing_grades = sorted([uni.get_point(g) for g in user_elec_dict.values() if g <= min_pass])
                if len(passing_grades) >= 3:
                    best_prog_aggregate = core_sum + sum(passing_grades[:3])
                    is_qualified = True
            else:
                for req in requirements:
                    la_name = (req.learning_area.name.lower() if req.learning_area else '').strip()
                    m_subs = [norm_sub(s.name) for s in req.mandatory_subjects.all()]
                    e_subs = [norm_sub(s.name) for s in req.elective_subjects.all()]

                    # Check mandatory electives
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

                    # Number of additional electives needed to form 3 electives
                    needed = max(0, 3 - len(m_points))

                    # Remaining available passing electives
                    rem_candidates = []
                    for sub_name, grade in user_elec_dict.items():
                        if sub_name not in used_subs and grade <= min_pass:
                            priority = 0
                            if e_subs and sub_name in e_subs:
                                priority = -1  # prioritized elective
                            rem_candidates.append((priority, uni.get_point(grade), sub_name))

                    rem_candidates.sort(key=lambda x: (x[0], x[1]))

                    if len(m_points) + len(rem_candidates) < 3:
                        continue  # Cannot form 3 electives for this route

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
                'margin': (cutoff - prog_aggregate) if (cutoff and prog_aggregate) else None,
                'category': category,
                'core_subjects': core_subjects,
                'requirements': req_list,
            })

    results.sort(key=lambda x: (not x['is_eligible'], not x['is_borderline'], x['cutoff'] or 999))

    label = 'Awaiting WASSCE Results' if is_awaiting else ('Outstanding' if aggregate <= 8 else 'Excellent' if aggregate <= 12 else 'Very Good' if aggregate <= 18 else 'Good' if aggregate <= 24 else 'Fair')

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
    import base64
    from django.conf import settings
    import urllib.request
    import os

    try:
        from google.oauth2 import service_account
        import google.auth.transport.requests
        has_google_auth = True
    except ImportError:
        has_google_auth = False
        service_account = None

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
    if has_google_auth and gcp_json_str:
        try:
            info = json.loads(gcp_json_str)
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        except Exception as e:
            print(f"DEBUG: Failed to parse GCP_KEY_JSON env var: {e}")

    if has_google_auth and not creds and os.path.exists(key_path):
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
            print(f"DEBUG: OCR Vertex AI auth failed: {e}")

    # 2. Fallback to Gemini Developer API Key if Vertex AI failed or creds not available
    if not parsed:
        gemini_key = os.getenv('GEMINI_API_KEY')
        for model_name in ["gemini-2.5-flash", "gemini-3.6-flash", "gemini-flash-latest", "gemini-3.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash"]:
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

