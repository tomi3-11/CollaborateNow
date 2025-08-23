import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f"chat_{self.project_id}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = self.scope['user'].id
        user = await User.objects.aget(id=user_id) # Asynchronous get
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.username,
            }
        )
        
    # Receives message from room group
    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user
        }))