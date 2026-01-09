from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from audit_log.models import LogEntry

class Command(BaseCommand):
    help = 'Log an action in the audit log'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the user performing the action')
        parser.add_argument('action', type=str, choices=[choice[0] for choice in LogEntry.ACTION_CHOICES], help='The type of action')
        parser.add_argument('object_type', type=str, help='The type of object being acted upon')
        parser.add_argument('object_id', type=str, help='The ID of the object being acted upon')
        parser.add_argument('--message', type=str, help='An optional message for the log entry')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        action = kwargs['action']
        object_type = kwargs['object_type']
        object_id = kwargs['object_id']
        message = kwargs['message']

        try:
            user = User.objects.get(username=username)
            LogEntry.objects.create(
                user=user,
                action=action,
                object_type=object_type,
                object_id=object_id,
                message=message
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully logged action: {action} by {username} on {object_type} {object_id}'))

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with username {username} does not exist.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error logging action: {e}'))
