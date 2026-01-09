from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from students.models import Student
from grading.models import Grade

class Command(BaseCommand):
    help = 'Generate statistics on student performance'

    def handle(self, *args, **kwargs):
        total_students = Student.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total Students: {total_students}'))

        avg_total_score = Grade.objects.aggregate(Avg('total_score'))['total_score__avg']
        self.stdout.write(self.style.SUCCESS(f'Average Total Score Across All Enrollments: {avg_total_score:.2f}'))

        # Example: Average score per course
        course_avg_scores = Grade.objects.values('enrollment__course_offering__course__title').annotate(avg_score=Avg('total_score'))
        self.stdout.write(self.style.SUCCESS('\nAverage Total Score Per Course:'))
        for item in course_avg_scores:
            self.stdout.write(f'- {item["enrollment__course_offering__course__title"]}: {item["avg_score"]:.2f}')

        # Example: Number of enrollments per session
        enrollments_per_session = Grade.objects.values('enrollment__course_offering__session__name').annotate(count=Count('id'))
        self.stdout.write(self.style.SUCCESS('\nNumber of Enrollments Per Session:'))
        for item in enrollments_per_session:
            self.stdout.write(f'- {item["enrollment__course_offering__session__name"]}: {item["count"]}')
