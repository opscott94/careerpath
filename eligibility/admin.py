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
    list_display = ['short_name', 'name', 'location']
    inlines = [ProgramInline]

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'university', 'campus', 'faculty', 'aggregate', 'year']
    list_filter = ['university', 'campus', 'faculty']
    search_fields = ['name', 'campus', 'note']
    filter_horizontal = ['core_subjects']
    inlines = [ProgramRequirementInline]

@admin.register(ProgramRequirement)
class ProgramRequirementAdmin(admin.ModelAdmin):
    list_display = ['program', 'learning_area']
    list_filter = ['learning_area']
    search_fields = ['program__name']
    filter_horizontal = ['mandatory_subjects', 'elective_subjects']

