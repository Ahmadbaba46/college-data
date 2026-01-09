from django.db import models
from django.contrib.auth.models import User

from teachers.models import Teacher


class UserProfile(models.Model):
    """Optional extension of Django User for domain-specific links.

    Used primarily to associate an auth user with a Teacher record.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    teacher = models.OneToOneField(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profile',
    )

    def __str__(self) -> str:
        return f"Profile for {self.user.username}"


class Role(models.Model):
    """System roles for RBAC"""
    ADMIN = 'Admin'
    DATA_ENTRY = 'DataEntry'
    TEACHER = 'Teacher'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (DATA_ENTRY, 'Data Entry Staff'),
        (TEACHER, 'Teacher'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    """Links users to roles (many-to-many through model)"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles_assigned'
    )
    
    class Meta:
        unique_together = ['user', 'role']
        ordering = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class UserSession(models.Model):
    """Track user sessions for security"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tracked_sessions'
    )
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.session_key[:8]}..."
