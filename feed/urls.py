from django.urls import path
from feed import views

app_name = 'feed'

urlpatterns = [
    path('', views.FeedView, name='feed'),
    path('prof/',views.Profile, name='profile'),
    path('get_posts/',views.Get_Posts, name='get_posts')
    
]
