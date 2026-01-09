import json
from io import StringIO

from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User, Group


class ListUsersCommandTest(TestCase):
    def test_list_users_json(self):
        u = User.objects.create_user(username='u1', password='pass')
        g, _ = Group.objects.get_or_create(name='DataEntry')
        u.groups.add(g)

        out = StringIO()
        call_command('list_users', '--json', stdout=out)
        data = json.loads(out.getvalue())
        assert any(
            row['username'] == 'u1'
            and 'DataEntry' in row['roles']
            and row.get('email') is not None
            and 'date_joined' in row
            for row in data
        )
