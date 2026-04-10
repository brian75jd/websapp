from django.urls import path
from usermanager import views

app_name = 'usermanager'

urlpatterns = [
    path('follow_user/',views.ToggleBtn,name='follow_user')
]
