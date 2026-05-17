from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('jhs-guide/', views.jhs_guide, name='jhs_guide'),
    path('shs-eligibility/', views.shs_eligibility, name='shs_eligibility'),
    path('roadmap/', views.roadmap, name='roadmap'),
    path('jhs-guide/career/<int:career_id>/', views.career_detail, name='career_detail'),
]
