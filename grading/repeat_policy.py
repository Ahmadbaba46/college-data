from __future__ import annotations

import re
from dataclasses import dataclass

from grading.models import Enrollment, Grade, GradingSettings


SEMESTER_ORDER = {
    Enrollment.SEMESTER_FIRST: 1,
    Enrollment.SEMESTER_SECOND: 2,
    Enrollment.SEMESTER_SUMMER: 3,
}


def get_repeat_policy() -> str:
    """
    Get the current repeat policy from AcademicPolicySettings.
    Returns 'ALL', 'LATEST', or 'BEST'.
    """
    from configuration.models import AcademicPolicySettings
    
    try:
        policy = AcademicPolicySettings.get_solo().repeat_policy
        return policy.upper()
    except Exception:
        # Default to 'ALL' if settings don't exist
        return 'ALL'


def _session_sort_key(session_name: str | None) -> int:
    """Best-effort sort key for session strings like '2023/2024'."""
    if not session_name:
        return 0
    m = re.search(r'(\d{4})', session_name)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return 0
    return 0


def term_sort_key(enrollment: Enrollment) -> tuple[int, int]:
    return (
        _session_sort_key(getattr(enrollment.session, 'name', None)),
        SEMESTER_ORDER.get(enrollment.semester, 0),
    )


def grade_point_for_enrollment(enrollment: Enrollment) -> float:
    grade = Grade.objects.filter(enrollment=enrollment).first()
    if not grade or not grade.grade:
        return -1.0
    setting = GradingSettings.objects.filter(grade_name=grade.grade).first()
    if not setting:
        return -1.0
    return float(setting.grade_point)


def select_enrollments_for_gpa(enrollments, repeat_policy: str) -> set[int]:
    """Return enrollment ids that should be counted for GPA/CGPA.

    repeat_policy:
      - 'ALL': count all enrollments
      - 'LATEST': for each course, count only the latest attempt (by session/year then semester order)
      - 'BEST': for each course, count only the best attempt (by grade_point, then latest tie-break)

    Note: display can still include all attempts; this is only for GPA computation.
    """
    repeat_policy = (repeat_policy or 'ALL').upper()

    # If queryset, force evaluation with related objects for sorting
    enroll_list = list(enrollments.select_related('course_offering__course', 'course_offering__session')) if hasattr(enrollments, 'select_related') else list(enrollments)

    if repeat_policy == 'ALL':
        return {e.id for e in enroll_list}

    by_course: dict[str, list[Enrollment]] = {}
    for e in enroll_list:
        by_course.setdefault(e.course.code, []).append(e)

    chosen: set[int] = set()

    for _course_code, attempts in by_course.items():
        if repeat_policy == 'LATEST':
            best = max(attempts, key=term_sort_key)
            chosen.add(best.id)
            continue

        if repeat_policy == 'BEST':
            # best grade_point, tie-break latest
            best = max(attempts, key=lambda x: (grade_point_for_enrollment(x), term_sort_key(x)))
            chosen.add(best.id)
            continue

        # unknown policy => safe default
        chosen.update(e.id for e in attempts)

    return chosen
