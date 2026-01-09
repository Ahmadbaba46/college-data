import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from users.models import UserProfile


class Command(BaseCommand):
    help = 'List users with their roles (Django Groups).'

    def add_arguments(self, parser):
        parser.add_argument('--json', action='store_true', help='Output JSON')
        parser.add_argument('--with-teachers', action='store_true', help='Include linked teacher staff_id (UserProfile.teacher)')

    def handle(self, *args, **opts):
        include_teacher = bool(opts.get('with_teachers'))
        out_json = bool(opts.get('json'))

        users = User.objects.all().order_by('username')

        results = []
        for u in users:
            roles = list(u.groups.values_list('name', flat=True))
            row = {
                'username': u.username,
                'email': u.email,
                'last_login': u.last_login.isoformat() if u.last_login else None,
                'date_joined': u.date_joined.isoformat() if u.date_joined else None,
                'is_superuser': bool(u.is_superuser),
                'is_staff': bool(u.is_staff),
                'is_active': bool(u.is_active),
                'roles': roles,
            }
            if include_teacher:
                prof = UserProfile.objects.filter(user=u).select_related('teacher').first()
                row['teacher_staff_id'] = prof.teacher.staff_id if prof and prof.teacher else None
            results.append(row)

        if out_json:
            self.stdout.write(json.dumps(results, indent=2))
            return

        # Text table output
        self.stdout.write('Users:')
        for r in results:
            base = (
                f"- {r['username']} | email={r['email']} | last_login={r['last_login']} | date_joined={r['date_joined']} "
                f"| superuser={r['is_superuser']} | staff={r['is_staff']} | active={r['is_active']} | roles={r['roles']}"
            )
            if include_teacher:
                base += f" | teacher_staff_id={r.get('teacher_staff_id')}"
            self.stdout.write(base)
