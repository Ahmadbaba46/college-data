import csv
from django.core.management.base import BaseCommand
from students.models import Student, Session
from courses.models import Course, CourseOffering
from grading.models import Enrollment
from courses.registration_rules import can_enroll

class Command(BaseCommand):
    help = 'Bulk enroll students from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file containing enrollment data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                student_id = row.get('student_id')
                course_code = row.get('course_code')
                session_name = row.get('session_name')
                semester = (row.get('semester') or '').strip().upper() or None

                if not all([student_id, course_code, session_name]):
                    self.stdout.write(self.style.ERROR(f'Skipping row due to missing data: {row}'))
                    continue

                try:
                    student = Student.objects.get(student_id=student_id)
                    course = Course.objects.get(code=course_code)
                    session = Session.objects.get(name=session_name)

                    if not semester:
                        semester = course.default_semester or Enrollment.SEMESTER_FIRST

                    # Basic availability validation: ensure course is configured for this session & level
                    if not course.sessions.filter(pk=session.pk).exists():
                        self.stdout.write(self.style.ERROR(f'Course {course.code} is not available for session {session.name}.'))
                        continue
                    if student.current_level and not course.levels.filter(pk=student.current_level.pk).exists():
                        self.stdout.write(self.style.ERROR(f'Course {course.code} is not available for student level {student.current_level}.'))
                        continue

                    offering, _ = CourseOffering.objects.get_or_create(
                        course=course,
                        session=session,
                        semester=semester,
                        level=student.current_level,
                    )

                    rule = can_enroll(student, offering)
                    if not rule.ok:
                        self.stdout.write(self.style.ERROR(f'Cannot enroll {student.student_id} into {course.code}: {rule.error}'))
                        continue

                    enrollment, created = Enrollment.objects.get_or_create(
                        student=student,
                        course_offering=offering,
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Enrolled student {student} in course {course} for session {session}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Student {student} is already enrolled in course {course} for session {session}'))

                except Student.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Student with ID {student_id} does not exist. Skipping enrollment.'))
                except Course.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Course with code {course_code} does not exist. Skipping enrollment.'))
                except Session.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Session with name {session_name} does not exist. Skipping enrollment.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error enrolling student {student_id} in course {course_code} for session {session_name}: {e}'))
