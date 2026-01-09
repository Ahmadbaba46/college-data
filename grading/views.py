from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count

from grading.models import Enrollment, Grade
from students.models import Student, Level, Session
from courses.models import Course, CourseOffering
from users.decorators import admin_or_data_entry_required, admin_required, role_required
from django.utils import timezone
from django.http import JsonResponse


@login_required
def enrollment_list(request):
    """
    List all enrollments with filters.
    All authenticated users can view.
    """
    enrollments = Enrollment.objects.select_related(
        'student',
        'course_offering__course',
        'course_offering__session'
    ).order_by('-enrollment_date')
    
    # Search by student
    search_query = request.GET.get('search', '').strip()
    if search_query:
        enrollments = enrollments.filter(
            Q(student__student_id__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query)
        )
    
    # Filter by session
    session_id = request.GET.get('session')
    if session_id:
        enrollments = enrollments.filter(course_offering__session_id=session_id)
    
    # Filter by course (multi-select)
    course_ids = request.GET.getlist('course')
    if course_ids:
        enrollments = enrollments.filter(course_offering__course_id__in=course_ids)
    
    # Pagination
    paginator = Paginator(enrollments, 30)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'sessions': Session.objects.all(),
        'courses': Course.objects.all()[:50],  # Limit for performance
        'search_query': search_query,
        'total_count': enrollments.count(),
    }
    
    return render(request, 'grading/enrollment_list.html', context)


@admin_or_data_entry_required
def enrollment_create(request):
    """
    Create single enrollment.
    Only Admin and DataEntry can access.
    """
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            offering_id = request.POST.get('course_offering')
            
            student = Student.objects.get(id=student_id)
            offering = CourseOffering.objects.get(id=offering_id)
            
            # Check if already enrolled
            if Enrollment.objects.filter(student=student, course_offering=offering).exists():
                messages.warning(request, f'{student.full_name} is already enrolled in {offering.course.code}')
                return redirect('grading:enrollment_create')
            
            # Create enrollment
            enrollment = Enrollment.objects.create(
                student=student,
                course_offering=offering,
                enrollment_date=request.POST.get('enrollment_date')
            )
            
            messages.success(request, f'Successfully enrolled {student.full_name} in {offering.course.code}')
            return redirect('grading:enrollment_list')
        
        except Exception as e:
            messages.error(request, f'Error creating enrollment: {str(e)}')
    
    context = {
        'students': Student.objects.all().order_by('student_id'),
        'offerings': CourseOffering.objects.filter(is_active=True).select_related('course', 'session').order_by('-session__name'),
    }
    
    return render(request, 'grading/enrollment_create.html', context)


@admin_or_data_entry_required
def enrollment_bulk(request):
    """
    Bulk enrollment interface.
    Only Admin and DataEntry can access.
    """
    if request.method == 'POST':
        try:
            offering_id = request.POST.get('course_offering')
            student_ids = request.POST.getlist('students')
            
            if not offering_id or not student_ids:
                messages.error(request, 'Please select course offering and at least one student')
                return redirect('grading:enrollment_bulk')
            
            offering = CourseOffering.objects.get(id=offering_id)
            enrolled_count = 0
            skipped_count = 0
            
            for student_id in student_ids:
                student = Student.objects.get(id=student_id)
                
                # Check if already enrolled
                if Enrollment.objects.filter(student=student, course_offering=offering).exists():
                    skipped_count += 1
                    continue
                
                Enrollment.objects.create(
                    student=student,
                    course_offering=offering
                )
                enrolled_count += 1
            
            messages.success(request, f'Enrolled {enrolled_count} students. Skipped {skipped_count} (already enrolled)')
            return redirect('grading:enrollment_list')
        
        except Exception as e:
            messages.error(request, f'Error in bulk enrollment: {str(e)}')
    
    # Get offerings with enrollment counts
    offerings = CourseOffering.objects.filter(
        is_active=True
    ).select_related('course', 'session').annotate(
        enrollment_count=Count('enrollment')
    ).order_by('-session__name')
    
    # Get students grouped by level
    students = Student.objects.select_related('current_level').order_by('current_level__name', 'student_id')
    
    context = {
        'offerings': offerings,
        'students': students,
        'levels': Level.objects.all(),
        'sessions': Session.objects.all(),
    }
    
    return render(request, 'grading/enrollment_bulk.html', context)


@role_required('Teacher', 'Admin')
def teacher_courses(request):
    """
    View teacher's assigned courses and offerings.
    Teachers can only see their own courses.
    """
    from teachers.models import Teacher
    
    # Get teacher profile
    teacher = None
    try:
        if hasattr(request.user, 'profile') and request.user.profile.teacher:
            teacher = request.user.profile.teacher
    except:
        messages.error(request, 'No teacher profile found for your account.')
        return redirect('portal:dashboard')
    
    if not teacher:
        messages.error(request, 'No teacher profile found for your account.')
        return redirect('portal:dashboard')
    
    # Get teacher's courses
    assigned_courses = teacher.courses.all()
    
    # Get active offerings for these courses
    offerings = CourseOffering.objects.filter(
        course__in=assigned_courses,
        is_active=True
    ).select_related('course', 'session').annotate(
        enrollment_count=Count('enrollment'),
        draft_count=Count('enrollment__grade', filter=Q(enrollment__grade__status=Grade.STATUS_DRAFT)),
        submitted_count=Count('enrollment__grade', filter=Q(enrollment__grade__status=Grade.STATUS_SUBMITTED)),
        approved_count=Count('enrollment__grade', filter=Q(enrollment__grade__status=Grade.STATUS_APPROVED))
    ).order_by('-session__name', 'course__code')
    
    ctx = {
        'teacher': teacher,
        'assigned_courses': assigned_courses,
        'offerings': offerings,
    }
    
    return render(request, 'grading/teacher_courses.html', ctx)


@role_required('Teacher', 'Admin')
def grade_entry(request, offering_id):
    """
    Grade entry page for a specific offering.
    Shows all enrolled students with inline grade editing.
    """
    offering = get_object_or_404(CourseOffering, id=offering_id)
    
    # Check if teacher has access (teachers can only access their assigned courses)
    if not request.user.is_staff:
        try:
            teacher = request.user.profile.teacher
            if offering.course not in teacher.courses.all():
                messages.error(request, 'You do not have access to this course.')
                return redirect('grading:teacher_courses')
        except:
            messages.error(request, 'No teacher profile found.')
            return redirect('portal:dashboard')
    
    # Handle grade updates via AJAX
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            enrollment_id = request.POST.get('enrollment_id')
            ca_score = float(request.POST.get('ca_score', 0))
            exam_score = float(request.POST.get('exam_score', 0))
            
            enrollment = Enrollment.objects.get(id=enrollment_id, course_offering=offering)
            
            # Get or create grade
            grade, created = Grade.objects.get_or_create(enrollment=enrollment)
            
            # Only allow editing if status is DRAFT or REJECTED
            if grade.status not in [Grade.STATUS_DRAFT, Grade.STATUS_REJECTED]:
                return JsonResponse({'success': False, 'error': 'Cannot edit submitted or approved grades'})
            
            grade.ca_score = ca_score
            grade.exam_score = exam_score
            grade.status = Grade.STATUS_DRAFT
            grade.save()
            
            return JsonResponse({
                'success': True,
                'total_score': grade.total_score,
                'grade': grade.grade
            })
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - show grade entry form
    enrollments = Enrollment.objects.filter(
        course_offering=offering
    ).select_related('student', 'student__current_level').order_by('student__student_id')
    
    # Get or create grades for all enrollments
    for enrollment in enrollments:
        if not hasattr(enrollment, 'grade'):
            Grade.objects.create(enrollment=enrollment)
    
    # Refresh to get grades
    enrollments = Enrollment.objects.filter(
        course_offering=offering
    ).select_related('student', 'student__current_level', 'grade').order_by('student__student_id')
    
    # Count grades by status
    total_students = enrollments.count()
    draft_count = enrollments.filter(grade__status=Grade.STATUS_DRAFT).count()
    submitted_count = enrollments.filter(grade__status=Grade.STATUS_SUBMITTED).count()
    approved_count = enrollments.filter(grade__status=Grade.STATUS_APPROVED).count()
    rejected_count = enrollments.filter(grade__status=Grade.STATUS_REJECTED).count()
    
    ctx = {
        'offering': offering,
        'enrollments': enrollments,
        'total_students': total_students,
        'draft_count': draft_count,
        'submitted_count': submitted_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'grading/grade_entry.html', ctx)


@role_required('Teacher', 'Admin')
def grade_submit(request, offering_id):
    """Submit all grades for an offering for approval"""
    if request.method != 'POST':
        return redirect('grading:grade_entry', offering_id=offering_id)
    
    offering = get_object_or_404(CourseOffering, id=offering_id)
    
    # Check teacher access
    if not request.user.is_staff:
        try:
            teacher = request.user.profile.teacher
            if offering.course not in teacher.courses.all():
                messages.error(request, 'You do not have access to this course.')
                return redirect('grading:teacher_courses')
        except:
            messages.error(request, 'No teacher profile found.')
            return redirect('portal:dashboard')
    
    # Get all draft or rejected grades for this offering
    grades = Grade.objects.filter(
        enrollment__course_offering=offering,
        status__in=[Grade.STATUS_DRAFT, Grade.STATUS_REJECTED]
    )
    
    if not grades.exists():
        messages.warning(request, 'No grades to submit.')
        return redirect('grading:grade_entry', offering_id=offering_id)
    
    # Submit all grades
    submitted_count = grades.update(
        status=Grade.STATUS_SUBMITTED,
        submitted_at=timezone.now()
    )
    
    messages.success(request, f'Successfully submitted {submitted_count} grade(s) for approval.')
    return redirect('grading:teacher_courses')


@admin_required
def approval_queue(request):
    """View all submitted grades pending approval"""
    # Get filter parameters
    session_id = request.GET.get('session')
    course_id = request.GET.get('course')
    
    # Get submitted grades
    grades = Grade.objects.filter(
        status=Grade.STATUS_SUBMITTED
    ).select_related(
        'enrollment__student',
        'enrollment__course_offering__course',
        'enrollment__course_offering__session'
    ).order_by(
        '-submitted_at',
        'enrollment__course_offering__course__code',
        'enrollment__student__student_id'
    )
    
    # Apply filters
    if session_id:
        grades = grades.filter(enrollment__course_offering__session_id=session_id)
    if course_id:
        grades = grades.filter(enrollment__course_offering__course_id=course_id)
    
    # Group by offering
    from itertools import groupby
    offerings_with_grades = []
    for offering_key, grade_list in groupby(grades, key=lambda g: g.enrollment.course_offering):
        grade_list = list(grade_list)
        offerings_with_grades.append({
            'offering': offering_key,
            'grades': grade_list,
            'count': len(grade_list)
        })
    
    ctx = {
        'offerings_with_grades': offerings_with_grades,
        'total_pending': grades.count(),
        'sessions': Session.objects.all(),
        'courses': Course.objects.all()[:50],
    }
    
    return render(request, 'grading/approval_queue.html', ctx)


@admin_required
def grade_approve(request, grade_id):
    """Approve a grade or all grades for an offering"""
    if request.method != 'POST':
        return redirect('grading:approval_queue')
    
    # Check if bulk approve for offering
    offering_id = request.POST.get('offering_id')
    
    if offering_id:
        # Bulk approve all submitted grades for this offering
        grades = Grade.objects.filter(
            enrollment__course_offering_id=offering_id,
            status=Grade.STATUS_SUBMITTED
        )
        
        count = grades.update(
            status=Grade.STATUS_APPROVED,
            approved_at=timezone.now(),
            approved_by=request.user
        )
        
        messages.success(request, f'Approved {count} grade(s).')
    else:
        # Single grade approval
        grade = get_object_or_404(Grade, id=grade_id)
        
        if grade.status != Grade.STATUS_SUBMITTED:
            messages.error(request, 'Only submitted grades can be approved.')
            return redirect('grading:approval_queue')
        
        grade.status = Grade.STATUS_APPROVED
        grade.approved_at = timezone.now()
        grade.approved_by = request.user
        grade.save()
        
        messages.success(request, 'Grade approved successfully.')
    
    return redirect('grading:approval_queue')


@admin_required
def grade_reject(request, grade_id):
    """Reject a grade with reason"""
    if request.method != 'POST':
        return redirect('grading:approval_queue')
    
    grade = get_object_or_404(Grade, id=grade_id)
    
    if grade.status != Grade.STATUS_SUBMITTED:
        messages.error(request, 'Only submitted grades can be rejected.')
        return redirect('grading:approval_queue')
    
    rejection_reason = request.POST.get('rejection_reason', '').strip()
    if not rejection_reason:
        messages.error(request, 'Please provide a rejection reason.')
        return redirect('grading:approval_queue')
    
    grade.status = Grade.STATUS_REJECTED
    grade.rejection_reason = rejection_reason
    grade.save()
    
    messages.success(request, 'Grade rejected. Teacher can revise and resubmit.')
    return redirect('grading:approval_queue')


@login_required
def grade_history(request):
    """View grade change history for a student or course"""
    student_id = request.GET.get('student_id')
    course_id = request.GET.get('course_id')
    offering_id = request.GET.get('offering_id')
    
    grades = Grade.objects.select_related(
        'enrollment__student',
        'enrollment__course_offering__course',
        'enrollment__course_offering__session',
        'approved_by'
    ).order_by('-approved_at', '-submitted_at')
    
    # Apply filters
    if student_id:
        grades = grades.filter(enrollment__student__student_id=student_id)
    if course_id:
        grades = grades.filter(enrollment__course_offering__course_id=course_id)
    if offering_id:
        grades = grades.filter(enrollment__course_offering_id=offering_id)
    
    # Only show non-draft grades
    grades = grades.exclude(status=Grade.STATUS_DRAFT)
    
    # Get filter options
    students = Student.objects.all().order_by('student_id')[:100]
    courses = Course.objects.all().order_by('code')[:50]
    
    ctx = {
        'grades': grades[:200],  # Limit to recent 200
        'students': students,
        'courses': courses,
        'selected_student_id': student_id,
        'selected_course_id': course_id,
    }
    
    return render(request, 'grading/grade_history.html', ctx)


@login_required
def repeated_courses_report(request):
    """
    Show students who have repeated courses with GPA impact analysis.
    """
    from django.db.models import Count, Q, Avg, F
    from grading.repeat_policy import get_repeat_policy
    
    # Get students with repeated enrollments
    repeated_enrollments = (
        Enrollment.objects
        .values('student', 'course_offering__course')
        .annotate(
            attempt_count=Count('id'),
            student_id_display=F('student__student_id'),
            student_name=F('student__first_name'),
            course_code=F('course_offering__course__code'),
            course_title=F('course_offering__course__title')
        )
        .filter(attempt_count__gt=1)
        .order_by('-attempt_count', 'student__student_id')
    )
    
    # Build detailed repeat data
    repeat_data = []
    for item in repeated_enrollments:
        student = Student.objects.get(id=item['student'])
        course = Course.objects.get(id=item['course_offering__course'])
        
        # Get all enrollments for this student-course combination
        enrollments = Enrollment.objects.filter(
            student=student,
            course_offering__course=course
        ).select_related('course_offering__session', 'grade').order_by('enrollment_date')
        
        attempts = []
        for enrollment in enrollments:
            if hasattr(enrollment, 'grade'):
                attempts.append({
                    'session': enrollment.course_offering.session.name,
                    'semester': enrollment.course_offering.get_semester_display(),
                    'total_score': enrollment.grade.total_score,
                    'grade': enrollment.grade.grade,
                    'status': enrollment.grade.get_status_display(),
                })
        
        repeat_data.append({
            'student': student,
            'course': course,
            'attempt_count': item['attempt_count'],
            'attempts': attempts,
        })
    
    # Get repeat policy info
    repeat_policy = get_repeat_policy()
    
    # Statistics
    total_students_with_repeats = len(set([item['student'].id for item in repeat_data]))
    total_repeat_instances = len(repeat_data)
    
    # Most repeated courses
    course_repeat_counts = {}
    for item in repeat_data:
        course_code = item['course'].code
        if course_code not in course_repeat_counts:
            course_repeat_counts[course_code] = {
                'course': item['course'],
                'count': 0
            }
        course_repeat_counts[course_code]['count'] += 1
    
    top_repeated = sorted(
        course_repeat_counts.values(),
        key=lambda x: x['count'],
        reverse=True
    )[:10]
    
    ctx = {
        'repeat_data': repeat_data[:100],  # Limit display
        'total_students_with_repeats': total_students_with_repeats,
        'total_repeat_instances': total_repeat_instances,
        'top_repeated_courses': top_repeated,
        'repeat_policy': repeat_policy,
    }
    
    return render(request, 'grading/repeated_courses_report.html', ctx)
