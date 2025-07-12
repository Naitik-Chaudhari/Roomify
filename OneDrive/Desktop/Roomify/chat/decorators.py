from django.shortcuts import redirect
from functools import wraps

def session_required(view_func):
    """Ensures that the user has an active session before accessing a view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("username"):
            return redirect("login")  # Redirect to login if no session
        return view_func(request, *args, **kwargs)
    return wrapper


def chatroom_access_required(view_func):
    """Restricts access to chatrooms only if the user has joined the room."""
    @wraps(view_func)
    def wrapper(request, chatroom_id, *args, **kwargs):
        joined_rooms = request.session.get("joined_chatrooms", [])
        if chatroom_id not in joined_rooms:
            return redirect("chatroom_list")  # Redirect if not in session
        return view_func(request, chatroom_id, *args, **kwargs)
    return wrapper


from django.utils.timezone import now

def track_chatroom_activity(view_func):
    """Tracks the last chatroom a user visited and stores timestamp."""
    @wraps(view_func)
    def wrapper(request, chatroom_id, *args, **kwargs):
        request.session["last_active_chatroom"] = chatroom_id
        request.session["last_active_time"] = str(now())
        return view_func(request, chatroom_id, *args, **kwargs)
    return wrapper

