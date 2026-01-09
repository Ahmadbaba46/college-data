from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone

from grading.models import Grade


class Command(BaseCommand):
    help = 'Reject grades (Admin action)'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Reviewer username (must exist)')
        parser.add_argument('--reason', required=True, help='Rejection reason')
        parser.add_argument('--student-id', type=str, default=None)
        parser.add_argument('--course', type=str, default=None)
        parser.add_argument('--session', type=str, default=None)
        parser.add_argument('--semester', type=str, choices=['FIRST', 'SECOND', 'SUMMER'], default=None)

    def handle(self, *args, **opts):
        try:
            user = User.objects.get(username=opts['username'])
        except User.DoesNotExist:
            raise CommandError('Reviewer user not found')

        qs = Grade.objects.select_related('enrollment', 'enrollment__student', 'enrollment__course_offering__course', 'enrollment__course_offering__session')

        if opts.get('student_id'):
            qs = qs.filter(enrollment__student__student_id=opts['student_id'])
        if opts.get('course'):
            qs = qs.filter(enrollment__course_offering__course__code=opts['course'])
        if opts.get('session'):
            qs = qs.filter(enrollment__course_offering__session__name=opts['session'])
        if opts.get('semester'):
            qs = qs.filter(enrollment__course_offering__semester=opts['semester'])

        updated = qs.update(status=Grade.STATUS_REJECTED, approved_at=timezone.now(), approved_by=user, rejection_reason=opts['reason'])
        self.stdout.write(self.style.SUCCESS(f'Rejected {updated} grade(s).'))
