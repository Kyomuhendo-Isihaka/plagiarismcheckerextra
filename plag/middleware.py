from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    """Middleware for consistent error handling and user feedback"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Handle uncaught exceptions with user-friendly messages"""
        
        if isinstance(exception, PermissionDenied):
            messages.error(request, "You don't have permission to access this resource.")
            if request.user.is_authenticated:
                return redirect('plag:dashboard')
            else:
                return redirect('plag:login')
        
        # Log the error for debugging
        logger.error(f"Unhandled exception: {exception}", exc_info=True)
        
        # Don't handle in DEBUG mode - let Django show the error page
        from django.conf import settings
        if settings.DEBUG:
            return None
        
        # In production, show user-friendly error message
        messages.error(request, "An unexpected error occurred. Please try again.")
        
        if request.user.is_authenticated:
            return redirect('plag:dashboard')
        else:
            return redirect('plag:login')

class MessageCleanupMiddleware:
    """Middleware to clean up old messages and prevent message buildup"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Clean up messages after response (they should be consumed by templates)
        if hasattr(request, '_messages'):
            # Force consumption of messages to prevent buildup
            list(messages.get_messages(request))
        
        return response

class ProfileRequiredMiddleware:
    """Middleware to ensure authenticated users have role set"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that don't require profile check
        self.exempt_urls = [
            '/login/',
            '/logout/',
            '/register/',
            '/admin/',
            '/',
        ]

    def __call__(self, request):
        # Check if user needs profile
        if (request.user.is_authenticated and 
            not request.user.is_superuser and
            not any(request.path.startswith(url) for url in self.exempt_urls)):
            
            # Set default role if not set
            if not hasattr(request.user, 'role') or not request.user.role:
                request.user.role = 'individual'
                request.user.is_individual = True
                request.user.save()
        
        response = self.get_response(request)
        return response