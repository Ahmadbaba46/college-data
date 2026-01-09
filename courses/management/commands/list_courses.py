from django.core.management.base import BaseCommand
from courses.models import Course

class Command(BaseCommand):
    help = 'List all courses in the database'

    def handle(self, *args, **kwargs):
        courses = Course.objects.all()
        if courses:
            self.stdout.write(self.style.SUCCESS('List of courses:'))
            for course in courses:
                self.stdout.write(f'- {course}')
        else:
            self.stdout.write(self.style.WARNING('No courses found.'))
