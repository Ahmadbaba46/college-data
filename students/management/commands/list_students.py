from django.core.management.base import BaseCommand
from students.models import Student

class Command(BaseCommand):
    help = 'List all students in the database'

    def handle(self, *args, **kwargs):
        students = Student.objects.all()
        if students:
            self.stdout.write(self.style.SUCCESS('List of students:'))
            for student in students:
                self.stdout.write(f'- {student} - Level: {student.current_level}')
        else:
            self.stdout.write(self.style.WARNING('No students found.'))
