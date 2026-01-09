import json

from django.core.management.base import BaseCommand, CommandError

from students.models import Student
from academics.eligibility import suggest_courses_for_student


class Command(BaseCommand):
    help = 'Suggest eligible curriculum courses for a student for a semester (based on prerequisites and passed courses)'

    def add_arguments(self, parser):
        parser.add_argument('student_id', type=str)
        parser.add_argument('--semester', choices=['FIRST', 'SECOND', 'SUMMER'], required=True)
        parser.add_argument('--json', action='store_true')

    def handle(self, *args, **opts):
        try:
            student = Student.objects.get(student_id=opts['student_id'])
        except Student.DoesNotExist:
            raise CommandError('Student not found')

        suggestions = suggest_courses_for_student(student, opts['semester'])

        if opts['json']:
            self.stdout.write(json.dumps([s.__dict__ for s in suggestions], indent=2))
            return

        if not suggestions:
            self.stdout.write(self.style.WARNING('No suggestions (missing program/level or all courses already passed).'))
            return

        self.stdout.write(self.style.SUCCESS(f"Course suggestions for {student.student_id} ({opts['semester']}):"))
        for s in suggestions:
            status = 'ELIGIBLE' if s.eligible else 'BLOCKED'
            msg = f" - {s.course_code} {s.course_title}: {status}"
            if s.reason:
                msg += f" ({s.reason})"
            self.stdout.write(msg)
