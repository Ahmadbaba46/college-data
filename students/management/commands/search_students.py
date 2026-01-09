from django.core.management.base import BaseCommand
from students.models import Student, Level, Session

class Command(BaseCommand):
    help = 'Search for students using various criteria'

    def add_arguments(self, parser):
        parser.add_argument('--first_name', type=str, help='Search by first name')
        parser.add_argument('--last_name', type=str, help='Search by last name')
        parser.add_argument('--student_id', type=str, help='Search by student ID')
        parser.add_argument('--level_name', type=str, help='Search by current level name')
        parser.add_argument('--session_name', type=str, help='Search by current session name')

    def handle(self, *args, **kwargs):
        students = Student.objects.all()

        if kwargs['first_name']:
            students = students.filter(first_name__icontains=kwargs['first_name'])
        if kwargs['last_name']:
            students = students.filter(last_name__icontains=kwargs['last_name'])
        if kwargs['student_id']:
            students = students.filter(student_id__icontains=kwargs['student_id'])
        if kwargs['level_name']:
            try:
                level = Level.objects.get(name__icontains=kwargs['level_name'])
                students = students.filter(current_level=level)
            except Level.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Level with name "{kwargs["level_name"]}" not found.'))
                return
        if kwargs['session_name']:
            try:
                session = Session.objects.get(name__icontains=kwargs['session_name'])
                students = students.filter(current_session=session)
            except Session.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Session with name "{kwargs["session_name"]}" not found.'))
                return

        if students.exists():
            self.stdout.write(self.style.SUCCESS('Matching students:'))
            for student in students:
                self.stdout.write(f'- {student}')
        else:
            self.stdout.write(self.style.WARNING('No students found matching the criteria.'))