from .program_data import PROGRAMS_BY_UNI
from django.shortcuts import render
from eligibility.models import Program
from django.db.models import Q

def landing(request):
    unis = ['KNUST', 'UG', 'UCC', 'UDS', 'UENR']
    program_counts = {}
    for uni in unis:
        program_counts[uni] = Program.objects.filter(
            Q(university__short_name__iexact=uni) | Q(university__name__icontains=uni)
        ).count()
    total_programs = Program.objects.count()
    return render(request, 'frontend/landing.html', {
        'unis': unis, 
        'program_counts': program_counts,
        'total_programs': total_programs
    })

def universities(request):
    unis = ['KNUST', 'UG', 'UCC', 'UDS', 'UENR']
    program_counts = {}
    for uni in unis:
        program_counts[uni] = Program.objects.filter(
            Q(university__short_name__iexact=uni) | Q(university__name__icontains=uni)
        ).count()
    total_programs = Program.objects.count()
    return render(request, 'frontend/universities.html', {
        'program_counts': program_counts,
        'total_programs': total_programs
    })

def jhs_guide(request):
    import os
    import dotenv
    dotenv.load_dotenv(override=True)
    gemini_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDnUoGfv6RdAdUDkhFk9zWg3qy1TFzugaQ')
    print("DEBUG: views.py gemini_key =", repr(gemini_key))
    return render(request, 'frontend/jhs_guide.html', {'GEMINI_API_KEY': gemini_key})

def shs_eligibility(request):
    from careers.models import Subject
    core_names = ['Mathematics', 'Core Mathematics', 'English Language', 'Social Studies', 'General Science', 'Integrated Science']
    
    elective_subjects = Subject.objects.exclude(name__in=core_names).order_by('name').distinct()

    return render(request, 'frontend/shs_eligibility.html', {
        'elective_subjects': elective_subjects,
    })

def career_detail(request, career_id):
    from careers.models import Career
    career = Career.objects.prefetch_related("core_subjects","mandatory_electives","recommended_electives").get(id=career_id)
    return render(request, "frontend/career_detail.html", {"career": career})

def roadmap(request):
    return render(request, 'frontend/roadmap.html')

def university_detail(request, uni_key):
    uni_data = {
        'knust': {'name': 'KNUST', 'full': 'Kwame Nkrumah University of Science and Technology', 'location': 'Kumasi, Ashanti Region', 'est': 1952, 'color': '#052e16', 'website': 'https://knust.edu.gh', 'image': 'https://explorekumasi.com/wp-content/uploads/2025/07/kwame-nkrumah-university-ghana.webp', 'thumb': 'https://pbs.twimg.com/media/ErS9PB8WMAA6ZmG.jpg', 'thumb': 'https://pbs.twimg.com/media/ErS9PB8WMAA6ZmG.jpg', 'about': 'Kwame Nkrumah University of Science and Technology (KNUST) is a public research university in Kumasi, the Ashanti Regional capital. Founded in 1952 as the Kumasi College of Technology, it was granted full university status in 1961 and named after Ghana\'s first president, Kwame Nkrumah. KNUST is the largest university in the Ashanti Region and Ghana\'s top-ranked university in West Africa by U.S. News & World Report. Its sprawling 2,500-acre campus houses six semi-autonomous colleges covering engineering, health sciences, agriculture, art, science and social sciences. Notable alumni include UN Secretary-General Kofi Annan and former Vice-President Aliu Mahama.'},
        'ug': {'name': 'UG', 'full': 'University of Ghana', 'location': 'Legon, Accra', 'est': 1948, 'color': '#0c1445', 'website': 'https://ug.edu.gh', 'image': 'https://www.graphic.com.gh/images/2025/jun/26/aaaaUG.jpg', 'thumb': 'https://images.unsplash.com/photo-1762340034235-881592eaa7a3?q=80&w=1672&auto=format&fit=crop', 'thumb': 'https://images.unsplash.com/photo-1762340034235-881592eaa7a3?q=80&w=1672&auto=format&fit=crop', 'about': 'The University of Ghana, founded on August 11, 1948 as the University College of the Gold Coast, is the oldest and largest public university in Ghana. Located in Legon, Accra, it gained full university status by an Act of Parliament in 1961, with Ghana\'s first president Kwame Nkrumah as its first Chancellor. With over 60,000 students, UG operates on a collegiate system covering arts, sciences, social sciences, medicine, agriculture and law. It is a leading research university in Africa and home to distinguished alumni including Nobel Peace Prize laureate Kofi Annan.'},
        'ucc': {'name': 'UCC', 'full': 'University of Cape Coast', 'location': 'Cape Coast, Central Region', 'est': 1962, 'color': '#7f1d1d', 'website': 'https://ucc.edu.gh', 'image': 'https://geshub.org/wp-content/uploads/2023/01/University-of-Cape-Coast-720x375.png', 'about': 'The University of Cape Coast was established in October 1962 as a university college affiliated to the University of Ghana, Legon. It gained full autonomous university status on 1st October 1971. Uniquely situated on a hill overlooking the Atlantic Ocean near the historic Cape Coast Castle, UCC\'s campus is one of the few seafront universities in the world. Originally mandated to train graduate professional teachers, UCC has since expanded into a comprehensive collegiate university covering humanities, science, agriculture, education and health sciences, with over 70,000 students.'},
        'uds': {'name': 'UDS', 'full': 'University for Development Studies', 'location': 'Tamale, Northern Region', 'est': 1992, 'color': '#4c1d95', 'website': 'https://uds.edu.gh', 'image': 'https://uds.edu.gh/logmein/uploads/posts/dc197f2771bc06880a1ee8bbe9570882.jpg', 'about': 'The University for Development Studies (UDS), established in May 1992 by PNDC Law 279, is Ghana\'s first public university in the North and the fifth public university in the country. Headquartered in Tamale, UDS operates across multiple campuses with a unique mission: to blend the academic world with that of the community for the development of northern Ghana and beyond. It began academic work in September 1993 with 39 students in the Faculty of Agriculture at Nyankpala. UDS consistently ranks among Ghana\'s top four universities and runs graduate and undergraduate programmes alongside community outreach activities.'},
        'uenr': {'name': 'UENR', 'full': 'University of Energy and Natural Resources', 'location': 'Sunyani, Bono Region', 'est': 2011, 'color': '#7c2d12', 'website': 'https://uenr.edu.gh', 'image': 'https://i0.wp.com/galexgh.com/wp-content/uploads/2021/09/EoD7M0VW8AAHCIr.jpg', 'about': 'The University of Energy and Natural Resources (UENR) was established by an Act of Parliament (Act 830) on December 31, 2011, making it one of Ghana\'s newest public universities. Located in Sunyani in the Bono Region, UENR is a national institution with a unique focus on energy and natural resource management. It emphasises interdisciplinary research integrating economics, law, policy, science, technology and engineering to tackle Ghana\'s energy and environmental challenges. UENR offers programmes in renewable energy, engineering, agriculture, health sciences and natural resource management.'},
        'uhas': {'name': 'UHAS', 'full': 'University of Health and Allied Sciences', 'location': 'Ho, Volta Region', 'est': 2011, 'color': '#7f1d1d', 'website': 'https://www.uhas.edu.gh', 'image': 'https://upload.wikimedia.org/wikipedia/commons/2/2a/University_of_Health_and_Allied_Sciences.jpg', 'about': 'The University of Health and Allied Sciences (UHAS) is a public university located in Ho, the Volta Regional capital, established in 2011. It is the first public university dedicated wholly to training healthcare professionals in Ghana. UHAS runs seven schools, including the School of Medicine, School of Pharmacy, School of Nursing and Midwifery, and School of Allied Health Sciences, across its Ho and Hohoe campuses.'},
        'upsa': {'name': 'UPSA', 'full': 'University of Professional Studies, Accra', 'location': 'Legon, Accra', 'est': 1965, 'color': '#1e3a8a', 'website': 'https://www.upsa.edu.gh', 'image': 'https://upsa.edu.gh/wp-content/uploads/2021/06/campus-13.jpg', 'thumb': 'https://metrotvonline.com/wp-content/uploads/2023/04/UPSA.jpg', 'about': 'The University of Professional Studies, Accra (UPSA) is a public university specialising in business and professional education. Originally established in 1965, it was granted full university status in 2012. UPSA is renowned for its programmes in accounting, business administration, law, and information technology, blending academic rigour with practical, career-focused training.'},
    }
    uni_data_old = {'knust': {'name': 'KNUST', 'full': 'Kwame Nkrumah University of Science and Technology', 'location': 'Kumasi, Ashanti Region', 'est': 1952, 'color': '#052e16', 'about': 'Kwame Nkrumah University of Science and Technology (KNUST) is a public research university in Kumasi, the Ashanti Regional capital. Founded in 1952 as the Kumasi College of Technology, it was granted full university status in 1961 and named after Ghana\'s first president, Kwame Nkrumah. KNUST is the largest university in the Ashanti Region and Ghana\'s top-ranked university in West Africa by U.S. News & World Report. Its sprawling 2,500-acre campus houses six semi-autonomous colleges covering engineering, health sciences, agriculture, art, science and social sciences. Notable alumni include UN Secretary-General Kofi Annan and former Vice-President Aliu Mahama.'},
        'ug': {'name': 'UG', 'full': 'University of Ghana', 'location': 'Legon, Accra', 'est': 1948, 'color': '#0c1445', 'about': 'The University of Ghana is the oldest and largest university in Ghana, located in Legon, Accra. It offers programs across arts, sciences, social sciences and professional fields.'},
        'ucc': {'name': 'UCC', 'full': 'University of Cape Coast', 'location': 'Cape Coast, Central Region', 'est': 1962, 'color': '#7f1d1d', 'about': 'UCC is a public research university in Cape Coast. It is known for teacher education and offers a wide range of programs in arts, sciences and professional studies.'},
        'uds': {'name': 'UDS', 'full': 'University for Development Studies', 'location': 'Tamale, Northern Region', 'est': 1992, 'color': '#4c1d95', 'about': 'UDS was established to integrate the university into the community for development. It focuses on development-oriented programs and serves northern Ghana.'},
        'uenr': {'name': 'UENR', 'full': 'University of Energy and Natural Resources', 'location': 'Sunyani, Bono Region', 'est': 2011, 'color': '#7c2d12', 'about': 'UENR focuses on energy and natural resources education and research. It is one of the newer technical universities in Ghana located in Sunyani.'},
    }
    
    uni = uni_data.get(uni_key.lower())
    if not uni:
        from django.http import Http404
        raise Http404
    
    uni_name = uni['name']
    
    from eligibility.models import University, Program
    from django.db.models import Q

    if uni_obj:
        if uni_obj.name:
            uni['full'] = uni_obj.name
        if uni_obj.location:
            uni['location'] = uni_obj.location
        if uni_obj.website:
            uni['website'] = uni_obj.website
        if uni_obj.about:
            uni['about'] = uni_obj.about
        if uni_obj.image:
            uni['image'] = uni_obj.image
        if uni_obj.thumbnail:
            uni['thumb'] = uni_obj.thumbnail
        uni['academic_year_start'] = uni_obj.academic_year_start or 'September 2026'
        uni['application_deadline'] = uni_obj.application_deadline or 'June 2026'
        if uni_obj.entry_requirements and uni_obj.entry_requirements.strip():
            uni['entry_requirements_list'] = [line.strip() for line in uni_obj.entry_requirements.splitlines() if line.strip()]
        programs_qs = Program.objects.filter(university=uni_obj)
    else:
        uni['academic_year_start'] = 'September 2026'
        uni['application_deadline'] = 'June 2026'
        programs_qs = Program.objects.filter(
            Q(university__short_name__iexact=uni_name) | Q(university__short_name__iexact=uni_key)
        )

    programs_qs = programs_qs.prefetch_related(
        'core_subjects',
        'requirements__learning_area',
        'requirements__mandatory_subjects',
        'requirements__elective_subjects'
    )

    programs = list(programs_qs)
    programs.sort(key=lambda p: (p.college or 'ZZZ', p.name.lower()))

    grouped_programs_raw = {}
    for p in programs:
        col_name = p.college.strip() if p.college and p.college.strip() else 'General Programmes'
        if col_name not in grouped_programs_raw:
            grouped_programs_raw[col_name] = []
        
        reqs = []
        for req in p.requirements.all():
            reqs.append({
                'learning_area': req.learning_area.name if req.learning_area else 'General Track',
                'mandatory': [s.name for s in req.mandatory_subjects.all()],
                'electives': [s.name for s in req.elective_subjects.all()]
            })

        grouped_programs_raw[col_name].append({
            'id': p.id,
            'name': p.name,
            'college': col_name,
            'campus': p.campus or 'Main Campus',
            'duration_years': p.duration_years,
            'aggregate': p.aggregate,
            'year': p.year or 2024,
            'note': p.note or '',
            'core_subjects': [s.name for s in p.core_subjects.all()],
            'requirements': reqs
        })

    # Sort colleges alphabetically and sort programs alphabetically inside each college
    grouped_programs = dict(sorted(grouped_programs_raw.items(), key=lambda x: x[0].lower()))
    for col_name in grouped_programs:
        grouped_programs[col_name].sort(key=lambda item: item['name'].lower())

    import json
    program_map = {}
    for col, p_list in grouped_programs.items():
        for p in p_list:
            program_map[str(p['id'])] = p

    return render(request, 'frontend/university_detail.html', {
        'uni': uni,
        'programs': programs,
        'grouped_programs': grouped_programs,
        'program_map_json': json.dumps(program_map),
    })
