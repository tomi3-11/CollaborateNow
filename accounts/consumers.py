import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import logging
from .models import Whiteboard
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles new WebSocket connection"""
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f"chat_{self.project_id}"

        # Join the chat group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """Handles message received from WebSocket"""
        import logging
        logger = logging.getLogger(__name__)

        logger.debug(f"🔹 receive() triggered | text_data={text_data} | bytes_data={bytes_data}")

        if text_data is None:  
            logger.debug("⚠️ No text_data received (probably a ping or binary frame)")
            return

        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {e} | raw data: {text_data}")
            return

        message = (text_data_json.get("message") or "").strip()
        logger.debug(f"Extracted message: '{message}'")

        if not message:
            logger.debug("⚠️ Empty message ignored")
            return

        user = self.scope.get("user")
        logger.debug(f"User from scope: {user}")

        if not user or not getattr(user, "is_authenticated", False):
            username = "Anonymous"
            logger.debug("User not authenticated, defaulting to Anonymous")
        else:
            username = await self.get_username(user.id)
            logger.debug(f"Resolved username: {username}")

        payload = {
            "type": "chat_message",
            "message": message,
            "user": username,
        }
        logger.debug(f"Sending to group {self.room_group_name}: {payload}")

        await self.channel_layer.group_send(self.room_group_name, payload)
        logger.debug("✅ Message sent to group successfully")

        
        
    async def chat_message(self, event):
        """Receive message from group and send to WebSocket"""
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "user": event["user"],
        }))

    @database_sync_to_async
    def get_username(self, user_id):
        """Safely fetches username in async context"""
        from django.contrib.auth import get_user_model   # 👈 lazy import
        User = get_user_model()
        try:
            return User.objects.get(id=user_id).username
        except User.DoesNotExist:
            return "Unknown"
        
        
class WhiteboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f"Whiteboard_{self.project_id}"
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()
        
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json['content']
        user_id = self.scope['user'].id
        user = await User.objects.aget(id=user_id)
        
        # Save the content to the database (optional, for persistence)
        try:
            whiteboard = await Whiteboard.objects.aget(project_id=self.project_id)
            whiteboard.content = content
            await whiteboard.asave()
        except Whiteboard.DoesNotExist:
            whiteboard = await Whiteboard.objects.acreate(project_id=self.projects_id, content=content)
            
        # Broadcast the content to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'whiteboard_update',
                'content': content
                'user': user.username,
            }
        )
        
    async def whiteboard_update(self, event):
        content = event['connect']
        user = event['user']
            
        # Send the content to the WebSocket
        await self.send(text_data=json.dumps({
            'content': content,
            'user': user,
        }))
