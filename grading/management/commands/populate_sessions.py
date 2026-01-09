from django.core.management.base import BaseCommand
from grading.models import Enrollment
from students.models import Session

class Command(BaseCommand):
    help = 'Populate the session for existing enrollments that have a null session.'

    def handle(self, *args, **kwargs):
        try:
            default_session = Session.objects.get(name='2023/2024')
            enrollments_to_update = Enrollment.objects.filter(session__isnull=True)
            
            if enrollments_to_update.exists():
                count = enrollments_to_update.update(session=default_session)
                self.stdout.write(self.style.SUCCESS(f'Successfully populated session for {count} enrollments.'))
            else:
                self.stdout.write(self.style.WARNING('No enrollments with null session found.'))

        except Session.DoesNotExist:
            self.stdout.write(self.style.ERROR('Default session "2023/2024" not found. Please create it first.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error populating sessions: {e}'))
