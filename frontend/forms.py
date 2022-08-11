from django import forms
from accounts.models import User

class UserForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ('email', 'name', 'user_type', 'password', 'phone_number', 'avatar')
