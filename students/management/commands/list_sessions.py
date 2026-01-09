from django.core.management.base import BaseCommand
from students.models import Session

class Command(BaseCommand):
    help = 'List all sessions in the database'

    def handle(self, *args, **kwargs):
        sessions = Session.objects.all()
        if sessions:
            self.stdout.write(self.style.SUCCESS('List of sessions:'))
            for session in sessions:
                self.stdout.write(f'- {session}')
        else:
            self.stdout.write(self.style.WARNING('No sessions found.'))
