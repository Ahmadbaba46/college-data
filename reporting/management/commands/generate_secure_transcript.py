"""
Django Management Command for Generating Secure Transcripts
==========================================================

This command generates transcripts with full security features including
QR codes, verification codes, and digital signature preparation.
"""

from django.core.management.base import BaseCommand, CommandError
from reporting.transcript_generator import TranscriptGenerator
from reporting.security_features import verify_transcript_code
import json


class Command(BaseCommand):
    help = 'Generate secure transcripts with QR codes, verification codes, and digital signatures'

    def add_arguments(self, parser):
        parser.add_argument('student_id', type=str, help='The ID of the student')
        parser.add_argument('output_file', type=str, help='The path to the output PDF file')
        
        parser.add_argument(
            '--layout',
            type=str,
            choices=['standard', 'detailed', 'official', 'simple'],
            default='official',
            help='Layout template to use (default: official for security)'
        )
        
        # Security options
        parser.add_argument(
            '--add-watermark',
            action='store_true',
            help='Add watermark to transcript'
        )
        parser.add_argument(
            '--watermark-text',
            type=str,
            default='OFFICIAL',
            help='Text for watermark (default: OFFICIAL)'
        )
        parser.add_argument(
            '--no-qr-code',
            action='store_true',
            help='Disable QR code generation'
        )
        parser.add_argument(
            '--show-security-info',
            action='store_true',
            help='Show security information in transcript content'
        )
        
        # Output options
        parser.add_argument(
            '--save-security-data',
            action='store_true',
            help='Save security data to JSON file'
        )
        parser.add_argument(
            '--verify-after-generation',
            action='store_true',
            help='Verify the transcript immediately after generation'
        )

    def handle(self, *args, **options):
        student_id = options['student_id']
        output_file = options['output_file']
        
        try:
            # Initialize generator with appropriate layout
            layout_map = {
                'standard': 'STANDARD_LAYOUT',
                'detailed': 'DETAILED_LAYOUT',
                'official': 'OFFICIAL_LAYOUT',
                'simple': 'SIMPLE_LAYOUT'
            }
            
            generator = TranscriptGenerator(layout_map[options['layout']])
            
            # Build configuration with security features
            config = {
                'add_security_features': not options['no_qr_code'],
                'show_certification': True,
                'show_signatures': True,
                'show_security_info': options['show_security_info']
            }
            
            if options['add_watermark']:
                config['add_watermark'] = True
                config['watermark_text'] = options['watermark_text']
            
            # Generate secure transcript
            self.stdout.write(f'Generating secure transcript for student {student_id}...')
            
            result = generator.generate_transcript(
                student_id,
                output_file,
                config,
                return_security_data=True,
            )

            if result.get('success'): 
                security_data = result.get('security_data') or {}
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Secure transcript generated successfully: {output_file}')
                )
                
                # Save security data if requested
                if options['save_security_data']:
                    self._save_security_data(student_id, output_file, security_data)

                # Verify transcript if requested
                if options['verify_after_generation']:
                    self._verify_generated_transcript(security_data)
                    
            else:
                raise CommandError(result.get('error') or 'Failed to generate transcript')
                
        except Exception as e:
            raise CommandError(f'Error generating secure transcript: {str(e)}')

    def _save_security_data(self, student_id, output_file, security_data):
        """Save security data (actual verification payload) to JSON file"""
        try:
            payload = {
                'student_id': student_id,
                'output_file': output_file,
                'security_data': security_data,
                'note': 'Security data saved for audit trail',
            }

            json_file = output_file.replace('.pdf', '_security.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, default=str)

            self.stdout.write(f'Security data saved to: {json_file}')

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not save security data: {str(e)}'))

    def _verify_generated_transcript(self, security_data: dict):
        """Verify the generated transcript using its verification code."""
        try:
            verification_code = (security_data or {}).get('verification_code')
            if not verification_code:
                self.stdout.write(self.style.WARNING('No verification code available to verify.'))
                return

            self.stdout.write(f'Verifying transcript code {verification_code}...')
            result = verify_transcript_code(verification_code)

            if result.get('valid'):
                self.stdout.write(self.style.SUCCESS('✅ Transcript verification: PASSED'))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Transcript verification: FAILED ({result.get('error')})"))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Verification check failed: {str(e)}'))