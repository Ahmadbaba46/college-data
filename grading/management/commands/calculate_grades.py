from django.core.management.base import BaseCommand
from django.db import transaction
from grading.models import Grade
from students.models import Session
from courses.models import Course
from users.rbac_helpers import resolve_acting_context


class Command(BaseCommand):
    help = (
        'Recalculate total scores and assign grades for existing Grade records. '
        'Uses Grade.save() to apply the current GradingSettings scheme.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--session',
            type=str,
            help='Limit to a specific session name (e.g., "2023/2024")',
        )
        parser.add_argument(
            '--course',
            type=str,
            help='Limit to a specific course code (e.g., "CS101")',
        )
        parser.add_argument(
            '--semester',
            type=str,
            choices=['FIRST', 'SECOND', 'SUMMER'],
            help='Limit to a semester (FIRST/SECOND/SUMMER)',
        )
        parser.add_argument(
            '--student',
            type=str,
            help='Limit to a specific student_id',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would change without saving',
        )
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='(RBAC) Acting Django username. If a Teacher, only their assigned courses will be processed.',
        )

    def handle(self, *args, **options):
        qs = Grade.objects.select_related(
            'enrollment',
            'enrollment__student',
            'enrollment__course_offering__course',
            'enrollment__course_offering__session',
        )

        username = options.get('username')
        if username:
            try:
                ctx = resolve_acting_context(username)
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
                return

            if ctx.is_teacher_limited and ctx.teacher is not None:
                qs = qs.filter(enrollment__course_offering__course__in=ctx.teacher.courses.all())

        if options.get('session'):
            session = Session.objects.get(name=options['session'])
            qs = qs.filter(enrollment__course_offering__session=session)

        if options.get('course'):
            course = Course.objects.get(code=options['course'])
            qs = qs.filter(enrollment__course_offering__course=course)

        if options.get('semester'):
            qs = qs.filter(enrollment__course_offering__semester=options['semester'])

        if options.get('student'):
            qs = qs.filter(enrollment__student__student_id=options['student'])

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No grade records found for the given filters.'))
            return

        updated = 0
        unchanged = 0

        self.stdout.write(f'Processing {total} grade record(s)...')

        with transaction.atomic():
            for grade in qs.iterator():
                before_total = grade.total_score
                before_letter = grade.grade

                # Trigger recalculation
                grade.save()

                after_total = grade.total_score
                after_letter = grade.grade

                if before_total != after_total or before_letter != after_letter:
                    updated += 1
                    self.stdout.write(
                        f"Updated {grade.enrollment.student.student_id} / {grade.enrollment.course.code} / {grade.enrollment.session.name}: "
                        f"{before_total}->{after_total}, {before_letter}->{after_letter}"
                    )
                else:
                    unchanged += 1

            if options.get('dry_run'):
                # Roll back any writes made during the loop.
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(f'Done. Updated: {updated}, Unchanged: {unchanged}'))
        if options.get('dry_run'):
            self.stdout.write(self.style.WARNING('Dry-run enabled: no changes were saved.'))
