import csv
from django.core.management.base import BaseCommand
from teachers.models import Teacher
from courses.models import Course

class Command(BaseCommand):
    help = 'Bulk assign teachers to courses from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file containing teacher assignment data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                staff_id = row.get('staff_id')
                course_code = row.get('course_code')

                if not all([staff_id, course_code]):
                    self.stdout.write(self.style.ERROR(f'Skipping row due to missing data: {row}'))
                    continue

                try:
                    teacher = Teacher.objects.get(staff_id=staff_id)
                    course = Course.objects.get(code=course_code)

                    teacher.courses.add(course)
                    self.stdout.write(self.style.SUCCESS(f'Successfully assigned teacher {teacher} to course {course}'))

                except Teacher.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Teacher with staff ID {staff_id} does not exist. Skipping assignment.'))
                except Course.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Course with code {course_code} does not exist. Skipping assignment.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error assigning teacher {staff_id} to course {course_code}: {e}'))
