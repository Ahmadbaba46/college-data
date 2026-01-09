from django.db import models
from django.utils import timezone
from students.models import Student, Session
from courses.models import Course

class Enrollment(models.Model):
    # Keep semester constants for backwards compatibility in command options/tests.
    SEMESTER_FIRST = 'FIRST'
    SEMESTER_SECOND = 'SECOND'
    SEMESTER_SUMMER = 'SUMMER'

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_offering = models.ForeignKey('courses.CourseOffering', on_delete=models.CASCADE)
    enrollment_date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('student', 'course_offering')
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['course_offering']),
            models.Index(fields=['enrollment_date']),
            models.Index(fields=['student', 'course_offering']),
        ]

    @property
    def course(self):
        return self.course_offering.course

    @property
    def session(self):
        return self.course_offering.session

    @property
    def semester(self):
        return self.course_offering.semester

    def __str__(self):
        return f'{self.student} enrolled in {self.course} for {self.session} ({self.course_offering.get_semester_display()})'

class Grade(models.Model):
    STATUS_DRAFT = 'DRAFT'
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    ca_score = models.FloatField(default=0)
    exam_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)
    grade = models.CharField(max_length=2, blank=True)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_grades')
    rejection_reason = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['grade']),
            models.Index(fields=['total_score']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['approved_at']),
        ]

    def save(self, *args, **kwargs):
        self.total_score = self.ca_score + self.exam_score
        grading_scheme = GradingSettings.objects.all().order_by('-min_score')
        
        assigned_grade = 'N/A'
        if grading_scheme.exists():
            for setting in grading_scheme:
                if self.total_score >= setting.min_score:
                    assigned_grade = setting.grade_name
                    break
        self.grade = assigned_grade
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Grade for {self.enrollment}'

class GradingSettings(models.Model):
    grade_name = models.CharField(max_length=2)
    min_score = models.FloatField()
    max_score = models.FloatField()
    grade_point = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-min_score']
        indexes = [
            models.Index(fields=['min_score']),
            models.Index(fields=['grade_name']),
        ]

    # Alias for backwards compatibility with views
    @property
    def grade(self):
        return self.grade_name
    
    @property
    def remark(self):
        """Generate a remark based on grade point"""
        if self.grade_point >= 4.0:
            return 'Excellent'
        elif self.grade_point >= 3.0:
            return 'Very Good'
        elif self.grade_point >= 2.0:
            return 'Good'
        elif self.grade_point >= 1.0:
            return 'Pass'
        else:
            return 'Fail'

    def __str__(self):
        return f'{self.grade_name}: {self.min_score}-{self.max_score}'