from django.test import TestCase
from students.models import Student, Level, Session

class StudentModelTest(TestCase):
    def setUp(self):
        self.level1 = Level.objects.create(name='100 Level')
        self.session1 = Session.objects.create(name='2023/2024')
        self.student = Student.objects.create(
            first_name='John',
            last_name='Doe',
            student_id='JD001',
            entry_level=self.level1,
            current_level=self.level1,
            current_session=self.session1
        )

    def test_student_creation(self):
        self.assertEqual(self.student.first_name, 'John')
        self.assertEqual(self.student.last_name, 'Doe')
        self.assertEqual(self.student.student_id, 'JD001')
        self.assertEqual(self.student.entry_level, self.level1)
        self.assertEqual(self.student.current_level, self.level1)
        self.assertEqual(self.student.current_session, self.session1)

    def test_student_str(self):
        self.assertEqual(str(self.student), 'John Doe (JD001)')