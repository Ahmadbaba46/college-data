from django.core.management.base import BaseCommand
from django.db.models import Count
from teachers.models import Teacher

class Command(BaseCommand):
    help = 'Generate statistics on teacher workload'

    def handle(self, *args, **kwargs):
        teachers = Teacher.objects.annotate(num_courses=Count('courses'))

        self.stdout.write(self.style.SUCCESS('Teacher Workload:'))
        for teacher in teachers:
            self.stdout.write(f'- {teacher.first_name} {teacher.last_name} ({teacher.staff_id}): {teacher.num_courses} courses')
