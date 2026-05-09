from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save
from APIS.models import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save,sender=User)
def create_api_keys(sender,instance,created, **kwargs):
    if created:
        APIClient.objects.create(
            user = instance
        )
        print('API keys generated')