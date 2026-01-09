"""
Student Data Validation Command
==============================

Comprehensive data validation for student records, identifying and
optionally fixing data quality issues.
"""

from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction
from students.models import Student
from datetime import date, datetime
import re


class Command(BaseCommand):
    help = 'Validate student data and identify quality issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Attempt to automatically fix certain issues'
        )
        parser.add_argument(
            '--student-id',
            type=str,
            help='Validate specific student ID'
        )
        parser.add_argument(
            '--export-report',
            type=str,
            help='Export validation report to file'
        )
        parser.add_argument(
            '--show-all',
            action='store_true',
            help='Show all validation results, including passed checks'
        )

    def handle(self, *args, **options):
        # Get students to validate
        if options['student_id']:
            try:
                students = [Student.objects.get(student_id=options['student_id'])]
            except Student.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Student {options["student_id"]} not found'))
                return
        else:
            students = Student.objects.all()

        self.stdout.write(f'Validating {len(students)} student records...')
        self.stdout.write('=' * 60)

        validation_results = {
            'total_students': len(students),
            'issues_found': 0,
            'issues_fixed': 0,
            'validation_details': []
        }

        for student in students:
            student_issues = self.validate_student(student, options)
            if student_issues['has_issues'] or options['show_all']:
                validation_results['validation_details'].append(student_issues)
                if student_issues['has_issues']:
                    validation_results['issues_found'] += len(student_issues['issues'])

        # Display summary
        self.display_summary(validation_results, options)

        # Export report if requested
        if options['export_report']:
            self.export_report(validation_results, options['export_report'])

    def validate_student(self, student, options):
        """Validate a single student record"""
        issues = []
        fixes_applied = []

        # 1. Required field validation
        if not student.email:
            issues.append({
                'type': 'missing_data',
                'field': 'email',
                'message': 'Email address missing',
                'severity': 'medium'
            })

        if not student.phone:
            issues.append({
                'type': 'missing_data',
                'field': 'phone',
                'message': 'Phone number missing',
                'severity': 'medium'
            })

        if not student.date_of_birth:
            issues.append({
                'type': 'missing_data',
                'field': 'date_of_birth',
                'message': 'Date of birth missing',
                'severity': 'high'
            })

        if not student.current_level:
            issues.append({
                'type': 'missing_data',
                'field': 'current_level',
                'message': 'Current level not set',
                'severity': 'high'
            })

        # 2. Email validation
        if student.email:
            if not self.is_valid_email(student.email):
                issues.append({
                    'type': 'invalid_format',
                    'field': 'email',
                    'message': f'Invalid email format: {student.email}',
                    'severity': 'high'
                })

        # 3. Phone validation
        if student.phone:
            if not self.is_valid_phone(student.phone):
                issues.append({
                    'type': 'invalid_format',
                    'field': 'phone',
                    'message': f'Invalid phone format: {student.phone}',
                    'severity': 'medium'
                })

        # 4. Date validation
        if student.date_of_birth:
            age = student.get_age()
            if age and (age < 10 or age > 80):
                issues.append({
                    'type': 'invalid_data',
                    'field': 'date_of_birth',
                    'message': f'Unusual age: {age} years old',
                    'severity': 'medium'
                })

        # 5. Academic data validation
        if student.current_cgpa < 0 or student.current_cgpa > 4.0:
            issues.append({
                'type': 'invalid_data',
                'field': 'current_cgpa',
                'message': f'CGPA out of range: {student.current_cgpa}',
                'severity': 'high'
            })

        if student.total_units_passed > student.total_units_attempted:
            issues.append({
                'type': 'data_inconsistency',
                'field': 'units',
                'message': f'Units passed ({student.total_units_passed}) > units attempted ({student.total_units_attempted})',
                'severity': 'high'
            })

        # 6. Status validation
        if student.status == 'graduated' and not student.graduation_date:
            issue = {
                'type': 'missing_data',
                'field': 'graduation_date',
                'message': 'Graduation date missing for graduated student',
                'severity': 'high'
            }
            issues.append(issue)

            # Auto-fix: Set graduation date to admission date + 4 years
            if options['fix_issues']:
                estimated_grad_date = date(
                    student.admission_date.year + 4,
                    student.admission_date.month,
                    student.admission_date.day
                )
                student.graduation_date = estimated_grad_date
                student.save(update_fields=['graduation_date'])
                fixes_applied.append(f'Set graduation date to {estimated_grad_date}')

        # 7. Emergency contact validation
        if student.emergency_contact and not student.emergency_phone:
            issues.append({
                'type': 'incomplete_data',
                'field': 'emergency_contact',
                'message': 'Emergency contact name provided but no phone number',
                'severity': 'medium'
            })

        # 8. Photo validation
        if not student.photo:
            issues.append({
                'type': 'missing_data',
                'field': 'photo',
                'message': 'Student photo missing',
                'severity': 'low'
            })

        # 9. Academic progression validation
        if student.entry_level and student.current_level:
            def _level_sort_key(level_obj):
                """Best-effort ordering for levels.

                Tries to extract a numeric level (e.g., 100/200) from the name,
                otherwise falls back to pk ordering.
                """
                import re
                name = (getattr(level_obj, 'name', '') or '').strip().lower()
                m = re.search(r'(\d+)', name)
                if m:
                    try:
                        return int(m.group(1))
                    except ValueError:
                        pass
                # fallback: stable but not semantically perfect
                return int(getattr(level_obj, 'pk', 0) or 0)

            entry_key = _level_sort_key(student.entry_level)
            current_key = _level_sort_key(student.current_level)

            if current_key < entry_key:
                issues.append({
                    'type': 'academic_progression',
                    'field': 'current_level',
                    'message': (
                        f"Current level ({student.current_level}) appears below entry level "
                        f"({student.entry_level})."
                    ),
                    'severity': 'high',
                })

                # Auto-fix: set current_level to entry_level
                if options['fix_issues']:
                    student.current_level = student.entry_level
                    student.save(update_fields=['current_level'])
                    fixes_applied.append(f'Reset current level to entry level: {student.entry_level}')

        # 10. Duplicate check
        duplicates = Student.objects.filter(
            first_name=student.first_name,
            last_name=student.last_name,
            date_of_birth=student.date_of_birth
        ).exclude(pk=student.pk)

        if duplicates.exists():
            issues.append({
                'type': 'potential_duplicate',
                'field': 'identity',
                'message': f'Potential duplicate: {[s.student_id for s in duplicates]}',
                'severity': 'high'
            })

        return {
            'student_id': student.student_id,
            'student_name': student.full_name,
            'has_issues': len(issues) > 0,
            'issue_count': len(issues),
            'issues': issues,
            'fixes_applied': fixes_applied
        }

    def is_valid_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def is_valid_phone(self, phone):
        """Validate phone number format"""
        # Remove common formatting characters
        clean_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
        # Check if it's all digits and reasonable length
        return clean_phone.isdigit() and 10 <= len(clean_phone) <= 15

    def display_summary(self, results, options):
        """Display validation summary"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('VALIDATION SUMMARY')
        self.stdout.write('=' * 60)

        self.stdout.write(f'Total students validated: {results["total_students"]}')
        self.stdout.write(f'Students with issues: {len([s for s in results["validation_details"] if s["has_issues"]])}')
        self.stdout.write(f'Total issues found: {results["issues_found"]}')

        if options['fix_issues']:
            total_fixes = sum(len(s['fixes_applied']) for s in results['validation_details'])
            self.stdout.write(f'Issues automatically fixed: {total_fixes}')

        # Group issues by severity
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        issue_type_counts = {}

        for student_result in results['validation_details']:
            for issue in student_result['issues']:
                severity_counts[issue['severity']] += 1
                issue_type = issue['type']
                issue_type_counts[issue_type] = issue_type_counts.get(issue_type, 0) + 1

        self.stdout.write('\nIssues by Severity:')
        for severity, count in severity_counts.items():
            if count > 0:
                style = self.style.ERROR if severity == 'high' else (
                    self.style.WARNING if severity == 'medium' else self.style.HTTP_INFO
                )
                self.stdout.write(style(f'  {severity.upper()}: {count}'))

        self.stdout.write('\nIssues by Type:')
        for issue_type, count in sorted(issue_type_counts.items()):
            self.stdout.write(f'  {issue_type}: {count}')

        # Show detailed issues for students with problems
        if not options['show_all']:
            problem_students = [s for s in results['validation_details'] if s['has_issues']][:10]
        else:
            problem_students = results['validation_details'][:10]

        if problem_students:
            self.stdout.write('\nDetailed Issues (showing first 10):')
            for student_result in problem_students:
                self.stdout.write(f'\n{student_result["student_id"]} - {student_result["student_name"]}:')
                
                for issue in student_result['issues']:
                    severity_style = self.style.ERROR if issue['severity'] == 'high' else (
                        self.style.WARNING if issue['severity'] == 'medium' else self.style.HTTP_INFO
                    )
                    self.stdout.write(f'  {severity_style("●")} {issue["message"]} ({issue["severity"]})')

                if student_result['fixes_applied']:
                    self.stdout.write('  Fixes applied:')
                    for fix in student_result['fixes_applied']:
                        self.stdout.write(f'    ✓ {fix}')

    def export_report(self, results, filename):
        """Export validation report to file"""
        import json
        
        # Prepare data for export
        export_data = {
            'validation_date': datetime.now().isoformat(),
            'summary': {
                'total_students': results['total_students'],
                'students_with_issues': len([s for s in results['validation_details'] if s['has_issues']]),
                'total_issues': results['issues_found']
            },
            'detailed_results': results['validation_details']
        }

        # Write to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        self.stdout.write(f'\nValidation report exported to: {filename}')