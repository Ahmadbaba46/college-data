from django.core.management.base import BaseCommand
from reporting.transcript_generator import (
    TranscriptGenerator, 
    generate_standard_transcript,
    generate_detailed_transcript,
    generate_official_transcript,
    generate_simple_transcript
)
from reporting.transcript_style_guide import TranscriptLayoutConfig

class Command(BaseCommand):
    help = 'Generate a PDF transcript for a student using the new template system'

    def add_arguments(self, parser):
        parser.add_argument('student_id', type=str, help='The ID of the student')
        parser.add_argument('output_file', type=str, help='The path to the output PDF file')
        parser.add_argument(
            '--layout', 
            type=str, 
            choices=['standard', 'detailed', 'official', 'simple'],
            default='standard',
            help='Layout template to use (default: standard)'
        )
        parser.add_argument(
            '--show-grade-points',
            action='store_true',
            help='Include grade points in the transcript'
        )
        parser.add_argument(
            '--show-student-photo',
            action='store_true',
            help='Include student photo if available'
        )
        parser.add_argument(
            '--no-session-gpa',
            action='store_true',
            help='Hide session GPA calculations'
        )
        parser.add_argument(
            '--no-logo',
            action='store_true',
            help='Hide college logo'
        )
        parser.add_argument(
            '--simple-table',
            action='store_true',
            help='Use simplified table without grade points'
        )

    def handle(self, *args, **kwargs):
        student_id = kwargs['student_id']
        output_file = kwargs['output_file']
        layout = kwargs['layout']

        try:
            # Use predefined layouts for quick generation
            if layout == 'standard' and not any([
                kwargs['show_grade_points'], kwargs['show_student_photo'],
                kwargs['no_session_gpa'], kwargs['no_logo'], kwargs['simple_table']
            ]):
                success = generate_standard_transcript(student_id, output_file)
            elif layout == 'detailed' and not any([
                kwargs['no_session_gpa'], kwargs['no_logo'], kwargs['simple_table']
            ]):
                success = generate_detailed_transcript(student_id, output_file)
            elif layout == 'official' and not any([
                kwargs['no_session_gpa'], kwargs['no_logo'], kwargs['simple_table']
            ]):
                success = generate_official_transcript(student_id, output_file)
            elif layout == 'simple' and not any([
                kwargs['show_grade_points'], kwargs['show_student_photo']
            ]):
                success = generate_simple_transcript(student_id, output_file)
            else:
                # Use custom configuration
                success = self._generate_custom_transcript(student_id, output_file, layout, kwargs)

            if success:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully generated {layout} transcript for student {student_id} to {output_file}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to generate transcript')
                )

        except ValueError as e:
            self.stdout.write(self.style.ERROR(str(e)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating transcript: {e}'))

    def _generate_custom_transcript(self, student_id: str, output_file: str, layout: str, options: dict) -> bool:
        """Generate transcript with custom configuration"""
        
        # Start with base layout
        layout_map = {
            'standard': 'STANDARD_LAYOUT',
            'detailed': 'DETAILED_LAYOUT', 
            'official': 'OFFICIAL_LAYOUT',
            'simple': 'SIMPLE_LAYOUT'
        }
        
        generator = TranscriptGenerator(layout_map[layout])
        
        # Build custom configuration from options
        custom_config = {}
        
        if options['show_grade_points']:
            if 'Grade Point' not in generator.layout_config['table_columns']:
                custom_config['table_columns'] = generator.layout_config['table_columns'] + ['Grade Point']
        
        if options['simple_table']:
            custom_config['table_columns'] = ['Course Code', 'Course Title', 'Units', 'Grade']
            custom_config['show_grade_points'] = False
        
        if options['show_student_photo']:
            custom_config['show_student_photo'] = True
        
        if options['no_session_gpa']:
            custom_config['show_session_gpa'] = False
        
        if options['no_logo']:
            custom_config['show_logo'] = False
        
        return generator.generate_transcript(student_id, output_file, custom_config)