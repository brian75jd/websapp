from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from chat.models import ChatRoom, Message
from chat.utils import get_room_name
import json
from django.db.models import Max

User = get_user_model()

@login_required
def start_chat(request,user_id):
    other_user = User.objects.get(id=user_id)
    room_name = get_room_name(request.user,other_user)
    room, created = ChatRoom.objects.get_or_create(
        name = room_name
    )
    room.users.add(request.user, other_user)

    return JsonResponse({
        'room_name':room.name
    })

@login_required
def chatView(request,room_name,user_id):
    user = User.objects.get(id=user_id)
    room = ChatRoom.objects.get(name=room_name)
    messages = Message.objects.filter(room = room).order_by('timestamp')
    message_data = [
        {
            'sender':msg.sender.username,
            'sender_id':msg.sender.id,
            'profile':msg.sender.photo.url,
            'message':msg.content,
            'time':msg.timestamp.strftime("%H:%M")
        }
        for msg in messages
    ]
    return render(request,'messages/chats.html',{
        'room_name':room_name,
        "user":user,
        'messages_json':json.dumps(message_data)
        })

@login_required
def ChatListOrdering(request):
    user = request.user
    chat_data = []

    rooms = ChatRoom.objects.filter(users=user).annotate(
        last_timestamp=Max('messages__timestamp')  # fix related name
    ).order_by('-last_timestamp')

    for room in rooms:
        other_user = room.users.exclude(id=user.id).first()
        last_message = Message.objects.filter(room=room).order_by('-timestamp').first()

        try:
            chat_data.append({
                'room_id': room.id,
                'user_id': other_user.id if other_user else None,
                'first_name': other_user.first_name if other_user else '',
                'last_name': other_user.last_name if other_user else '',
                'room_name': room.name,
                'photo': other_user.photo.url if other_user and other_user.photo else '',
                'last_message': last_message.content if last_message else "",
                'time': last_message.timestamp.strftime('%H:%M') if last_message else ''
            })
        except Exception as exp:
            return JsonResponse({'detail': str(exp)})

    return JsonResponse({'data_chat': chat_data})

@login_required
def Chat_List(request):
    return render(request,'messages/chat_list.html',{
    })
    
