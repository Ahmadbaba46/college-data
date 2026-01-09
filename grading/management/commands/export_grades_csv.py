import csv
from django.core.management.base import BaseCommand
from grading.models import Grade
from users.rbac_helpers import resolve_acting_context
from audit_log.models import LogEntry

class Command(BaseCommand):
    help = 'Export grades to a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('output_file', type=str, help='The path to the output CSV file')
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='(RBAC) Acting username. If Teacher, only grades for assigned courses are exported.',
        )
        parser.add_argument(
            '--session',
            type=str,
            default=None,
            help='Filter by session name (e.g., "2023/2024")',
        )
        parser.add_argument(
            '--course',
            type=str,
            default=None,
            help='Filter by course code',
        )
        parser.add_argument(
            '--semester',
            type=str,
            default=None,
            choices=['FIRST', 'SECOND', 'SUMMER'],
            help='Filter by semester (FIRST/SECOND/SUMMER)',
        )

    def handle(self, *args, **kwargs):
        output_file = kwargs['output_file']

        from configuration.models import AcademicPolicySettings
        policy = AcademicPolicySettings.get_solo()

        grades = Grade.objects.select_related(
            'enrollment',
            'enrollment__student',
            'enrollment__course_offering__course',
            'enrollment__course_offering__session',
        )

        session_name = kwargs.get('session')
        if session_name:
            grades = grades.filter(enrollment__course_offering__session__name=session_name)

        course_code = kwargs.get('course')
        if course_code:
            grades = grades.filter(enrollment__course_offering__course__code=course_code)

        semester = kwargs.get('semester')
        if semester:
            grades = grades.filter(enrollment__course_offering__semester=semester)

        if policy.require_approved_for_exports:
            grades = grades.filter(status=Grade.STATUS_APPROVED)

        username = kwargs.get('username')
        ctx = None
        if username:
            try:
                ctx = resolve_acting_context(username)
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
                return

            if ctx.is_teacher_limited and ctx.teacher is not None:
                grades = grades.filter(enrollment__course_offering__course__in=ctx.teacher.courses.all())

        row_count = grades.count()

        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['student_id', 'student_name', 'course_code', 'course_title', 'session_name', 'ca_score', 'exam_score', 'total_score', 'grade']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for grade in grades:
                writer.writerow({
                    'student_id': grade.enrollment.student.student_id,
                    'student_name': str(grade.enrollment.student),
                    'course_code': grade.enrollment.course.code,
                    'course_title': grade.enrollment.course.title,
                    'session_name': grade.enrollment.session.name,
                    'ca_score': grade.ca_score,
                    'exam_score': grade.exam_score,
                    'total_score': grade.total_score,
                    'grade': grade.grade,
                })
        self.stdout.write(self.style.SUCCESS(f'Successfully exported grades to {output_file}'))

        # Audit export
        if ctx is not None and ctx.user is not None:
            LogEntry.log_action(
                user=ctx.user,
                action='EXPORT',
                object_type='Grade',
                object_id='*',
                message=(
                    f"Exported grades CSV to {output_file} "
                    f"(rows={row_count}, session={session_name or 'ALL'}, teacher_limited={bool(ctx.teacher)})"
                ),
            )
