from django.core.management.base import BaseCommand
from students.models import Student, Session
from courses.models import Course, CourseOffering
from grading.models import Enrollment
from courses.registration_rules import can_enroll

class Command(BaseCommand):
    help = 'Enroll a student in a course for a specific session'

    def add_arguments(self, parser):
        parser.add_argument('student_id', type=str, help='The ID of the student to enroll')
        parser.add_argument('course_code', type=str, help='The code of the course to enroll in')
        parser.add_argument('session_name', type=str, help='The name of the session')
        parser.add_argument(
            '--semester',
            type=str,
            default=None,
            choices=[Enrollment.SEMESTER_FIRST, Enrollment.SEMESTER_SECOND, Enrollment.SEMESTER_SUMMER],
            help='Semester (FIRST/SECOND/SUMMER). If omitted, uses course default_semester (or FIRST).',
        )

    def handle(self, *args, **kwargs):
        student_id = kwargs['student_id']
        course_code = kwargs['course_code']
        session_name = kwargs['session_name']
        semester = kwargs.get('semester')  # may be None; inferred from course if not provided

        try:
            student = Student.objects.get(student_id=student_id)
            course = Course.objects.get(code=course_code)
            session = Session.objects.get(name=session_name)

            if not semester:
                # Infer from course default_semester (FIRST/SECOND) when available.
                semester = course.default_semester or Enrollment.SEMESTER_FIRST

            # Basic availability validation: ensure course is configured for this session & level
            if not course.sessions.filter(pk=session.pk).exists():
                self.stdout.write(self.style.ERROR('Course is not available for this session.'))
                return
            if student.current_level and not course.levels.filter(pk=student.current_level.pk).exists():
                self.stdout.write(self.style.ERROR('Course is not available for the student\'s current level.'))
                return

            offering, _ = CourseOffering.objects.get_or_create(
                course=course,
                session=session,
                semester=semester,
                level=student.current_level,
            )

            rule = can_enroll(student, offering)
            if not rule.ok:
                self.stdout.write(self.style.ERROR(rule.error or 'Enrollment not allowed.'))
                return

            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course_offering=offering,
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully enrolled student {student} in course {course} for session {session}'))
            else:
                self.stdout.write(self.style.WARNING(f'Student {student} is already enrolled in course {course} for session {session}'))

        except Student.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Student with ID {student_id} does not exist.'))
        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Course with code {course_code} does not exist.'))
        except Session.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Session with name {session_name} does not exist.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error enrolling student: {e}'))
