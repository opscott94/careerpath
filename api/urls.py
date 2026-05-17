from django.urls import path
from . import views

urlpatterns = [
    path('career-search/', views.career_search, name='career_search'),
    path('subject-recommendation/', views.subject_recommendation, name='subject_recommendation'),
    path('wassce-check/', views.wassce_check, name='wassce_check'),
    path('universities/', views.universities_list, name='universities_list'),
]
