from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from chat.forms import SignupForm
from chat.models import FriendRequest
from .models import ChatRoomParticipant, Message, User
from .forms import ChatRoomForm
from .models import FriendRequest
from .models import ChatRoom
from .models import JoinChatRoomRequest
from .models import ChatRoomMessage



def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = SignupForm()
    return render(request, 'chat/signup.html', {'form': form})



def Login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home/')
    return render(request, 'chat/login.html')



@login_required
def Home_view(request):
    users = User.objects.exclude(id=request.user.id)

    # Get pending friend requests (sent & received)
    sent_requests = FriendRequest.objects.filter(sender=request.user, status="pending").values_list("receiver_id", flat=True)
    received_requests = FriendRequest.objects.filter(receiver=request.user, status="pending").select_related('sender')

    # Get accepted friends
    accepted_sent = FriendRequest.objects.filter(sender=request.user, status="accepted").values_list("receiver_id", flat=True)
    accepted_received = FriendRequest.objects.filter(receiver=request.user, status="accepted").values_list("sender_id", flat=True)

    # Merge pending requests and accepted friends
    excluded_users = set(sent_requests) | set(received_requests.values_list("sender_id", flat=True)) | set(accepted_sent) | set(accepted_received)


    accepted_sender = FriendRequest.objects.filter(sender=request.user, status="accepted").values_list("receiver__username", flat=True)  # Fetch username instead of ID
    accepted_receiver = FriendRequest.objects.filter(receiver=request.user, status="accepted").values_list("sender__username", flat=True)  # Fetch username instead of ID
    friends = set(accepted_sender) | set(accepted_receiver)
    print(friends)
    

    # Exclude all users who are in pending requests or are already friends
    users = users.exclude(id__in=excluded_users)

    return render(request, "chat/home.html", {
        "users": users, 
        "received_requests": received_requests,
        "friends": friends
    })



def Addfriend_view(request):
    users = User.objects.all()

    if request.method == "POST":
        friend_id = request.POST.get("friend_id")
        friend = get_object_or_404(User, id=friend_id)

        if request.user == friend:
            messages.error(request, "You cannot send a friend request to yourself.")
        else:
            existing_request = FriendRequest.objects.filter(sender=request.user, receiver=friend, status="pending").exists()

            if not existing_request:
                FriendRequest.objects.create(sender=request.user, receiver=friend)
                messages.success(request, f"Friend request sent to {friend.username}!")
            else:
                messages.warning(request, "Friend request already sent.")

        return redirect("home")

    return render(request, "chat/home.html", {"users": users})



def Acceptfriend_view(request):
    if request.method == "POST":
        request_id = request.POST.get("request_id")
        friend_request = get_object_or_404(FriendRequest, id=request_id)

        if friend_request.receiver == request.user:  # Ensure the logged-in user is the receiver
            friend_request.status = "accepted"
            friend_request.save()
            messages.success(request, f"You are now friends with {friend_request.sender.username}!")

    return redirect("home")



def Declinefriend_view(request):
    if request.method == "POST":
        request_id = request.POST.get("request_id")
        friend_request = get_object_or_404(FriendRequest, id=request_id)

        if friend_request.receiver == request.user:
            friend_request.delete()  # Remove the friend request from the database
            messages.info(request, "Friend request declined.")

    return redirect("home")


from django.db.models import Q


def removefriend_view(request, friend_username):
    if request.method == "POST":
        user = request.user
        friend = get_object_or_404(User, username=friend_username)  # Get user by username

        # Delete the friend connection
        FriendRequest.objects.filter(
            Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user),
            status="accepted"
        ).delete()

        # Delete all messages between user and friend
        Message.objects.filter(
            Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user)
        ).delete()

        return redirect("home")  # Redirect to the home page or another view




@login_required
def private_chat_view(request):
    # Get all friends (users who have accepted the friend request)
    friends = User.objects.filter(
        id__in=FriendRequest.objects.filter(
            status="accepted",
        ).filter(sender=request.user).values_list("receiver_id", flat=True)
    ) | User.objects.filter(
        id__in=FriendRequest.objects.filter(
            status="accepted",
        ).filter(receiver=request.user).values_list("sender_id", flat=True)
    )

    return render(request, "chat/private_chat.html", {"friends": friends})



@login_required
def ChatWithFriend_view(request, friend_id):
    # Get all friends (users who have accepted the friend request)
    friends = User.objects.filter(
        id__in=FriendRequest.objects.filter(
            status="accepted",
        ).filter(sender=request.user).values_list("receiver_id", flat=True)
    ) | User.objects.filter(
        id__in=FriendRequest.objects.filter(
            status="accepted",
        ).filter(receiver=request.user).values_list("sender_id", flat=True)
    )



    user = User.objects.get(id=request.user.id) 
    friend = User.objects.get(id=friend_id)
    
    # Get previous messages between the logged-in user and the friend
    messages = Message.objects.filter(
        sender__in=[user, friend], 
        receiver__in=[friend, user]
    ).order_by("timestamp")

    return render(request, "chat/chat_with_friend.html", {"friend": friend, "messages": messages, "friends": friends})



@login_required
def create_chatroom(request):
    if request.method == 'POST':
        form = ChatRoomForm(request.POST)
        if form.is_valid():
            chatroom = form.save(commit=False)
            chatroom.created_by = request.user  # Assign the logged-in user
            chatroom.save()  # Now save
            return redirect('chatroom_view')  # Redirect to chatroom list view

    else:
        form = ChatRoomForm()

    return render(request, 'chat/create_chatroom.html', {'form': form})



@login_required
def chatroom_view(request):
    # Chatrooms created by the logged-in user
    owned_chatrooms = ChatRoom.objects.filter(created_by=request.user)
    
    # Chatrooms the user has already joined
    joined_chatrooms = ChatRoom.objects.filter(participants=request.user)
    
    # Chatrooms the user hasn't joined and doesn't own
    joinable_chatrooms = ChatRoom.objects.exclude(participants=request.user).exclude(created_by=request.user)
    
    return render(request, "chat/chatroom.html", {
        "owned_chatrooms": owned_chatrooms,
        "joined_chatrooms": joined_chatrooms,
        "joinable_chatrooms": joinable_chatrooms
    })



@login_required
def join_chatroom(request, room_id):
    """Handles joining a chatroom: Direct join for public, request for private."""
    chatroom = get_object_or_404(ChatRoom, id=room_id)

    if request.user in chatroom.participants.all():
        messages.info(request, "You have already joined this chatroom.")
        return redirect("chatroom_view")

    if chatroom.private:
        # Check if a request already exists
        existing_request = JoinChatRoomRequest.objects.filter(user=request.user, chat_room=chatroom, status="pending").first()
        if existing_request:
            messages.warning(request, "You have already requested to join this chatroom.")
        else:
            JoinChatRoomRequest.objects.create(user=request.user, chat_room=chatroom)
            messages.success(request, "Join request sent. Waiting for admin approval.")
    else:
        ChatRoomParticipant.objects.create(user=request.user, chat_room=chatroom)
        chatroom.participants.add(request.user)
        messages.success(request, f"You have successfully joined {chatroom.name}.")

    return redirect("chatroom_view")



from django.utils import timezone
from .models import ChatRoom, ChatRoomMessage, JoinChatRoomRequest, ChatRoomParticipant

@login_required
def chatroom_detail(request, room_id):
    chatroom = get_object_or_404(ChatRoom, id=room_id)

    participants = chatroom.participants.all()  # All current participants
    join_requests = None

    # If user is owner, they can see all messages
    if request.user == chatroom.created_by:
        messages = ChatRoomMessage.objects.filter(chat_room=chatroom).order_by("timestamp")
        join_requests = JoinChatRoomRequest.objects.filter(chat_room=chatroom, status="pending")
    else:
        try:
            participant = ChatRoomParticipant.objects.get(chat_room=chatroom, user=request.user)
            joined_at = participant.joined_at
            messages = ChatRoomMessage.objects.filter(
                chat_room=chatroom, timestamp__gte=joined_at
            ).order_by("timestamp")
        except ChatRoomParticipant.DoesNotExist:
            # User is not a participant; no messages
            messages = []

    return render(request, "chat/chatroom_detail.html", {
        "chatroom": chatroom,
        "messages": messages,
        "join_requests": join_requests,
        "participants": participants,
    })




@login_required
def accept_join_request(request, request_id):
    join_request = get_object_or_404(JoinChatRoomRequest, id=request_id)

    # Ensure only the chatroom owner can accept requests
    if request.user != join_request.chat_room.created_by:
        messages.error(request, "You do not have permission to approve requests.")
        return redirect("chatroom_details", room_id=join_request.chat_room.id)
    
    if not ChatRoomParticipant.objects.filter(user=join_request.user, chat_room=join_request.chat_room).exists():
        ChatRoomParticipant.objects.create(user=join_request.user, chat_room=join_request.chat_room)

    # Add the user to the chatroom and delete the request
    join_request.chat_room.participants.add(join_request.user)
    join_request.delete()

    messages.success(request, f"{join_request.user.username} has been added to the chatroom!")
    return redirect("chatroom_details", room_id=join_request.chat_room.id)



@login_required
def reject_join_request(request, request_id):
    join_request = get_object_or_404(JoinChatRoomRequest, id=request_id)

    # Ensure only the chatroom owner can reject requests
    if request.user != join_request.chat_room.created_by:
        messages.error(request, "You do not have permission to reject requests.")
        return redirect("chatroom_details", room_id=join_request.chat_room.id)

    # Remove the request
    join_request.delete()
    
    messages.info(request, f"{join_request.user.username}'s request has been rejected.")
    return redirect("chatroom_details", room_id=join_request.chat_room.id)



@login_required
def remove_participant(request, room_id, user_id):
    chatroom = get_object_or_404(ChatRoom, id=room_id)
    
    # Ensure only admins can remove participants
    if request.user != chatroom.created_by:
        messages.error(request, "You are not allowed to remove participants.")
        return redirect("chatroom_details", room_id=room_id)

    user_to_remove = get_object_or_404(User, id=user_id)

    # Remove the user from participants
    chatroom.participants.remove(user_to_remove)
    messages.success(request, f"{user_to_remove.username} has been removed.")
    
    return redirect("chatroom_details", room_id=room_id)



@login_required
def delete_chatroom(request, room_id):
    chatroom = get_object_or_404(ChatRoom, id=room_id)

    # Ensure only the admin can delete the chatroom
    if request.user == chatroom.created_by:
        chatroom.delete()
        return redirect("chatroom_view")  # Redirect to home page or chatroom list

    return redirect("chatroom_details", room_id=room_id)  # If not admin, stay on the page



@login_required
def logout_view(request):
    logout(request)
    request.session.flush()  # Ensure session is fully cleared
    return redirect("login")