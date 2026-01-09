"""
Role-based access control decorators for views
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def has_role(user, role_name: str) -> bool:
    """
    Check if a user has a specific role.
    Uses both Role model and Django groups for backward compatibility.
    """
    if not user.is_authenticated:
        return False
    
    # Superusers always have all roles
    if user.is_superuser:
        return True
    
    # Admin: superuser or staff or has Admin role
    if role_name == 'Admin':
        if user.is_staff:
            return True
    
    # Check UserRole model
    from users.models import UserRole
    if UserRole.objects.filter(user=user, role__name=role_name).exists():
        return True
    
    # Fall back to Django groups
    if user.groups.filter(name=role_name).exists():
        return True
    
    # Special case: Teacher role via profile
    if role_name == 'Teacher':
        try:
            if hasattr(user, 'profile') and user.profile.teacher is not None:
                return True
        except Exception:
            pass
    
    return False


def get_user_roles(user) -> list:
    """Get all roles for a user"""
    if not user.is_authenticated:
        return []
    
    roles = set()
    
    # Check superuser/staff
    if user.is_superuser:
        roles.add('Superuser')
    if user.is_staff:
        roles.add('Admin')
    
    # Get from UserRole model
    from users.models import UserRole
    for ur in UserRole.objects.filter(user=user).select_related('role'):
        roles.add(ur.role.name)
    
    # Get from Django groups
    for group_name in user.groups.values_list('name', flat=True):
        roles.add(group_name)
    
    # Check Teacher via profile
    try:
        if hasattr(user, 'profile') and user.profile.teacher is not None:
            roles.add('Teacher')
    except Exception:
        pass
    
    return list(roles)


def role_required(*role_names):
    """
    Decorator to restrict access to users with specific roles.
    Superusers and staff always have access.
    
    Usage:
        @role_required('Admin', 'DataEntry')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            user = request.user
            
            # Superusers bypass all checks
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Staff have Admin role implicitly
            if user.is_staff and 'Admin' in role_names:
                return view_func(request, *args, **kwargs)
            
            # Check if user has any of the required roles
            if any(has_role(user, role) for role in role_names):
                return view_func(request, *args, **kwargs)
            
            # Access denied
            messages.error(request, f'Access denied. Required role: {" or ".join(role_names)}')
            return redirect('portal:dashboard')
        
        return wrapped_view
    return decorator


def admin_or_data_entry_required(view_func):
    """Shortcut decorator for Admin or DataEntry only"""
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.is_staff:
            return view_func(request, *args, **kwargs)
        if has_role(user, 'Admin') or has_role(user, 'DataEntry'):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Admin or Data Entry role required.')
        return redirect('portal:dashboard')
    return wrapped_view


def admin_required(view_func):
    """Shortcut decorator for Admin only"""
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.is_staff:
            return view_func(request, *args, **kwargs)
        if has_role(user, 'Admin'):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Administrator role required.')
        return redirect('portal:dashboard')
    return wrapped_view


def teacher_required(view_func):
    """Shortcut decorator for Teacher only (also allows Admin)"""
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.is_staff:
            return view_func(request, *args, **kwargs)
        if has_role(user, 'Teacher') or has_role(user, 'Admin'):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Teacher role required.')
        return redirect('portal:dashboard')
    return wrapped_view
