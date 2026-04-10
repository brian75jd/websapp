from AppSettings import views
from django.urls import path

app_name = 'appsettings'


urlpatterns = [
    path('',views.AppSettings,name='settings')
]