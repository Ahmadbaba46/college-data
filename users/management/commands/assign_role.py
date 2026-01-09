from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Assign a user to a group (role)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the user')
        parser.add_argument('group_name', type=str, help='The name of the group (role) to assign')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        group_name = kwargs['group_name']

        try:
            user = User.objects.get(username=username)
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            self.stdout.write(self.style.SUCCESS(f'Successfully assigned user {username} to group {group_name}'))

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with username {username} does not exist.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error assigning role: {e}'))
