import json
from io import StringIO

from django.test import TestCase
from django.core.management import call_command

from academics.models import Program, CurriculumCourse, Prerequisite
from students.models import Student, Level, Session
from courses.models import Course, CourseOffering
from grading.models import Enrollment, Grade, GradingSettings


class SuggestCoursesTest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(name='100 Level')
        self.session = Session.objects.create(name='2023/2024')
        self.program = Program.objects.create(code='CS', name='Computer Science', classification_scheme=Program.CLASS_SCHEME_BSC)

        self.student = Student.objects.create(
            first_name='Elig',
            last_name='Able',
            student_id='EL1',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session,
            program=self.program,
        )

        self.course1 = Course.objects.create(code='CS101', title='Intro', units=2)
        self.course2 = Course.objects.create(code='CS102', title='Next', units=2)

        CurriculumCourse.objects.create(program=self.program, course=self.course1, level=self.level, semester='FIRST', is_compulsory=True)
        CurriculumCourse.objects.create(program=self.program, course=self.course2, level=self.level, semester='FIRST', is_compulsory=True)

        Prerequisite.objects.create(program=self.program, course=self.course2, prerequisite_course=self.course1)

        # student passed CS101
        GradingSettings.objects.create(grade_name='A', min_score=90, max_score=100, grade_point=4.0)
        offering = CourseOffering.objects.create(course=self.course1, session=self.session, semester='FIRST', level=self.level)
        enr = Enrollment.objects.create(student=self.student, course_offering=offering)
        Grade.objects.create(enrollment=enr, ca_score=20, exam_score=70, grade='A', total_score=90)

    def test_suggest_courses_json(self):
        out = StringIO()
        call_command('suggest_courses', 'EL1', '--semester', 'FIRST', '--json', stdout=out)
        data = json.loads(out.getvalue())
        # CS101 passed, so should suggest CS102 and mark eligible
        codes = {d['course_code']: d for d in data}
        assert 'CS101' not in codes
        assert codes['CS102']['eligible'] is True
