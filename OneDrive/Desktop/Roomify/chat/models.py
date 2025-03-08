from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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