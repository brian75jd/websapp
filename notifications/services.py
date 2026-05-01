from notifications.models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_notification(sender, receiver,notification_type,message):
    notification = Notification.objects.create(
        sender = sender,
        receiver = receiver,
        notification_type = notification_type
    )
    unread_count = Notification.objects.filter(
        receiver = receiver,
        is_read = False
    ).count()
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f'user_{receiver.id}',
        {
            'type':"send_notification",
            'data':{
            'sender':sender.username if sender else None,
            'message': message,
            'notification_type':notification_type,
            'profile':sender.photo.url if sender and sender.photo else None,
            'time':notification.created_at.strftime('%H:%M'),
            'unread_count':unread_count
            }
        }
    )
    
    return notification