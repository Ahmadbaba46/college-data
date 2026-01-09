from django.core.management.base import BaseCommand
from grading.models import Enrollment

class Command(BaseCommand):
    help = 'Check for enrollments with a null session.'

    def handle(self, *args, **kwargs):
        null_session_enrollments = Enrollment.objects.filter(session__isnull=True)
        if null_session_enrollments.exists():
            self.stdout.write(self.style.ERROR('Found enrollments with a null session:'))
            for enrollment in null_session_enrollments:
                self.stdout.write(f'- Enrollment ID: {enrollment.id}')
        else:
            self.stdout.write(self.style.SUCCESS('No enrollments with a null session found.'))
