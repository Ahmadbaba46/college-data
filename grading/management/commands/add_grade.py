from django.core.management.base import BaseCommand
from grading.models import Enrollment, Grade, GradingSettings
from audit_log.models import LogEntry
from users.rbac_helpers import resolve_acting_context

class Command(BaseCommand):
    help = 'Add a grade for a student enrollment'

    def add_arguments(self, parser):
        parser.add_argument('enrollment_id', type=int, help='The ID of the enrollment to add a grade for')
        parser.add_argument('ca_score', type=float, help='The CA score')
        parser.add_argument('exam_score', type=float, help='The exam score')
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='(RBAC) Acting Django username. If a Teacher, they must be assigned to the enrollment course.',
        )

    def handle(self, *args, **kwargs):
        enrollment_id = kwargs['enrollment_id']
        ca_score = kwargs['ca_score']
        exam_score = kwargs['exam_score']
        username = kwargs.get('username')

        try:
            ctx = resolve_acting_context(username)
            acting_user = ctx.user
            teacher = ctx.teacher if ctx.is_teacher_limited else None

            enrollment = Enrollment.objects.select_related('course').get(id=enrollment_id)

            if teacher is not None:
                if not teacher.courses.filter(pk=enrollment.course.pk).exists():
                    self.stdout.write(
                        self.style.ERROR(
                            f'Permission denied: teacher {teacher.staff_id} is not assigned to course {enrollment.course.code}.'
                        )
                    )
                    return
            total_score = ca_score + exam_score

            grade_setting = GradingSettings.objects.filter(min_score__lte=total_score, max_score__gte=total_score).first()
            grade = grade_setting.grade_name if grade_setting else 'N/A'

            grade_obj, created = Grade.objects.update_or_create(
                enrollment=enrollment,
                defaults={
                    'ca_score': ca_score,
                    'exam_score': exam_score,
                    'total_score': total_score,
                    'grade': grade
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully added grade for {enrollment}'))
                LogEntry.log_action(
                    user=acting_user,
                    action='CREATE',
                    object_type='Grade',
                    object_id=str(grade_obj.pk),
                    message=(
                        f"Added grade via add_grade: enrollment={enrollment.pk}, course={enrollment.course.code}, "
                        f"ca={ca_score}, exam={exam_score}, total={total_score}, grade={grade}"
                    ),
                )
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully updated grade for {enrollment}'))
                LogEntry.log_action(
                    user=acting_user,
                    action='UPDATE',
                    object_type='Grade',
                    object_id=str(grade_obj.pk),
                    message=(
                        f"Updated grade via add_grade: enrollment={enrollment.pk}, course={enrollment.course.code}, "
                        f"ca={ca_score}, exam={exam_score}, total={total_score}, grade={grade}"
                    ),
                )

        except Enrollment.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Enrollment with ID {enrollment_id} does not exist.'))
