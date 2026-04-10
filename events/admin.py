from django.contrib import admin
from events.models import Event,EventAttendance

admin.site.register(Event)
admin.site.register(EventAttendance)
