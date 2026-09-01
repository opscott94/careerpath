from django.db import models
from careers.models import LearningArea, Subject

# Default WASSCE grading: A1=1, B2=2, B3=3, C4=4, C5=5, C6=6, D7=7, E8=8, F9=9
STANDARD_GRADING = {"1":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9}
# KNUST weighted grading: C4, C5, C6 all count as 4 points
KNUST_GRADING = {"1":1, "2":2, "3":3, "4":4, "5":4, "6":4, "7":7, "8":8, "9":9}

class University(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    about = models.TextField(blank=True, help_text='Overview description of the university')
    image = models.URLField(blank=True, help_text='Hero background image URL')
    thumbnail = models.URLField(blank=True, help_text='Campus thumbnail image URL')
    academic_year_start = models.CharField(
        max_length=100,
        default='September 2026',
        blank=True,
        help_text='e.g., September 2026'
    )
    application_deadline = models.CharField(
        max_length=100,
        default='June 2026',
        blank=True,
        help_text='e.g., June 2026'
    )
    entry_requirements = models.TextField(
        blank=True,
        help_text='General entry requirements (one per line or paragraph). Leave blank to use default WASSCE requirements.'
    )
    grading_scale = models.JSONField(
        default=dict,
        blank=True,
        help_text='Maps WASSCE numeric grades (1-9) to university-specific aggregate points. E.g. KNUST: C4,C5,C6 all count as 4.'
    )

    def get_point(self, raw_grade):
        """Convert a raw WASSCE grade (1-9) to this university's aggregate point value."""
        scale = self.grading_scale or STANDARD_GRADING
        return scale.get(str(raw_grade), raw_grade)

    def __str__(self):
        return self.short_name

    class Meta:
        verbose_name_plural = 'Universities'


class Program(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=200)
    college = models.CharField(max_length=200, blank=True)
    duration_years = models.IntegerField(default=4)
    aggregate = models.IntegerField(help_text='WASSCE aggregate cut-off (lower is better)', null=True, blank=True)
    year = models.IntegerField(default=2024, null=True, blank=True)
    campus = models.CharField(max_length=150, default='Main Campus', blank=True)
    note = models.TextField(blank=True, help_text='Additional notes or requirements for this program offering')
    min_passing_grade = models.IntegerField(
        default=6,
        help_text='Worst acceptable WASSCE grade for this program (6=C6, 7=D7). Most programs require C6 or better.'
    )
    core_subjects = models.ManyToManyField(
        Subject, 
        related_name='programs', 
        blank=True,
        limit_choices_to={'name__in': ['Mathematics', 'English Language', 'Social Studies', 'General Science']}
    )

    def __str__(self):
        return f"{self.university.short_name} — {self.name}"


class ProgramRequirement(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='requirements')
    learning_area = models.ForeignKey(LearningArea, on_delete=models.CASCADE, null=True, blank=True)
    mandatory_subjects = models.ManyToManyField(Subject, related_name='program_mandatory_requirements', blank=True)
    elective_subjects = models.ManyToManyField(Subject, related_name='program_elective_requirements', blank=True)

    def __str__(self):
        if self.learning_area:
            return f"{self.program.name} - {self.learning_area.name}"
        return f"{self.program.name} - Direct Subjects"
