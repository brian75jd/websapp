from django.urls import path
from chat import views

app_name = 'chat'
urlpatterns = [
    path('',views.Chat_List, name='chat_list'),
    path('start-chat/<int:user_id>/',views.start_chat,name='start-chat'),
    path('chat/<str:room_name>/<int:user_id>/',views.chatView,name='chat'),
    path('chat_oder/',views.ChatListOrdering,name='chat_oder')
    
]
