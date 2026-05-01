from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomuserAdmin(UserAdmin):
    model = User

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info',{
            'fields':('phone_number','photo','department','date_of_birth','gender','cover_photo','last_active','is_organizer'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info',{
            "fields":('phone_number','department','gender','cover_photo')
        }),
    )
    list_display = ('username','email','phone_number','first_name','last_name','is_organizer','is_approved')

admin.site.register(User, CustomuserAdmin)