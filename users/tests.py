from django.test import TestCase
from django.contrib.auth.models import User, Group

from teachers.models import Teacher
from users.models import UserProfile


class UserProfileTest(TestCase):
    def test_profile_links_teacher(self):
        user = User.objects.create_user(username='u1', password='pass')
        teacher = Teacher.objects.create(first_name='Alan', last_name='Turing', staff_id='T001')
        profile = UserProfile.objects.create(user=user, teacher=teacher)
        self.assertEqual(profile.teacher.staff_id, 'T001')
