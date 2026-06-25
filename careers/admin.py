from django.contrib import admin
from .models import LearningArea, Subject, Career, CareerRecommendationReason, SubjectLearningArea

class SubjectLearningAreaInline(admin.TabularInline):
    model = SubjectLearningArea
    extra = 1

@admin.register(LearningArea)
class LearningAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_type']
    list_filter = ['school_type']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'is_mandatory', 'is_externally_examinable']
    list_filter = ['group', 'learning_areas', 'is_mandatory']
    search_fields = ['name']
    inlines = [SubjectLearningAreaInline]

@admin.register(SubjectLearningArea)
class SubjectLearningAreaAdmin(admin.ModelAdmin):
    list_display = ['subject', 'learning_area', 'group']
    list_filter = ['group', 'learning_area']

class ReasonInline(admin.TabularInline):
    model = CareerRecommendationReason
    extra = 1

@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'learning_area']
    list_filter = ['learning_area']
    search_fields = ['name', 'keywords']
    filter_horizontal = ['core_subjects', 'mandatory_electives', 'recommended_electives']
    inlines = [ReasonInline]

@admin.register(CareerRecommendationReason)
class CareerRecommendationReasonAdmin(admin.ModelAdmin):
    list_display = ['career', 'subject']
