from django.contrib import admin
from .models import University, Program, Cutoff

class CutoffInline(admin.TabularInline):
    model = Cutoff
    extra = 1

class ProgramInline(admin.TabularInline):
    model = Program
    extra = 1
    show_change_link = True

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['short_name', 'name', 'location']
    inlines = [ProgramInline]

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'university', 'faculty']
    list_filter = ['university']
    search_fields = ['name']
    filter_horizontal = ['required_subjects']
    inlines = [CutoffInline]

@admin.register(Cutoff)
class CutoffAdmin(admin.ModelAdmin):
    list_display = ['program', 'aggregate', 'year']
    list_filter = ['year', 'program__university']
