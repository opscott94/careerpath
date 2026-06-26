from django.db import models

class LearningArea(models.Model):
    SCHOOL_TYPE_CHOICES = [
        ('SHS', 'Senior High School'),
        ('STEM', 'STEM School'),
        ('BOTH', 'Both'),
    ]
    name = models.CharField(max_length=100)
    school_type = models.CharField(max_length=4, choices=SCHOOL_TYPE_CHOICES, default='SHS')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    is_externally_examinable = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    learning_areas = models.ManyToManyField(LearningArea, through='SubjectLearningArea', related_name='subjects', blank=True)

    def __str__(self):
        return self.name


class SubjectLearningArea(models.Model):
    GROUP_CHOICES = [
        ('A', 'Core'),
        ('B', 'Learning Area Elective'),
        ('C', 'Related Learning Area Elective'),
        ('D', 'Other Elective'),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_learning_areas')
    learning_area = models.ForeignKey(LearningArea, on_delete=models.CASCADE, related_name='subject_learning_areas')
    group = models.CharField(max_length=1, choices=GROUP_CHOICES)
    is_mandatory = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject.name} - {self.learning_area.name} (Group {self.group}, Mandatory: {self.is_mandatory})"


class Career(models.Model):
    name = models.CharField(max_length=150)
    icon = models.CharField(max_length=50, default='🎯')
    description = models.TextField(blank=True)
    keywords = models.TextField(help_text='Comma-separated keywords for NLP matching')
    learning_area = models.ForeignKey(LearningArea, on_delete=models.SET_NULL, null=True)
    core_subjects = models.ManyToManyField(Subject, related_name='career_core', blank=True)
    mandatory_electives = models.ManyToManyField(Subject, related_name='career_mandatory', blank=True)
    recommended_electives = models.ManyToManyField(Subject, related_name='career_recommended', blank=True)
    why_text = models.TextField(blank=True, help_text='Explanation shown to student')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def keywords_list(self):
        return [k.strip().lower() for k in self.keywords.split(',')]


class CareerRecommendationReason(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='recommendation_reasons')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    reason = models.TextField()

    def __str__(self):
        return f"{self.career.name} → {self.subject.name}"