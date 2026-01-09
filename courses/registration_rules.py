from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from courses.models import CourseOffering, Course
from grading.models import Enrollment


@dataclass
class RegistrationResult:
    ok: bool
    error: str | None = None
    warnings: List[str] = field(default_factory=list)


def check_prerequisites(student, course: Course) -> List[str]:
    """Return list of unsatisfied prerequisite course codes."""
    unmet = []
    try:
        from academics.models import Prerequisite
        from grading.models import Grade
        
        prereqs = Prerequisite.objects.filter(course=course).select_related('prerequisite')
        for prereq in prereqs:
            # Check if student passed the prerequisite (score >= 40)
            passed = Grade.objects.filter(
                enrollment__student=student,
                enrollment__course_offering__course=prereq.prerequisite,
                total_score__gte=40
            ).exists()
            if not passed:
                unmet.append(prereq.prerequisite.code)
    except Exception:
        pass  # Fail open if prerequisites module not available
    return unmet


def check_repeat_limit(student, course: Course, max_repeats: int = 3) -> bool:
    """Check if student has exceeded max repeat attempts for a course."""
    count = Enrollment.objects.filter(
        student=student,
        course_offering__course=course
    ).count()
    return count < max_repeats


def check_already_enrolled(student, offering: CourseOffering) -> bool:
    """Check if student is already enrolled in this offering."""
    return not Enrollment.objects.filter(
        student=student,
        course_offering=offering
    ).exists()


def can_enroll(student, offering: CourseOffering, strict_prereqs: bool = False) -> RegistrationResult:
    """
    Validate registration rules for enrolling a student into a CourseOffering.
    
    Args:
        student: The student to enroll
        offering: The course offering
        strict_prereqs: If True, missing prerequisites block enrollment
    
    Returns:
        RegistrationResult with ok status, error message, and warnings
    """
    warnings = []
    
    # Check if offering is active
    if not offering.is_active:
        return RegistrationResult(False, 'Course offering is not active.')
    
    # Check if already enrolled
    if not check_already_enrolled(student, offering):
        return RegistrationResult(False, 'Student is already enrolled in this course offering.')
    
    # Level constraint (if offering has a level)
    if offering.level is not None and getattr(student, 'current_level_id', None) is not None:
        if student.current_level_id != offering.level_id:
            level_msg = f"Student level ({student.current_level}) does not match offering level ({offering.level})."
            if strict_prereqs:
                return RegistrationResult(False, level_msg)
            else:
                warnings.append(level_msg)

    # Capacity constraint
    if offering.capacity is not None:
        current = Enrollment.objects.filter(course_offering=offering).count()
        if current >= offering.capacity:
            return RegistrationResult(False, 'Course offering is full (capacity reached).')
    
    # Repeat limit check
    try:
        from configuration.models import AcademicPolicySettings
        policy = AcademicPolicySettings.objects.first()
        max_repeats = policy.max_course_repeats if policy else 3
    except Exception:
        max_repeats = 3
    
    if not check_repeat_limit(student, offering.course, max_repeats):
        return RegistrationResult(
            False, 
            f'Student has reached maximum repeat limit ({max_repeats}) for this course.'
        )
    
    # Prerequisites check
    unmet_prereqs = check_prerequisites(student, offering.course)
    if unmet_prereqs:
        prereq_msg = f"Missing prerequisites: {', '.join(unmet_prereqs)}"
        if strict_prereqs:
            return RegistrationResult(False, prereq_msg)
        else:
            warnings.append(prereq_msg)

    return RegistrationResult(True, warnings=warnings)


def get_enrollment_status(student, offering: CourseOffering) -> dict:
    """Get detailed enrollment status for a student/offering combination."""
    result = can_enroll(student, offering, strict_prereqs=False)
    
    return {
        'can_enroll': result.ok,
        'error': result.error,
        'warnings': result.warnings,
        'is_enrolled': not check_already_enrolled(student, offering),
        'available_seats': offering.available_seats,
        'is_full': offering.is_full,
        'prerequisites_met': len(check_prerequisites(student, offering.course)) == 0,
    }


def bulk_validate_enrollments(student, offerings: List[CourseOffering]) -> List[dict]:
    """Validate enrollment eligibility for multiple offerings at once."""
    results = []
    for offering in offerings:
        status = get_enrollment_status(student, offering)
        status['offering'] = offering
        results.append(status)
    return results
