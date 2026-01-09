import json

from django.core.management.base import BaseCommand, CommandError

from academics.models import Program
from academics.graduation import audit_student_graduation
from students.models import Student, Level, Session


class Command(BaseCommand):
    help = 'Graduation audit for a cohort (filter by program, level, and/or session).'

    def add_arguments(self, parser):
        parser.add_argument('--program', type=str, default=None, help='Program code')
        parser.add_argument('--level', type=str, default=None, help='Level name')
        parser.add_argument('--session', type=str, default=None, help='Current session name')
        parser.add_argument('--json', action='store_true')

    def handle(self, *args, **opts):
        qs = Student.objects.select_related('program', 'current_level', 'current_session')

        if opts.get('program'):
            try:
                program = Program.objects.get(code=opts['program'])
            except Program.DoesNotExist:
                raise CommandError('Program not found')
            qs = qs.filter(program=program)

        if opts.get('level'):
            try:
                level = Level.objects.get(name=opts['level'])
            except Level.DoesNotExist:
                raise CommandError('Level not found')
            qs = qs.filter(current_level=level)

        if opts.get('session'):
            try:
                session = Session.objects.get(name=opts['session'])
            except Session.DoesNotExist:
                raise CommandError('Session not found')
            qs = qs.filter(current_session=session)

        results = []
        for s in qs.order_by('student_id'):
            audit = audit_student_graduation(s)
            results.append(
                {
                    'student_id': s.student_id,
                    'student_name': s.full_name,
                    'program': getattr(s.program, 'code', None),
                    'cgpa': audit.cgpa,
                    'total_units_earned': audit.total_units_earned,
                    'eligible': audit.eligible,
                    'classification': audit.classification,
                    'missing_compulsory_courses': audit.missing_compulsory_courses,
                    'notes': audit.notes,
                }
            )

        summary = {
            'count': len(results),
            'eligible_count': sum(1 for r in results if r['eligible']),
            'ineligible_count': sum(1 for r in results if not r['eligible']),
        }

        if opts.get('json'):
            self.stdout.write(json.dumps({'summary': summary, 'results': results}, indent=2))
            return

        self.stdout.write(self.style.SUCCESS('Cohort Graduation Audit'))
        self.stdout.write(f"Total: {summary['count']} | Eligible: {summary['eligible_count']} | Ineligible: {summary['ineligible_count']}")
        for r in results:
            status = 'ELIGIBLE' if r['eligible'] else 'INELIGIBLE'
            self.stdout.write(f"- {r['student_id']} {r['student_name']} ({r.get('program')}): {status} CGPA={r['cgpa']} {r.get('classification') or ''}")
            if not r['eligible'] and r['notes']:
                for n in r['notes']:
                    self.stdout.write(f"    * {n}")
