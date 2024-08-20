from django import forms
from django.contrib.auth.forms import UserCreationForm
from restaurant.models import User, Restaurant, Food, Comment, ContactMessage, Cuisine
from django.core.validators import MaxValueValidator, MinValueValidator
from cities_light.models import City, Country


class SearchRestaurantForm(forms.Form):
    country = forms.ModelChoiceField(queryset=Country.objects.all(), label='Country', required=False)
    city = forms.ModelChoiceField(queryset=City.objects.all(), label='City', required=False)
    cuisine = forms.ModelChoiceField(queryset=Cuisine.objects.all(), label='Cuisine', required=False)


class UserCreationForm(UserCreationForm):
    isOwner = forms.BooleanField(required=False, label='Are you the owner of (a) restaurant(s)?')

    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'isOwner', 'password1', 'password2']


class AddRestaurantForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    cuisine = forms.ModelChoiceField(queryset=Cuisine.objects.all(), required=True)
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=True)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=True)
    name = forms.CharField(required=True)
    lat = forms.FloatField(required=True)
    lng = forms.FloatField(required=True)

    class Meta:
        model = Restaurant
        fields = ['name', 'country', 'city', 'cuisine', 'image', 'lat', 'lng']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.all()
        self.fields['country'].queryset = Country.objects.all()


class AddMealForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Food
        fields = ['name', 'price', 'description', 'image']


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
