from django.core.management.base import BaseCommand
from teachers.models import Teacher

class Command(BaseCommand):
    help = 'List all teachers and their assigned courses'

    def handle(self, *args, **kwargs):
        teachers = Teacher.objects.all()
        if teachers:
            self.stdout.write(self.style.SUCCESS('List of teachers:'))
            for teacher in teachers:
                self.stdout.write(f'- {teacher}')
                courses = teacher.courses.all()
                if courses:
                    self.stdout.write(self.style.SUCCESS('  Assigned courses:'))
                    for course in courses:
                        self.stdout.write(f'    - {course}')
                else:
                    self.stdout.write(self.style.WARNING('  No courses assigned.'))
        else:
            self.stdout.write(self.style.WARNING('No teachers found.'))
