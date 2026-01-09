from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Avg

from django.contrib.auth.models import User
from students.models import Student, Level
from courses.models import CourseOffering
from grading.models import Enrollment, Grade, GradingSettings


@login_required
def dashboard(request):
    return render(request, 'portal/dashboard.html')


@login_required
def system_stats_partial(request):
    ctx = {
        'users_count': User.objects.count(),
        'students_count': Student.objects.count(),
        'offerings_count': CourseOffering.objects.count(),
        'updated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    return render(request, 'portal/partials/system_stats.html', ctx)


@login_required
def enrollment_stats_data(request):
    """API endpoint for enrollment trends chart"""
    stats = (
        Enrollment.objects
        .values('course_offering__session__name')
        .annotate(count=Count('id'))
        .order_by('course_offering__session__name')
    )
    
    labels = [item['course_offering__session__name'] or 'Unknown' for item in stats]
    values = [item['count'] for item in stats]
    
    return JsonResponse({'labels': labels, 'values': values})


@login_required
def student_distribution_data(request):
    """API endpoint for student distribution by level"""
    stats = (
        Student.objects
        .values('current_level__name')
        .annotate(count=Count('id'))
        .order_by('current_level__name')
    )
    
    labels = [item['current_level__name'] or 'No Level' for item in stats]
    values = [item['count'] for item in stats]
    
    return JsonResponse({'labels': labels, 'values': values})


@login_required
def grade_distribution_data(request):
    """API endpoint for grade distribution chart"""
    # Only show approved grades
    grades = (
        Grade.objects
        .filter(status=Grade.STATUS_APPROVED)
        .values('grade')
        .annotate(count=Count('id'))
        .order_by('grade')
    )
    
    labels = [item['grade'] for item in grades if item['grade']]
    values = [item['count'] for item in grades if item['grade']]
    
    # Calculate pass/fail rates
    total_approved = Grade.objects.filter(status=Grade.STATUS_APPROVED).count()
    
    if total_approved > 0:
        # Get passing grade point threshold
        passing_grades = GradingSettings.objects.filter(grade_point__gt=0).values_list('grade_name', flat=True)
        pass_count = Grade.objects.filter(status=Grade.STATUS_APPROVED, grade__in=passing_grades).count()
        
        pass_rate = f"{(pass_count / total_approved * 100):.1f}%"
        fail_rate = f"{((total_approved - pass_count) / total_approved * 100):.1f}%"
    else:
        pass_rate = "0%"
        fail_rate = "0%"
    
    # Calculate average CGPA (simplified - just average of all grade points)
    grade_points = []
    for g in Grade.objects.filter(status=Grade.STATUS_APPROVED, grade__isnull=False):
        gs = GradingSettings.objects.filter(grade_name=g.grade).first()
        if gs:
            grade_points.append(gs.grade_point)
    
    avg_cgpa = f"{sum(grade_points) / len(grade_points):.2f}" if grade_points else "0.00"
    
    return JsonResponse({
        'labels': labels,
        'values': values,
        'avg_cgpa': avg_cgpa,
        'pass_rate': pass_rate,
        'fail_rate': fail_rate,
    })


@login_required
def recent_activity_partial(request):
    """Fetch recent activity for dashboard"""
    from django.utils.html import mark_safe
    from audit_log.models import LogEntry
    
    activities = []
    
    # Get recent enrollments (last 10)
    recent_enrollments = Enrollment.objects.select_related(
        'student', 'course_offering__course', 'course_offering__session'
    ).order_by('-enrollment_date')[:5]
    
    for enrollment in recent_enrollments:
        activities.append({
            'title': f'New Enrollment',
            'description': f'{enrollment.student.full_name} enrolled in {enrollment.course_offering.course.code}',
            'timestamp': enrollment.enrollment_date.strftime('%b %d, %Y'),
            'color_class': 'bg-gradient-to-br from-blue-500 to-indigo-500 text-white',
            'icon': mark_safe('<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>')
        })
    
    # Get recent grade submissions
    recent_grades = Grade.objects.filter(
        status=Grade.STATUS_SUBMITTED
    ).select_related('enrollment__student', 'enrollment__course_offering__course').order_by('-submitted_at')[:5]
    
    for grade in recent_grades:
        if grade.submitted_at:
            activities.append({
                'title': 'Grade Submitted',
                'description': f'{grade.enrollment.course_offering.course.code} - Awaiting approval',
                'timestamp': grade.submitted_at.strftime('%b %d, %Y %H:%M'),
                'color_class': 'bg-gradient-to-br from-amber-500 to-orange-500 text-white',
                'icon': mark_safe('<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>')
            })
    
    # Sort by timestamp (most recent first)
    activities = sorted(activities, key=lambda x: x['timestamp'], reverse=True)[:10]
    
    return render(request, 'portal/partials/activity_feed.html', {'activities': activities})


@login_required
def repeated_courses_alert_partial(request):
    """Widget showing students with repeated courses"""
    from django.db.models import Count
    
    # Get students with repeated courses (more than 1 enrollment in same course)
    repeats = (
        Enrollment.objects
        .values('student__student_id', 'student__first_name', 'student__last_name', 'course_offering__course__code')
        .annotate(attempts=Count('id'))
        .filter(attempts__gt=1)
        .order_by('-attempts')
    )
    
    # Count unique students with repeats
    students_with_repeats = len(set([r['student__student_id'] for r in repeats]))
    
    # Get top 5 most repeated courses
    top_repeated = (
        Enrollment.objects
        .values('course_offering__course__code', 'course_offering__course__title')
        .annotate(total_repeats=Count('student', distinct=True))
        .filter(total_repeats__gt=1)
        .order_by('-total_repeats')[:5]
    )
    
    ctx = {
        'students_with_repeats': students_with_repeats,
        'total_repeat_instances': len(repeats),
        'top_repeated_courses': top_repeated,
    }
    return render(request, 'portal/partials/repeated_courses_alert.html', ctx)


@login_required
def graduation_eligibility_partial(request):
    """Widget showing graduation eligibility preview"""
    from academics.graduation import audit_student_graduation
    from academics.models import Program
    
    # Get all students with programs
    students = Student.objects.filter(program__isnull=False).select_related('program')
    
    eligible_count = 0
    by_program = {}
    
    for student in students:
        result = audit_student_graduation(student)
        if result.eligible:
            eligible_count += 1
            program_code = student.program.code if student.program else 'Unknown'
            if program_code not in by_program:
                by_program[program_code] = 0
            by_program[program_code] += 1
    
    ctx = {
        'total_students': students.count(),
        'eligible_count': eligible_count,
        'by_program': sorted(by_program.items(), key=lambda x: x[1], reverse=True),
    }
    return render(request, 'portal/partials/graduation_eligibility.html', ctx)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('portal:dashboard')

        messages.error(request, 'Invalid username or password')

    return render(request, 'portal/login.html')


def logout_view(request):
    logout(request)
    return redirect('portal:login')
