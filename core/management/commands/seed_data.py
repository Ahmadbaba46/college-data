from django.core.management.base import BaseCommand
from students.models import Level, Session

class Command(BaseCommand):
    help = 'Seed the database with initial data for Levels and Sessions'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Create Levels
        Level.objects.get_or_create(name='100 Level')
        Level.objects.get_or_create(name='200 Level')
        Level.objects.get_or_create(name='300 Level')
        Level.objects.get_or_create(name='400 Level')

        # Create Sessions
        Session.objects.get_or_create(name='2023/2024')
        Session.objects.get_or_create(name='2024/2025')

        self.stdout.write(self.style.SUCCESS('Successfully seeded data'))
