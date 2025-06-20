from .models import Notification

def unread_notifications_count(request):
    if request.user.is_authenticated:
        notifications_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    else:
        notifications_count = 0

    return {'unread_notifications_count':notifications_count}