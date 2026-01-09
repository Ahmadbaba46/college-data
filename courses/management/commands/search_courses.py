from django.core.management.base import BaseCommand
from courses.models import Course
from students.models import Level, Session

class Command(BaseCommand):
    help = 'Search for courses using various criteria'

    def add_arguments(self, parser):
        parser.add_argument('--code', type=str, help='Search by course code')
        parser.add_argument('--title', type=str, help='Search by course title')
        parser.add_argument('--level_name', type=str, help='Search by associated level name')
        parser.add_argument('--session_name', type=str, help='Search by associated session name')

    def handle(self, *args, **kwargs):
        courses = Course.objects.all()

        if kwargs['code']:
            courses = courses.filter(code__icontains=kwargs['code'])
        if kwargs['title']:
            courses = courses.filter(title__icontains=kwargs['title'])
        if kwargs['level_name']:
            try:
                level = Level.objects.get(name__icontains=kwargs['level_name'])
                courses = courses.filter(levels=level)
            except Level.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Level with name "{kwargs["level_name"]}" not found.'))
                return
        if kwargs['session_name']:
            try:
                session = Session.objects.get(name__icontains=kwargs['session_name'])
                courses = courses.filter(sessions=session)
            except Session.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Session with name "{kwargs["session_name"]}" not found.'))
                return

        if courses.exists():
            self.stdout.write(self.style.SUCCESS('Matching courses:'))
            for course in courses:
                self.stdout.write(f'- {course}')
        else:
            self.stdout.write(self.style.WARNING('No courses found matching the criteria.'))
