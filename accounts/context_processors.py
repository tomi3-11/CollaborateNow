from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')
        return {'unread_notifications': unread_notifications}
    return {'unread_notifications': []}