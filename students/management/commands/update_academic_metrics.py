"""
Update Academic Metrics Command
=============================

This command recalculates and updates CGPA and other academic metrics
for students based on their current grades.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from students.models import Student
from django.utils import timezone


class Command(BaseCommand):
    help = 'Update academic metrics (CGPA, units, etc.) for students'

    def add_arguments(self, parser):
        parser.add_argument(
            '--student-id',
            type=str,
            help='Update metrics for specific student ID'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Update metrics for all students'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['active', 'suspended', 'graduated', 'dropped', 'transferred', 'deferred', 'expelled'],
            help='Update metrics for students with specific status'
        )
        parser.add_argument(
            '--level',
            type=str,
            help='Update metrics for students at specific level'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )

    def handle(self, *args, **options):
        # Determine which students to update
        if options['student_id']:
            try:
                students = [Student.objects.get(student_id=options['student_id'])]
            except Student.DoesNotExist:
                raise CommandError(f'Student with ID {options["student_id"]} does not exist.')
        
        elif options['all']:
            students = Student.objects.all()
        
        elif options['status']:
            students = Student.objects.filter(status=options['status'])
        
        elif options['level']:
            from students.models import Level
            try:
                level = Level.objects.get(name=options['level'])
                students = Student.objects.filter(current_level=level)
            except Level.DoesNotExist:
                raise CommandError(f'Level "{options["level"]}" does not exist.')
        
        else:
            raise CommandError('Must specify --all, --student-id, --status, or --level')

        if not students:
            self.stdout.write(self.style.WARNING('No students found matching criteria.'))
            return

        self.stdout.write(f'Found {len(students)} student(s) to update.')

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))

        updated_count = 0
        error_count = 0

        with transaction.atomic():
            for student in students:
                try:
                    # Store old values for comparison
                    old_cgpa = student.current_cgpa
                    old_attempted = student.total_units_attempted
                    old_passed = student.total_units_passed
                    
                    if not options['dry_run']:
                        student.update_academic_metrics(save=True)
                    else:
                        # Calculate new values without saving
                        student.update_academic_metrics(save=False)
                    
                    # Show changes if verbose or dry run
                    if options['verbose'] or options['dry_run']:
                        cgpa_change = student.current_cgpa - old_cgpa
                        attempted_change = student.total_units_attempted - old_attempted
                        passed_change = student.total_units_passed - old_passed
                        
                        self.stdout.write(
                            f'Student {student.student_id} ({student.full_name}):'
                        )
                        self.stdout.write(
                            f'  CGPA: {old_cgpa:.2f} → {student.current_cgpa:.2f} '
                            f'({"+" if cgpa_change >= 0 else ""}{cgpa_change:.2f})'
                        )
                        self.stdout.write(
                            f'  Units Attempted: {old_attempted} → {student.total_units_attempted} '
                            f'({"+" if attempted_change >= 0 else ""}{attempted_change})'
                        )
                        self.stdout.write(
                            f'  Units Passed: {old_passed} → {student.total_units_passed} '
                            f'({"+" if passed_change >= 0 else ""}{passed_change})'
                        )
                        self.stdout.write(
                            f'  Performance: {student.academic_performance_level}'
                        )
                        self.stdout.write(
                            f'  Completion Rate: {student.completion_rate}%'
                        )
                        if student.is_at_risk:
                            self.stdout.write(
                                self.style.WARNING('  ⚠️  STUDENT AT RISK')
                            )
                        self.stdout.write('')
                    
                    updated_count += 1

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error updating {student.student_id}: {str(e)}'
                        )
                    )

        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN COMPLETE: Would update {updated_count} students'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} students'
                )
            )

        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'Errors encountered: {error_count}')
            )

        # Summary statistics
        if updated_count > 0 and not options['dry_run']:
            self.show_summary_statistics(students)

    def show_summary_statistics(self, students):
        """Show summary statistics after update"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SUMMARY STATISTICS')
        self.stdout.write('='*50)
        
        # Performance distribution
        performance_counts = {
            'Excellent (First Class)': 0,
            'Good (Second Class Upper)': 0,
            'Satisfactory (Second Class Lower)': 0,
            'Pass (Third Class)': 0,
            'Below Average': 0
        }
        
        at_risk_count = 0
        total_cgpa = 0
        
        for student in students:
            student.refresh_from_db()  # Get updated values
            performance_counts[student.academic_performance_level] += 1
            if student.is_at_risk:
                at_risk_count += 1
            total_cgpa += student.current_cgpa
        
        self.stdout.write('\nPerformance Distribution:')
        for performance, count in performance_counts.items():
            percentage = (count / len(students)) * 100
            self.stdout.write(f'  {performance}: {count} ({percentage:.1f}%)')
        
        average_cgpa = total_cgpa / len(students) if students else 0
        self.stdout.write(f'\nAverage CGPA: {average_cgpa:.2f}')
        self.stdout.write(f'Students at Risk: {at_risk_count} ({(at_risk_count/len(students)*100):.1f}%)')
        
        self.stdout.write('\n' + '='*50)