from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import Teacher
from courses.models import Course, CourseOffering
from grading.models import Grade
from core.models import Department


@login_required
def teacher_list(request):
    """List all teachers with search and filters"""
    teachers = Teacher.objects.select_related('department').annotate(
        course_count=Count('courses', distinct=True)
    ).order_by('staff_id')
    
    # Search
    search_query = request.GET.get('search', '').strip()
    if search_query:
        teachers = teachers.filter(
            Q(staff_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'active':
        teachers = teachers.filter(is_active=True)
    elif status == 'inactive':
        teachers = teachers.filter(is_active=False)
    
    # Filter by department
    department_id = request.GET.get('department')
    if department_id:
        teachers = teachers.filter(department_id=department_id)
    
    # Pagination
    paginator = Paginator(teachers, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    departments = Department.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'departments': departments,
        'search_query': search_query,
        'total_count': teachers.count(),
    }
    
    return render(request, 'teachers/list.html', context)


@login_required
def teacher_detail(request, teacher_id):
    """View teacher details with courses and statistics"""
    teacher = get_object_or_404(
        Teacher.objects.annotate(
            course_count=Count('courses', distinct=True)
        ),
        id=teacher_id
    )
    
    # Get assigned courses
    courses = teacher.courses.all().order_by('code')
    
    # Get course offerings for courses assigned to this teacher
    offerings = CourseOffering.objects.filter(
        course__in=teacher.courses.all()
    ).select_related('course', 'session').order_by('-session__name')[:20]
    
    # Grade statistics
    passing_grades = ['A', 'B', 'C', 'D']
    total_grades = Grade.objects.filter(
        enrollment__course_offering__course__in=teacher.courses.all(),
        status='APPROVED'
    ).count()
    
    passed_grades = Grade.objects.filter(
        enrollment__course_offering__course__in=teacher.courses.all(),
        status='APPROVED',
        grade__in=passing_grades
    ).count()
    
    pass_rate = (passed_grades / total_grades * 100) if total_grades > 0 else 0
    
    context = {
        'teacher': teacher,
        'courses': courses,
        'offerings': offerings,
        'total_grades': total_grades,
        'pass_rate': round(pass_rate, 1),
    }
    
    return render(request, 'teachers/detail.html', context)


@login_required
def teacher_create(request):
    """Create a new teacher - Admin only"""
    from users.decorators import admin_required
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can create teachers.')
        return redirect('teachers:list')
    
    if request.method == 'POST':
        try:
            department_id = request.POST.get('department')
            department = None
            if department_id:
                department = Department.objects.filter(id=department_id).first()
            
            teacher = Teacher.objects.create(
                staff_id=request.POST.get('staff_id'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email') or None,
                phone=request.POST.get('phone', ''),
                department=department,
                is_active=request.POST.get('is_active') == 'on',
            )
            
            messages.success(request, f'Teacher {teacher.full_name} created successfully!')
            return redirect('teachers:detail', teacher_id=teacher.id)
        
        except Exception as e:
            messages.error(request, f'Error creating teacher: {str(e)}')
    
    departments = Department.objects.filter(is_active=True).order_by('name')
    context = {'departments': departments}
    return render(request, 'teachers/create.html', context)


@login_required
def teacher_edit(request, teacher_id):
    """Edit teacher details - Admin only"""
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can edit teachers.')
        return redirect('teachers:list')
    
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        try:
            department_id = request.POST.get('department')
            department = None
            if department_id:
                department = Department.objects.filter(id=department_id).first()
            
            teacher.staff_id = request.POST.get('staff_id')
            teacher.first_name = request.POST.get('first_name')
            teacher.last_name = request.POST.get('last_name')
            teacher.email = request.POST.get('email') or None
            teacher.phone = request.POST.get('phone', '')
            teacher.department = department
            teacher.is_active = request.POST.get('is_active') == 'on'
            teacher.save()
            
            messages.success(request, f'Teacher {teacher.full_name} updated successfully!')
            return redirect('teachers:detail', teacher_id=teacher.id)
        
        except Exception as e:
            messages.error(request, f'Error updating teacher: {str(e)}')
    
    departments = Department.objects.filter(is_active=True).order_by('name')
    context = {
        'teacher': teacher,
        'departments': departments,
    }
    return render(request, 'teachers/edit.html', context)


@login_required
def teacher_delete(request, teacher_id):
    """Delete teacher - Admin only"""
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can delete teachers.')
        return redirect('teachers:list')
    
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        teacher_name = teacher.full_name
        teacher.delete()
        messages.success(request, f'Teacher {teacher_name} deleted successfully!')
        return redirect('teachers:list')
    
    # For GET, redirect to detail with confirmation needed
    return redirect('teachers:detail', teacher_id=teacher_id)


@login_required
def assign_courses(request, teacher_id):
    """Assign courses to teacher - Admin only"""
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can assign courses.')
        return redirect('teachers:list')
    
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            course_ids = request.POST.getlist('course_ids')
            added = 0
            for course_id in course_ids:
                try:
                    course = Course.objects.get(id=course_id)
                    teacher.courses.add(course)
                    added += 1
                except Course.DoesNotExist:
                    pass
            
            if added > 0:
                messages.success(request, f'Assigned {added} course(s) to {teacher.full_name}.')
        
        elif action == 'remove':
            course_id = request.POST.get('course_id')
            try:
                course = Course.objects.get(id=course_id)
                teacher.courses.remove(course)
                messages.success(request, f'Removed {course.code} from {teacher.full_name}.')
            except Course.DoesNotExist:
                messages.error(request, 'Course not found.')
        
        return redirect('teachers:assign_courses', teacher_id=teacher.id)
    
    # GET - show form
    assigned_courses = teacher.courses.all().order_by('code')
    available_courses = Course.objects.exclude(id__in=assigned_courses).order_by('code')
    
    context = {
        'teacher': teacher,
        'assigned_courses': assigned_courses,
        'available_courses': available_courses,
    }
    
    return render(request, 'teachers/assign_courses.html', context)
