import json

from django.core.management.base import BaseCommand
from django.db.models import Count

from configuration.models import AcademicPolicySettings
from grading.models import Enrollment, Grade, GradingSettings
from grading.repeat_policy import select_enrollments_for_gpa, term_sort_key


class Command(BaseCommand):
    help = 'Report repeated courses per student (useful for advising)'

    def add_arguments(self, parser):
        parser.add_argument('--student-id', type=str, default=None, help='Filter to a specific student_id')
        parser.add_argument('--session', type=str, default=None, help='Filter to a session name (e.g., 2023/2024)')
        parser.add_argument('--json', action='store_true', help='Output as JSON')

    def handle(self, *args, **options):
        qs = Enrollment.objects.select_related('student', 'course_offering__course', 'course_offering__session')

        if options.get('student_id'):
            qs = qs.filter(student__student_id=options['student_id'])

        if options.get('session'):
            qs = qs.filter(course_offering__session__name=options['session'])

        # Count attempts per (student, course)
        repeats = (
            qs.values('student__student_id', 'student__first_name', 'student__last_name', 'course_offering__course__code', 'course_offering__course__title')
            .annotate(attempts=Count('id'))
            .filter(attempts__gt=1)
            .order_by('student__student_id', '-attempts', 'course_offering__course__code')
        )

        policy = AcademicPolicySettings.get_solo().repeat_policy

        results = []
        for r in repeats:
            student_id = r['student__student_id']
            course_code = r['course_offering__course__code']

            attempts_qs = (
                qs.filter(student__student_id=student_id, course_offering__course__code=course_code)
                .select_related('student', 'course_offering__course', 'course_offering__session')
                .order_by('course_offering__session__name', 'course_offering__semester', 'id')
            )

            counted_ids = select_enrollments_for_gpa(attempts_qs, policy)

            attempt_details = []
            for e in sorted(list(attempts_qs), key=term_sort_key):
                g = Grade.objects.filter(enrollment=e).first()
                grade_name = g.grade if g else None
                total_score = g.total_score if g else None
                ca = g.ca_score if g else None
                exam = g.exam_score if g else None

                gp = None
                if grade_name:
                    gs = GradingSettings.objects.filter(grade_name=grade_name).first()
                    gp = gs.grade_point if gs else None

                attempt_details.append(
                    {
                        'enrollment_id': e.id,
                        'session': e.course_offering.session.name,
                        'semester': e.course_offering.semester,
                        'semester_display': e.course_offering.get_semester_display(),
                        'ca_score': ca,
                        'exam_score': exam,
                        'total_score': total_score,
                        'grade': grade_name,
                        'grade_point': gp,
                        'counts_for_gpa': e.id in counted_ids,
                    }
                )

            results.append(
                {
                    'student_id': student_id,
                    'student_name': f"{r['student__first_name']} {r['student__last_name']}",
                    'course_code': course_code,
                    'course_title': r['course_offering__course__title'], 
                    'attempts': r['attempts'],
                    'repeat_policy': policy,
                    'attempt_details': attempt_details,
                }
            )

        if options.get('json'):
            self.stdout.write(json.dumps({'count': len(results), 'results': results}, indent=2))
            return

        if not results:
            self.stdout.write(self.style.SUCCESS('No repeated courses found.'))
            return

        self.stdout.write(self.style.SUCCESS('Repeated Courses Report'))
        for item in results:
            self.stdout.write(
                f"- {item['student_id']} ({item['student_name']}): {item['course_code']} {item['course_title']} "
                f"(attempts={item['attempts']}, policy={item['repeat_policy']})"
            )
            for a in item['attempt_details']:
                counts = 'YES' if a['counts_for_gpa'] else 'NO'
                self.stdout.write(
                    f"    * {a['session']} {a['semester_display']}: grade={a['grade'] or 'N/A'} total={a['total_score']} counts_for_gpa={counts}"
                )
