from django.core.management.base import BaseCommand
from students.models import Student, Session
from courses.models import Course, CourseOffering
from grading.models import Enrollment, Grade
from audit_log.models import LogEntry
from users.rbac_helpers import resolve_acting_context

class Command(BaseCommand):
    help = 'Record CA and exam scores for a student in a course for a specific session'

    def add_arguments(self, parser):
        parser.add_argument('student_id', type=str, help='The ID of the student')
        parser.add_argument('course_code', type=str, help='The code of the course')
        parser.add_argument('session_name', type=str, help='The name of the session')
        parser.add_argument('ca_score', type=float, help='The Continuous Assessment score')
        parser.add_argument('exam_score', type=float, help='The Exam score')
        parser.add_argument(
            '--semester',
            type=str,
            default=Enrollment.SEMESTER_FIRST,
            choices=[Enrollment.SEMESTER_FIRST, Enrollment.SEMESTER_SECOND, Enrollment.SEMESTER_SUMMER],
            help='Semester (FIRST/SECOND/SUMMER). Default FIRST.',
        )
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='(RBAC) Acting Django username. If a Teacher, they must be assigned to the course.',
        )

    def handle(self, *args, **kwargs):
        student_id = kwargs['student_id']
        course_code = kwargs['course_code']
        session_name = kwargs['session_name']
        ca_score = kwargs['ca_score']
        exam_score = kwargs['exam_score']
        username = kwargs.get('username')
        semester = kwargs.get('semester') or Enrollment.SEMESTER_FIRST

        try:
            ctx = resolve_acting_context(username)
            acting_user = ctx.user
            teacher = ctx.teacher if ctx.is_teacher_limited else None

            student = Student.objects.get(student_id=student_id)
            course = Course.objects.get(code=course_code)
            session = Session.objects.get(name=session_name)

            # RBAC enforcement: teachers can only record scores for their assigned courses
            if teacher is not None:
                if not teacher.courses.filter(pk=course.pk).exists():
                    self.stdout.write(
                        self.style.ERROR(
                            f'Permission denied: teacher {teacher.staff_id} is not assigned to course {course.code}.'
                        )
                    )
                    return

            offering = CourseOffering.objects.get(course=course, session=session, semester=semester, level=None)
            enrollment = Enrollment.objects.get(student=student, course_offering=offering)

            grade, created = Grade.objects.get_or_create(
                enrollment=enrollment,
                defaults={'ca_score': ca_score, 'exam_score': exam_score}
            )

            if not created:
                grade.ca_score = ca_score
                grade.exam_score = exam_score
                grade.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated scores for {enrollment}'))
                LogEntry.log_action(
                    user=acting_user,
                    action='UPDATE',
                    object_type='Grade',
                    object_id=str(grade.pk),
                    message=(
                        f"Updated scores: student={student.student_id}, course={course.code}, session={session.name}, "
                        f"ca={ca_score}, exam={exam_score}, total={grade.total_score}, grade={grade.grade}"
                    ),
                )
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully recorded scores for {enrollment}'))
                LogEntry.log_action(
                    user=acting_user,
                    action='CREATE',
                    object_type='Grade',
                    object_id=str(grade.pk),
                    message=(
                        f"Recorded scores: student={student.student_id}, course={course.code}, session={session.name}, "
                        f"ca={ca_score}, exam={exam_score}, total={grade.total_score}, grade={grade.grade}"
                    ),
                )

        except Student.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Student with ID {student_id} does not exist.'))
        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Course with code {course_code} does not exist.'))
        except Session.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Session with name {session_name} does not exist.'))
        except Enrollment.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Enrollment for student {student_id} in course {course_code} for session {session_name} does not exist.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error recording scores: {e}'))
