from django.test import TestCase

from configuration.models import AcademicPolicySettings
from students.models import Student, Level, Session
from courses.models import Course
from grading.models import Enrollment, Grade, GradingSettings


class RepeatPolicyCGPATest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(name='100 Level')
        self.s1 = Session.objects.create(name='2023/2024')
        self.s2 = Session.objects.create(name='2024/2025')
        self.student = Student.objects.create(
            first_name='Pol',
            last_name='Icy',
            student_id='POL1',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.s2,
        )
        self.course = Course.objects.create(code='POL101', title='Policy', units=3)

        GradingSettings.objects.create(grade_name='A', min_score=90, max_score=100, grade_point=4.0)
        GradingSettings.objects.create(grade_name='C', min_score=70, max_score=79, grade_point=2.0)

        from courses.models import CourseOffering
        o1 = CourseOffering.objects.create(course=self.course, session=self.s1, semester='FIRST')
        o2 = CourseOffering.objects.create(course=self.course, session=self.s2, semester='FIRST')
        e1 = Enrollment.objects.create(student=self.student, course_offering=o1)
        e2 = Enrollment.objects.create(student=self.student, course_offering=o2)

        Grade.objects.create(enrollment=e1, ca_score=10, exam_score=60)  # 70 -> C (2.0)
        Grade.objects.create(enrollment=e2, ca_score=20, exam_score=70)  # 90 -> A (4.0)

    def test_repeat_policy_all_counts_both(self):
        s = AcademicPolicySettings.get_solo()
        s.repeat_policy = AcademicPolicySettings.REPEAT_ALL
        s.save()

        self.student.update_academic_metrics(save=False)
        # (3*2 + 3*4)/(3+3) = 3.0
        self.assertEqual(self.student.current_cgpa, 3.0)

    def test_repeat_policy_latest_counts_latest_only(self):
        s = AcademicPolicySettings.get_solo()
        s.repeat_policy = AcademicPolicySettings.REPEAT_LATEST
        s.save()

        self.student.update_academic_metrics(save=False)
        # latest is A => 4.0
        self.assertEqual(self.student.current_cgpa, 4.0)

    def test_repeat_policy_best_counts_best_only(self):
        s = AcademicPolicySettings.get_solo()
        s.repeat_policy = AcademicPolicySettings.REPEAT_BEST
        s.save()

        self.student.update_academic_metrics(save=False)
        # best is A => 4.0
        self.assertEqual(self.student.current_cgpa, 4.0)
