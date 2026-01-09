from django.core.management.base import BaseCommand
from students.models import Student

class Command(BaseCommand):
    help = 'Delete a student from the database'

    def add_arguments(self, parser):
        parser.add_argument('student_id', type=str, help='The ID of the student to delete')

    def handle(self, *args, **kwargs):
        student_id = kwargs['student_id']

        try:
            student = Student.objects.get(student_id=student_id)
            student.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted student with ID: {student_id}'))

        except Student.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Student with ID {student_id} does not exist.'))
