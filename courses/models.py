from django.db import models
from students.models import Level, Session

class Course(models.Model):
    SEMESTER_FIRST = 'FIRST'
    SEMESTER_SECOND = 'SECOND'
    SEMESTER_CHOICES = [
        (SEMESTER_FIRST, 'First Semester'),
        (SEMESTER_SECOND, 'Second Semester'),
    ]

    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    units = models.PositiveIntegerField(default=0)
    # Optional default semester for convenience during enrollment
    default_semester = models.CharField(max_length=6, choices=SEMESTER_CHOICES, null=True, blank=True)
    
    # Department this course belongs to
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        help_text="Department offering this course"
    )

    levels = models.ManyToManyField(Level)
    sessions = models.ManyToManyField(Session)

    def __str__(self):
        return f'{self.title} ({self.code})'


class CourseOffering(models.Model):
    SEMESTER_FIRST = 'FIRST'
    SEMESTER_SECOND = 'SECOND'
    SEMESTER_SUMMER = 'SUMMER'
    SEMESTER_CHOICES = [
        (SEMESTER_FIRST, 'First Semester'),
        (SEMESTER_SECOND, 'Second Semester'),
        (SEMESTER_SUMMER, 'Summer'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    semester = models.CharField(max_length=6, choices=SEMESTER_CHOICES, default=SEMESTER_FIRST)
    # Optional: offering level (useful for curriculum/registration rules)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Teacher assigned to this offering
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_offerings',
        help_text="Teacher assigned to teach this offering"
    )

    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('course', 'session', 'semester', 'level')
        indexes = [
            models.Index(fields=['session', 'semester']),
            models.Index(fields=['course', 'session']),
            models.Index(fields=['teacher']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        level = f" - {self.level.name}" if self.level else ''
        return f"{self.course.code} {self.session.name} {self.get_semester_display()}{level}"
    
    @property
    def enrollment_count(self):
        """Get current enrollment count for this offering"""
        from grading.models import Enrollment
        return Enrollment.objects.filter(course_offering=self).count()
    
    @property
    def available_seats(self):
        """Get remaining seats (None if unlimited)"""
        if self.capacity is None:
            return None
        return max(0, self.capacity - self.enrollment_count)
    
    @property
    def is_full(self):
        """Check if offering has reached capacity"""
        if self.capacity is None:
            return False
        return self.enrollment_count >= self.capacity