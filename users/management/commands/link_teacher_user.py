from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from teachers.models import Teacher
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Link a Django user to a Teacher record (UserProfile.teacher)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Django username')
        parser.add_argument('staff_id', type=str, help='Teacher staff_id')

    def handle(self, *args, **options):
        username = options['username']
        staff_id = options['staff_id']

        try:
            user = User.objects.get(username=username)
            teacher = Teacher.objects.get(staff_id=staff_id)
        except User.DoesNotExist as e:
            raise CommandError(str(e))
        except Teacher.DoesNotExist as e:
            raise CommandError(str(e))

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.teacher = teacher
        profile.save(update_fields=['teacher'])

        self.stdout.write(self.style.SUCCESS(f'Linked user {username} to teacher {teacher.staff_id}'))
