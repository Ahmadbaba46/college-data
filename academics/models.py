from django.db import models

from students.models import Level
from courses.models import Course


class Program(models.Model):
    CLASS_SCHEME_BSC = 'BSC'
    CLASS_SCHEME_ND = 'ND'

    CLASSIFICATION_SCHEMES = [
        (CLASS_SCHEME_BSC, 'University (BSc) classification'),
        (CLASS_SCHEME_ND, 'Polytechnic (ND/HND) classification'),
    ]

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    
    # Department this program belongs to
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='programs',
        help_text="Department offering this program"
    )

    # Minimum units required for graduation (program-specific)
    min_units_to_graduate = models.PositiveIntegerField(default=0)

    classification_scheme = models.CharField(
        max_length=8,
        choices=CLASSIFICATION_SCHEMES,
        default=CLASS_SCHEME_BSC,
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class CurriculumCourse(models.Model):
    """Defines what courses are required/elective for a Program at a given Level+Semester."""

    SEM_FIRST = 'FIRST'
    SEM_SECOND = 'SECOND'
    SEM_SUMMER = 'SUMMER'

    SEM_CHOICES = [
        (SEM_FIRST, 'First Semester'),
        (SEM_SECOND, 'Second Semester'),
        (SEM_SUMMER, 'Summer'),
    ]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='curriculum_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    semester = models.CharField(max_length=6, choices=SEM_CHOICES)

    is_compulsory = models.BooleanField(default=True)

    class Meta:
        unique_together = ('program', 'course', 'level', 'semester')

    def __str__(self) -> str:
        return f"{self.program.code}: {self.course.code} ({self.level.name} {self.semester})"


class ProgramClassificationThreshold(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='classification_thresholds')
    label = models.CharField(max_length=64)
    min_cgpa = models.FloatField()

    class Meta:
        unique_together = ('program', 'label')
        ordering = ['-min_cgpa']

    def __str__(self) -> str:
        return f"{self.program.code}: {self.label} >= {self.min_cgpa}"


class Prerequisite(models.Model):
    """Course prerequisite relationship within a program."""

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='prerequisites')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prereq_for')
    prerequisite_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='is_prereq_of')

    class Meta:
        unique_together = ('program', 'course', 'prerequisite_course')

    def __str__(self) -> str:
        return f"{self.program.code}: {self.course.code} requires {self.prerequisite_course.code}"
