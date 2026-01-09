from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create a new user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username for the new user')
        parser.add_argument('password', type=str, help='The password for the new user')
        parser.add_argument('--is_staff', action='store_true', help='Designates whether the user can log into this admin site.')
        parser.add_argument('--is_superuser', action='store_true', help='Designates that this user has all permissions without explicitly assigning them.')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        is_staff = kwargs['is_staff']
        is_superuser = kwargs['is_superuser']

        try:
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully created user: {username}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating user: {e}'))
