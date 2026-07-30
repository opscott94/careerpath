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
