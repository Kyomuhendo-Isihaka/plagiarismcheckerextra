from django.utils.deprecation import MiddlewareMixin
from .models import UserProfile

class UserProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and not hasattr(request.user, '_profile_checked'):
            try:
                request.user.userprofile
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(
                    user=request.user,
                    role='individual' if not request.user.is_superuser else 'admin',
                    is_individual=not request.user.is_superuser
                )
            request.user._profile_checked = True
        return None