from django.core.management.base import BaseCommand
from django.db.models import Count
from grading.models import Enrollment

class Command(BaseCommand):
    help = 'Generate statistics on enrollment trends'

    def handle(self, *args, **kwargs):
        total_enrollments = Enrollment.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total Enrollments: {total_enrollments}'))

        enrollments_per_session = Enrollment.objects.values('course_offering__session__name').annotate(count=Count('pk'))
        self.stdout.write(self.style.SUCCESS('\nEnrollments Per Session:'))
        for item in enrollments_per_session:
            self.stdout.write(f'- {item["course_offering__session__name"]}: {item["count"]}')

        enrollments_per_course = Enrollment.objects.values('course_offering__course__title').annotate(count=Count('pk'))
        self.stdout.write(self.style.SUCCESS('\nEnrollments Per Course:'))
        for item in enrollments_per_course:
            self.stdout.write(f'- {item["course_offering__course__title"]}: {item["count"]}')
