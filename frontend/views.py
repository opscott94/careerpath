from .program_data import PROGRAMS_BY_UNI
from django.shortcuts import render

def landing(request):
    unis = ['KNUST', 'UG', 'UCC', 'UDS', 'UENR']
    program_counts = {
        uni: sum(len(entries) for entries in PROGRAMS_BY_UNI.get(uni, {}).values())
        for uni in unis
    }
    return render(request, 'frontend/landing.html', {'unis': unis, 'program_counts': program_counts})

def jhs_guide(request):
    import os
    import dotenv
    dotenv.load_dotenv(override=True)
    gemini_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDnUoGfv6RdAdUDkhFk9zWg3qy1TFzugaQ')
    print("DEBUG: views.py gemini_key =", repr(gemini_key))
    return render(request, 'frontend/jhs_guide.html', {'GEMINI_API_KEY': gemini_key})

def shs_eligibility(request):
    return render(request, 'frontend/shs_eligibility.html')

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
    programs = []
    for category, entries in PROGRAMS_BY_UNI.get(uni_name, {}).items():
        for entry in entries:
            name = entry[0]
            cutoff = entry[1]
            note = entry[2] if len(entry) > 2 else None
            display = cutoff if cutoff is not None else (note or 'N/A')
            programs.append((name, display))

    def _sort_key(item):
        val = item[1]
        return (0, val) if isinstance(val, int) else (1, str(val))
    programs.sort(key=_sort_key)
    
    return render(request, 'frontend/university_detail.html', {
        'uni': uni,
        'programs': programs,
    })
