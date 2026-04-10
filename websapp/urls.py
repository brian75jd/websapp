
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('authuser.urls')),
    path('feed/',include('feed.urls')),
    path('events/',include('events.urls')),
    path('groups/',include('groups.urls')),
    path('profile/',include('ProfileManager.urls')),
    path('settings/',include('AppSettings.urls')),
    path('users/',include('usermanager.urls')),
    path('posts/',include('posts.urls')),
    path('notification/',include('notifications.urls')),
    path('chat/',include('chat.urls'))
]
