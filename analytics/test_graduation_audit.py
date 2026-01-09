import json
from io import StringIO

from django.test import TestCase
from django.core.management import call_command

from academics.models import Program, CurriculumCourse, ProgramClassificationThreshold
from students.models import Student, Level, Session
from courses.models import Course, CourseOffering
from grading.models import Enrollment, Grade, GradingSettings


class GraduationAuditReportTest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(name='100 Level')
        self.session = Session.objects.create(name='2023/2024')

        # BSc program
        self.program = Program.objects.create(code='BSC-CS', name='BSc CS', classification_scheme=Program.CLASS_SCHEME_BSC, min_units_to_graduate=3)

        self.student = Student.objects.create(
            first_name='Grad',
            last_name='Uate',
            student_id='GRAD1',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session,
            program=self.program,
        )

        self.course = Course.objects.create(code='G101', title='GradCourse', units=3)
        CurriculumCourse.objects.create(program=self.program, course=self.course, level=self.level, semester='FIRST', is_compulsory=True)

        GradingSettings.objects.create(grade_name='A', min_score=90, max_score=100, grade_point=4.0)

        offering = CourseOffering.objects.create(course=self.course, session=self.session, semester='FIRST', level=self.level)
        enr = Enrollment.objects.create(student=self.student, course_offering=offering)
        Grade.objects.create(enrollment=enr, ca_score=20, exam_score=70, grade='A', total_score=90)

    def test_graduation_audit_json(self):
        out = StringIO()
        call_command('graduation_audit_report', 'GRAD1', '--json', stdout=out)
        data = json.loads(out.getvalue())
        assert data['eligible'] is True

        # Override thresholds: require 3.9 for First Class
        ProgramClassificationThreshold.objects.filter(program=self.program, label='First Class').update(min_cgpa=3.9)

        out2 = StringIO()
        call_command('graduation_audit_report', 'GRAD1', '--json', stdout=out2)
        data2 = json.loads(out2.getvalue())
        # cgpa is 4.0 so still First Class
        assert data2['classification'] == 'First Class'
