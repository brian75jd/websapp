from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('authuser.urls')),
    path('feed/',include('feed.urls')),
    path('',include('events.urls')),
    path('groups/',include('groups.urls')),
    path('profile/',include('ProfileManager.urls')),
    path('settings/',include('AppSettings.urls')),
    path('users/',include('usermanager.urls')),
    path('posts/',include('posts.urls')),
    path('notification/',include('notifications.urls')),
    path('chat/',include('chat.urls')),
    path('payment/',include('payment.urls'))
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
