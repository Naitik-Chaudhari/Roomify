import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection"""
        self.friend_id = self.scope["url_route"]["kwargs"]["friend_id"]
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Generate a unique private chat room name
        self.room_group_name = f"private_chat_{min(self.user.id, int(self.friend_id))}_{max(self.user.id, int(self.friend_id))}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✅ WebSocket Connected: {self.room_group_name}")

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ WebSocket Disconnected: {self.room_group_name}")

    async def receive(self, text_data):
        """Handles receiving messages via WebSocket, saving to DB, and broadcasting"""
        data = json.loads(text_data)
        message_text = data.get("message", "").strip()
        sender_name = data.get("sender_name", "")
        receiver_id = data.get("receiver_id", None)

        if not message_text or not receiver_id:
            return  # Ignore empty messages or missing receiver

        try:
            sender = await sync_to_async(User.objects.get)(username=sender_name)
            receiver = await sync_to_async(User.objects.get)(id=receiver_id)
        except User.DoesNotExist:
            print("❌ User not found!")
            return  # Prevent errors if users are missing

        print(f"💾 Saving message: {message_text} from {sender.username} to {receiver.username}")

        # Save message to the database
        message = await sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            content=message_text
        )

        print(f"✅ Message saved: {message_text}")

        # Send the message to the chat room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_text,
                "sender": sender.username,
            }
        )

    async def chat_message(self, event):
        """Handles sending messages to WebSocket clients"""
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"]
        }))
