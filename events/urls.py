from django.urls import path
from events import views


app_name = 'events'

urlpatterns = [
    path('',views.Events,name='events'),
    path('get_events/',views.GetEvents,name='get_events')
]
