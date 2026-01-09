from __future__ import annotations

import json
from typing import Any

from students.models import Student
from grading.models import Enrollment, Grade, GradingSettings
from configuration.models import CollegeSettings


def build_canonical_transcript_payload(
    *,
    student: Student,
    enrollments,
    college_settings: CollegeSettings | None,
) -> dict[str, Any]:
    """Build a stable, JSON-serializable payload representing transcript content.

    This payload is used to compute a tamper-evident document hash that reflects
    the actual academic data displayed on the transcript.
    """

    items: list[dict[str, Any]] = []

    for enrollment in enrollments:
        grade_obj = Grade.objects.filter(enrollment=enrollment).first()
        grade_name = grade_obj.grade if grade_obj else None
        total_score = grade_obj.total_score if grade_obj else None

        grade_point = None
        if grade_name:
            gs = GradingSettings.objects.filter(grade_name=grade_name).first()
            if gs:
                grade_point = gs.grade_point

        items.append(
            {
                'session': getattr(enrollment.session, 'name', None),
                'semester': getattr(enrollment, 'semester', None),
                'course_code': enrollment.course.code,
                'course_title': enrollment.course.title,
                'units': enrollment.course.units,
                'grade': grade_name,
                'total_score': total_score,
                'grade_point': grade_point,
            }
        )

    payload: dict[str, Any] = {
        'college': {
            'name': getattr(college_settings, 'college_name', None) if college_settings else None,
            'address': getattr(college_settings, 'college_address', None) if college_settings else None,
        },
        'student': {
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'entry_level': getattr(student.entry_level, 'name', None),
            'current_level': getattr(student.current_level, 'name', None),
            'current_session': getattr(student.current_session, 'name', None),
        },
        'enrollments': items,
    }

    return payload


def canonical_json(payload: dict[str, Any]) -> str:
    """Stable JSON encoding for hashing."""
    return json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
