from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ChatRoom


class SignupForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']



class ChatRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ['name', 'private']
        labels = {
            'name': 'Chat Room Name',
            'private': 'Private Room'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter room name'}),
            'private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
