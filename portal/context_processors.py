import os

from django.conf import settings


def static_versions(request):
    """Provide cache-busting versions for static assets."""
    css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'app.css')
    try:
        v = str(int(os.path.getmtime(css_path)))
    except OSError:
        v = '0'
    return {'APP_CSS_VERSION': v}


def debug_mode(request):
    """Provide DEBUG flag to templates for conditional rendering."""
    return {'debug': settings.DEBUG}


def user_role(request):
    """Provide user role information to templates."""
    user = request.user
    context = {
        'is_admin': False,
        'is_teacher': False,
        'is_data_entry': False,
        'user_roles': [],
    }
    
    if user.is_authenticated:
        # Superusers and staff are admins
        if user.is_superuser or user.is_staff:
            context['is_admin'] = True
            context['is_data_entry'] = True  # Admins can do data entry
        
        # Check UserRole model
        from users.models import UserRole
        user_role_names = set(UserRole.objects.filter(user=user).values_list('role__name', flat=True))
        
        # Also check Django groups for backward compatibility
        user_groups = set(user.groups.values_list('name', flat=True))
        all_roles = user_role_names | user_groups
        
        if 'Admin' in all_roles:
            context['is_admin'] = True
            context['is_data_entry'] = True
        if 'DataEntry' in all_roles:
            context['is_data_entry'] = True
        if 'Teacher' in all_roles:
            context['is_teacher'] = True
        
        # Check Teacher via profile
        try:
            if hasattr(user, 'profile') and user.profile.teacher is not None:
                context['is_teacher'] = True
                all_roles.add('Teacher')
        except Exception:
            pass
        
        context['user_roles'] = list(all_roles)
    
    return context
