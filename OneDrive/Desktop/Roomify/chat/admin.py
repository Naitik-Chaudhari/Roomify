from django.contrib import admin
from .models import FriendRequest
from .models import ChatRoomMessage
from .models import Message
from .models import ChatRoom, JoinChatRoomRequest


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("sender__username", "receiver__username")



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "content", "timestamp")
    search_fields = ("sender__username", "receiver__username", "content")
    ordering = ("-timestamp",)



@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "private", "created_by", "created_at")
    list_filter = ("private", "created_at")
    search_fields = ("name", "created_by__username")

    

@admin.register(JoinChatRoomRequest)
class JoinChatRoomRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "chat_room", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "chat_room__name")
    actions = ["approve_request", "reject_request"]

    def approve_request(self, request, queryset):
        """Approve selected join requests and add users to chatroom."""
        for join_request in queryset:
            if join_request.status == "pending":
                join_request.chat_room.participants.add(join_request.user)
                join_request.status = "accepted"
                join_request.save()
        self.message_user(request, "Selected requests have been approved.")

    def reject_request(self, request, queryset):
        """Reject selected join requests."""
        queryset.update(status="rejected")
        self.message_user(request, "Selected requests have been rejected.")

    approve_request.short_description = "Approve selected requests"
    reject_request.short_description = "Reject selected requests"



@admin.register(ChatRoomMessage)
class ChatRoomMessageAdmin(admin.ModelAdmin):
    list_display = ("chat_room", "sender", "content", "timestamp")
    search_fields = ("content", "sender__username", "chat_room__name")
    list_filter = ("timestamp", "chat_room")


from django.contrib import admin
from .models import ChatRoomParticipant

@admin.register(ChatRoomParticipant)
class ChatRoomParticipantAdmin(admin.ModelAdmin):
    list_display = ("user", "chat_room", "joined_at")
    list_filter = ("chat_room", "joined_at")
    search_fields = ("user__username", "chat_room__name")

