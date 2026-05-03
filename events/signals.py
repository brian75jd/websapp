from django.db.models.signals import post_delete
from django.dispatch import receiver
from events.models import Event


@receiver(post_delete, sender=Event)
def delete_event_images(sender, instance, **kwargs):
    if instance.poster:
        instance.poster.delete(save=False)

    if instance.thumbnail:
        instance.thumbnail.delete(save=False)