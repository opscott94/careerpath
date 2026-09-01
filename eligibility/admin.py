from django.contrib import admin
from .models import University, Program, ProgramRequirement

class ProgramInline(admin.TabularInline):
    model = Program
    extra = 1
    show_change_link = True

class ProgramRequirementInline(admin.StackedInline):
    model = ProgramRequirement
    extra = 1
    filter_horizontal = ['mandatory_subjects', 'elective_subjects']

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['short_name', 'name', 'location', 'academic_year_start', 'application_deadline']
    search_fields = ['name', 'short_name', 'location']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_name', 'location', 'website', 'about', 'image', 'thumbnail')
        }),
        ('Admissions & Important Dates (Appears on Detail Page)', {
            'fields': ('academic_year_start', 'application_deadline', 'entry_requirements'),
            'description': 'Dates and entry requirements configured here will dynamically appear on the university detail page.'
        }),
        ('Grading Scale Configuration', {
            'fields': ('grading_scale',),
            'classes': ('collapse',)
        }),
    )
    inlines = [ProgramInline]

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'university', 'campus', 'college', 'aggregate', 'min_passing_grade', 'year']
    list_filter = ['university', 'campus', 'college', 'min_passing_grade']
    list_editable = ['min_passing_grade']
    search_fields = ['name', 'campus', 'note']
    filter_horizontal = ['core_subjects']
    inlines = [ProgramRequirementInline]

@admin.register(ProgramRequirement)
class ProgramRequirementAdmin(admin.ModelAdmin):
    list_display = ['program', 'learning_area']
    list_filter = ['learning_area']
    search_fields = ['program__name']
    filter_horizontal = ['mandatory_subjects', 'elective_subjects']

