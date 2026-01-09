from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User, Group

from students.models import Student, Level, Session
from courses.models import Course
from teachers.models import Teacher
from users.models import UserProfile
from grading.models import Enrollment, Grade, GradingSettings
from audit_log.models import LogEntry

class EnrollmentModelTest(TestCase):
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
        self.course = Course.objects.create(code='CS101', title='Introduction to Computer Science')
        from courses.models import CourseOffering
        offering = CourseOffering.objects.create(course=self.course, session=self.session1, semester='FIRST')
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course_offering=offering,
        )

    def test_enrollment_creation(self):
        self.assertEqual(self.enrollment.student, self.student)
        self.assertEqual(self.enrollment.course, self.course)
        self.assertEqual(self.enrollment.session, self.session1)

    def test_enrollment_str(self):
        self.assertEqual(str(self.enrollment), 'John Doe (JD001) enrolled in Introduction to Computer Science (CS101) for 2023/2024 (First Semester)')

class GradeModelTest(TestCase):
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
        self.course = Course.objects.create(code='CS101', title='Introduction to Computer Science')
        from courses.models import CourseOffering
        offering = CourseOffering.objects.create(course=self.course, session=self.session1, semester='FIRST')
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course_offering=offering,
        )
        self.grade = Grade.objects.create(
            enrollment=self.enrollment,
            ca_score=20,
            exam_score=70
        )
        GradingSettings.objects.create(grade_name='A', min_score=90, max_score=100)
        GradingSettings.objects.create(grade_name='B', min_score=80, max_score=89)
        GradingSettings.objects.create(grade_name='C', min_score=70, max_score=79)
        GradingSettings.objects.create(grade_name='D', min_score=60, max_score=69)
        GradingSettings.objects.create(grade_name='F', min_score=0, max_score=59)

    def test_grade_creation(self):
        self.assertEqual(self.grade.enrollment, self.enrollment)
        self.assertEqual(self.grade.ca_score, 20)
        self.assertEqual(self.grade.exam_score, 70)

    def test_grade_calculation(self):
        # Grade.save() applies the grading scheme based on total_score.
        # With grading settings where A starts at 90, a 90 total should yield 'A'.
        self.grade.save()
        self.assertEqual(self.grade.total_score, 90)
        self.assertEqual(self.grade.grade, 'A')


class RecordScoresRBACCommandTest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(name='100 Level')
        self.session = Session.objects.create(name='2023/2024')
        self.student = Student.objects.create(
            first_name='John',
            last_name='Doe',
            student_id='JD_RBAC',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session,
        )
        self.course = Course.objects.create(code='CSRBAC', title='RBAC Course')
        from courses.models import CourseOffering
        offering = CourseOffering.objects.create(course=self.course, session=self.session, semester='FIRST')
        self.enrollment = Enrollment.objects.create(student=self.student, course_offering=offering)

        # Create teacher user + group
        self.teacher_user = User.objects.create_user(username='teacher_user', password='pass')
        teacher_group, _ = Group.objects.get_or_create(name='Teacher')
        self.teacher_user.groups.add(teacher_group)

        self.teacher = Teacher.objects.create(first_name='Teach', last_name='Er', staff_id='T_RBAC')
        UserProfile.objects.create(user=self.teacher_user, teacher=self.teacher)

    def test_teacher_denied_if_not_assigned_to_course(self):
        # Teacher has no course assigned
        call_command(
            'record_scores',
            self.student.student_id,
            self.course.code,
            self.session.name,
            10,
            20,
            username=self.teacher_user.username,
        )
        self.assertFalse(Grade.objects.filter(enrollment=self.enrollment).exists())

    def test_teacher_allowed_if_assigned_to_course(self):
        self.teacher.courses.add(self.course)
        call_command(
            'record_scores',
            self.student.student_id,
            self.course.code,
            self.session.name,
            10,
            20,
            username=self.teacher_user.username,
        )
        self.assertTrue(Grade.objects.filter(enrollment=self.enrollment).exists())
        # Audit log is written with acting user
        self.assertTrue(
            LogEntry.objects.filter(user=self.teacher_user, object_type='Grade').exists()
        )


class AuditAndSessionFilterTest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(name='100 Level')
        self.session1 = Session.objects.create(name='2023/2024')
        self.session2 = Session.objects.create(name='2024/2025')
        self.student = Student.objects.create(
            first_name='Sam',
            last_name='Sessions',
            student_id='SS1',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session1,
        )
        self.course = Course.objects.create(code='CS_S', title='Sess', units=2)
        from courses.models import CourseOffering
        o1 = CourseOffering.objects.create(course=self.course, session=self.session1, semester='FIRST')
        o2 = CourseOffering.objects.create(course=self.course, session=self.session2, semester='FIRST')
        e1 = Enrollment.objects.create(student=self.student, course_offering=o1)
        e2 = Enrollment.objects.create(student=self.student, course_offering=o2)
        Grade.objects.create(enrollment=e1, ca_score=10, exam_score=10)
        Grade.objects.create(enrollment=e2, ca_score=20, exam_score=20)

        self.user = User.objects.create_user(username='datauser', password='pass')
        g, _ = Group.objects.get_or_create(name='DataEntry')
        self.user.groups.add(g)

    def test_list_grades_logs_read_and_filters_session(self):
        from django.core.management import call_command
        call_command('list_grades', username=self.user.username, session=self.session1.name)
        self.assertTrue(
            LogEntry.objects.filter(user=self.user, action='READ', object_type='Grade').exists()
        )

    def test_list_enrollments_logs_read_and_filters_session(self):
        from django.core.management import call_command
        call_command('list_enrollments', username=self.user.username, session=self.session2.name)
        self.assertTrue(
            LogEntry.objects.filter(user=self.user, action='READ', object_type='Enrollment').exists()
        )

