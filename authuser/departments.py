from django.db import models

class Department(models.TextChoices):
    PHYSICS = 'Physics','Physics'

class FormDepartment:
    ('Physics','Physics')