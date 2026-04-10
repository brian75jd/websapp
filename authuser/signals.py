from django.db.models.signals import pre_save,post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import uuid

User = get_user_model()

def compress_image(image, quality=85, max_size = (800,800)):
    img = Image.open(image)
    if img.mode in ('RGBA','P'):
        img = img.convert('RGB')
    
    img.thumbnail(max_size)
    buffer = BytesIO()
    filename = f"{uuid.uuid4().hex}.jpg"
    img.save(buffer, format='JPEG',quality=quality, optimize=True)
    return ContentFile(buffer.getvalue(),name=filename)

@receiver(pre_save, sender=User)
def handle_user_images(sender,instance,**kwargs):
    #print('signal running!')
    if not instance.pk:
        for field in ['photo','cover_photo']:
            image = getattr(instance,field)
            if image:
                setattr(instance,field,compress_image(image))
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    for field in ['photo','cover_photo']:
       old_photo = getattr(old_instance,field)
       new_photo = getattr(instance,field)

       if old_photo and old_photo != new_photo:
            old_photo.delete(save=False)
            
       if new_photo and old_photo !=new_photo:
            setattr(instance,field,compress_image(new_photo))

@receiver(post_delete, sender=User)
def delete_profile_photo_on_user_deletion(sender,instance,**kwargs):
    for field in ['photo','cover_photo']:
        image = getattr(instance,field)
        if image:
            image.delete(save=False)