from django.db import models

class CollegeSettings(models.Model):
    """Singleton-like configuration for institution branding and transcript outputs.

    This is the canonical CollegeSettings model (replacing the older core.CollegeSettings).
    """

    college_name = models.CharField(max_length=255, blank=True, null=True)
    college_address = models.TextField(blank=True, null=True)

    # Branding assets
    college_logo = models.ImageField(upload_to='college_logos/', blank=True, null=True)

    # Signature assets (kept for backward compatibility with older naming)
    principal_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    signature = models.ImageField(upload_to='college_signatures/', blank=True, null=True)

    # Legacy/extra text fields used by some commands
    letterhead = models.TextField(blank=True, null=True)

    # Add other configurable settings as needed

    class Meta:
        verbose_name_plural = "College Settings"

    def __str__(self):
        return "College Settings"


class AcademicPolicySettings(models.Model):
    """Singleton-like academic policy configuration.

    repeat_policy determines how CGPA/GPA handle repeated courses.
    """

    REPEAT_ALL = 'ALL'
    REPEAT_LATEST = 'LATEST'
    REPEAT_BEST = 'BEST'

    REPEAT_POLICY_CHOICES = [
        (REPEAT_ALL, 'Count all attempts'),
        (REPEAT_LATEST, 'Use latest attempt per course'),
        (REPEAT_BEST, 'Use best attempt per course'),
    ]

    repeat_policy = models.CharField(max_length=16, choices=REPEAT_POLICY_CHOICES, default=REPEAT_ALL)

    # Approval enforcement flags
    require_approved_for_transcripts = models.BooleanField(
        default=False,
        help_text='If true, transcripts only count APPROVED grades for GPA/CGPA (unapproved show as pending).',
    )
    require_approved_for_exports = models.BooleanField(
        default=False,
        help_text='If true, grade exports only include APPROVED grades.',
    )
    require_approved_for_metrics = models.BooleanField(
        default=False,
        help_text='If true, CGPA/metrics computations only count APPROVED grades.',
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Academic Policy Settings'

    def __str__(self) -> str:
        return f"Academic Policy (repeat_policy={self.repeat_policy})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
