from django.core.management.base import BaseCommand

from configuration.models import AcademicPolicySettings


class Command(BaseCommand):
    help = 'Update academic policy settings (e.g., repeat course policy)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--repeat-policy',
            choices=[
                AcademicPolicySettings.REPEAT_ALL,
                AcademicPolicySettings.REPEAT_LATEST,
                AcademicPolicySettings.REPEAT_BEST,
            ],
            required=False,
            help='How to handle repeated courses in GPA/CGPA',
        )
        parser.add_argument('--require-approved-for-transcripts', action='store_true', help='Require APPROVED grades for transcript GPA/CGPA')
        parser.add_argument('--require-approved-for-exports', action='store_true', help='Only export APPROVED grades')
        parser.add_argument('--require-approved-for-metrics', action='store_true', help='Require APPROVED grades for CGPA/metrics')
        parser.add_argument('--clear-require-approved-for-transcripts', action='store_true')
        parser.add_argument('--clear-require-approved-for-exports', action='store_true')
        parser.add_argument('--clear-require-approved-for-metrics', action='store_true')

    def handle(self, *args, **options):
        s = AcademicPolicySettings.get_solo()

        changed = []
        if options.get('repeat_policy'):
            s.repeat_policy = options['repeat_policy']
            changed.append('repeat_policy')

        if options.get('require_approved_for_transcripts'):
            s.require_approved_for_transcripts = True
            changed.append('require_approved_for_transcripts')
        if options.get('require_approved_for_exports'):
            s.require_approved_for_exports = True
            changed.append('require_approved_for_exports')
        if options.get('require_approved_for_metrics'):
            s.require_approved_for_metrics = True
            changed.append('require_approved_for_metrics')

        if options.get('clear_require_approved_for_transcripts'):
            s.require_approved_for_transcripts = False
            changed.append('require_approved_for_transcripts')
        if options.get('clear_require_approved_for_exports'):
            s.require_approved_for_exports = False
            changed.append('require_approved_for_exports')
        if options.get('clear_require_approved_for_metrics'):
            s.require_approved_for_metrics = False
            changed.append('require_approved_for_metrics')

        if not changed:
            self.stdout.write(self.style.WARNING('No changes specified.'))
            return

        s.save(update_fields=list(set(changed)))
        self.stdout.write(self.style.SUCCESS('Updated academic policy settings.'))
        self.stdout.write(f"repeat_policy={s.repeat_policy}")
        self.stdout.write(f"require_approved_for_transcripts={s.require_approved_for_transcripts}")
        self.stdout.write(f"require_approved_for_exports={s.require_approved_for_exports}")
        self.stdout.write(f"require_approved_for_metrics={s.require_approved_for_metrics}")
