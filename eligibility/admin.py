from django.contrib import admin
from .models import University, Program

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
    list_display = ['name', 'university', 'faculty', 'aggregate', 'year']
    list_filter = ['university']
    search_fields = ['name']
    filter_horizontal = ['required_subjects']

