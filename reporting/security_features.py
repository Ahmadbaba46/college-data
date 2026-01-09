"""
Advanced Security Features for Academic Transcripts
=================================================

This module provides advanced security features including:
1. QR code generation for transcript verification
2. Digital signature preparation and validation
3. Secure transcript verification system
4. Tamper-evident features
"""

import hashlib
import uuid
import json
import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing, String, Rect
from reportlab.graphics import renderPDF
from reportlab.lib import colors

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from students.models import Student
from grading.models import Enrollment, Grade
from configuration.models import CollegeSettings
from reporting.models import TranscriptVerificationRecord
from reporting.canonical_payload import canonical_json


class TranscriptVerificationSystem:
    """System for generating and verifying transcript authenticity.

    Verification records are stored durably in the database (reporting.TranscriptVerificationRecord)
    and also cached for performance.
    """

    def __init__(self):
        self.verification_cache_timeout = 86400 * 30  # 30 days
        self.base_verification_url = getattr(
            settings,
            'TRANSCRIPT_VERIFICATION_URL',
            'https://college.edu/verify'
        )
    
    def generate_verification_code(self, student_id: str, generation_timestamp: datetime.datetime) -> str:
        """
        Generate a unique verification code for a transcript
        
        Args:
            student_id: Student ID
            generation_timestamp: When transcript was generated
            
        Returns:
            Unique verification code
        """
        # Create a hash based on student info and timestamp
        hash_input = f"{student_id}:{generation_timestamp.isoformat()}:{settings.SECRET_KEY}"
        hash_object = hashlib.sha256(hash_input.encode())
        
        # Use first 12 characters of hash for readable code
        verification_code = hash_object.hexdigest()[:12].upper()
        
        return f"TXN-{verification_code}"
    
    def store_verification_data(self, verification_code: str, transcript_data: Dict) -> bool:
        """Store transcript verification data durably (DB) and in cache."""
        try:
            verification_key = f"transcript_verify:{verification_code}"

            # Cache first (best-effort)
            cache.set(verification_key, transcript_data, self.verification_cache_timeout)

            # Durable storage
            student_id = transcript_data.get('student_id')
            if not student_id:
                return False

            student = Student.objects.get(student_id=student_id)

            generation_ts = transcript_data.get('generation_timestamp')
            if isinstance(generation_ts, str):
                generation_ts = timezone.datetime.fromisoformat(generation_ts.replace('Z', '+00:00'))

            expires_at = timezone.now() + datetime.timedelta(seconds=self.verification_cache_timeout)

            with transaction.atomic():
                TranscriptVerificationRecord.objects.update_or_create(
                    verification_code=verification_code,
                    defaults={
                        'student': student,
                        'student_name': transcript_data.get('student_name', ''),
                        'generation_timestamp': generation_ts or timezone.now(),
                        'document_hash': transcript_data.get('document_hash', ''),
                        'college_name': transcript_data.get('college_name', ''),
                        'verification_url': transcript_data.get('verification_url', ''),
                        'payload_json': transcript_data,
                        'expires_at': expires_at,
                    },
                )

            return True
        except Exception:
            return False
    
    def verify_transcript(self, verification_code: str) -> Optional[Dict]:
        """Verify transcript authenticity using verification code.

        NOTE: For tamper-evidence, the source of truth is the DB record.
        We may still use cache as an optimization but always re-validate
        the canonical payload hash against the stored DB payload.
        """
        try:
            verification_code = (verification_code or '').strip().upper()
            verification_key = f"transcript_verify:{verification_code}"

            # Load from DB first (authoritative)
            record = (
                TranscriptVerificationRecord.objects
                .filter(verification_code=verification_code)
                .select_related('student')
                .first()
            )
            if not record or not record.is_active():
                return None

            verification_data = dict(record.payload_json)
            verification_data['verified_at'] = timezone.now().isoformat()

            # Re-seed cache (best effort)
            cache.set(verification_key, verification_data, self.verification_cache_timeout)
            return verification_data
        except Exception:
            # Fallback: try cache only
            try:
                verification_data = cache.get(f"transcript_verify:{verification_code}")
                if verification_data:
                    verification_data['verified_at'] = timezone.now().isoformat()
                return verification_data
            except Exception:
                return None
    
    def generate_qr_code(self, verification_code: str) -> str:
        """
        Generate QR code for transcript verification
        
        Args:
            verification_code: Verification code to encode
            
        Returns:
            Path to generated QR code image
        """
        # Create verification URL
        verification_url = f"{self.base_verification_url}?code={verification_code}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # Create styled QR code image
        qr_image = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer()
        )
        
        # Save QR code
        qr_filename = f"qr_code_{verification_code}.png"
        qr_path = Path("tmp") / qr_filename
        qr_path.parent.mkdir(exist_ok=True)
        
        qr_image.save(qr_path)
        
        return str(qr_path)


class DigitalSignatureSystem:
    """System for digital signature preparation and validation"""
    
    def __init__(self):
        self.signature_algorithm = 'SHA256'
        
    def generate_document_hash(self, transcript_content: str) -> str:
        """
        Generate cryptographic hash of transcript content
        
        Args:
            transcript_content: Full transcript text content
            
        Returns:
            SHA256 hash of content
        """
        content_bytes = transcript_content.encode('utf-8')
        hash_object = hashlib.sha256(content_bytes)
        return hash_object.hexdigest()
    
    def create_signature_data(self, student_id: str, transcript_hash: str, 
                            college_settings: CollegeSettings) -> Dict:
        """
        Create signature data structure for digital signing
        
        Args:
            student_id: Student ID
            transcript_hash: Hash of transcript content
            college_settings: College configuration
            
        Returns:
            Signature data structure
        """
        timestamp = timezone.now()
        
        signature_data = {
            'student_id': student_id,
            'document_hash': transcript_hash,
            'algorithm': self.signature_algorithm,
            'timestamp': timestamp.isoformat(),
            'issuer': college_settings.college_name if college_settings else 'Unknown College',
            'issuer_id': college_settings.id if college_settings else None,
            'signature_version': '1.0'
        }
        
        return signature_data
    
    def prepare_for_digital_signing(self, signature_data: Dict) -> str:
        """
        Prepare data for external digital signing process
        
        Args:
            signature_data: Signature data structure
            
        Returns:
            JSON string ready for digital signing
        """
        # In production, this would integrate with a digital signature service
        # like DocuSign, Adobe Sign, or a PKI infrastructure
        
        return json.dumps(signature_data, sort_keys=True)


class TamperEvidenceSystem:
    """System for tamper-evident features"""
    
    @staticmethod
    def generate_security_pattern() -> Drawing:
        """Generate a security background pattern"""
        d = Drawing(8.5 * inch, 11 * inch)
        
        # Create subtle security lines
        pattern_color = colors.Color(0.95, 0.95, 0.95, alpha=0.3)
        
        # Diagonal lines pattern
        for i in range(0, int(8.5 * inch), 20):
            for j in range(0, int(11 * inch), 20):
                d.add(String(i, j, '•', fontSize=8, fillColor=pattern_color))
        
        return d
    
    @staticmethod
    def add_microtext(story, verification_code: str):
        """Add microtext for security"""
        from reportlab.lib.styles import getSampleStyleSheet
        
        styles = getSampleStyleSheet()
        microtext_style = styles['Normal'].clone('Microtext')
        microtext_style.fontSize = 4
        microtext_style.textColor = colors.Color(0.9, 0.9, 0.9)
        
        microtext = f"SECURE-{verification_code}-AUTHENTICATED"
        
        story.append(Paragraph(microtext, microtext_style))


class SecureTranscriptFeatures:
    """Main class integrating all security features"""

    def _validate_tamper_evidence(self, verification_data: Dict) -> Tuple[bool, str | None]:
        """Recompute the document hash from canonical payload and compare."""
        payload = verification_data.get('canonical_payload')
        stored_hash = verification_data.get('document_hash')
        if not payload or not stored_hash:
            # Backward compatibility for old records
            return True, None

        try:
            recomputed = self.signature_system.generate_document_hash(canonical_json(payload))
        except Exception:
            return False, 'Could not recompute document hash'

        if recomputed != stored_hash:
            return False, 'Transcript data does not match stored hash (possible tampering)'
        return True, None

    
    def __init__(self):
        self.verification_system = TranscriptVerificationSystem()
        self.signature_system = DigitalSignatureSystem()
        self.tamper_system = TamperEvidenceSystem()
    
    def create_secure_transcript_data(self, student: Student, 
                                    transcript_content,
                                    college_settings: CollegeSettings) -> Dict:
        """
        Create comprehensive security data for a transcript
        
        Args:
            student: Student object
            transcript_content: Full transcript content
            college_settings: College configuration
            
        Returns:
            Security data including verification code, QR code, etc.
        """
        generation_timestamp = timezone.now()
        
        # Generate verification code
        verification_code = self.verification_system.generate_verification_code(
            student.student_id, generation_timestamp
        )
        
        # Create document hash
        if isinstance(transcript_content, dict):
            document_hash = self.signature_system.generate_document_hash(canonical_json(transcript_content))
        else:
            document_hash = self.signature_system.generate_document_hash(str(transcript_content))
        
        # Create signature data
        signature_data = self.signature_system.create_signature_data(
            student.student_id, document_hash, college_settings
        )
        
        # Generate QR code
        qr_code_path = self.verification_system.generate_qr_code(verification_code)
        
        # Store verification data
        verification_data = {
            'student_id': student.student_id,
            'student_name': f"{student.first_name} {student.last_name}",
            'generation_timestamp': generation_timestamp.isoformat(),
            'document_hash': document_hash,
            'signature_data': signature_data,
            'college_name': college_settings.college_name if college_settings else 'Unknown',
            'verification_url': f"{self.verification_system.base_verification_url}?code={verification_code}",
            'canonical_payload': transcript_content if isinstance(transcript_content, dict) else None,
        }
        
        self.verification_system.store_verification_data(verification_code, verification_data)
        
        security_features = {
            'verification_code': verification_code,
            'qr_code_path': qr_code_path,
            'document_hash': document_hash,
            'signature_data': signature_data,
            'verification_url': verification_data['verification_url'],
            'generation_timestamp': generation_timestamp
        }
        
        return security_features
    
    def verify_transcript_security(self, verification_code: str) -> Optional[Dict]:
        """
        Verify transcript using security features
        
        Args:
            verification_code: Verification code to check
            
        Returns:
            Verification result with details
        """
        verification_data = self.verification_system.verify_transcript(verification_code)
        
        if verification_data:
            ok, err = self._validate_tamper_evidence(verification_data)
            if not ok:
                return {
                    'valid': False,
                    'error': err,
                    'verified_at': timezone.now().isoformat(),
                    'data': verification_data,
                }

            return {
                'valid': True,
                'data': verification_data,
                'verified_at': timezone.now().isoformat()
            }
        else:
            return {
                'valid': False,
                'error': 'Invalid or expired verification code',
                'verified_at': timezone.now().isoformat()
            }


# Convenience functions
def create_secure_transcript(student: Student, transcript_content: str, 
                           college_settings: CollegeSettings) -> Dict:
    """Create secure transcript with all security features"""
    security_system = SecureTranscriptFeatures()
    return security_system.create_secure_transcript_data(
        student, transcript_content, college_settings
    )


def verify_transcript_code(verification_code: str) -> Dict:
    """Verify a transcript using its verification code"""
    security_system = SecureTranscriptFeatures()
    return security_system.verify_transcript_security(verification_code)