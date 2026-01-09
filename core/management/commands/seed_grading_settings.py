from django.core.management.base import BaseCommand

from grading.models import GradingSettings
from users.rbac_helpers import resolve_acting_context

class Command(BaseCommand):
    help = 'Seed the database with initial grading settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='(RBAC) Acting username. Must be Admin to seed grading settings.',
        )

    def handle(self, *args, **kwargs):
        username = kwargs.get('username')
        if username:
            try:
                ctx = resolve_acting_context(username)
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
                return

            if ctx.user is None or not getattr(ctx.user, 'is_superuser', False):
                if 'Admin' not in set(ctx.user.groups.values_list('name', flat=True)):
                    self.stdout.write(self.style.ERROR('Permission denied: only Admin can seed grading settings.'))
                    return

        self.stdout.write('Seeding grading settings...')

        GradingSettings.objects.update_or_create(grade_name='A', defaults={'min_score': 70, 'max_score': 100, 'grade_point': 4.0})
        GradingSettings.objects.update_or_create(grade_name='B', defaults={'min_score': 60, 'max_score': 69.99, 'grade_point': 3.0})
        GradingSettings.objects.update_or_create(grade_name='C', defaults={'min_score': 50, 'max_score': 59.99, 'grade_point': 2.0})
        GradingSettings.objects.update_or_create(grade_name='D', defaults={'min_score': 45, 'max_score': 49.99, 'grade_point': 1.0})
        GradingSettings.objects.update_or_create(grade_name='E', defaults={'min_score': 40, 'max_score': 44.99, 'grade_point': 0.0})
        GradingSettings.objects.update_or_create(grade_name='F', defaults={'min_score': 0, 'max_score': 39.99, 'grade_point': 0.0})

        self.stdout.write(self.style.SUCCESS('Successfully seeded grading settings'))
