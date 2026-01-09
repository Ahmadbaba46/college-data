from django.db import models

class Level(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Session(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_current = models.BooleanField(default=False, help_text="Mark as the current session")

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one session is current at a time
        if self.is_current:
            Session.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_current_session(cls):
        """Return the current session, or None if none is set."""
        return cls.objects.filter(is_current=True).first()
    
    # Backward compatibility alias
    @classmethod
    def get_active_session(cls):
        return cls.get_current_session()

class Student(models.Model):
    # Basic identification
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True, help_text="Student's photograph")
    
    # Academic tracking
    entry_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='entry_students')
    current_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, related_name='current_students')
    current_session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    entry_session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, related_name='entry_students', help_text="Session when student first enrolled")
    program = models.ForeignKey('academics.Program', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    
    # Personal information
    email = models.EmailField(unique=True, blank=True, null=True, help_text="Student's email address")
    phone = models.CharField(max_length=15, blank=True, null=True, help_text="Student's phone number")
    date_of_birth = models.DateField(blank=True, null=True, help_text="Student's date of birth")
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Male'), 
        ('F', 'Female'), 
        ('O', 'Other')
    ], blank=True, null=True)
    
    # Contact information
    address = models.TextField(blank=True, null=True, help_text="Home address")
    emergency_contact = models.CharField(max_length=100, blank=True, null=True, help_text="Emergency contact person")
    emergency_phone = models.CharField(max_length=15, blank=True, null=True, help_text="Emergency contact phone")
    
    # Academic status
    admission_date = models.DateField(auto_now_add=True, help_text="Date student was admitted")
    graduation_date = models.DateField(blank=True, null=True, help_text="Date student graduated")
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('graduated', 'Graduated'),
        ('dropped', 'Dropped Out'),
        ('transferred', 'Transferred'),
        ('deferred', 'Deferred'),
        ('expelled', 'Expelled')
    ], default='active', help_text="Current academic status")
    
    # Academic performance tracking
    current_cgpa = models.FloatField(default=0.0, help_text="Current Cumulative Grade Point Average")
    total_units_attempted = models.PositiveIntegerField(default=0, help_text="Total units attempted")
    total_units_passed = models.PositiveIntegerField(default=0, help_text="Total units passed")
    total_sessions_completed = models.PositiveIntegerField(default=0, help_text="Number of completed sessions")
    
    # Additional contact and personal info
    nationality = models.CharField(max_length=50, blank=True, null=True, default='Nigerian')
    state_of_origin = models.CharField(max_length=50, blank=True, null=True)
    local_government = models.CharField(max_length=100, blank=True, null=True)
    
    # Enhanced emergency contact
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True, 
                                                    help_text="Relationship to emergency contact")
    emergency_email = models.EmailField(blank=True, null=True, help_text="Emergency contact email")
    
    # Academic flags and notes
    is_scholarship_recipient = models.BooleanField(default=False, help_text="Student is on scholarship")
    special_needs = models.TextField(blank=True, null=True, help_text="Special accommodation needs")
    notes = models.TextField(blank=True, null=True, help_text="Internal notes about student")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_id']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['email']),
            models.Index(fields=['current_level', 'status']),
            models.Index(fields=['entry_session']),
            models.Index(fields=['status']),
            models.Index(fields=['admission_date']),
            models.Index(fields=['current_cgpa']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(current_cgpa__gte=0.0) & models.Q(current_cgpa__lte=4.0),
                name='valid_cgpa_range'
            ),
            models.CheckConstraint(
                check=models.Q(total_units_passed__lte=models.F('total_units_attempted')),
                name='passed_units_not_exceed_attempted'
            ),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.student_id})'
    
    @property
    def full_name(self):
        """Return student's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        """Calculate and return student's current age"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            age = (today - self.date_of_birth).days / 365.25
            return int(age)
        return None
    
    def is_active(self):
        """Check if student is currently active"""
        return self.status == 'active'
    
    def get_contact_info(self):
        """Return formatted contact information"""
        contact = []
        if self.email:
            contact.append(f"Email: {self.email}")
        if self.phone:
            contact.append(f"Phone: {self.phone}")
        return " | ".join(contact) if contact else "No contact information available"
    
    def get_emergency_contact_info(self):
        """Return formatted emergency contact information"""
        if self.emergency_contact and self.emergency_phone:
            return f"{self.emergency_contact} - {self.emergency_phone}"
        return "No emergency contact information"
    
    def years_enrolled(self):
        """Calculate how many years student has been enrolled"""
        if self.admission_date:
            from datetime import date
            today = date.today()
            years = (today - self.admission_date).days / 365.25
            return round(years, 1)
        return None
    
    def can_graduate(self):
        """Check if student meets basic graduation criteria (can be extended)"""
        # Basic check - student must be active or in good standing
        # This can be extended with GPA requirements, course completion, etc.
        return self.status == 'active' and self.current_level is not None and self.current_cgpa >= 2.0
    
    @property
    def academic_performance_level(self):
        """Categorize academic performance based on CGPA"""
        if self.current_cgpa >= 3.5:
            return 'Excellent (First Class)'
        elif self.current_cgpa >= 3.0:
            return 'Good (Second Class Upper)'
        elif self.current_cgpa >= 2.5:
            return 'Satisfactory (Second Class Lower)'
        elif self.current_cgpa >= 2.0:
            return 'Pass (Third Class)'
        else:
            return 'Below Average'
    
    @property
    def completion_rate(self):
        """Calculate percentage of units passed vs attempted"""
        if self.total_units_attempted > 0:
            return round((self.total_units_passed / self.total_units_attempted) * 100, 2)
        return 0.0
    
    @property
    def is_at_risk(self):
        """Determine if student is at academic risk"""
        return self.current_cgpa < 2.0 or self.completion_rate < 70
    
    def update_academic_metrics(self, save=True):
        """Recalculate and update CGPA and academic metrics"""
        from grading.models import Grade, GradingSettings
        from configuration.models import AcademicPolicySettings
        from grading.repeat_policy import select_enrollments_for_gpa
        from django.db.models import Sum, Count
        
        # Get all enrollments for this student
        enrollments = self.enrollment_set.all()
        policy = AcademicPolicySettings.get_solo().repeat_policy
        counted_ids = select_enrollments_for_gpa(enrollments, policy)
        total_grade_points = 0
        total_units = 0
        passed_units = 0
        sessions_set = set()
        
        for enrollment in enrollments:
            try:
                grade = Grade.objects.get(enrollment=enrollment)

                policy_settings = AcademicPolicySettings.get_solo()
                if policy_settings.require_approved_for_metrics and grade.status != Grade.STATUS_APPROVED:
                    # Skip unapproved results for metrics
                    continue
                grading_setting = GradingSettings.objects.get(grade_name=grade.grade)
                
                course_units = enrollment.course.units
                grade_points = grading_setting.grade_point * course_units
                
                if enrollment.id in counted_ids:
                    total_grade_points += grade_points
                    total_units += course_units
                sessions_set.add(enrollment.session.id)
                
                # Count passed units (assuming grade_point > 0 means pass)
                if grading_setting.grade_point > 0:
                    passed_units += course_units
                    
            except (Grade.DoesNotExist, GradingSettings.DoesNotExist):
                # Count attempted units even if no grade or grading setting
                if enrollment.id in counted_ids:
                    total_units += enrollment.course.units
                sessions_set.add(enrollment.session.id)
        
        # Update metrics
        if total_units > 0:
            self.current_cgpa = round(total_grade_points / total_units, 2)
        else:
            self.current_cgpa = 0.0
            
        self.total_units_attempted = total_units
        self.total_units_passed = passed_units
        self.total_sessions_completed = len(sessions_set)
        
        if save:
            self.save(update_fields=[
                'current_cgpa', 'total_units_attempted', 
                'total_units_passed', 'total_sessions_completed'
            ])
    
    def promote_to_level(self, new_level, save=True):
        """Promote student to a new academic level"""
        from django.utils import timezone
        
        if self.current_level != new_level:
            old_level = self.current_level
            self.current_level = new_level
            
            if save:
                self.save(update_fields=['current_level'])
            
            # Log the promotion
            from audit_log.models import LogEntry
            LogEntry.log_action(
                user=None,
                action='PROMOTE',
                object_type='Student',
                object_id=self.student_id,
                message=f'Promoted from {old_level} to {new_level}'
            )
    
    def change_status(self, new_status, reason=None, user=None, save=True):
        """Change student status with audit logging"""
        if self.status != new_status:
            old_status = self.status
            self.status = new_status
            
            # Set graduation date if graduating
            if new_status == 'graduated' and not self.graduation_date:
                from django.utils import timezone
                self.graduation_date = timezone.now().date()
            
            if save:
                self.save(update_fields=['status', 'graduation_date'] if new_status == 'graduated' else ['status'])
            
            # Log the status change
            from audit_log.models import LogEntry
            message = f'Status changed from {old_status} to {new_status}'
            if reason:
                message += f'. Reason: {reason}'
            
            LogEntry.log_action(
                user=user,
                action='STATUS_CHANGE',
                object_type='Student',
                object_id=self.student_id,
                message=message
            )
    
    def get_transcript_data(self):
        """Get formatted data for transcript generation"""
        from grading.models import Enrollment, Grade
        
        enrollments = Enrollment.objects.filter(student=self).select_related(
            'course', 'session'
        ).order_by('course_offering__session__name', 'course_offering__course__title')
        
        transcript_data = {
            'student': self,
            'enrollments': enrollments,
            'academic_summary': {
                'cgpa': self.current_cgpa,
                'units_attempted': self.total_units_attempted,
                'units_passed': self.total_units_passed,
                'completion_rate': self.completion_rate,
                'performance_level': self.academic_performance_level,
                'sessions_completed': self.total_sessions_completed
            }
        }
        
        return transcript_data
    
    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date
        
        errors = {}
        
        # Validate email format and uniqueness if provided
        if self.email:
            if not self.email.strip():
                errors['email'] = 'Email cannot be empty if provided.'
            else:
                # Check for duplicate email
                existing = Student.objects.filter(email=self.email).exclude(pk=self.pk).first()
                if existing:
                    errors['email'] = f'This email is already registered to student {existing.student_id}'
        
        # Validate phone number format
        if self.phone:
            phone_digits = self.phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            if not phone_digits.isdigit():
                errors['phone'] = 'Phone number should contain only digits, spaces, hyphens, plus sign, and parentheses'
            elif len(phone_digits) < 10:
                errors['phone'] = 'Phone number should have at least 10 digits'
        
        # Validate date of birth (reasonable age check)
        if self.date_of_birth:
            today = date.today()
            age = (today - self.date_of_birth).days / 365.25
            if age < 10:
                errors['date_of_birth'] = 'Student age cannot be less than 10 years'
            elif age > 80:
                errors['date_of_birth'] = 'Please verify the date of birth - age seems unusually high'
            elif self.date_of_birth > today:
                errors['date_of_birth'] = 'Date of birth cannot be in the future'
        
        # Validate graduation date
        if self.graduation_date and self.admission_date:
            if self.graduation_date < self.admission_date:
                errors['graduation_date'] = 'Graduation date cannot be before admission date'
        
        # Validate status transitions
        if self.status == 'graduated' and not self.graduation_date:
            errors['status'] = 'Graduation date is required for graduated students'
        
        if self.status == 'dropped' and self.graduation_date:
            errors['status'] = 'Dropped out students should not have a graduation date'
        
        # Validate emergency contact completeness
        if self.emergency_contact and not self.emergency_phone:
            errors['emergency_phone'] = 'Emergency phone is required when emergency contact is provided'
        if self.emergency_phone and not self.emergency_contact:
            errors['emergency_contact'] = 'Emergency contact name is required when emergency phone is provided'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)