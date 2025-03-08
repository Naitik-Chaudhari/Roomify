from django.urls import include, path
from chat.views import Acceptfriend_view, Addfriend_view, ChatWithFriend_view, Declinefriend_view, Home_view, Login_view, logout_view, private_chat_view, profile_view, signup_view

urlpatterns = [
    path('',Login_view, name="login"),
    path('signup/',signup_view, name="signup"),
    path('home/', Home_view, name="home"),
    path("addfriend/", Addfriend_view, name="addfriend"),
    path("acceptfriend/", Acceptfriend_view, name="acceptfriend"),
    path("declinefriend/", Declinefriend_view, name="declinefriend"),
    path("profile/", profile_view, name="profile"),
    path("private_chat/", private_chat_view, name="private_chat"),
    path("logout/", logout_view, name="logout"),
    path("chat/<int:friend_id>/", ChatWithFriend_view, name="chat_with_friend"),
]
