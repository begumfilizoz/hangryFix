from django import forms
from django.contrib.auth.forms import UserCreationForm
from testdb.models import User, Restaurant, Food, Comment, ContactMessage
from django.core.validators import MaxValueValidator, MinValueValidator


class UserCreationForm(UserCreationForm):
    isOwner = forms.BooleanField(required=False, label='Are you the owner of (a) restaurant(s)?')

    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'isOwner', 'location', 'password1', 'password2']


class AddRestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'city', 'cuisine']


class AddMealForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'price', 'description']


class AddCommentForm(forms.ModelForm):
    rating = forms.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="Enter a rating between 0.0 and 5.0"
    )

    class Meta:
        model = Comment
        fields = ['rating', 'comment']


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
