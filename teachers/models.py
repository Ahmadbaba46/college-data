from django.db import models
from courses.models import Course

class Teacher(models.Model):
    # Basic identification
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='teachers/photos/', blank=True, null=True, help_text="Teacher's photograph")
    courses = models.ManyToManyField(Course, blank=True)
    
    # Personal information
    email = models.EmailField(unique=True, blank=True, null=True, help_text="Teacher's email address")
    phone = models.CharField(max_length=15, blank=True, null=True, help_text="Teacher's phone number")
    date_of_birth = models.DateField(blank=True, null=True, help_text="Teacher's date of birth")
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Male'), 
        ('F', 'Female'), 
        ('O', 'Other')
    ], blank=True, null=True)
    
    # Contact information
    address = models.TextField(blank=True, null=True, help_text="Home address")
    
    # Professional information
    # Legacy text field - kept for backward compatibility
    department_name = models.CharField(max_length=100, blank=True, null=True, help_text="Department name (legacy)")
    # New FK to Department model
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers',
        help_text="Department/Faculty"
    )
    qualification = models.CharField(max_length=200, blank=True, null=True, help_text="Highest qualification")
    specialization = models.CharField(max_length=200, blank=True, null=True, help_text="Area of specialization")
    
    # Employment details
    hire_date = models.DateField(blank=True, null=True, help_text="Date of employment")
    employment_type = models.CharField(max_length=20, choices=[
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'), 
        ('contract', 'Contract'),
        ('visiting', 'Visiting'),
        ('adjunct', 'Adjunct')
    ], default='full_time', help_text="Employment status")
    
    # Teaching capacity
    max_courses = models.PositiveIntegerField(default=6, help_text="Maximum number of courses per session")
    is_active = models.BooleanField(default=True, help_text="Currently employed")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['staff_id']),
            models.Index(fields=['department']),
            models.Index(fields=['employment_type', 'is_active']),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.staff_id})'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate email format if provided
        if self.email and not self.email.strip():
            raise ValidationError({'email': 'Email cannot be empty if provided.'})
        
        # Validate max_courses
        if self.max_courses < 0:
            raise ValidationError({'max_courses': 'Maximum courses cannot be negative.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)