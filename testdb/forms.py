from django import forms
from django.contrib.auth.forms import UserCreationForm
from testdb.models import User, Restaurant


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'location', 'password1', 'password2']


class AddRestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = '__all__'