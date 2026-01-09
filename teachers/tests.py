from django.test import TestCase
from teachers.models import Teacher
from courses.models import Course

class TeacherModelTest(TestCase):
    def setUp(self):
        self.course1 = Course.objects.create(code='CS101', title='Introduction to Computer Science')
        self.teacher = Teacher.objects.create(
            first_name='Alan',
            last_name='Turing',
            staff_id='AT001',
        )
        self.teacher.courses.add(self.course1)

    def test_teacher_creation(self):
        self.assertEqual(self.teacher.first_name, 'Alan')
        self.assertEqual(self.teacher.last_name, 'Turing')
        self.assertEqual(self.teacher.staff_id, 'AT001')
        self.assertIn(self.course1, self.teacher.courses.all())

    def test_teacher_str(self):
        self.assertEqual(str(self.teacher), 'Alan Turing (AT001)')