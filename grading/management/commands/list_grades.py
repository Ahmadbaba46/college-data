from django.core.management.base import BaseCommand
from grading.models import Grade
from users.rbac_helpers import resolve_acting_context
from audit_log.models import LogEntry

class Command(BaseCommand):
    help = 'List all grades'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='(RBAC) Acting username. If Teacher, only grades for assigned courses are shown.',
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

        username = kwargs.get('username')
        if username:
            try:
                ctx = resolve_acting_context(username)
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
                return

            if ctx.is_teacher_limited and ctx.teacher is not None:
                grades = grades.filter(enrollment__course_offering__course__in=ctx.teacher.courses.all())

            LogEntry.log_action(
                user=ctx.user,
                action='READ',
                object_type='Grade',
                object_id='*',
                message=f"Listed grades (session={session_name or 'ALL'}, teacher_limited={bool(ctx.teacher)})",
            )
        if grades:
            self.stdout.write(self.style.SUCCESS('List of grades:'))
            for grade in grades:
                self.stdout.write(f'- {grade.enrollment}: CA={grade.ca_score}, Exam={grade.exam_score}, Total={grade.total_score}, Grade={grade.grade}')
        else:
            self.stdout.write(self.style.WARNING('No grades found.'))
