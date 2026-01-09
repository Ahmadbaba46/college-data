from django.core.management.base import BaseCommand
from teachers.models import Teacher
from courses.models import Course

class Command(BaseCommand):
    help = 'Assign a teacher to a course'

    def add_arguments(self, parser):
        parser.add_argument('staff_id', type=str, help='The staff ID of the teacher')
        parser.add_argument('course_code', type=str, help='The code of the course to assign')

    def handle(self, *args, **kwargs):
        staff_id = kwargs['staff_id']
        course_code = kwargs['course_code']

        try:
            teacher = Teacher.objects.get(staff_id=staff_id)
            course = Course.objects.get(code=course_code)

            teacher.courses.add(course)
            self.stdout.write(self.style.SUCCESS(f'Successfully assigned teacher {teacher} to course {course}'))

        except Teacher.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Teacher with staff ID {staff_id} does not exist.'))
        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Course with code {course_code} does not exist.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error assigning teacher: {e}'))