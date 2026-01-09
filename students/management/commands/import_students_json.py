import json
from django.core.management.base import BaseCommand
from students.models import Student, Level, Session

class Command(BaseCommand):
    help = 'Import students from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the JSON file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                for row in data:
                    try:
                        entry_level = Level.objects.get(id=row['entry_level_id'])
                        current_level = Level.objects.get(id=row['current_level_id'])
                        current_session = Session.objects.get(id=row['current_session_id'])

                        student, created = Student.objects.get_or_create(
                            student_id=row['student_id'],
                            defaults={
                                'first_name': row['first_name'],
                                'last_name': row['last_name'],
                                'entry_level': entry_level,
                                'current_level': current_level,
                                'current_session': current_session
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Successfully created student: {student}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Student with ID {row["student_id"]} already exists.'))

                    except Level.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'Invalid Level ID in row: {row}'))
                    except Session.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'Invalid Session ID in row: {row}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found at: {file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON format in file: {file_path}'))
