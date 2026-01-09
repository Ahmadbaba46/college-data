from django.test import TestCase
from courses.models import Course
from students.models import Level, Session

class CourseModelTest(TestCase):
    def setUp(self):
        self.level1 = Level.objects.create(name='100 Level')
        self.session1 = Session.objects.create(name='2023/2024')
        self.course = Course.objects.create(code='CS101', title='Introduction to Computer Science')
        self.course.levels.add(self.level1)
        self.course.sessions.add(self.session1)

    def test_course_creation(self):
        self.assertEqual(self.course.code, 'CS101')
        self.assertEqual(self.course.title, 'Introduction to Computer Science')
        self.assertIn(self.level1, self.course.levels.all())
        self.assertIn(self.session1, self.course.sessions.all())

    def test_course_str(self):
        self.assertEqual(str(self.course), 'Introduction to Computer Science (CS101)')