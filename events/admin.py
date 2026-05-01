from django.contrib import admin
from events.models import Event,EventAttendance,Ticket,TicketType,Question



admin.site.register(Event)
admin.site.register(EventAttendance)
admin.site.register(Ticket)
admin.site.register(TicketType)
admin.site.register(Question)




