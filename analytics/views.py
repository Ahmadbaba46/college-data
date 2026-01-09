from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q, F
from datetime import datetime, timedelta

from students.models import Student, Session, Level
from courses.models import Course
from grading.models import Enrollment, Grade, GradingSettings
from academics.models import Program
from teachers.models import Teacher


@login_required
def analytics_overview(request):
    """Main analytics dashboard with key metrics"""
    
    # Key Metrics
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_programs = Program.objects.count()
    total_enrollments = Enrollment.objects.count()
    
    # Students by level
    students_by_level = Student.objects.values(
        'current_level__name'
    ).annotate(
        count=Count('id')
    ).order_by('current_level__name')
    
    # Students by program
    students_by_program = Student.objects.filter(
        program__isnull=False
    ).values(
        'program__code', 'program__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Recent enrollments trend (last 6 sessions)
    recent_sessions = Session.objects.all().order_by('-name')[:6]
    enrollment_trend = []
    for session in recent_sessions:
        count = Enrollment.objects.filter(course_offering__session=session).count()
        enrollment_trend.append({
            'session': session.name,
            'count': count
        })
    enrollment_trend.reverse()
    
    # Grade distribution
    grade_distribution = Grade.objects.filter(
        status='APPROVED'
    ).values('grade').annotate(
        count=Count('id')
    ).order_by('grade')
    
    # Pass/Fail rates
    passing_grades = ['A', 'B', 'C', 'D']
    total_graded = Grade.objects.filter(status='APPROVED').count()
    passed = Grade.objects.filter(status='APPROVED', grade__in=passing_grades).count()
    pass_rate = (passed / total_graded * 100) if total_graded > 0 else 0
    
    # Teachers stats
    total_teachers = Teacher.objects.count()
    active_teachers = Teacher.objects.filter(is_active=True).count()
    
    import json
    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_programs': total_programs,
        'total_enrollments': total_enrollments,
        'total_teachers': total_teachers,
        'active_teachers': active_teachers,
        'students_by_level': list(students_by_level),
        'students_by_program': list(students_by_program),
        'enrollment_trend': json.dumps(enrollment_trend),
        'grade_distribution': json.dumps(list(grade_distribution)),
        'pass_rate': round(pass_rate, 1),
    }
    
    return render(request, 'analytics/overview.html', context)


@login_required
def enrollment_analytics(request):
    """Enrollment statistics and trends"""
    
    # Enrollment by session
    enrollments_by_session = Enrollment.objects.values(
        'course_offering__session__name'
    ).annotate(
        count=Count('id')
    ).order_by('-course_offering__session__name')[:10]
    
    # Enrollment by semester
    enrollments_by_semester = Enrollment.objects.values(
        'course_offering__semester'
    ).annotate(
        count=Count('id')
    ).order_by('course_offering__semester')
    
    # Top enrolled courses
    top_courses = Enrollment.objects.values(
        'course_offering__course__code',
        'course_offering__course__title'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Enrollment by level
    enrollments_by_level = Enrollment.objects.values(
        'student__current_level__name'
    ).annotate(
        count=Count('id')
    ).order_by('student__current_level__name')
    
    # Recent enrollment activity
    recent_enrollments = Enrollment.objects.select_related(
        'student', 'course_offering__course', 'course_offering__session'
    ).order_by('-id')[:20]
    
    import json
    context = {
        'enrollments_by_session': json.dumps(list(enrollments_by_session)),
        'enrollments_by_semester': list(enrollments_by_semester),
        'top_courses': list(top_courses),
        'enrollments_by_level': json.dumps(list(enrollments_by_level)),
        'recent_enrollments': recent_enrollments,
        'total_enrollments': Enrollment.objects.count(),
    }
    return render(request, 'analytics/enrollments.html', context)


@login_required
def student_analytics(request):
    """Student performance analytics"""
    
    # Students by level distribution
    students_by_level = Student.objects.values(
        'current_level__name'
    ).annotate(
        count=Count('id')
    ).order_by('current_level__name')
    
    # Students by program
    students_by_program = Student.objects.filter(
        program__isnull=False
    ).values(
        'program__code', 'program__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Students by gender
    students_by_gender = Student.objects.exclude(
        gender__isnull=True
    ).values('gender').annotate(
        count=Count('id')
    )
    
    # Average GPA by level (if GPA field exists)
    # For now, we'll calculate based on approved grades
    gpa_by_level = []
    for level in Level.objects.all():
        students = Student.objects.filter(current_level=level)
        if students.exists():
            # Calculate average grade points for students at this level
            grades = Grade.objects.filter(
                enrollment__student__current_level=level,
                status='APPROVED'
            )
            
            if grades.exists():
                # Get grading settings for each grade
                total_points = 0
                count = 0
                for g in grades:
                    try:
                        setting = GradingSettings.objects.filter(grade=g.grade).first()
                        if setting:
                            total_points += setting.grade_point
                            count += 1
                    except:
                        pass
                
                if count > 0:
                    avg_gpa = total_points / count
                    gpa_by_level.append({
                        'level': level.name,
                        'avg_gpa': round(avg_gpa, 2)
                    })
    
    # Top performing students (by grade count)
    from django.db.models import Exists, OuterRef
    top_students = Student.objects.annotate(
        grade_count=Count('enrollment', filter=Q(enrollment__grade__status='APPROVED'))
    ).filter(grade_count__gt=0).order_by('-grade_count')[:10]
    
    import json
    context = {
        'students_by_level': json.dumps(list(students_by_level)),
        'students_by_program': list(students_by_program),
        'students_by_gender': list(students_by_gender),
        'gpa_by_level': gpa_by_level,
        'top_students': top_students,
        'total_students': Student.objects.count(),
    }
    return render(request, 'analytics/students.html', context)


@login_required
def grade_analytics(request):
    """Grade distribution and analysis"""
    
    # Overall grade distribution
    grade_distribution = Grade.objects.filter(
        status='APPROVED'
    ).values('grade').annotate(
        count=Count('id')
    ).order_by('grade')
    
    # Grade distribution by level
    grades_by_level = {}
    for level in Level.objects.all():
        level_grades = Grade.objects.filter(
            status='APPROVED',
            enrollment__student__current_level=level
        ).values('grade').annotate(
            count=Count('id')
        )
        if level_grades:
            grades_by_level[level.name] = list(level_grades)
    
    # Pass/Fail statistics by course
    passing_grades = ['A', 'B', 'C', 'D']
    course_pass_rates = []
    
    courses_with_grades = Course.objects.filter(
        offerings__enrollments__grade__status='APPROVED'
    ).distinct()[:20]
    
    for course in courses_with_grades:
        total = Grade.objects.filter(
            enrollment__course_offering__course=course,
            status='APPROVED'
        ).count()
        
        passed = Grade.objects.filter(
            enrollment__course_offering__course=course,
            status='APPROVED',
            grade__in=passing_grades
        ).count()
        
        if total > 0:
            pass_rate = (passed / total) * 100
            course_pass_rates.append({
                'code': course.code,
                'title': course.title,
                'total': total,
                'passed': passed,
                'pass_rate': round(pass_rate, 1)
            })
    
    course_pass_rates.sort(key=lambda x: x['pass_rate'])
    
    # Grading status overview
    grading_status = Grade.objects.values('status').annotate(
        count=Count('id')
    )
    
    import json
    context = {
        'grade_distribution': json.dumps(list(grade_distribution)),
        'grades_by_level': grades_by_level,
        'course_pass_rates': course_pass_rates[:10],  # Hardest courses
        'grading_status': list(grading_status),
        'total_grades': Grade.objects.count(),
    }
    return render(request, 'analytics/grades.html', context)


@login_required
def teacher_analytics(request):
    """Teacher performance metrics"""
    from courses.models import CourseOffering
    
    # Total teachers
    total_teachers = Teacher.objects.count()
    active_teachers = Teacher.objects.filter(is_active=True).count()
    
    # Teacher workload (by course assignments)
    teacher_workload = Teacher.objects.annotate(
        course_count=Count('courses', distinct=True)
    ).filter(course_count__gt=0).order_by('-course_count')[:10]
    
    # Teachers by department (if available)
    teachers_by_dept = Teacher.objects.exclude(
        department__isnull=True
    ).exclude(
        department=''
    ).values('department').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Course offerings by teacher (recent offerings)
    teacher_offerings = CourseOffering.objects.select_related(
        'course', 'session'
    ).filter(
        teacher__isnull=False
    ).values(
        'teacher__staff_id',
        'teacher__first_name',
        'teacher__last_name'
    ).annotate(
        offering_count=Count('id')
    ).order_by('-offering_count')[:15]
    
    # Grade statistics by teacher
    teacher_grade_stats = []
    # Get teachers who have taught courses (offerings without teacher field for now)
    top_teachers = Teacher.objects.filter(is_active=True)[:10]
    
    passing_grades = ['A', 'B', 'C', 'D']
    for teacher in top_teachers:
        # Count grades for courses assigned to this teacher
        total_grades = Grade.objects.filter(
            enrollment__course_offering__course__in=teacher.courses.all(),
            status='APPROVED'
        ).count()
        
        if total_grades > 0:
            passed = Grade.objects.filter(
                enrollment__course_offering__course__in=teacher.courses.all(),
                status='APPROVED',
                grade__in=passing_grades
            ).count()
            
            pass_rate = (passed / total_grades) * 100
            teacher_grade_stats.append({
                'teacher': teacher,
                'total_grades': total_grades,
                'pass_rate': round(pass_rate, 1)
            })
    
    teacher_grade_stats.sort(key=lambda x: x['total_grades'], reverse=True)
    
    import json
    context = {
        'total_teachers': total_teachers,
        'active_teachers': active_teachers,
        'teacher_workload': teacher_workload,
        'teachers_by_dept': list(teachers_by_dept),
        'teacher_offerings': teacher_offerings,
        'teacher_grade_stats': teacher_grade_stats[:10],
    }
    return render(request, 'analytics/teachers.html', context)


@login_required
def graduation_analytics(request):
    """Graduation eligibility and cohort analysis"""
    # Note: check_graduation_eligibility may not exist, so we'll check manually
    
    # Students by level (potential graduates)
    students_by_level = Student.objects.values(
        'current_level__name'
    ).annotate(
        count=Count('id')
    ).order_by('current_level__name')
    
    # Check graduation eligibility for final year students
    # Assuming final year is determined by highest level
    final_levels = Level.objects.all().order_by('-name')[:2]  # Top 2 levels
    
    eligible_students = []
    not_eligible_students = []
    
    # Simple eligibility check based on approved grades count
    for level in final_levels:
        students = Student.objects.filter(current_level=level, program__isnull=False)[:50]
        for student in students:
            try:
                # Count approved grades
                approved_count = Grade.objects.filter(
                    enrollment__student=student,
                    status='APPROVED'
                ).count()
                
                # Simple rule: if more than 20 approved grades, consider eligible
                if approved_count >= 20:
                    eligible_students.append({
                        'student': student,
                        'details': {'message': f'{approved_count} courses completed'}
                    })
                else:
                    not_eligible_students.append({
                        'student': student,
                        'details': {'message': f'Only {approved_count} courses completed'}
                    })
            except Exception:
                # Skip if check fails
                pass
    
    # Students by program (graduation candidates)
    students_by_program = Student.objects.filter(
        program__isnull=False,
        current_level__in=final_levels
    ).values(
        'program__code', 'program__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Completion rate by program
    program_completion = []
    for program in Program.objects.all()[:10]:
        total_students = Student.objects.filter(program=program).count()
        if total_students > 0:
            # Students with enough approved grades (rough estimate)
            completed = Student.objects.filter(
                program=program,
                enrollments__grade__status='APPROVED'
            ).annotate(
                approved_count=Count('enrollments__grade')
            ).filter(approved_count__gte=20).distinct().count()
            
            completion_rate = (completed / total_students) * 100
            program_completion.append({
                'program': program,
                'total': total_students,
                'completed': completed,
                'rate': round(completion_rate, 1)
            })
    
    import json
    context = {
        'students_by_level': json.dumps(list(students_by_level)),
        'eligible_count': len(eligible_students),
        'not_eligible_count': len(not_eligible_students),
        'eligible_students': eligible_students[:20],
        'not_eligible_students': not_eligible_students[:20],
        'students_by_program': list(students_by_program),
        'program_completion': program_completion,
    }
    return render(request, 'analytics/graduation.html', context)


# Export Views
import csv
from django.http import HttpResponse

@login_required
def export_enrollments(request):
    """Export enrollment analytics to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="enrollment_analytics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Course Code', 'Course Title', 'Session', 'Semester', 'Level'])
    
    enrollments = Enrollment.objects.select_related(
        'student', 'course_offering__course', 'course_offering__session', 'student__current_level'
    ).all()[:1000]  # Limit for performance
    
    for enrollment in enrollments:
        writer.writerow([
            enrollment.student.student_id,
            enrollment.student.full_name,
            enrollment.course_offering.course.code,
            enrollment.course_offering.course.title,
            enrollment.course_offering.session.name,
            enrollment.course_offering.get_semester_display(),
            enrollment.student.current_level.name if enrollment.student.current_level else '-'
        ])
    
    return response


@login_required
def export_students(request):
    """Export student analytics to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_analytics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'First Name', 'Last Name', 'Level', 'Program', 'Gender', 'Completed Courses'])
    
    students = Student.objects.select_related('current_level', 'program').annotate(
        course_count=Count('enrollments__grade', filter=Q(enrollments__grade__status='APPROVED'))
    ).all()
    
    for student in students:
        writer.writerow([
            student.student_id,
            student.first_name,
            student.last_name,
            student.current_level.name if student.current_level else '-',
            student.program.code if student.program else '-',
            student.get_gender_display() if student.gender else '-',
            student.course_count
        ])
    
    return response


@login_required
def export_grades(request):
    """Export grade analytics to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="grade_analytics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Course Code', 'Course Title', 'Grade', 'Total Score', 'Status', 'Session'])
    
    grades = Grade.objects.select_related(
        'enrollment__student',
        'enrollment__course_offering__course',
        'enrollment__course_offering__session'
    ).filter(status='APPROVED').all()[:1000]
    
    for grade in grades:
        writer.writerow([
            grade.enrollment.student.student_id,
            grade.enrollment.student.full_name,
            grade.enrollment.course_offering.course.code,
            grade.enrollment.course_offering.course.title,
            grade.grade,
            grade.total_score,
            grade.get_status_display(),
            grade.enrollment.course_offering.session.name
        ])
    
    return response


@login_required
def export_teachers(request):
    """Export teacher analytics to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="teacher_analytics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Staff ID', 'First Name', 'Last Name', 'Department', 'Is Active', 'Course Assignments'])
    
    teachers = Teacher.objects.annotate(
        course_count=Count('courses', distinct=True)
    ).all()
    
    for teacher in teachers:
        writer.writerow([
            teacher.staff_id,
            teacher.first_name,
            teacher.last_name,
            teacher.department or '-',
            'Yes' if teacher.is_active else 'No',
            teacher.course_count
        ])
    
    return response


@login_required
def export_graduation(request):
    """Export graduation analytics to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="graduation_analytics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Program', 'Level', 'Eligible', 'Reason'])
    
    final_levels = Level.objects.all().order_by('-name')[:2]
    students = Student.objects.filter(current_level__in=final_levels, program__isnull=False).select_related('program', 'current_level')[:200]
    
    for student in students:
        try:
            # Simple eligibility check
            approved_count = Grade.objects.filter(
                enrollment__student=student,
                status='APPROVED'
            ).count()
            
            is_eligible = approved_count >= 20
            reason = f'{approved_count} courses completed'
            
            writer.writerow([
                student.student_id,
                student.full_name,
                student.program.code if student.program else '-',
                student.current_level.name if student.current_level else '-',
                'Yes' if is_eligible else 'No',
                reason
            ])
        except Exception as e:
            writer.writerow([
                student.student_id,
                student.full_name,
                student.program.code if student.program else '-',
                student.current_level.name if student.current_level else '-',
                'Error',
                str(e)
            ])
    
    return response
