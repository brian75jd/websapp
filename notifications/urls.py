from notifications import views
from django.urls import path

app_name = 'notifications'

urlpatterns = [
    path('',views.NotificationView,name='notification'),
    path('search/',views.HandleSearch,name='search'),
    path('mark_read/',views.Mark_Read,name='mark_read'),

]
