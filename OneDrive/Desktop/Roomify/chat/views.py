from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from chat.forms import SignupForm
from chat.models import FriendRequest
from .models import Message, User

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


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import FriendRequest

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

    # Exclude all users who are in pending requests or are already friends
    users = users.exclude(id__in=excluded_users)

    return render(request, "chat/home.html", {
        "users": users, 
        "received_requests": received_requests  # Now sender should be properly loaded
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


@login_required
def profile_view(request):
    return render(request, "chat/profile.html")


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
    user = User.objects.get(id=request.user.id) 
    friend = User.objects.get(id=friend_id)
    
    # Get previous messages between the logged-in user and the friend
    messages = Message.objects.filter(
        sender__in=[user, friend], 
        receiver__in=[friend, user]
    ).order_by("timestamp")

    return render(request, "chat/chat_with_friend.html", {"friend": friend, "messages": messages})


def logout_view(request):
    logout(request)
    return redirect("home")