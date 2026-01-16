# applications/context_processors.py
 
from .models import Notification
 
def navbar_context(request):
    if request.user.is_authenticated and request.user.role == 'employer':
        notif_count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        notif_count = 0
    return {'notif_count': notif_count}