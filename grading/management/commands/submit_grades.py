from django.core.management.base import BaseCommand
from django.utils import timezone

from grading.models import Grade


class Command(BaseCommand):
    help = 'Mark grades as SUBMITTED (by filters)'

    def add_arguments(self, parser):
        parser.add_argument('--student-id', type=str, default=None)
        parser.add_argument('--course', type=str, default=None)
        parser.add_argument('--session', type=str, default=None)
        parser.add_argument('--semester', type=str, choices=['FIRST', 'SECOND', 'SUMMER'], default=None)

    def handle(self, *args, **opts):
        qs = Grade.objects.select_related('enrollment', 'enrollment__student', 'enrollment__course_offering__course', 'enrollment__course_offering__session')

        if opts.get('student_id'):
            qs = qs.filter(enrollment__student__student_id=opts['student_id'])
        if opts.get('course'):
            qs = qs.filter(enrollment__course_offering__course__code=opts['course'])
        if opts.get('session'):
            qs = qs.filter(enrollment__course_offering__session__name=opts['session'])
        if opts.get('semester'):
            qs = qs.filter(enrollment__course_offering__semester=opts['semester'])

        updated = qs.exclude(status=Grade.STATUS_APPROVED).update(status=Grade.STATUS_SUBMITTED, submitted_at=timezone.now(), rejection_reason=None)
        self.stdout.write(self.style.SUCCESS(f'Submitted {updated} grade(s).'))
