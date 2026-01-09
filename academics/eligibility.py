from __future__ import annotations

from dataclasses import dataclass

from academics.models import CurriculumCourse, Prerequisite
from configuration.models import AcademicPolicySettings
from grading.models import Enrollment, Grade, GradingSettings


@dataclass
class CourseEligibility:
    course_code: str
    course_title: str
    eligible: bool
    reason: str | None = None


def student_passed_course(student, course) -> bool:
    """Return True if the student has a passing attempt for this course.

    Respects AcademicPolicySettings.require_approved_for_metrics:
    - when enabled, only APPROVED grades count as passes for prerequisites/eligibility.
    """
    policy = AcademicPolicySettings.get_solo()
    require_approved = bool(policy.require_approved_for_metrics)

    for e in Enrollment.objects.filter(student=student, course_offering__course=course).select_related('course_offering__course'):
        g = Grade.objects.filter(enrollment=e).first()
        if not g or not g.grade:
            continue
        if require_approved and g.status != Grade.STATUS_APPROVED:
            continue

        gs = GradingSettings.objects.filter(grade_name=g.grade).first()
        if gs and gs.grade_point > 0:
            return True

    return False


def check_prerequisites(student, program, course) -> tuple[bool, str | None]:
    prereqs = Prerequisite.objects.filter(program=program, course=course).select_related('prerequisite_course')
    missing = []
    for p in prereqs:
        if not student_passed_course(student, p.prerequisite_course):
            missing.append(p.prerequisite_course.code)
    if missing:
        return False, f"Missing prerequisites: {', '.join(missing)}"
    return True, None


def suggest_courses_for_student(student, semester: str):
    if not student.program or not student.current_level:
        return []

    program = student.program

    curriculum = CurriculumCourse.objects.filter(program=program, level=student.current_level, semester=semester).select_related('course')

    suggestions = []
    for cc in curriculum:
        course = cc.course
        if student_passed_course(student, course):
            continue

        ok, reason = check_prerequisites(student, program, course)
        suggestions.append(CourseEligibility(course.code, course.title, ok, reason))

    return suggestions
