from django.db import models
from django.contrib.auth.models import AbstractUser
from authuser.departments import Department
import uuid

class User(AbstractUser):
    class Gender(models.TextChoices):
        MALE = 'male','male',
        FEMALE = 'female','female',     
        
    phone_number = models.CharField(max_length=20,blank=True,null=True)
    photo = models.ImageField(upload_to = 'media/', blank=True, null=True)
    department = models.CharField(max_length=200,blank=True,null=True)
    date_of_birth = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=10, null=True,blank=True)
    cover_photo = models.ImageField(upload_to='covers/',blank=True, null=True)
    last_active = models.DateTimeField(null=True,blank=True)
    is_approved = models.BooleanField(default=False)
    name = models.CharField(max_length=255,blank=True,null=True)
    is_organizer = models.BooleanField(default=False)
    bio = models.CharField(max_length =300,null=True,blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['first_name','last_name','username']),

        ] 

