from django.core.management.base import BaseCommand

from academics.models import Program


class Command(BaseCommand):
    help = 'Create a Program'

    def add_arguments(self, parser):
        parser.add_argument('code', type=str)
        parser.add_argument('name', type=str)
        parser.add_argument('--scheme', choices=[Program.CLASS_SCHEME_BSC, Program.CLASS_SCHEME_ND], default=Program.CLASS_SCHEME_BSC)

    def handle(self, *args, **opts):
        p, created = Program.objects.get_or_create(
            code=opts['code'],
            defaults={'name': opts['name'], 'classification_scheme': opts['scheme']},
        )
        if not created:
            p.name = opts['name']
            p.classification_scheme = opts['scheme']
            p.save(update_fields=['name', 'classification_scheme'])
        self.stdout.write(self.style.SUCCESS(f"Program {p.code} saved."))
