from django.db import models
from django.utils import timezone

from students.models import Student


class TranscriptVerificationRecord(models.Model):
    """Durable verification record for a generated transcript.

    This makes transcript verification survive cache clears and process restarts.
    """

    verification_code = models.CharField(max_length=32, unique=True, db_index=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transcript_verifications')
    student_name = models.CharField(max_length=255)

    generation_timestamp = models.DateTimeField()

    # Integrity fields
    document_hash = models.CharField(max_length=64)

    # Display/issuer fields
    college_name = models.CharField(max_length=255, blank=True)
    verification_url = models.URLField(blank=True)

    # Full verification payload (source of truth for API/UI)
    payload_json = models.JSONField()

    # Lifecycle
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    revoked_at = models.DateTimeField(null=True, blank=True, db_index=True)

    def is_active(self) -> bool:
        now = timezone.now()
        if self.revoked_at is not None:
            return False
        if self.expires_at is not None and self.expires_at <= now:
            return False
        return True

    def __str__(self) -> str:
        return f"{self.verification_code} ({self.student_id_display})"

    @property
    def student_id_display(self) -> str:
        return getattr(self.student, 'student_id', str(self.student_id))


class Transcript(models.Model):
    """Persistent record of generated transcript files.

    Stores the output_file path provided by the caller (CLI/API) so you have a
    history and audit trail.
    """

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transcripts')
    verification = models.ForeignKey(
        TranscriptVerificationRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transcripts',
    )
    generated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_transcripts',
    )

    layout = models.CharField(max_length=32, default='standard')
    output_file = models.CharField(max_length=512)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Transcript {self.student.student_id} ({self.layout})"