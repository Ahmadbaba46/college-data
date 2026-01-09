from django.core.management.base import BaseCommand
from teachers.models import Teacher

class Command(BaseCommand):
    help = 'Add a new teacher to the database'

    def add_arguments(self, parser):
        parser.add_argument('first_name', type=str, help='The teacher\'s first name')
        parser.add_argument('last_name', type=str, help='The teacher\'s last name')
        parser.add_argument('staff_id', type=str, help='The teacher\'s staff ID')

    def handle(self, *args, **kwargs):
        first_name = kwargs['first_name']
        last_name = kwargs['last_name']
        staff_id = kwargs['staff_id']

        try:
            teacher = Teacher.objects.create(first_name=first_name, last_name=last_name, staff_id=staff_id)
            self.stdout.write(self.style.SUCCESS(f'Successfully created teacher: {teacher}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating teacher: {e}'))