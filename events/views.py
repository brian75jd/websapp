from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from events.models import (Event, EventAttendance)

def Events(request):
    return render(request,template_name='pages/events.html')

@login_required
@require_GET
def GetEvents(request):
    events = Event.objects.all().order_by('-created_at')
    data = []

    for event in events:
        data.append({
            'id':event.id,
            'title':event.title,
            'description':event.description,
            'type':event.event_type,
            'location':event.location,
            'date':event.event_date,
            'start_at':event.start_time.strftime('%H:%M'),
            'finist_at':event.finish_time.strftime("%H:%M"),
            'poster':event.poster.url,
            'thumbnail':event.thumbnail.url if event.thumbnail else "",
        })
    
    return JsonResponse({'events':data})
