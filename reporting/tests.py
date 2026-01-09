from django.test import TestCase
from django.core.management import call_command

from students.models import Student, Level, Session
from courses.models import Course
from grading.models import Enrollment, Grade, GradingSettings
from reporting.transcript_generator import TranscriptGenerator


class TranscriptSecurityDataTest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(name='100 Level')
        self.session = Session.objects.create(name='2023/2024')
        self.student = Student.objects.create(
            first_name='John',
            last_name='Doe',
            student_id='JDSEC1',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session,
        )
        self.course = Course.objects.create(code='CS101', title='Intro', units=3)
        from courses.models import CourseOffering
        offering = CourseOffering.objects.create(course=self.course, session=self.session, semester='FIRST')
        self.enrollment = Enrollment.objects.create(student=self.student, course_offering=offering)
        # Minimal grading settings
        GradingSettings.objects.create(grade_name='A', min_score=90, max_score=100, grade_point=4.0)
        GradingSettings.objects.create(grade_name='F', min_score=0, max_score=59, grade_point=0.0)
        Grade.objects.create(enrollment=self.enrollment, ca_score=20, exam_score=70)  # total 90

    def test_generate_transcript_returns_security_data(self):
        gen = TranscriptGenerator('OFFICIAL_LAYOUT')
        result = gen.generate_transcript(
            self.student.student_id,
            'tmp/tmp_test_transcript.pdf',
            {'add_security_features': True},
            return_security_data=True,
        )
        self.assertTrue(result['success'], msg=result.get('error'))
        self.assertIn('security_data', result)
        self.assertTrue(result['security_data'])
        self.assertIn('verification_code', result['security_data'])


class CalculateGradesCommandTest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(name='100 Level')
        self.session = Session.objects.create(name='2023/2024')
        self.student = Student.objects.create(
            first_name='Jane',
            last_name='Doe',
            student_id='JDSEC2',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session,
        )
        self.course = Course.objects.create(code='CS102', title='Intro2', units=3)
        from courses.models import CourseOffering
        offering = CourseOffering.objects.create(course=self.course, session=self.session, semester='FIRST')
        self.enrollment = Enrollment.objects.create(student=self.student, course_offering=offering)
        GradingSettings.objects.create(grade_name='A', min_score=90, max_score=100, grade_point=4.0)
        GradingSettings.objects.create(grade_name='C', min_score=70, max_score=79, grade_point=2.0)
        GradingSettings.objects.create(grade_name='F', min_score=0, max_score=59, grade_point=0.0)
        self.grade = Grade.objects.create(enrollment=self.enrollment, ca_score=10, exam_score=60)  # total 70 => C

    def test_calculate_grades_command_runs(self):
        # mutate grade so command has something to fix
        self.grade.grade = ''
        self.grade.total_score = 0
        self.grade.save(update_fields=['grade', 'total_score'])

        call_command('calculate_grades')
        self.grade.refresh_from_db()
        self.assertEqual(self.grade.total_score, 70)
        self.assertEqual(self.grade.grade, 'C')

