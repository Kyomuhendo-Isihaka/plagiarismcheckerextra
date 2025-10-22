from .models import Notification
import time

def notifications(request):
    """Add notification count to all templates"""
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        return {
            'unread_notifications_count': unread_count,
            'has_unread_notifications': unread_count > 0
        }
    return {
        'unread_notifications_count': 0,
        'has_unread_notifications': False
    }

def cache_buster(request):
    """Add timestamp for cache busting"""
    return {
        'timestamp': int(time.time())
    }