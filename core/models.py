"""Core app models.

NOTE: Legacy `core.CollegeSettings` has been removed in favor of
`configuration.CollegeSettings`.

Keep core models file for future core-domain entities.
"""

from django.db import models


class Department(models.Model):
    """Academic department/faculty for organizing teachers and courses."""
    name = models.CharField(max_length=100, unique=True, help_text="Department name")
    code = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Short code (e.g., CS, ENG)")
    description = models.TextField(blank=True, null=True, help_text="Department description")
    head_name = models.CharField(max_length=200, blank=True, null=True, help_text="Department head name")
    is_active = models.BooleanField(default=True, help_text="Is department currently active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        if self.code:
            return f"{self.name} ({self.code})"
        return self.name
