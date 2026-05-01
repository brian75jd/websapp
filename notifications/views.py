from django.shortcuts import render
from notifications.models import Notification
from posts.models import Post
from django.db.models import Q
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def NotificationView(request):
    notifications = Notification.objects.filter(
        receiver = request.user
    ).select_related('receiver').order_by('-created_at')[:15]
    notify_data = [
        {
            'id':note.id,
            'is_read':note.is_read,
            'first_name':note.sender.first_name if note.sender else '',
            'last_name':note.sender.last_name if note.sender else '',
            'date':note.created_at.strftime('%H:%M'),
            'notification':note.get_content(),
            'profile': note.sender.photo.url if note.sender and note.sender.photo else None

        }
        for note in notifications
    ]
    return render(request,'pages/notification.html',{
        'notify_data':json.dumps(notify_data)
    })


def HandleSearch(request):
    return render(request, template_name='pages/search_page.html')

@login_required
@require_POST
def Mark_Read(request):
    try:
        type = request.POST.get('type')
        note_id = request.POST.get('notificationId')
        notification = Notification.objects.get(id=note_id)
    except Notification.DoesNotExist:
        return JsonResponse({'detail':'Notification not found'})
    if type == 'unread':
        notification.is_read = True
        notification.save()
        return JsonResponse({'sucess':True})

    elif type == 'delete':
        notification.delete()
        return JsonResponse({'detail':'Notification deleted'})
        