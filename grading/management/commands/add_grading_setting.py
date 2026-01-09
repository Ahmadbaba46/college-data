from django.core.management.base import BaseCommand

from grading.models import GradingSettings
from users.rbac_helpers import resolve_acting_context

class Command(BaseCommand):
    help = 'Add a new grading setting'

    def add_arguments(self, parser):
        parser.add_argument('grade_name', type=str, help='The name of the grade (e.g., A, B, C)')
        parser.add_argument('min_score', type=float, help='The minimum score for this grade')
        parser.add_argument('max_score', type=float, help='The maximum score for this grade')
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='(RBAC) Acting username. Must be Admin to modify grading settings.',
        )

    def handle(self, *args, **kwargs):
        grade_name = kwargs['grade_name']
        min_score = kwargs['min_score']
        max_score = kwargs['max_score']

        username = kwargs.get('username')
        if username:
            try:
                ctx = resolve_acting_context(username)
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
                return

            if ctx.user is None or not getattr(ctx.user, 'is_superuser', False):
                # group-based Admin is checked by resolve_acting_context not making teacher-limited
                # but we require explicit Admin group or superuser
                if 'Admin' not in set(ctx.user.groups.values_list('name', flat=True)):
                    self.stdout.write(self.style.ERROR('Permission denied: only Admin can modify grading settings.'))
                    return

        try:
            setting, created = GradingSettings.objects.get_or_create(
                grade_name=grade_name,
                defaults={'min_score': min_score, 'max_score': max_score}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully added grading setting: {setting}'))
            else:
                setting.min_score = min_score
                setting.max_score = max_score
                setting.save()
                self.stdout.write(self.style.WARNING(f'Updated grading setting: {setting}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error adding grading setting: {e}'))
