
from django.core.management.base import BaseCommand
from students.models import Student, Level, Session
from django.db.models import F

class Command(BaseCommand):
    help = 'Promote students from a given level and session to the next level.'

    def add_arguments(self, parser):
        parser.add_argument('current_level_id', type=int, help='The ID of the current level of the students to promote.')
        parser.add_argument('current_session_id', type=int, help='The ID of the current session of the students to promote.')
        parser.add_argument('--student_ids', nargs='*', type=str, help='Optional list of student IDs to promote. If not provided, all eligible students will be promoted.')

    def handle(self, *args, **kwargs):
        current_level_id = kwargs['current_level_id']
        current_session_id = kwargs['current_session_id']
        student_ids = kwargs['student_ids']

        try:
            current_level = Level.objects.get(id=current_level_id)
            current_session = Session.objects.get(id=current_session_id)

            # Determine the next level
            try:
                next_level_number = int(current_level.name.split()[0]) + 100
                next_level_name = f'{next_level_number} Level'
                next_level = Level.objects.get(name=next_level_name)
            except (ValueError, Level.DoesNotExist):
                self.stdout.write(self.style.ERROR(f'Could not determine the next level after {current_level.name}. Please ensure the next level exists.'))
                return

            students_to_promote = Student.objects.filter(
                current_level=current_level,
                current_session=current_session
            )

            if student_ids:
                students_to_promote = students_to_promote.filter(student_id__in=student_ids)

            if not students_to_promote.exists():
                self.stdout.write(self.style.WARNING('No students found to promote for the given criteria.'))
                return

            promoted_count = students_to_promote.update(current_level=next_level)

            self.stdout.write(self.style.SUCCESS(f'Successfully promoted {promoted_count} students to {next_level.name}.'))

        except Level.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Level with ID {current_level_id} does not exist.'))
        except Session.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Session with ID {current_session_id} does not exist.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred during promotion: {e}'))
