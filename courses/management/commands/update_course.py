from django.core.management.base import BaseCommand
from courses.models import Course
from students.models import Level, Session

class Command(BaseCommand):
    help = 'Update an existing course'

    def add_arguments(self, parser):
        parser.add_argument('course_id', type=int, help='The ID of the course to update')
        parser.add_argument('--code', type=str, help='The new course code')
        parser.add_argument('--title', type=str, help='The new course title')
        parser.add_argument('--level_ids', nargs='+', type=int, help='The new IDs of the levels for this course')
        parser.add_argument('--session_ids', nargs='+', type=int, help='The new IDs of the sessions for this course')

    def handle(self, *args, **kwargs):
        course_id = kwargs['course_id']
        code = kwargs['code']
        title = kwargs['title']
        level_ids = kwargs['level_ids']
        session_ids = kwargs['session_ids']

        try:
            course = Course.objects.get(id=course_id)

            if code:
                course.code = code
            if title:
                course.title = title

            if level_ids:
                levels = Level.objects.filter(id__in=level_ids)
                course.levels.set(levels)
            
            if session_ids:
                sessions = Session.objects.filter(id__in=session_ids)
                course.sessions.set(sessions)

            course.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully updated course: {course}'))

        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Course with ID {course_id} does not exist.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating course: {e}'))
