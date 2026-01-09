from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.files import File

from configuration.models import CollegeSettings

class Command(BaseCommand):
    help = 'Update college settings'

    def add_arguments(self, parser):
        parser.add_argument('--college_name', type=str, help='The name of the college')
        parser.add_argument('--college_address', type=str, help='The address of the college')
        parser.add_argument('--college_logo', type=str, help='The path to the college logo image')
        parser.add_argument('--principal_signature', type=str, help='The path to the principal\'s signature image')

    def handle(self, *args, **kwargs):
        settings, created = CollegeSettings.objects.get_or_create(pk=1) # Assuming a single settings instance

        if kwargs['college_name']:
            settings.college_name = kwargs['college_name']
        if kwargs['college_address']:
            settings.college_address = kwargs['college_address']
        if kwargs['college_logo']:
            logo_path = Path(kwargs['college_logo'])
            if not logo_path.exists():
                raise FileNotFoundError(f'college_logo not found: {logo_path}')
            with logo_path.open('rb') as f:
                settings.college_logo.save(logo_path.name, File(f), save=False)

        if kwargs['principal_signature']:
            sig_path = Path(kwargs['principal_signature'])
            if not sig_path.exists():
                raise FileNotFoundError(f'principal_signature not found: {sig_path}')
            with sig_path.open('rb') as f:
                settings.principal_signature.save(sig_path.name, File(f), save=False)
        
        settings.save()
        self.stdout.write(self.style.SUCCESS('College settings updated successfully.'))
