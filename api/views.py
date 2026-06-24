from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from careers.models import Career, Subject
from eligibility.models import University, Program
import json

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
            })
        data.append({
            'id': uni.id,
            'name': uni.name,
            'short_name': uni.short_name,
            'location': uni.location,
            'programs': programs,
        })
    return JsonResponse({'universities': data})
