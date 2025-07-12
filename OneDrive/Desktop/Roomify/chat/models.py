from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        default="pending",
    )

    class Meta:
        unique_together = ("sender", "receiver")  # Prevent duplicate requests

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.status})"



class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]  # Show recent messages first
        
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"
    

User = get_user_model()

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Room name
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_rooms")  # Room creator
    participants = models.ManyToManyField(User, related_name="chat_rooms")  # Users in the room
    private = models.BooleanField(default=False)  # True = Private, False = Public
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when room was created

    def __str__(self):
        return self.name



class JoinChatRoomRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="join_requests")  # User requesting to join
    chat_room = models.ForeignKey("ChatRoom", on_delete=models.CASCADE, related_name="join_requests")  # Target chat room
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        default="pending"
    )  # Request status
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of request

    def __str__(self):
        return f"{self.user.username} -> {self.chat_room.name} ({self.status})"
    


class ChatRoomMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")  # Room the message belongs to
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")  # User who sent the message
    content = models.TextField()  # Message content
    timestamp = models.DateTimeField(auto_now_add=True)  # Time message was sent

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]} ({self.timestamp})"
    

class ChatRoomParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "chat_room")  # Prevent duplicate entries
    