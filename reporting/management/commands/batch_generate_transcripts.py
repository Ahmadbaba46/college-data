"""
Django Management Command for Batch Transcript Generation
========================================================

This command provides batch processing capabilities for generating
multiple transcripts with various filtering and output options.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from students.models import Student, Session, Level
from grading.models import Enrollment
from reporting.batch_transcript_generator import BatchTranscriptGenerator
import os
import json


class Command(BaseCommand):
    help = 'Generate transcripts for multiple students in batch with various filtering options'

    def add_arguments(self, parser):
        # Target selection arguments
        target_group = parser.add_mutually_exclusive_group(required=True)
        target_group.add_argument(
            '--all-students',
            action='store_true',
            help='Generate transcripts for all students'
        )
        target_group.add_argument(
            '--student-ids',
            nargs='+',
            help='Space-separated list of student IDs'
        )
        target_group.add_argument(
            '--session',
            type=str,
            help='Generate transcripts for all students in specified session'
        )
        target_group.add_argument(
            '--level',
            type=str,
            help='Generate transcripts for all students at specified level'
        )
        target_group.add_argument(
            '--from-file',
            type=str,
            help='Read student IDs from text file (one per line)'
        )

        # Output configuration
        parser.add_argument(
            '--output-dir',
            type=str,
            default='batch_transcripts',
            help='Output directory for generated transcripts (default: batch_transcripts)'
        )
        parser.add_argument(
            '--layout',
            type=str,
            choices=['standard', 'detailed', 'official', 'simple'],
            default='standard',
            help='Layout template to use (default: standard)'
        )

        # Processing options
        parser.add_argument(
            '--max-workers',
            type=int,
            default=4,
            help='Number of parallel workers (default: 4)'
        )
        parser.add_argument(
            '--create-zip',
            action='store_true',
            help='Create zip archive of all generated transcripts'
        )

        # Security and watermark options
        parser.add_argument(
            '--add-watermark',
            action='store_true',
            help='Add watermark to transcripts'
        )
        parser.add_argument(
            '--watermark-text',
            type=str,
            default='OFFICIAL',
            help='Text for watermark (default: OFFICIAL)'
        )

        # Layout customization
        parser.add_argument(
            '--show-grade-points',
            action='store_true',
            help='Include grade points in transcripts'
        )
        parser.add_argument(
            '--show-student-photo',
            action='store_true',
            help='Include student photos if available'
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

        # Progress and output options
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Suppress progress output'
        )
        parser.add_argument(
            '--save-report',
            action='store_true',
            help='Save detailed generation report as JSON'
        )

    def handle(self, *args, **options):
        try:
            # Initialize batch generator
            layout_map = {
                'standard': 'STANDARD_LAYOUT',
                'detailed': 'DETAILED_LAYOUT',
                'official': 'OFFICIAL_LAYOUT',
                'simple': 'SIMPLE_LAYOUT'
            }
            
            batch_gen = BatchTranscriptGenerator(layout_map[options['layout']])
            
            # Get student IDs based on selection criteria
            student_ids = self._get_student_ids(options)
            
            if not student_ids:
                raise CommandError('No students found matching the specified criteria.')
            
            # Build custom configuration
            custom_config = self._build_custom_config(options)
            
            # Setup progress callback
            progress_callback = None if options['quiet'] else self._progress_callback
            
            self.stdout.write(
                self.style.SUCCESS(f'Starting batch generation for {len(student_ids)} students...')
            )
            
            # Generate transcripts
            results = batch_gen.generate_batch_transcripts(
                student_ids=student_ids,
                output_dir=options['output_dir'],
                layout=options['layout'],
                custom_config=custom_config,
                add_watermark=options['add_watermark'],
                watermark_text=options['watermark_text'],
                create_zip=options['create_zip'],
                max_workers=options['max_workers'],
                progress_callback=progress_callback
            )
            
            # Display results
            self._display_results(results, options)
            
            # Save report if requested
            if options['save_report']:
                self._save_report(results, options['output_dir'])

        except Exception as e:
            raise CommandError(f'Batch generation failed: {str(e)}')

    def _get_student_ids(self, options):
        """Get list of student IDs based on selection criteria"""
        
        if options['all_students']:
            return list(Student.objects.values_list('student_id', flat=True))
        
        elif options['student_ids']:
            # Validate that all student IDs exist
            existing_ids = set(Student.objects.filter(
                student_id__in=options['student_ids']
            ).values_list('student_id', flat=True))
            
            missing_ids = set(options['student_ids']) - existing_ids
            if missing_ids:
                self.stdout.write(
                    self.style.WARNING(f'Warning: The following student IDs were not found: {", ".join(missing_ids)}')
                )
            
            return list(existing_ids)
        
        elif options['session']:
            try:
                session = Session.objects.get(name=options['session'])
                enrollments = Enrollment.objects.filter(session=session)
                return list(enrollments.values_list('student__student_id', flat=True).distinct())
            except Session.DoesNotExist:
                raise CommandError(f'Session "{options["session"]}" not found.')
        
        elif options['level']:
            try:
                students = Student.objects.filter(
                    Q(entry_level__name=options['level']) | 
                    Q(current_level__name=options['level'])
                )
                return list(students.values_list('student_id', flat=True))
            except:
                raise CommandError(f'Level "{options["level"]}" not found.')
        
        elif options['from_file']:
            if not os.path.exists(options['from_file']):
                raise CommandError(f'File "{options["from_file"]}" not found.')
            
            try:
                with open(options['from_file'], 'r') as f:
                    student_ids = [line.strip() for line in f if line.strip()]
                
                # Validate student IDs
                existing_ids = set(Student.objects.filter(
                    student_id__in=student_ids
                ).values_list('student_id', flat=True))
                
                missing_ids = set(student_ids) - existing_ids
                if missing_ids:
                    self.stdout.write(
                        self.style.WARNING(f'Warning: {len(missing_ids)} student IDs from file were not found.')
                    )
                
                return list(existing_ids)
            except Exception as e:
                raise CommandError(f'Error reading file "{options["from_file"]}": {str(e)}')
        
        return []

    def _build_custom_config(self, options):
        """Build custom configuration from command options"""
        config = {}
        
        if options['show_grade_points']:
            config['show_grade_points'] = True
            # Add Grade Point column if not already present
            base_columns = ['Course Code', 'Course Title', 'Units', 'Grade']
            if 'Grade Point' not in base_columns:
                config['table_columns'] = base_columns + ['Grade Point']
        
        if options['show_student_photo']:
            config['show_student_photo'] = True
        
        if options['no_session_gpa']:
            config['show_session_gpa'] = False
        
        if options['no_logo']:
            config['show_logo'] = False
        
        return config

    def _progress_callback(self, completed, total, message):
        """Progress callback for batch processing"""
        percentage = (completed / total) * 100
        self.stdout.write(f'Progress: {completed}/{total} ({percentage:.1f}%) - {message}')

    def _display_results(self, results, options):
        """Display generation results"""
        if results['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nBatch generation completed successfully!'
                )
            )
            self.stdout.write(f'Total students processed: {results["total_students"]}')
            self.stdout.write(f'Successfully generated: {results["successful"]}')
            
            if results['failed'] > 0:
                self.stdout.write(
                    self.style.WARNING(f'Failed: {results["failed"]}')
                )
                for error in results['errors']:
                    self.stdout.write(f'  - {error}')
            
            self.stdout.write(f'Output directory: {options["output_dir"]}')
            
            if results.get('zip_file'):
                self.stdout.write(f'Zip archive created: {results["zip_file"]}')
            
            duration = results['duration'].total_seconds()
            self.stdout.write(f'Total time: {duration:.2f} seconds')
            
            if results['successful'] > 0:
                avg_time = duration / results['successful']
                self.stdout.write(f'Average time per transcript: {avg_time:.2f} seconds')
        
        else:
            self.stdout.write(
                self.style.ERROR(f'Batch generation failed: {results.get("error", "Unknown error")}')
            )

    def _save_report(self, results, output_dir):
        """Save detailed generation report as JSON"""
        import json
        from datetime import datetime
        
        # Convert datetime objects to strings for JSON serialization
        report = results.copy()
        if 'start_time' in report:
            report['start_time'] = report['start_time'].isoformat()
        if 'end_time' in report:
            report['end_time'] = report['end_time'].isoformat()
        if 'duration' in report:
            report['duration'] = str(report['duration'])
        
        report_filename = f'batch_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_path = os.path.join(output_dir, report_filename)
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.stdout.write(f'Generation report saved: {report_path}')