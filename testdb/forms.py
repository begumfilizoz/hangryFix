from django import forms
from django.contrib.auth.forms import UserCreationForm
from testdb.models import User, Restaurant, Food


class UserCreationForm(UserCreationForm):
    isOwner = forms.BooleanField(required=False, label='Are you the owner of (a) restaurant(s)?')
    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'isOwner', 'location', 'password1', 'password2']


class AddRestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'point', 'city', 'cuisine']

class AddMealForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'price', 'description']