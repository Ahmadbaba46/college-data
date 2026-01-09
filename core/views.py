from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from students.models import Session, Level
from core.models import Department
from configuration.models import CollegeSettings, AcademicPolicySettings
from grading.models import GradingSettings


# ============== SESSIONS ==============

@login_required
def session_list(request):
    """List all sessions - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage sessions.')
        return redirect('portal:dashboard')
    
    sessions = Session.objects.all().order_by('-name')
    
    context = {
        'sessions': sessions,
    }
    return render(request, 'core/sessions/list.html', context)


@login_required
def session_create(request):
    """Create new session - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can create sessions.')
        return redirect('core:session_list')
    
    if request.method == 'POST':
        try:
            is_current = request.POST.get('is_current') == 'on'
            Session.objects.create(
                name=request.POST.get('name'),
                is_current=is_current
            )
            messages.success(request, 'Session created successfully!')
            return redirect('core:session_list')
        except Exception as e:
            messages.error(request, f'Error creating session: {str(e)}')
    
    return render(request, 'core/sessions/create.html')


@login_required
def session_edit(request, session_id):
    """Edit session - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can edit sessions.')
        return redirect('core:session_list')
    
    session = get_object_or_404(Session, id=session_id)
    
    if request.method == 'POST':
        try:
            session.name = request.POST.get('name')
            session.is_current = request.POST.get('is_current') == 'on'
            session.save()
            messages.success(request, 'Session updated successfully!')
            return redirect('core:session_list')
        except Exception as e:
            messages.error(request, f'Error updating session: {str(e)}')
    
    context = {'session': session}
    return render(request, 'core/sessions/edit.html', context)


@login_required
def session_set_current(request, session_id):
    """Set a session as current - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can change session status.')
        return redirect('core:session_list')
    
    if request.method == 'POST':
        session = get_object_or_404(Session, id=session_id)
        session.is_current = True
        session.save()
        messages.success(request, f'Session "{session.name}" is now the current session.')
    
    return redirect('core:session_list')


@login_required
def session_delete(request, session_id):
    """Delete session - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can delete sessions.')
        return redirect('core:session_list')
    
    session = get_object_or_404(Session, id=session_id)
    
    if request.method == 'POST':
        session_name = session.name
        session.delete()
        messages.success(request, f'Session {session_name} deleted successfully!')
        return redirect('core:session_list')
    
    return redirect('core:session_list')


# ============== LEVELS ==============

@login_required
def level_list(request):
    """List all levels - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage levels.')
        return redirect('portal:dashboard')
    
    from django.db.models import Count
    
    levels = Level.objects.annotate(
        student_count=Count('student', distinct=True)
    ).order_by('order', 'name')
    
    context = {
        'levels': levels,
    }
    return render(request, 'core/levels/list.html', context)


@login_required
def level_create(request):
    """Create new level - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can create levels.')
        return redirect('core:level_list')
    
    if request.method == 'POST':
        try:
            Level.objects.create(
                name=request.POST.get('name')
            )
            messages.success(request, 'Level created successfully!')
            return redirect('core:level_list')
        except Exception as e:
            messages.error(request, f'Error creating level: {str(e)}')
    
    return render(request, 'core/levels/create.html')


@login_required
def level_edit(request, level_id):
    """Edit level - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can edit levels.')
        return redirect('core:level_list')
    
    level = get_object_or_404(Level, id=level_id)
    
    if request.method == 'POST':
        try:
            level.name = request.POST.get('name')
            level.save()
            messages.success(request, 'Level updated successfully!')
            return redirect('core:level_list')
        except Exception as e:
            messages.error(request, f'Error updating level: {str(e)}')
    
    context = {'level': level}
    return render(request, 'core/levels/edit.html', context)


@login_required
def level_delete(request, level_id):
    """Delete level - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can delete levels.')
        return redirect('core:level_list')
    
    level = get_object_or_404(Level, id=level_id)
    
    if request.method == 'POST':
        level_name = level.name
        level.delete()
        messages.success(request, f'Level {level_name} deleted successfully!')
        return redirect('core:level_list')
    
    return redirect('core:level_list')


# ============== DEPARTMENTS ==============

@login_required
def department_list(request):
    """List all departments - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage departments.')
        return redirect('portal:dashboard')
    
    from teachers.models import Teacher
    from academics.models import Program
    from courses.models import Course
    from django.db.models import Count
    
    # Use annotation for counts - department is now a FK
    departments = Department.objects.annotate(
        teacher_count=Count('teachers', distinct=True),
        program_count=Count('programs', distinct=True),
        course_count=Count('courses', distinct=True),
    ).order_by('name')
    
    context = {
        'departments': departments,
    }
    return render(request, 'core/departments/list.html', context)


@login_required
def department_detail(request, department_id):
    """View department details with teachers, programs, courses"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can view department details.')
        return redirect('portal:dashboard')
    
    from teachers.models import Teacher
    from academics.models import Program
    from courses.models import Course
    
    department = get_object_or_404(Department, id=department_id)
    
    teachers = Teacher.objects.filter(department=department).order_by('last_name', 'first_name')
    programs = Program.objects.filter(department=department).order_by('code')
    courses = Course.objects.filter(department=department).order_by('code')
    
    context = {
        'department': department,
        'teachers': teachers,
        'programs': programs,
        'courses': courses,
    }
    return render(request, 'core/departments/detail.html', context)


@login_required
def department_create(request):
    """Create new department - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can create departments.')
        return redirect('core:department_list')
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip() or None
            description = request.POST.get('description', '').strip() or None
            head_name = request.POST.get('head_name', '').strip() or None
            is_active = request.POST.get('is_active') == 'on'
            
            if not name:
                messages.error(request, 'Department name is required.')
                return render(request, 'core/departments/create.html')
            
            Department.objects.create(
                name=name,
                code=code,
                description=description,
                head_name=head_name,
                is_active=is_active
            )
            messages.success(request, f'Department "{name}" created successfully!')
            return redirect('core:department_list')
        except Exception as e:
            messages.error(request, f'Error creating department: {str(e)}')
    
    return render(request, 'core/departments/create.html')


@login_required
def department_edit(request, department_id):
    """Edit department - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can edit departments.')
        return redirect('core:department_list')
    
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        try:
            department.name = request.POST.get('name', '').strip()
            department.code = request.POST.get('code', '').strip() or None
            department.description = request.POST.get('description', '').strip() or None
            department.head_name = request.POST.get('head_name', '').strip() or None
            department.is_active = request.POST.get('is_active') == 'on'
            
            if not department.name:
                messages.error(request, 'Department name is required.')
                return render(request, 'core/departments/edit.html', {'department': department})
            
            department.save()
            messages.success(request, f'Department "{department.name}" updated successfully!')
            return redirect('core:department_list')
        except Exception as e:
            messages.error(request, f'Error updating department: {str(e)}')
    
    context = {'department': department}
    return render(request, 'core/departments/edit.html', context)


@login_required
def department_delete(request, department_id):
    """Delete department - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can delete departments.')
        return redirect('core:department_list')
    
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        dept_name = department.name
        department.delete()
        messages.success(request, f'Department "{dept_name}" deleted successfully!')
        return redirect('core:department_list')
    
    return redirect('core:department_list')


# ============== COLLEGE SETTINGS ==============

@login_required
def college_settings(request):
    """View and edit college settings - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage college settings.')
        return redirect('portal:dashboard')
    
    # Get or create college settings (singleton pattern)
    settings, created = CollegeSettings.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        try:
            settings.college_name = request.POST.get('college_name', '')
            settings.college_address = request.POST.get('college_address', '')
            settings.college_phone = request.POST.get('college_phone', '')
            settings.college_email = request.POST.get('college_email', '')
            settings.college_website = request.POST.get('college_website', '')
            settings.college_motto = request.POST.get('college_motto', '')
            settings.registrar_name = request.POST.get('registrar_name', '')
            settings.registrar_title = request.POST.get('registrar_title', '')
            
            # Handle file uploads
            if 'college_logo' in request.FILES:
                settings.college_logo = request.FILES['college_logo']
            if 'registrar_signature' in request.FILES:
                settings.registrar_signature = request.FILES['registrar_signature']
            
            settings.save()
            messages.success(request, 'College settings updated successfully!')
            return redirect('core:college_settings')
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
    
    context = {'settings': settings}
    return render(request, 'core/settings/college.html', context)


# ============== ACADEMIC POLICY SETTINGS ==============

@login_required
def academic_policy_settings(request):
    """View and edit academic policy settings - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage academic policy.')
        return redirect('portal:dashboard')
    
    # Get or create academic policy settings (singleton pattern)
    policy, _created = AcademicPolicySettings.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        try:
            # Repeat policy (matches configuration.models.AcademicPolicySettings)
            policy.repeat_policy = request.POST.get('repeat_policy', AcademicPolicySettings.REPEAT_ALL)

            # Approval enforcement flags (matches model fields)
            policy.require_approved_for_transcripts = request.POST.get('require_approved_for_transcripts') == 'on'
            policy.require_approved_for_exports = request.POST.get('require_approved_for_exports') == 'on'
            policy.require_approved_for_metrics = request.POST.get('require_approved_for_metrics') == 'on'

            policy.save()
            messages.success(request, 'Academic policy settings updated successfully!')
            return redirect('core:academic_policy_settings')
        except Exception as e:
            messages.error(request, f'Error updating policy: {str(e)}')
    
    context = {
        'policy': policy,
        'repeat_policy_choices': AcademicPolicySettings.REPEAT_POLICY_CHOICES,
    }
    return render(request, 'core/settings/academic_policy.html', context)


# ============== GRADING SETTINGS ==============

@login_required
def grading_settings(request):
    """View and edit grading scale settings - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage grading settings.')
        return redirect('portal:dashboard')
    
    grades = GradingSettings.objects.all().order_by('-min_score')
    
    context = {'grades': grades}
    return render(request, 'core/settings/grading.html', context)


@login_required
def grading_settings_edit(request, grade_id):
    """Edit a single grading setting - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage grading settings.')
        return redirect('core:grading_settings')
    
    grade = get_object_or_404(GradingSettings, id=grade_id)
    
    if request.method == 'POST':
        try:
            grade.min_score = float(request.POST.get('min_score', 0))
            grade.max_score = float(request.POST.get('max_score', 100))
            grade.grade_name = request.POST.get('grade', '')
            grade_point_str = request.POST.get('grade_point', '').strip()
            grade_point = float(grade_point_str) if grade_point_str else 0.0
            if grade_point < 0 or grade_point > 5.0:
                raise ValueError('Grade point must be between 0.0 and 5.0')
            grade.grade_point = grade_point
            grade.save()
            messages.success(request, f'Grade {grade.grade_name} updated successfully!')
            return redirect('core:grading_settings')
        except Exception as e:
            messages.error(request, f'Error updating grade: {str(e)}')
    
    context = {'grade': grade}
    return render(request, 'core/settings/grading_edit.html', context)


@login_required
def grading_settings_create(request):
    """Create a new grading setting - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage grading settings.')
        return redirect('core:grading_settings')
    
    if request.method == 'POST':
        try:
            grade_point_str = request.POST.get('grade_point', '').strip()
            grade_point = float(grade_point_str) if grade_point_str else 0.0
            if grade_point < 0 or grade_point > 5.0:
                raise ValueError('Grade point must be between 0.0 and 5.0')
            GradingSettings.objects.create(
                min_score=float(request.POST.get('min_score', 0)),
                max_score=float(request.POST.get('max_score', 100)),
                grade_name=request.POST.get('grade', ''),
                grade_point=grade_point,
            )
            messages.success(request, 'Grade scale added successfully!')
            return redirect('core:grading_settings')
        except Exception as e:
            messages.error(request, f'Error creating grade: {str(e)}')
    
    return render(request, 'core/settings/grading_create.html')


@login_required
def grading_settings_delete(request, grade_id):
    """Delete a grading setting - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage grading settings.')
        return redirect('core:grading_settings')
    
    grade = get_object_or_404(GradingSettings, id=grade_id)
    
    if request.method == 'POST':
        grade_name = grade.grade
        grade.delete()
        messages.success(request, f'Grade {grade_name} deleted successfully!')
    
    return redirect('core:grading_settings')


# ============== USER MANAGEMENT ==============

@login_required
def user_list(request):
    """List all users - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage users.')
        return redirect('portal:dashboard')
    
    from django.contrib.auth import get_user_model
    from users.models import Role, UserRole
    
    User = get_user_model()
    users = list(User.objects.all().order_by('username'))
    
    # Search
    search_query = request.GET.get('search', '').strip()
    if search_query:
        from django.db.models import Q
        users = list(User.objects.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        ).order_by('username'))
    
    # Get roles for display - build a dict of user_id -> role names
    user_roles = {}
    for ur in UserRole.objects.select_related('user', 'role').all():
        if ur.user_id not in user_roles:
            user_roles[ur.user_id] = []
        user_roles[ur.user_id].append(ur.role.name)
    
    # Add role_names attribute to each user for easy template access
    for user in users:
        user.role_names = user_roles.get(user.id, [])
    
    roles = Role.objects.all()
    
    context = {
        'users': users,
        'roles': roles,
        'search_query': search_query,
    }
    return render(request, 'core/settings/users.html', context)


@login_required
def user_edit(request, user_id):
    """Edit user roles - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage users.')
        return redirect('core:user_list')
    
    from django.contrib.auth import get_user_model
    from users.models import Role, UserRole
    
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    roles = Role.objects.all()
    current_roles = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
    
    if request.method == 'POST':
        try:
            # Update basic info
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.is_active = request.POST.get('is_active') == 'on'
            user.is_staff = request.POST.get('is_staff') == 'on'
            user.save()
            
            # Update roles
            selected_roles = request.POST.getlist('roles')
            UserRole.objects.filter(user=user).delete()
            for role_id in selected_roles:
                role = Role.objects.get(id=role_id)
                UserRole.objects.create(user=user, role=role)
            
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('core:user_list')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    context = {
        'edit_user': user,
        'roles': roles,
        'current_roles': list(current_roles),
    }
    return render(request, 'core/settings/user_edit.html', context)


# ============== AUDIT LOG ==============

@login_required
def audit_log(request):
    """View audit log entries - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can view audit logs.')
        return redirect('portal:dashboard')
    
    from audit_log.models import LogEntry
    from django.core.paginator import Paginator
    from datetime import datetime
    
    logs = LogEntry.objects.select_related('user').order_by('-timestamp')
    
    # Filter by action type
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    # Filter by user
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        try:
            logs = logs.filter(timestamp__date__gte=date_from)
        except ValueError:
            pass
    if date_to:
        try:
            logs = logs.filter(timestamp__date__lte=date_to)
        except ValueError:
            pass
    
    # Search in details
    search = request.GET.get('search', '').strip()
    if search:
        from django.db.models import Q
        logs = logs.filter(
            Q(details__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get action choices and users for filters
    from django.contrib.auth import get_user_model
    User = get_user_model()
    action_choices = LogEntry.ACTION_CHOICES if hasattr(LogEntry, 'ACTION_CHOICES') else []
    
    context = {
        'page_obj': page_obj,
        'action_choices': action_choices,
        'users': User.objects.all().order_by('username'),
        'total_count': logs.count(),
    }
    return render(request, 'core/settings/audit_log.html', context)


@login_required
def audit_log_export(request):
    """Export audit log to CSV - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can export audit logs.')
        return redirect('portal:dashboard')
    
    import csv
    from django.http import HttpResponse
    from audit_log.models import LogEntry
    
    logs = LogEntry.objects.select_related('user').order_by('-timestamp')
    
    # Apply same filters as the view
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        try:
            logs = logs.filter(timestamp__date__gte=date_from)
        except ValueError:
            pass
    if date_to:
        try:
            logs = logs.filter(timestamp__date__lte=date_to)
        except ValueError:
            pass
    
    search = request.GET.get('search', '').strip()
    if search:
        from django.db.models import Q
        logs = logs.filter(
            Q(details__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_log.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'User', 'Action', 'Details'])
    
    for log in logs[:5000]:  # Limit to 5000 rows
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.user.username if log.user else 'System',
            log.get_action_display() if hasattr(log, 'get_action_display') else log.action,
            log.details or '',
        ])
    
    return response
