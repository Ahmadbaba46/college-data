from django.test import TestCase
from django.core.management import call_command

from configuration.models import AcademicPolicySettings
from students.models import Student, Level, Session
from courses.models import Course, CourseOffering
from grading.models import Enrollment, Grade, GradingSettings


class ApprovalWorkflowTest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(name='100 Level')
        self.session = Session.objects.create(name='2023/2024')
        self.student = Student.objects.create(
            first_name='App',
            last_name='Rove',
            student_id='APP1',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session,
        )
        self.course = Course.objects.create(code='APP101', title='Approve', units=3)
        self.course.levels.add(self.level)
        self.course.sessions.add(self.session)
        self.offering = CourseOffering.objects.create(course=self.course, session=self.session, semester='FIRST', level=self.level)
        self.enrollment = Enrollment.objects.create(student=self.student, course_offering=self.offering)

        GradingSettings.objects.create(grade_name='A', min_score=90, max_score=100, grade_point=4.0)
        GradingSettings.objects.create(grade_name='F', min_score=0, max_score=59, grade_point=0.0)

        self.grade = Grade.objects.create(enrollment=self.enrollment, ca_score=20, exam_score=70)  # total 90

    def test_metrics_can_require_approved(self):
        policy = AcademicPolicySettings.get_solo()
        policy.require_approved_for_metrics = True
        policy.save()

        # grade is DRAFT, so CGPA should be 0
        self.student.update_academic_metrics(save=False)
        self.assertEqual(self.student.current_cgpa, 0.0)

        # approve grade
        self.grade.status = Grade.STATUS_APPROVED
        self.grade.save(update_fields=['status'])

        self.student.update_academic_metrics(save=False)
        self.assertEqual(self.student.current_cgpa, 4.0)
