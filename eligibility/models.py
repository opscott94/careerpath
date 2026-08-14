from django.db import models
from careers.models import LearningArea, Subject

class University(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    website = models.URLField(blank=True)

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
