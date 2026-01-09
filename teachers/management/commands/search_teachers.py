from django.core.management.base import BaseCommand
from teachers.models import Teacher
from courses.models import Course

class Command(BaseCommand):
    help = 'Search for teachers using various criteria'

    def add_arguments(self, parser):
        parser.add_argument('--first_name', type=str, help='Search by first name')
        parser.add_argument('--last_name', type=str, help='Search by last name')
        parser.add_argument('--staff_id', type=str, help='Search by staff ID')
        parser.add_argument('--course_code', type=str, help='Search by assigned course code')

    def handle(self, *args, **kwargs):
        teachers = Teacher.objects.all()

        if kwargs['first_name']:
            teachers = teachers.filter(first_name__icontains=kwargs['first_name'])
        if kwargs['last_name']:
            teachers = teachers.filter(last_name__icontains=kwargs['last_name'])
        if kwargs['staff_id']:
            teachers = teachers.filter(staff_id__icontains=kwargs['staff_id'])
        if kwargs['course_code']:
            try:
                course = Course.objects.get(code__icontains=kwargs['course_code'])
                teachers = teachers.filter(courses=course)
            except Course.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Course with code "{kwargs["course_code"]}" not found.'))
                return

        if teachers.exists():
            self.stdout.write(self.style.SUCCESS('Matching teachers:'))
            for teacher in teachers:
                self.stdout.write(f'- {teacher}')
        else:
            self.stdout.write(self.style.WARNING('No teachers found matching the criteria.'))
