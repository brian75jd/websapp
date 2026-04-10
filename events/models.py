from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
from django.utils import timezone

User = get_user_model()

class Event(models.Model):
    class EVENT_TYPE(models.TextChoices):
        SOCIAL = 'Social','Social'
        ACADEMIC = 'Academic','Academic'
        SPORTS = 'Sports','Sports'
        OTHER = 'Other','Other'
    
    title = models.CharField(max_length = 100)
    description = models.TextField()
    location = models.CharField(max_length=255)
    event_date = models.DateField(default=timezone.now)
    poster = models.ImageField(upload_to='events/posters/',null=True,blank=True)
    thumbnail = models.ImageField(upload_to='events/thumbnails/',null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    start_time = models.TimeField()
    finish_time = models.TimeField()
    event_type = models.CharField(max_length=200, choices=EVENT_TYPE,default=EVENT_TYPE.OTHER)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self,*args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if self.poster and is_new:
            try:
                img = Image.open(self.poster)
                if img.mode in ('RGBA','P'):
                    img = img.convert('RGB')
                
                main_img = img.copy()
                main_img.thumbnail((900,900))
                main_buffer = BytesIO()
                main_img.save(main_buffer,format='WEBP', quality=75)
                main_img = self.poster.name.split('.')[0] + ".webp"

                self.poster.save(
                    main_img,
                    ContentFile(main_buffer.getvalue()),
                    save=False
                )

                thumb_img = img.copy()
                thumb_img.thumbnail((300,300))
                thumb_buffer = BytesIO()
                thumb_img.save(thumb_img,format='WEBP', quality = 600)
                thumb_name = 'thumb_'+self.poster.name.split('/')[-1].split('.')[0]+".webp"

                self.thumbnail.save(
                    thumb_name,
                    ContentFile(thumb_buffer.getvalue()),
                    save = False
                )
                super().save(update_fields=['poster','thumbnail'])
            except Exception as e:
                print('Image processing failed',e)


    def __str__(self):
        return f"{self.title} posted on {self.created_at}"


class EventAttendance(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    event = models.ForeignKey(Event,on_delete=models.CASCADE)
    is_attending = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user','event'],name='unique event attendance')
        ]

    def __str__(self):
        return f"{self.user.username} plans to attend {self.event.title}"


