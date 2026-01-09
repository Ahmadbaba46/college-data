import json

from django.test import TestCase
from django.core.management import call_command
from io import StringIO

from students.models import Student, Level, Session
from courses.models import Course
from grading.models import Enrollment


class RepeatedCoursesReportTest(TestCase):
    def setUp(self):
        level = Level.objects.create(name='100 Level')
        s1 = Session.objects.create(name='2023/2024')
        s2 = Session.objects.create(name='2024/2025')
        self.student = Student.objects.create(
            first_name='Rep',
            last_name='Eater',
            student_id='REP1',
            entry_level=level,
            current_level=level,
            current_session=s2,
        )
        course = Course.objects.create(code='CSC999', title='Repeatable', units=2)
        from courses.models import CourseOffering
        o1 = CourseOffering.objects.create(course=course, session=s1, semester='FIRST')
        o2 = CourseOffering.objects.create(course=course, session=s2, semester='FIRST')
        Enrollment.objects.create(student=self.student, course_offering=o1)
        Enrollment.objects.create(student=self.student, course_offering=o2)

    def test_repeated_courses_report_json(self):
        out = StringIO()
        call_command('repeated_courses_report', '--json', stdout=out)
        payload = json.loads(out.getvalue())
        assert payload['count'] == 1
        assert payload['results'][0]['student_id'] == 'REP1'
        assert payload['results'][0]['course_code'] == 'CSC999'
        assert 'attempt_details' in payload['results'][0]
        assert len(payload['results'][0]['attempt_details']) == 2
