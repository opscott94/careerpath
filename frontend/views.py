from django.shortcuts import render

def landing(request):
    unis = ['KNUST', 'UG', 'UCC', 'UDS', 'UENR']
    return render(request, 'frontend/landing.html', {'unis': unis})

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
        'knust': {'name': 'KNUST', 'full': 'Kwame Nkrumah University of Science and Technology', 'location': 'Kumasi, Ashanti Region', 'est': 1952, 'color': '#052e16', 'website': 'https://knust.edu.gh', 'image': 'https://treck.knust.edu.gh/sites/default/files/styles/large/public/2020-04/covid-19-notice.jpg?itok=JcsOOXdY', 'about': 'KNUST is a public research university located in Kumasi. It is the second oldest public university in Ghana and focuses on science, technology, engineering and mathematics.'},
        'ug': {'name': 'UG', 'full': 'University of Ghana', 'location': 'Legon, Accra', 'est': 1948, 'color': '#0c1445', 'website': 'https://ug.edu.gh', 'image': 'https://www.graphic.com.gh/images/2025/jun/26/aaaaUG.jpg', 'about': 'The University of Ghana is the oldest and largest university in Ghana, located in Legon, Accra. It offers programs across arts, sciences, social sciences and professional fields.'},
        'ucc': {'name': 'UCC', 'full': 'University of Cape Coast', 'location': 'Cape Coast, Central Region', 'est': 1962, 'color': '#7f1d1d', 'website': 'https://ucc.edu.gh', 'image': 'https://geshub.org/wp-content/uploads/2023/01/University-of-Cape-Coast-720x375.png', 'about': 'UCC is a public research university in Cape Coast. It is known for teacher education and offers a wide range of programs in arts, sciences and professional studies.'},
        'uds': {'name': 'UDS', 'full': 'University for Development Studies', 'location': 'Tamale, Northern Region', 'est': 1992, 'color': '#4c1d95', 'website': 'https://uds.edu.gh', 'image': 'https://uds.edu.gh/logmein/uploads/posts/dc197f2771bc06880a1ee8bbe9570882.jpg', 'about': 'UDS was established to integrate the university into the community for development. It focuses on development-oriented programs and serves northern Ghana.'},
        'uenr': {'name': 'UENR', 'full': 'University of Energy and Natural Resources', 'location': 'Sunyani, Bono Region', 'est': 2011, 'color': '#7c2d12', 'website': 'https://uenr.edu.gh', 'image': 'https://i0.wp.com/galexgh.com/wp-content/uploads/2021/09/EoD7M0VW8AAHCIr.jpg', 'about': 'UENR focuses on energy and natural resources education and research. It is one of the newer technical universities in Ghana located in Sunyani.'},
    }
    uni_data_old = {'knust': {'name': 'KNUST', 'full': 'Kwame Nkrumah University of Science and Technology', 'location': 'Kumasi, Ashanti Region', 'est': 1952, 'color': '#052e16', 'about': 'KNUST is a public research university located in Kumasi. It is the second oldest public university in Ghana and focuses on science, technology, engineering and mathematics.'},
        'ug': {'name': 'UG', 'full': 'University of Ghana', 'location': 'Legon, Accra', 'est': 1948, 'color': '#0c1445', 'about': 'The University of Ghana is the oldest and largest university in Ghana, located in Legon, Accra. It offers programs across arts, sciences, social sciences and professional fields.'},
        'ucc': {'name': 'UCC', 'full': 'University of Cape Coast', 'location': 'Cape Coast, Central Region', 'est': 1962, 'color': '#7f1d1d', 'about': 'UCC is a public research university in Cape Coast. It is known for teacher education and offers a wide range of programs in arts, sciences and professional studies.'},
        'uds': {'name': 'UDS', 'full': 'University for Development Studies', 'location': 'Tamale, Northern Region', 'est': 1992, 'color': '#4c1d95', 'about': 'UDS was established to integrate the university into the community for development. It focuses on development-oriented programs and serves northern Ghana.'},
        'uenr': {'name': 'UENR', 'full': 'University of Energy and Natural Resources', 'location': 'Sunyani, Bono Region', 'est': 2011, 'color': '#7c2d12', 'about': 'UENR focuses on energy and natural resources education and research. It is one of the newer technical universities in Ghana located in Sunyani.'},
    }
    
    cutoffs = {
        'Medicine & Surgery (MBChB)': {'KNUST':6, 'UG':8, 'UCC':9, 'UDS':6, 'UENR':8},
        'Doctor of Pharmacy (Pharm D)': {'KNUST':6, 'UG':10, 'UCC':12, 'UDS':6, 'UENR':10},
        'BSc Nursing': {'KNUST':7, 'UG':12, 'UCC':9, 'UDS':6, 'UENR':15},
        'BSc Midwifery': {'KNUST':8, 'UG':12, 'UCC':9},
        'BSc Medical Laboratory Science': {'KNUST':7, 'UG':12, 'UDS':6, 'UENR':12},
        'Bachelor of Dental Surgery (BDS)': {'KNUST':6},
        'BSc Physiotherapy': {'KNUST':12, 'UENR':14},
        'BSc Dietetics': {'KNUST':9, 'UG':14, 'UCC':16, 'UENR':14},
        'BSc Civil Engineering': {'KNUST':7, 'UDS':6, 'UENR':6},
        'BSc Mechanical Engineering': {'KNUST':7, 'UDS':6, 'UENR':6},
        'BSc Electrical/Electronic Engineering': {'KNUST':6, 'UDS':6, 'UENR':6},
        'BSc Biomedical Engineering': {'KNUST':6, 'UG':6, 'UENR':6},
        'BSc Computer Engineering': {'KNUST':6, 'UDS':6, 'UENR':7},
        'BSc Chemical Engineering': {'KNUST':7, 'UG':18},
        'BSc Computer Science': {'KNUST':7, 'UG':15, 'UDS':6, 'UENR':7},
        'BSc Information Technology': {'KNUST':10, 'UG':15, 'UENR':10},
        'BSc Business Admin (Accounting)': {'KNUST':7, 'UG':15},
        'BSc Business Admin (Marketing)': {'KNUST':9},
        'LLB Bachelor of Laws': {'KNUST':6, 'UG':12, 'UENR':7},
        'BSc/BA Economics': {'KNUST':10, 'UG':16, 'UDS':6, 'UENR':6},
        'BSc Biochemistry': {'KNUST':9, 'UG':16},
        'BSc Mathematics': {'KNUST':8, 'UG':14, 'UDS':6},
        'BSc Chemistry': {'KNUST':9, 'UG':15},
        'BSc Agriculture': {'KNUST':12, 'UG':18, 'UDS':6, 'UENR':10},
        'BSc Agribusiness': {'KNUST':12, 'UG':18, 'UDS':6},
    }
    
    uni = uni_data.get(uni_key.lower())
    if not uni:
        from django.http import Http404
        raise Http404
    
    uni_name = uni['name']
    programs = [(prog, co) for prog, cos in cutoffs.items() if uni_name in cos for co in [cos[uni_name]]]
    programs.sort(key=lambda x: x[1])
    
    return render(request, 'frontend/university_detail.html', {
        'uni': uni,
        'programs': programs,
    })
