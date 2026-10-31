"""
Management command to audit and validate academic and admissions data integrity.
Checks programs for cutoffs, requirements, duplicate listings, and university configs.
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from eligibility.models import University, Program, ProgramRequirement
from careers.models import Career, Subject, LearningArea


class Command(BaseCommand):
    help = 'Validates academic programs, requirements, cut-offs, and admissions data integrity.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting CareerPath academic data audit..."))

        total_unis = University.objects.count()
        total_progs = Program.objects.count()
        total_reqs = ProgramRequirement.objects.count()
        total_careers = Career.objects.count()
        total_subjects = Subject.objects.count()
        total_la = LearningArea.objects.count()

        self.stdout.write(f"\n--- Entity Counts ---")
        self.stdout.write(f"Universities: {total_unis}")
        self.stdout.write(f"Degree Programs: {total_progs}")
        self.stdout.write(f"Program Requirements: {total_reqs}")
        self.stdout.write(f"Careers: {total_careers}")
        self.stdout.write(f"Subjects: {total_subjects}")
        self.stdout.write(f"Learning Areas: {total_la}")

        warnings = 0
        issues = 0

        self.stdout.write(f"\n--- Data Quality Checks ---")

        # 1. Programs missing cutoffs
        missing_cutoff = Program.objects.filter(aggregate__isnull=True)
        count_missing_cut = missing_cutoff.count()
        if count_missing_cut > 0:
            self.stdout.write(self.style.WARNING(f"[INFO] {count_missing_cut} programs have no cutoff aggregate (may be fee-paying/interview only)."))
            warnings += 1
        else:
            self.stdout.write(self.style.SUCCESS("[OK] All programs have defined cut-off aggregates."))

        # 2. Programs without requirements
        progs_without_reqs = Program.objects.annotate(rcount=Count('requirements')).filter(rcount=0)
        count_no_reqs = progs_without_reqs.count()
        if count_no_reqs > 0:
            self.stdout.write(self.style.WARNING(f"[WARN] {count_no_reqs} programs have no subject requirements mapped."))
            for p in progs_without_reqs[:5]:
                self.stdout.write(f"   - {p.university.short_name}: {p.name}")
            if count_no_reqs > 5:
                self.stdout.write(f"   ... and {count_no_reqs - 5} more.")
            warnings += 1
        else:
            self.stdout.write(self.style.SUCCESS("[OK] All programs have at least one requirement rule."))

        # 3. Duplicate programs (same university, same name, same campus)
        duplicates = (
            Program.objects.values('university_id', 'name', 'campus')
            .annotate(cnt=Count('id'))
            .filter(cnt__gt=1)
        )
        if duplicates.exists():
            self.stdout.write(self.style.ERROR(f"[ERR] Found {duplicates.count()} duplicate program offerings!"))
            for d in duplicates:
                self.stdout.write(f"   - Name: {d['name']}, Campus: {d['campus']}")
            issues += 1
        else:
            self.stdout.write(self.style.SUCCESS("[OK] No duplicate program offerings found."))

        # 4. Universities missing grading scales
        unis_missing_scale = University.objects.filter(grading_scale={})
        if unis_missing_scale.exists():
            self.stdout.write(self.style.WARNING(f"[WARN] {unis_missing_scale.count()} universities using standard default grading (no custom scale)."))
            warnings += 1
        else:
            self.stdout.write(self.style.SUCCESS("[OK] All universities have custom or default grading scales."))

        # 5. Empty requirement sets
        empty_reqs = ProgramRequirement.objects.annotate(
            m_count=Count('mandatory_subjects'),
            e_count=Count('elective_subjects')
        ).filter(m_count=0, e_count=0, learning_area__isnull=True)
        if empty_reqs.exists():
            self.stdout.write(self.style.WARNING(f"[WARN] Found {empty_reqs.count()} requirements with no subjects and no learning area."))
            warnings += 1
        else:
            self.stdout.write(self.style.SUCCESS("[OK] No empty requirement rules."))

        self.stdout.write(f"\n==========================================")
        if issues == 0:
            self.stdout.write(self.style.SUCCESS(f"Audit completed: 0 critical issues, {warnings} informational warnings."))
        else:
            self.stdout.write(self.style.ERROR(f"Audit completed with {issues} critical issues and {warnings} warnings."))

