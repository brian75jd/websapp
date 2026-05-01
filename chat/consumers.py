from channels.generic.websocket import AsyncWebsocketConsumer
import json
from chat.models import Message, ChatRoom
from channels.db import database_sync_to_async
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    active_connections = {} 

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        user = self.scope["user"]
        if user.is_authenticated:
            # Increment active connections
            ChatConsumer.active_connections[user.username] = ChatConsumer.active_connections.get(user.username, 0) + 1

            # Only broadcast online if this is the first connection
            if ChatConsumer.active_connections[user.username] == 1:
                await self.update_last_active(user)
                await self.broadcast_presence(user, online=True)
                print(self.active_connections)

    async def disconnect(self, close_code):
        user = self.scope["user"]
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        if user.is_authenticated:
            # Decrement active connections
            ChatConsumer.active_connections[user.username] -= 1

            # Only broadcast offline if no more active connections
            if ChatConsumer.active_connections[user.username] == 0:
                await self.broadcast_presence(user, online=False)
                del ChatConsumer.active_connections[user.username]

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope["user"]

        if not user.is_authenticated:
            return

        message_type = data.get("type")

        # Update last active for all actions
        await self.update_last_active(user)

        # ------------------- MESSAGE -------------------
        if message_type == "message":
            message = data.get("message", "")
            room = await database_sync_to_async(ChatRoom.objects.get)(name=self.room_name)

            await database_sync_to_async(Message.objects.create)(
                room=room,
                sender=user,
                content=message
            )

            photo_url = await self.get_user_profile(user)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': user.username,
                    'profile': photo_url
                }
            )

        # ------------------- TYPING -------------------
        elif message_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_event',
                    'user': user.username,
                    'typing': data.get('typing', False)
                }
            )

        # ------------------- HEARTBEAT -------------------
        elif message_type == "heartbeat":
            # Keep online status accurate even if no messages or typing
            if ChatConsumer.active_connections.get(user.username, 0) > 0:
                await self.broadcast_presence(user, online=True)

    # ------------------- HELPER METHODS -------------------
    @database_sync_to_async
    def get_user_profile(self, user):
        try:
            if user.photo:
                return user.photo.url
        except Exception as e:
            print('Error fetching photo:', str(e))
        return '/media/default/male.png'

    @database_sync_to_async
    def update_last_active(self, user):
        user.last_active = timezone.now()
        user.save()

    async def broadcast_presence(self, user, online=True):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence_update",
                "user": user.username,
                "last_active": str(user.last_active),
                "online": online
            }
        )

    # ------------------- EVENT HANDLERS -------------------
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'profile': event['profile']
        }))

    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'typing': event['typing']
        }))

    async def presence_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'user': event['user'],
            'last_active': event['last_active'],
            'online': event['online']
        }))