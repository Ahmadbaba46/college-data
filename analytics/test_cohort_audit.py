import json
from io import StringIO

from django.test import TestCase
from django.core.management import call_command

from academics.models import Program, CurriculumCourse
from students.models import Student, Level, Session
from courses.models import Course, CourseOffering
from grading.models import Enrollment, Grade, GradingSettings


class CohortAuditTest(TestCase):
    def setUp(self):
        level = Level.objects.create(name='100 Level')
        session = Session.objects.create(name='2023/2024')
        program = Program.objects.create(code='COH', name='Cohort', classification_scheme=Program.CLASS_SCHEME_ND, min_units_to_graduate=2)

        c = Course.objects.create(code='C1', title='Core', units=2)
        CurriculumCourse.objects.create(program=program, course=c, level=level, semester='FIRST', is_compulsory=True)

        GradingSettings.objects.create(grade_name='A', min_score=90, max_score=100, grade_point=4.0)

        offering = CourseOffering.objects.create(course=c, session=session, semester='FIRST', level=level)

        s1 = Student.objects.create(first_name='A', last_name='A', student_id='C1', entry_level=level, current_level=level, current_session=session, program=program)
        s2 = Student.objects.create(first_name='B', last_name='B', student_id='C2', entry_level=level, current_level=level, current_session=session, program=program)

        e1 = Enrollment.objects.create(student=s1, course_offering=offering)
        Grade.objects.create(enrollment=e1, ca_score=20, exam_score=70, grade='A', total_score=90)

        # s2 missing grade -> should be ineligible

    def test_cohort_audit_json(self):
        out = StringIO()
        call_command('cohort_graduation_audit', '--program', 'COH', '--json', stdout=out)
        payload = json.loads(out.getvalue())
        assert payload['summary']['count'] == 2
        assert payload['summary']['eligible_count'] == 1
