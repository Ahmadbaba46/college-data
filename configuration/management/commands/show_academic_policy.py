from django.core.management.base import BaseCommand

from configuration.models import AcademicPolicySettings


class Command(BaseCommand):
    help = 'Show academic policy settings (e.g., repeat course policy)'

    def handle(self, *args, **options):
        s = AcademicPolicySettings.get_solo()
        self.stdout.write(self.style.SUCCESS('Academic Policy Settings'))
        self.stdout.write(f"- repeat_policy: {s.repeat_policy}")
        self.stdout.write(f"- require_approved_for_transcripts: {s.require_approved_for_transcripts}")
        self.stdout.write(f"- require_approved_for_exports: {s.require_approved_for_exports}")
        self.stdout.write(f"- require_approved_for_metrics: {s.require_approved_for_metrics}")
