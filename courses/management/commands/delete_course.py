from django.core.management.base import BaseCommand
from courses.models import Course

class Command(BaseCommand):
    help = 'Delete an existing course'

    def add_arguments(self, parser):
        parser.add_argument('course_id', type=int, help='The ID of the course to delete')

    def handle(self, *args, **kwargs):
        course_id = kwargs['course_id']

        try:
            course = Course.objects.get(id=course_id)
            course.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted course with ID: {course_id}'))

        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Course with ID {course_id} does not exist.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error deleting course: {e}'))
