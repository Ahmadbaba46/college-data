from django.core.management.base import BaseCommand
from configuration.models import CollegeSettings

class Command(BaseCommand):
    help = 'Update college settings'

    def add_arguments(self, parser):
        parser.add_argument('--college_name', type=str, help='The name of the college')
        parser.add_argument('--college_address', type=str, help='The address of the college')
        parser.add_argument('--letterhead', type=str, help='The letterhead content')

    def handle(self, *args, **kwargs):
        settings, created = CollegeSettings.objects.get_or_create(id=1)

        if kwargs['college_name']:
            settings.college_name = kwargs['college_name']
        if kwargs.get('college_address'):
            settings.college_address = kwargs['college_address']
        if kwargs.get('letterhead'):
            settings.letterhead = kwargs['letterhead']

        settings.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated college settings.'))
