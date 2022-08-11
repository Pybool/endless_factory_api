from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from django import forms


class CreatUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'name', 'user_type', 'country']