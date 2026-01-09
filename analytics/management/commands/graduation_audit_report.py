import json

from django.core.management.base import BaseCommand, CommandError

from students.models import Student
from academics.graduation import audit_student_graduation


class Command(BaseCommand):
    help = 'Graduation audit + degree classification report for a student'

    def add_arguments(self, parser):
        parser.add_argument('student_id', type=str)
        parser.add_argument('--json', action='store_true')

    def handle(self, *args, **opts):
        try:
            student = Student.objects.get(student_id=opts['student_id'])
        except Student.DoesNotExist:
            raise CommandError('Student not found')

        result = audit_student_graduation(student)

        if opts['json']:
            self.stdout.write(json.dumps(result.__dict__, indent=2))
            return

        self.stdout.write(self.style.SUCCESS(f"Graduation Audit: {student.student_id} ({student.full_name})"))
        self.stdout.write(f"Program: {getattr(student.program, 'code', None)}")
        self.stdout.write(f"CGPA: {result.cgpa}")
        self.stdout.write(f"Total units earned: {result.total_units_earned}")
        self.stdout.write(f"Eligible: {result.eligible}")
        if result.classification:
            self.stdout.write(self.style.SUCCESS(f"Classification: {result.classification}"))
        if result.missing_compulsory_courses:
            self.stdout.write(self.style.WARNING(f"Missing compulsory courses: {', '.join(result.missing_compulsory_courses)}"))
        for n in result.notes:
            self.stdout.write(self.style.WARNING(n))
