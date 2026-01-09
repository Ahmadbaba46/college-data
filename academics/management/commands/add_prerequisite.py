from django.core.management.base import BaseCommand, CommandError

from academics.models import Program, Prerequisite
from courses.models import Course


class Command(BaseCommand):
    help = 'Add a prerequisite relationship within a Program'

    def add_arguments(self, parser):
        parser.add_argument('program_code', type=str)
        parser.add_argument('course_code', type=str)
        parser.add_argument('prereq_course_code', type=str)

    def handle(self, *args, **opts):
        try:
            program = Program.objects.get(code=opts['program_code'])
            course = Course.objects.get(code=opts['course_code'])
            prereq = Course.objects.get(code=opts['prereq_course_code'])
        except (Program.DoesNotExist, Course.DoesNotExist) as e:
            raise CommandError(str(e))

        obj, _ = Prerequisite.objects.get_or_create(program=program, course=course, prerequisite_course=prereq)
        self.stdout.write(self.style.SUCCESS(f'Prerequisite saved: {obj}'))
