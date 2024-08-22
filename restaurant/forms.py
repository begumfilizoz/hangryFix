from django import forms
from django.contrib.auth.forms import UserCreationForm
from restaurant.models import User, Restaurant, Food, Comment, ContactMessage, Cuisine, Booking
from django.core.validators import MaxValueValidator, MinValueValidator
from cities_light.models import City, Country


class SearchRestaurantForm(forms.Form):
    name = forms.CharField(label='Restaurant Name', max_length=200, required=False)
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


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
        fields = ['date', 'time']
        widgets = {
            'date': forms.widgets.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        self.restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if self.restaurant and date and time:
            if Booking.objects.filter(restaurant=self.restaurant, date=date).exists():
                raise forms.ValidationError("You already booked this restaurant at the selected date.")
        return cleaned_data
