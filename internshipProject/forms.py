from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from testdb.models import User

class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'location', 'password1', 'password2']