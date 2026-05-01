from notifications.models import Notification
from events.models import Event
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save
from notifications.services import send_notification


User = get_user_model()
@receiver(post_save, sender=Event)
def create_notification_on_event(sender,instance,created, **kwargs):
    if created:
        users = User.objects.all()
        print(instance)
        message = f"New event that you might be interested in was  uploaded. Check now"

        for user in users:
            send_notification(sender=None,receiver=user,notification_type='Event',
                              message=f"New event that you might be interested in was  uploaded. Check now")
