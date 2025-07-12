from django.urls import include, path
from chat.views import Acceptfriend_view, Addfriend_view, ChatWithFriend_view, Declinefriend_view, Home_view, Login_view, accept_join_request, chatroom_detail, chatroom_view, create_chatroom, delete_chatroom, join_chatroom, logout_view, private_chat_view, reject_join_request, remove_participant, removefriend_view, signup_view

urlpatterns = [
    path('',Login_view, name="login"),
    path('signup/',signup_view, name="signup"),
    path('home/', Home_view, name="home"),
    path("addfriend/", Addfriend_view, name="addfriend"),
    path("acceptfriend/", Acceptfriend_view, name="acceptfriend"),
    path("declinefriend/", Declinefriend_view, name="declinefriend"),
    path('removefriend/<str:friend_username>/', removefriend_view, name='removefriend'),
    path("private_chat/", private_chat_view, name="private_chat"),
    path("logout/", logout_view, name="logout"),
    path("chat/<int:friend_id>/", ChatWithFriend_view, name="chat_with_friend"),
    path("chatroom/", chatroom_view, name="chatroom_view"),
    path("chatroom/create/", create_chatroom, name="create_chatroom"),
    path('chatroom/join/<int:room_id>/', join_chatroom, name='join_chatroom'),
    path('chatroom/<int:room_id>/', chatroom_detail, name='chatroom_details'),
    path("join-request/accept/<int:request_id>/", accept_join_request, name="accept_join_request"),
    path("join-request/reject/<int:request_id>/", reject_join_request, name="reject_join_request"),
    path("chatroom/<int:room_id>/remove/<int:user_id>/", remove_participant, name="remove_participant"),
    path("delete-chatroom/<int:room_id>/", delete_chatroom, name="delete_chatroom"),
]
