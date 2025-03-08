from django.urls import re_path
from .consumers import ChatConsumer, ChatRoomConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<friend_id>\d+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/chatroom/(?P<chatroom_id>\d+)/$", ChatRoomConsumer.as_asgi()),
]
