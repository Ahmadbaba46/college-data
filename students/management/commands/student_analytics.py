"""
Student Analytics Command
========================

Generate comprehensive analytics and reports about student performance,
demographics, and academic progress.
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, Q, F
from students.models import Student, Level, Session
from grading.models import Enrollment
import json
from datetime import datetime, date


class Command(BaseCommand):
    help = 'Generate comprehensive student analytics and reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--report-type',
            type=str,
            choices=['demographics', 'performance', 'enrollment', 'at-risk', 'comprehensive'],
            default='comprehensive',
            help='Type of analytics report to generate'
        )
        parser.add_argument(
            '--session',
            type=str,
            help='Filter by specific session'
        )
        parser.add_argument(
            '--level',
            type=str,
            help='Filter by specific level'
        )
        parser.add_argument(
            '--export',
            type=str,
            choices=['json', 'csv'],
            help='Export results to file'
        )
        parser.add_argument(
            '--output-file',
            type=str,
            help='Output file path for export'
        )

    def handle(self, *args, **options):
        # Filter students based on options
        students = Student.objects.all()
        
        if options['session']:
            try:
                session = Session.objects.get(name=options['session'])
                students = students.filter(current_session=session)
            except Session.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Session "{options["session"]}" not found'))
                return
        
        if options['level']:
            try:
                level = Level.objects.get(name=options['level'])
                students = students.filter(current_level=level)
            except Level.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Level "{options["level"]}" not found'))
                return

        # Generate reports based on type
        report_data = {}
        
        if options['report_type'] in ['demographics', 'comprehensive']:
            report_data['demographics'] = self.generate_demographics_report(students)
        
        if options['report_type'] in ['performance', 'comprehensive']:
            report_data['performance'] = self.generate_performance_report(students)
        
        if options['report_type'] in ['enrollment', 'comprehensive']:
            report_data['enrollment'] = self.generate_enrollment_report(students)
        
        if options['report_type'] in ['at-risk', 'comprehensive']:
            report_data['at_risk'] = self.generate_at_risk_report(students)

        # Display reports
        self.display_reports(report_data, options)
        
        # Export if requested
        if options['export']:
            self.export_data(report_data, options)

    def generate_demographics_report(self, students):
        """Generate demographics analytics"""
        total_students = students.count()
        
        if total_students == 0:
            return {'total_students': 0}

        # Gender distribution
        gender_dist = students.values('gender').annotate(
            count=Count('id')
        ).order_by('gender')
        
        # Status distribution
        status_dist = students.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Level distribution
        level_dist = students.values('current_level__name').annotate(
            count=Count('id')
        ).order_by('current_level__name')
        
        # Age statistics (for students with date_of_birth)
        students_with_dob = students.filter(date_of_birth__isnull=False)
        ages = []
        for student in students_with_dob:
            if student.get_age():
                ages.append(student.get_age())
        
        age_stats = {
            'total_with_dob': len(ages),
            'average_age': sum(ages) / len(ages) if ages else 0,
            'min_age': min(ages) if ages else 0,
            'max_age': max(ages) if ages else 0
        }
        
        # Nationality distribution
        nationality_dist = students.values('nationality').annotate(
            count=Count('id')
        ).order_by('-count')[:10]  # Top 10
        
        return {
            'total_students': total_students,
            'gender_distribution': list(gender_dist),
            'status_distribution': list(status_dist),
            'level_distribution': list(level_dist),
            'age_statistics': age_stats,
            'nationality_distribution': list(nationality_dist)
        }

    def generate_performance_report(self, students):
        """Generate academic performance analytics"""
        total_students = students.count()
        
        if total_students == 0:
            return {'total_students': 0}

        # CGPA statistics
        cgpa_stats = students.aggregate(
            avg_cgpa=Avg('current_cgpa'),
            total_units_attempted=Avg('total_units_attempted'),
            total_units_passed=Avg('total_units_passed')
        )
        
        # Performance level distribution
        performance_levels = {}
        for student in students:
            level = student.academic_performance_level
            performance_levels[level] = performance_levels.get(level, 0) + 1
        
        # Students by CGPA ranges
        cgpa_ranges = {
            '3.5-4.0': students.filter(current_cgpa__gte=3.5).count(),
            '3.0-3.49': students.filter(current_cgpa__gte=3.0, current_cgpa__lt=3.5).count(),
            '2.5-2.99': students.filter(current_cgpa__gte=2.5, current_cgpa__lt=3.0).count(),
            '2.0-2.49': students.filter(current_cgpa__gte=2.0, current_cgpa__lt=2.5).count(),
            'Below 2.0': students.filter(current_cgpa__lt=2.0).count()
        }
        
        # Completion rate statistics
        completion_rates = []
        for student in students:
            if student.total_units_attempted > 0:
                completion_rates.append(student.completion_rate)
        
        completion_stats = {
            'average_completion_rate': sum(completion_rates) / len(completion_rates) if completion_rates else 0,
            'students_above_80_percent': len([r for r in completion_rates if r >= 80]),
            'students_below_70_percent': len([r for r in completion_rates if r < 70])
        }

        return {
            'total_students': total_students,
            'cgpa_statistics': cgpa_stats,
            'performance_levels': performance_levels,
            'cgpa_ranges': cgpa_ranges,
            'completion_statistics': completion_stats
        }

    def generate_enrollment_report(self, students):
        """Generate enrollment analytics"""
        total_students = students.count()
        
        if total_students == 0:
            return {'total_students': 0}

        # Enrollment by session
        session_enrollments = students.values('current_session__name').annotate(
            count=Count('id')
        ).order_by('current_session__name')
        
        # New students this academic year
        current_year = datetime.now().year
        new_students = students.filter(admission_date__year=current_year).count()
        
        # Students by admission year
        admission_years = students.values('admission_date__year').annotate(
            count=Count('id')
        ).order_by('-admission_date__year')
        
        # Students with missing information
        missing_info = {
            'no_email': students.filter(email__isnull=True).count(),
            'no_phone': students.filter(phone__isnull=True).count(),
            'no_photo': students.filter(photo='').count(),
            'no_date_of_birth': students.filter(date_of_birth__isnull=True).count(),
            'no_current_level': students.filter(current_level__isnull=True).count()
        }

        return {
            'total_students': total_students,
            'session_enrollments': list(session_enrollments),
            'new_students_this_year': new_students,
            'admission_years': list(admission_years),
            'missing_information': missing_info
        }

    def generate_at_risk_report(self, students):
        """Generate at-risk student analytics"""
        total_students = students.count()
        
        if total_students == 0:
            return {'total_students': 0}

        # Identify at-risk students
        at_risk_students = []
        for student in students:
            if student.is_at_risk:
                at_risk_students.append({
                    'student_id': student.student_id,
                    'name': student.full_name,
                    'cgpa': student.current_cgpa,
                    'completion_rate': student.completion_rate,
                    'level': student.current_level.name if student.current_level else 'N/A',
                    'status': student.status
                })
        
        # Risk factors analysis
        low_cgpa_count = students.filter(current_cgpa__lt=2.0).count()
        low_completion_count = 0
        for student in students:
            if student.completion_rate < 70:
                low_completion_count += 1
        
        return {
            'total_students': total_students,
            'at_risk_count': len(at_risk_students),
            'at_risk_percentage': (len(at_risk_students) / total_students * 100) if total_students > 0 else 0,
            'at_risk_students': at_risk_students,
            'risk_factors': {
                'low_cgpa': low_cgpa_count,
                'low_completion_rate': low_completion_count
            }
        }

    def display_reports(self, report_data, options):
        """Display formatted reports to console"""
        self.stdout.write(self.style.SUCCESS('=== STUDENT ANALYTICS REPORT ==='))
        self.stdout.write(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        if options['session']:
            self.stdout.write(f'Session Filter: {options["session"]}')
        if options['level']:
            self.stdout.write(f'Level Filter: {options["level"]}')
        
        self.stdout.write('')

        # Display demographics
        if 'demographics' in report_data:
            demo = report_data['demographics']
            self.stdout.write(self.style.HTTP_INFO('📊 DEMOGRAPHICS'))
            self.stdout.write(f'Total Students: {demo["total_students"]}')
            
            if demo['total_students'] > 0:
                self.stdout.write('\nGender Distribution:')
                for item in demo['gender_distribution']:
                    gender = item['gender'] or 'Not Specified'
                    self.stdout.write(f'  {gender}: {item["count"]}')
                
                self.stdout.write('\nStatus Distribution:')
                for item in demo['status_distribution']:
                    self.stdout.write(f'  {item["status"]}: {item["count"]}')
            
            self.stdout.write('')

        # Display performance
        if 'performance' in report_data:
            perf = report_data['performance']
            self.stdout.write(self.style.HTTP_INFO('📈 ACADEMIC PERFORMANCE'))
            
            if perf['total_students'] > 0:
                cgpa = perf['cgpa_statistics']
                self.stdout.write(f'Average CGPA: {cgpa["avg_cgpa"]:.2f}')
                self.stdout.write(f'Average Units Attempted: {cgpa["total_units_attempted"]:.1f}')
                self.stdout.write(f'Average Units Passed: {cgpa["total_units_passed"]:.1f}')
                
                self.stdout.write('\nPerformance Levels:')
                for level, count in perf['performance_levels'].items():
                    percentage = (count / perf['total_students']) * 100
                    self.stdout.write(f'  {level}: {count} ({percentage:.1f}%)')
            
            self.stdout.write('')

        # Display at-risk
        if 'at_risk' in report_data:
            risk = report_data['at_risk']
            self.stdout.write(self.style.WARNING('⚠️  AT-RISK STUDENTS'))
            self.stdout.write(f'Students at Risk: {risk["at_risk_count"]} ({risk["at_risk_percentage"]:.1f}%)')
            
            if risk['at_risk_students']:
                self.stdout.write('\nAt-Risk Student Details:')
                for student in risk['at_risk_students'][:10]:  # Show first 10
                    self.stdout.write(
                        f'  {student["student_id"]} - {student["name"]} '
                        f'(CGPA: {student["cgpa"]:.2f}, Completion: {student["completion_rate"]:.1f}%)'
                    )
                
                if len(risk['at_risk_students']) > 10:
                    self.stdout.write(f'  ... and {len(risk["at_risk_students"]) - 10} more')
            
            self.stdout.write('')

    def export_data(self, report_data, options):
        """Export report data to file"""
        filename = options['output_file'] or f'student_analytics_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        if options['export'] == 'json':
            filename += '.json'
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
        
        elif options['export'] == 'csv':
            filename += '.csv'
            # Implement CSV export for key metrics
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                
                # Write key metrics
                if 'demographics' in report_data:
                    writer.writerow(['Total Students', report_data['demographics']['total_students']])
                
                if 'performance' in report_data:
                    cgpa = report_data['performance']['cgpa_statistics']
                    writer.writerow(['Average CGPA', f"{cgpa['avg_cgpa']:.2f}"])
                
                if 'at_risk' in report_data:
                    writer.writerow(['At Risk Students', report_data['at_risk']['at_risk_count']])

        self.stdout.write(self.style.SUCCESS(f'Report exported to: {filename}'))