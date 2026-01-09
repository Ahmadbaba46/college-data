from django.core.management.base import BaseCommand, CommandError

from academics.models import Program, CurriculumCourse
from courses.models import Course
from students.models import Level


class Command(BaseCommand):
    help = 'Add a course to a Program curriculum for a specific level+semester'

    def add_arguments(self, parser):
        parser.add_argument('program_code', type=str)
        parser.add_argument('course_code', type=str)
        parser.add_argument('level_name', type=str)
        parser.add_argument('semester', choices=['FIRST', 'SECOND', 'SUMMER'])
        parser.add_argument('--elective', action='store_true', help='Mark as elective (default is compulsory)')

    def handle(self, *args, **opts):
        try:
            program = Program.objects.get(code=opts['program_code'])
            course = Course.objects.get(code=opts['course_code'])
            level = Level.objects.get(name=opts['level_name'])
        except (Program.DoesNotExist, Course.DoesNotExist, Level.DoesNotExist) as e:
            raise CommandError(str(e))

        cc, _ = CurriculumCourse.objects.update_or_create(
            program=program,
            course=course,
            level=level,
            semester=opts['semester'],
            defaults={'is_compulsory': not opts['elective']},
        )
        self.stdout.write(self.style.SUCCESS(f'Curriculum course saved: {cc}'))
