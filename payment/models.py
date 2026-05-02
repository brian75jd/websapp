from django.db import models
from events.models import Event

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    description = models.CharField(max_length=255,null=True,blank=True)
    phone = models.CharField(max_length=20,null=True,blank=True)
    event = models.ForeignKey(Event,on_delete=models.PROTECT,related_name='payments')
    tx_ref = models.CharField(max_length=100, unique=True)
    reference = models.CharField(max_length=100, unique=True, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='MWK')
    charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    email = models.EmailField(unique=False,null=True,blank=True)
    first_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100,null=True,blank=True)

    meta = models.JSONField(null=True, blank=True)

    payment_channel = models.CharField(max_length=50, null=True, blank=True)

    paid_at = models.DateTimeField(null=True, blank=True)
    created_at_gateway = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tx_ref} - {self.status}"