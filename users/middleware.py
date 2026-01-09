"""
Security and session management middleware
"""
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta


class SessionSecurityMiddleware:
    """
    Middleware for enhanced session security:
    - Session timeout after inactivity
    - Track session metadata
    - Limit concurrent sessions (optional)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Session timeout in minutes (default 30)
        self.timeout_minutes = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 30)
        # Max concurrent sessions per user (0 = unlimited)
        self.max_sessions = getattr(settings, 'MAX_CONCURRENT_SESSIONS', 0)
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Check session timeout
            if self._check_session_timeout(request):
                logout(request)
                messages.warning(request, 'Your session has expired due to inactivity. Please log in again.')
                return redirect('portal:login')
            
            # Update last activity
            request.session['last_activity'] = timezone.now().isoformat()
            
            # Track session if enabled
            if hasattr(settings, 'TRACK_USER_SESSIONS') and settings.TRACK_USER_SESSIONS:
                self._track_session(request)
        
        response = self.get_response(request)
        return response
    
    def _check_session_timeout(self, request):
        """Check if the session has timed out"""
        last_activity = request.session.get('last_activity')
        if last_activity:
            try:
                from datetime import datetime
                last = datetime.fromisoformat(last_activity)
                if timezone.is_naive(last):
                    last = timezone.make_aware(last)
                timeout = timedelta(minutes=self.timeout_minutes)
                if timezone.now() - last > timeout:
                    return True
            except (ValueError, TypeError):
                pass
        return False
    
    def _track_session(self, request):
        """Track user session for security monitoring"""
        from users.models import UserSession
        
        session_key = request.session.session_key
        if not session_key:
            return
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        # Update or create session record
        UserSession.objects.update_or_create(
            session_key=session_key,
            defaults={
                'user': request.user,
                'ip_address': ip,
                'user_agent': user_agent,
                'is_active': True,
            }
        )
        
        # Enforce max sessions if configured
        if self.max_sessions > 0:
            user_sessions = UserSession.objects.filter(
                user=request.user,
                is_active=True
            ).order_by('-last_activity')
            
            # Deactivate older sessions beyond the limit
            sessions_to_deactivate = user_sessions[self.max_sessions:]
            if sessions_to_deactivate:
                from django.contrib.sessions.models import Session
                for old_session in sessions_to_deactivate:
                    old_session.is_active = False
                    old_session.save()
                    # Also delete the Django session
                    try:
                        Session.objects.filter(session_key=old_session.session_key).delete()
                    except Exception:
                        pass


class DataPrivacyMiddleware:
    """
    Middleware to handle data privacy concerns:
    - Add security headers
    - Log sensitive data access
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Prevent caching of sensitive pages
        if request.user.is_authenticated:
            if any(path in request.path for path in ['/settings/', '/admin/', '/users/']):
                response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
                response['Pragma'] = 'no-cache'
        
        return response
