from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files import File
from PIL import Image
from io import BytesIO
from django.utils import timezone
from datetime import datetime
import qrcode
import hashlib
import string
import uuid
import random
from django.db.models import Sum

User = get_user_model()

    
class Event(models.Model):
    class EVENT_TYPE(models.TextChoices):
        SOCIAL = 'social', 'Social'
        ACADEMIC = 'academic', 'Academic'
        SPORTS = 'sports', 'Sports'
        OTHER = 'other', 'Other'

    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=255)
    is_paid = models.BooleanField(default=False)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    
    organizer = models.ForeignKey(User,on_delete=models.CASCADE,related_name='events',
                                  null=True,blank=True)
    poster = models.ImageField(upload_to='events/posters/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='events/thumbnails/', null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE.choices,default=EVENT_TYPE.SOCIAL)
    is_promoted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        super().save(*args, **kwargs)

        if self.poster and is_new:
            try:
                img = Image.open(self.poster)

                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

            
                main_img = img.copy()
                main_img.thumbnail((900, 900))

                main_buffer = BytesIO()
                main_img.save(main_buffer, format='WEBP', quality=75)

                main_name = self.poster.name.split('.')[0] + ".webp"

                self.poster.save(
                    main_name,
                    ContentFile(main_buffer.getvalue()),
                    save=False
                )

                # 🔥 THUMBNAIL
                thumb_img = img.copy()
                thumb_img.thumbnail((300, 300))

                thumb_buffer = BytesIO()
                thumb_img.save(thumb_buffer, format='WEBP', quality=60)

                thumb_name = "thumb_" + self.poster.name.split('/')[-1].split('.')[0] + ".webp"

                self.thumbnail.save(
                    thumb_name,
                    ContentFile(thumb_buffer.getvalue()),
                    save=False
                )

                super().save(update_fields=['poster', 'thumbnail'])

            except Exception as e:
                print('Image processing failed:', e)

    @property
    def event_date(self):
        return self.start_datetime.date()
    @property
    def start_time(self):
        return self.start_datetime.time()

    @property
    def finish_time(self):
        return self.end_datetime.time()
    
    @property
    def total_tickets_left(self):
        return Sum([t.tickets_left() for t in self.ticket_types.all()])

    def __str__(self):
        return f"{self.title} ({self.start_datetime})"


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


class TicketType(models.Model):
    class TypeChoices(models.TextChoices):
        VIP = 'vip', 'VIP'
        STANDARD = 'standard', 'Standard'
        REGULAR = 'regular', 'Regular'
    
    capacity = models.PositiveIntegerField(default=10) 

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    type = models.CharField(max_length=20, choices=TypeChoices.choices)
    price = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['price']
        constraints = [
            models.UniqueConstraint(fields=['event', 'type'], name='unique_ticket_type_per_event')
        ]
    

    def tickets_sold(self):
        return self.tickets.aggregate(total=Sum('quantity'))['total'] or 0

    def tickets_left(self):
        return self.capacity - self.tickets_sold()

    def __str__(self):
        return f"{self.type} - {self.event.title}"


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    ticket_code = models.CharField(null=True,blank=True)

    tx_reference = models.CharField(null=True,blank=True)

    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.CASCADE,
        related_name='tickets',null=True,blank=True
    )

    quantity = models.PositiveIntegerField(default=1)

    is_paid = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)

    amount_paid = models.PositiveIntegerField()

    qr_code = models.CharField(max_length=255, unique=True, blank=True, default='')
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True,null=True)
    verified_by = models.ForeignKey(User,on_delete = models.CASCADE,null=True,blank=True)


    ticket_code = models.CharField(max_length=225, blank=True,null=True,default='',unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        print(args)
        print(kwargs)
        if not self.qr_code:
            raw = f"{self.id}{self.event_id}"
            self.qr_code = hashlib.sha256(raw.encode()).hexdigest()

        super().save(*args, **kwargs)


        if self.qr_code and not self.qr_image:
            url = f"https://kaylin-plumbic-luana.ngrok-free.dev/verify/{self.qr_code}/"

            qr = qrcode.make(url)

            buffer = BytesIO()
            qr.save(buffer, format='PNG')

            self.qr_image.save(
                f"ticket_{self.id}.png",
                File(buffer),
                save=False
            )

            super().save(update_fields=['qr_image'])


class Question(models.Model):
    event = models.ForeignKey(Event,on_delete=models.CASCADE,related_name='questions')
    question = models.TextField()
    answer = models.TextField(null=True, blank=True)
    is_answered = models.BooleanField(default=False)
    sender_email = models.EmailField(null=True,blank=True)

    created_at =models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"{self.question[:30]}" 




