from messaging import views
from django.urls import path

app_name = 'messaging'

urlpatterns = [
    path('',views.Chat_List, name='chat_list'),
    path('chat/',views.ChatView,name='chat')
]
