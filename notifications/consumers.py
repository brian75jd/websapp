from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("NOTIFICATION CONSUMER CONNECTING", self.scope['user'])        
        self.user = self.scope['user']
        self.group_name = f'user_{self.user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
    async def send_notification(self, event):
        print('running notfications')
        await self.send(
            text_data=json.dumps(event['data'])
        )