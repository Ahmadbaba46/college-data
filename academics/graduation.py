from __future__ import annotations

from dataclasses import dataclass

from configuration.models import AcademicPolicySettings
from academics.models import Program, CurriculumCourse
from grading.models import Enrollment, Grade
from grading.models import GradingSettings


@dataclass
class GraduationAuditResult:
    eligible: bool
    cgpa: float
    total_units_earned: int
    missing_compulsory_courses: list[str]
    classification: str | None
    notes: list[str]


def _grade_point(enrollment: Enrollment, require_approved: bool) -> float | None:
    g = Grade.objects.filter(enrollment=enrollment).first()
    if not g or not g.grade:
        return None
    if require_approved and g.status != Grade.STATUS_APPROVED:
        return None
    setting = GradingSettings.objects.filter(grade_name=g.grade).first()
    if not setting:
        return None
    return float(setting.grade_point)


def compute_cgpa_for_program(student, require_approved: bool) -> tuple[float, int]:
    total_points = 0.0
    total_units = 0

    enrollments = Enrollment.objects.filter(student=student).select_related('course_offering__course')
    for e in enrollments:
        gp = _grade_point(e, require_approved=require_approved)
        if gp is None:
            continue
        units = int(e.course_offering.course.units)
        total_points += units * gp
        total_units += units

    if total_units == 0:
        return 0.0, 0

    return round(total_points / total_units, 2), total_units


def passed_course(student, course, require_approved: bool) -> bool:
    qs = Enrollment.objects.filter(student=student, course_offering__course=course)
    for e in qs:
        gp = _grade_point(e, require_approved=require_approved)
        if gp is None:
            continue
        if gp > 0:
            return True
    return False


def classify(program: Program, cgpa: float) -> str:
    """Classification based on program-specific thresholds."""
    thresholds = list(program.classification_thresholds.all())
    if not thresholds:
        # fallback to legacy defaults
        if program.classification_scheme == Program.CLASS_SCHEME_BSC:
            thresholds = [
                ('First Class', 3.5),
                ('Second Class Upper', 3.0),
                ('Second Class Lower', 2.0),
                ('Third Class', 1.0),
                ('Fail', 0.0),
            ]
        else:
            thresholds = [
                ('Distinction', 3.5),
                ('Upper Credit', 3.0),
                ('Lower Credit', 2.5),
                ('Pass', 2.0),
                ('Fail', 0.0),
            ]
        for label, min_cgpa in thresholds:
            if cgpa >= min_cgpa:
                return label
        return 'Fail'

    for t in thresholds:
        if cgpa >= t.min_cgpa:
            return t.label
    return thresholds[-1].label


def audit_student_graduation(student) -> GraduationAuditResult:
    notes: list[str] = []

    if not student.program:
        return GraduationAuditResult(False, 0.0, 0, [], None, ['Student has no program assigned'])

    policy = AcademicPolicySettings.get_solo()
    require_approved = bool(policy.require_approved_for_metrics)

    cgpa, total_units = compute_cgpa_for_program(student, require_approved=require_approved)

    program = student.program

    # Check compulsory curriculum completion (any level/semester)
    missing = []
    compulsory = CurriculumCourse.objects.filter(program=program, is_compulsory=True).select_related('course')
    for cc in compulsory:
        if not passed_course(student, cc.course, require_approved=require_approved):
            missing.append(cc.course.code)

    eligible = True

    if missing:
        eligible = False
        notes.append(f'Missing compulsory courses: {", ".join(sorted(set(missing)))}')

    if program.min_units_to_graduate and total_units < program.min_units_to_graduate:
        eligible = False
        notes.append(f'Insufficient units: {total_units}/{program.min_units_to_graduate}')

    classification = classify(program, cgpa) if eligible else None

    return GraduationAuditResult(
        eligible=eligible,
        cgpa=cgpa,
        total_units_earned=total_units,
        missing_compulsory_courses=sorted(set(missing)),
        classification=classification,
        notes=notes,
    )
