from django.core.management.base import BaseCommand
from courses.models import Course
from students.models import Level, Session

class Command(BaseCommand):
    help = 'Add a new course to the database'

    def add_arguments(self, parser):
        parser.add_argument('code', type=str, help='The course code')
        parser.add_argument('title', type=str, help='The course title')
        parser.add_argument('units', type=int, help='The credit units for the course')
        parser.add_argument('--level_ids', nargs='+', type=int, help='The IDs of the levels for this course')
        parser.add_argument('--session_ids', nargs='+', type=int, help='The IDs of the sessions for this course')

    def handle(self, *args, **kwargs):
        code = kwargs['code']
        title = kwargs['title']
        units = kwargs['units']
        level_ids = kwargs['level_ids']
        session_ids = kwargs['session_ids']

        try:
            course = Course.objects.create(code=code, title=title, units=units)

            if level_ids:
                levels = Level.objects.filter(id__in=level_ids)
                course.levels.set(levels)

            if session_ids:
                sessions = Session.objects.filter(id__in=session_ids)
                course.sessions.set(sessions)

            self.stdout.write(self.style.SUCCESS(f'Successfully created course: {course}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating course: {e}'))
