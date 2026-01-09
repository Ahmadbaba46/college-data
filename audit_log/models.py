from django.db import models
from django.contrib.auth.models import User

class LogEntry(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('ASSIGN', 'Assign'),
        ('ENROLL', 'Enroll'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('CALCULATE', 'Calculate'),
        # Student lifecycle / admin operations
        ('PROMOTE', 'Promote'),
        ('STATUS_CHANGE', 'Status Change'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Log Entries"
        ordering = ['-timestamp']

    @classmethod
    def log_action(
        cls,
        *,
        user=None,
        action: str,
        object_type: str,
        object_id: str,
        message: str | None = None,
    ):
        """Convenience API used throughout the codebase.

        Ensures action is stored using the model's allowed choices.
        """
        # Normalize
        action_norm = (action or '').strip().upper()

        # Backward-compatible mappings from older call sites
        action_map = {
            'STUDENT_PROMOTED': 'PROMOTE',
            'PROMOTED': 'PROMOTE',
            'STATUS_CHANGE': 'STATUS_CHANGE',
            'STATUS_CHANGED': 'STATUS_CHANGE',
            'STUDENT_STATUS_CHANGE': 'STATUS_CHANGE',
        }
        action_norm = action_map.get(action_norm, action_norm)

        allowed = {a for a, _ in cls.ACTION_CHOICES}
        if action_norm not in allowed:
            # fall back to UPDATE (most generic safe choice)
            action_norm = 'UPDATE'

        return cls.objects.create(
            user=user,
            action=action_norm,
            object_type=object_type,
            object_id=str(object_id),
            message=message,
        )

    def __str__(self):
        return f'{self.timestamp}: {self.user} {self.action} {self.object_type} {self.object_id}'
