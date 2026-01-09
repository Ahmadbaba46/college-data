"""
Django Management Command for Transcript Verification
===================================================

This command provides verification functionality for transcript
security codes and digital signatures.
"""

from django.core.management.base import BaseCommand, CommandError
from reporting.security_features import verify_transcript_code
import json


class Command(BaseCommand):
    help = 'Verify the authenticity of a transcript using its verification code'

    def add_arguments(self, parser):
        parser.add_argument(
            'verification_code',
            type=str,
            help='The verification code to check (e.g., TXN-1234567890AB)'
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output result in JSON format'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed verification information'
        )

    def handle(self, *args, **options):
        verification_code = options['verification_code']
        
        try:
            # Verify the transcript
            result = verify_transcript_code(verification_code)
            
            if options['json']:
                self.stdout.write(json.dumps(result, indent=2))
            else:
                self._display_verification_result(result, options['verbose'])
                
        except Exception as e:
            if options['json']:
                error_result = {
                    'valid': False,
                    'error': str(e),
                    'verification_code': verification_code
                }
                self.stdout.write(json.dumps(error_result, indent=2))
            else:
                raise CommandError(f'Verification failed: {str(e)}')

    def _display_verification_result(self, result, verbose=False):
        """Display verification result in human-readable format"""
        
        if result['valid']:
            self.stdout.write(
                self.style.SUCCESS('✅ TRANSCRIPT VERIFICATION SUCCESSFUL')
            )
            
            if verbose and 'data' in result:
                data = result['data']
                self.stdout.write('\n📋 Transcript Details:')
                self.stdout.write(f'   Student ID: {data.get("student_id", "N/A")}')
                self.stdout.write(f'   Student Name: {data.get("student_name", "N/A")}')
                self.stdout.write(f'   College: {data.get("college_name", "N/A")}')
                self.stdout.write(f'   Generated: {data.get("generation_timestamp", "N/A")}')
                self.stdout.write(f'   Document Hash: {data.get("document_hash", "N/A")[:16]}...')
                
                if 'signature_data' in data:
                    self.stdout.write(f'   Digital Signature: Present')
                    
                self.stdout.write(f'   Verified At: {result.get("verified_at", "N/A")}')
            
        else:
            self.stdout.write(
                self.style.ERROR('❌ TRANSCRIPT VERIFICATION FAILED')
            )
            self.stdout.write(f'   Error: {result.get("error", "Unknown error")}')
            
            if verbose:
                self.stdout.write(f'   Verification Code: {result.get("verification_code", "N/A")}')
                self.stdout.write(f'   Verified At: {result.get("verified_at", "N/A")}')
                
        self.stdout.write('')  # Empty line for better formatting