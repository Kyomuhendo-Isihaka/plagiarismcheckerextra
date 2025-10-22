from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render as django_render
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def require_profile(view_func):
    """Decorator to ensure user has a profile"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            from .models import Profile
            Profile.objects.create(user=request.user, role='Individual', is_individual=True)
            messages.info(request, "Profile created. Please update your information if needed.")
        return view_func(request, *args, **kwargs)
    return wrapper

def require_role(allowed_roles):
    """Decorator to check user role permissions"""
    def decorator(view_func):
        @wraps(view_func)
        @require_profile
        def wrapper(request, *args, **kwargs):
            user_role = request.user.profile.role if hasattr(request.user, 'profile') else None
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if user_role not in allowed_roles:
                messages.error(request, f"Access denied. Required role: {', '.join(allowed_roles)}")
                return django_render(request, '403.html', status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def safe_redirect(request, redirect_url, success_message=None, error_message=None):
    """Safe redirect with message handling"""
    try:
        if success_message:
            messages.success(request, success_message)
        elif error_message:
            messages.error(request, error_message)
        return redirect(redirect_url)
    except Exception as e:
        logger.error(f"Redirect error: {e}")
        messages.error(request, "Navigation error occurred")
        return redirect('plag:dashboard')

def handle_form_errors(request, form_errors):
    """Handle form validation errors consistently"""
    for field, errors in form_errors.items():
        for error in errors:
            messages.error(request, f"{field.title()}: {error}")

def check_organization_access(user, target_user=None, target_org=None):
    """Check if user has access to organization data"""
    if user.is_superuser:
        return True
    
    if not hasattr(user, 'profile'):
        return False
    
    user_profile = user.profile
    
    # Individual users have no org access
    if user_profile.is_individual:
        return False
    
    # Check target user access
    if target_user and hasattr(target_user, 'profile'):
        if user_profile.organization != target_user.profile.organization:
            return False
    
    # Check target org access
    if target_org and user_profile.organization != target_org:
        return False
    
    return True

def get_user_context(user):
    """Get consistent user context for templates"""
    context = {'user': user}
    
    if hasattr(user, 'profile'):
        context.update({
            'user_role': user.profile.role,
            'is_individual': user.profile.is_individual,
            'organization': user.profile.organization,
        })
    
    return context

class MessageHandler:
    """Centralized message handling"""
    
    @staticmethod
    def success(request, message, extra_tags=''):
        messages.success(request, message, extra_tags=extra_tags)
    
    @staticmethod
    def error(request, message, extra_tags=''):
        messages.error(request, message, extra_tags=extra_tags)
    
    @staticmethod
    def warning(request, message, extra_tags=''):
        messages.warning(request, message, extra_tags=extra_tags)
    
    @staticmethod
    def info(request, message, extra_tags=''):
        messages.info(request, message, extra_tags=extra_tags)
    
    @staticmethod
    def login_success(request, user):
        messages.success(request, f"Welcome back, {user.first_name or user.username}!")
    
    @staticmethod
    def login_failed(request):
        messages.error(request, "Invalid username or password")
    
    @staticmethod
    def logout_success(request):
        messages.success(request, "You have been logged out successfully")
    
    @staticmethod
    def profile_updated(request):
        messages.success(request, "Profile updated successfully")
    
    @staticmethod
    def upload_success(request, filename=None):
        msg = f"File '{filename}' uploaded successfully" if filename else "File uploaded successfully"
        messages.success(request, msg)
    
    @staticmethod
    def upload_failed(request, reason=None):
        msg = f"Upload failed: {reason}" if reason else "File upload failed"
        messages.error(request, msg)
    
    @staticmethod
    def permission_denied(request, action="perform this action"):
        messages.error(request, f"You don't have permission to {action}")
    
    @staticmethod
    def ai_detected(request, risk_level="Medium"):
        messages.warning(request, f"⚠️ AI-generated content detected (Risk: {risk_level})")