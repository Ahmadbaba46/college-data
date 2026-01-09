import re
from django.core.management.base import BaseCommand
from students.models import Student, Level, Session

class Command(BaseCommand):
    help = 'Add a new student to the database'

    def add_arguments(self, parser):
        parser.add_argument('first_name', type=str, help='The first name of the student')
        parser.add_argument('last_name', type=str, help='The last name of the student')
        parser.add_argument('student_id', type=str, help='The student ID (5 alphanumeric characters)')
        parser.add_argument('entry_level_id', type=int, help='The ID of the entry level')
        parser.add_argument('current_level_id', type=int, help='The ID of the current level')
        parser.add_argument('current_session_id', type=int, help='The ID of the current session')

    def handle(self, *args, **kwargs):
        first_name = kwargs['first_name']
        last_name = kwargs['last_name']
        student_id = kwargs['student_id']
        entry_level_id = kwargs['entry_level_id']
        current_level_id = kwargs['current_level_id']
        current_session_id = kwargs['current_session_id']

        if not re.fullmatch(r'[a-zA-Z0-9]{5}', student_id):
            self.stdout.write(self.style.ERROR('Invalid Student ID format. Must be 5 alphanumeric characters.'))
            return

        try:
            entry_level = Level.objects.get(id=entry_level_id)
            current_level = Level.objects.get(id=current_level_id)
            current_session = Session.objects.get(id=current_session_id)

            student = Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                student_id=student_id,
                entry_level=entry_level,
                current_level=current_level,
                current_session=current_session
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created student: {student}'))
        except Level.DoesNotExist:
            self.stdout.write(self.style.ERROR('Invalid Level ID'))
        except Session.DoesNotExist:
            self.stdout.write(self.style.ERROR('Invalid Session ID'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating student: {e}'))
