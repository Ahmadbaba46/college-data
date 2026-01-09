from django.core.management.base import BaseCommand
from students.models import Student, Level, Session

class Command(BaseCommand):
    help = 'Update a student\'s information'

    def add_arguments(self, parser):
        parser.add_argument('student_id', type=str, help='The ID of the student to update')
        parser.add_argument('--first_name', type=str, help='The new first name of the student')
        parser.add_argument('--last_name', type=str, help='The new last name of the student')
        parser.add_argument('--current_level_id', type=int, help='The new ID of the current level')
        parser.add_argument('--current_session_id', type=int, help='The new ID of the current session')

    def handle(self, *args, **kwargs):
        student_id = kwargs['student_id']

        try:
            student = Student.objects.get(student_id=student_id)

            if kwargs['first_name']:
                student.first_name = kwargs['first_name']
            if kwargs['last_name']:
                student.last_name = kwargs['last_name']
            if kwargs['current_level_id']:
                student.current_level = Level.objects.get(id=kwargs['current_level_id'])
            if kwargs['current_session_id']:
                student.current_session = Session.objects.get(id=kwargs['current_session_id'])

            student.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated student: {student}'))

        except Student.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Student with ID {student_id} does not exist.'))
        except Level.DoesNotExist:
            self.stdout.write(self.style.ERROR('Invalid Level ID'))
        except Session.DoesNotExist:
            self.stdout.write(self.style.ERROR('Invalid Session ID'))
