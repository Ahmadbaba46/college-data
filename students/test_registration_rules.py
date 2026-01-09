from django.test import TestCase
from django.core.management import call_command

from students.models import Student, Level, Session
from courses.models import Course, CourseOffering
from grading.models import Enrollment


class RegistrationRulesTest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(name='100 Level')
        self.session = Session.objects.create(name='2023/2024')
        self.student = Student.objects.create(
            first_name='Reg',
            last_name='Rule',
            student_id='REG1',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session,
        )
        self.course = Course.objects.create(code='REG101', title='Rules', units=2)
        self.course.levels.add(self.level)
        self.course.sessions.add(self.session)

    def test_capacity_blocks_enrollment(self):
        offering = CourseOffering.objects.create(course=self.course, session=self.session, semester='FIRST', level=self.level, capacity=1, is_active=True)
        Enrollment.objects.create(student=self.student, course_offering=offering)

        # second student
        s2 = Student.objects.create(
            first_name='Reg2',
            last_name='Rule2',
            student_id='REG2',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session,
        )

        call_command('enroll_student', s2.student_id, self.course.code, self.session.name)
        self.assertEqual(Enrollment.objects.filter(course_offering=offering).count(), 1)

    def test_inactive_offering_blocks_enrollment(self):
        offering = CourseOffering.objects.create(course=self.course, session=self.session, semester='FIRST', level=self.level, capacity=10, is_active=False)
        call_command('enroll_student', self.student.student_id, self.course.code, self.session.name)
        # should not create enrollment
        self.assertEqual(Enrollment.objects.count(), 0)
