from django.core.management.base import BaseCommand
from configuration.models import CollegeSettings

class Command(BaseCommand):
    help = 'Show college settings'

    def handle(self, *args, **kwargs):
        try:
            settings = CollegeSettings.objects.get(id=1)
            self.stdout.write(self.style.SUCCESS('College Settings:'))
            self.stdout.write(f'- College Name: {settings.college_name}')
            self.stdout.write(f'- College Address: {getattr(settings, "college_address", "")}')
            self.stdout.write(f'- Letterhead: {getattr(settings, "letterhead", "")}')
        except CollegeSettings.DoesNotExist:
            self.stdout.write(self.style.WARNING('No college settings found.'))
