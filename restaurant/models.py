from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg
from cities_light.models import City, Country
import datetime
from django.utils.timezone import now


# Create your models here.

class FavoritesList(models.Model):
    def __str__(self):
        return "FavoritesList for user"


class User(AbstractUser):
    isOwner = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    favorites = models.OneToOneField(FavoritesList, on_delete=models.SET_NULL, null=True, blank=True)
    favorites_is_private = models.BooleanField(default=False)
    # location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username


class Cuisine(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='restaurant-images/', default='images/restaurant.jpg')
    favorites = models.ManyToManyField(FavoritesList, related_name='favorites', blank=True, default=None)
    point = models.FloatField()
    lat = models.FloatField(default=0)
    lng = models.FloatField(default=0)
    tables = models.IntegerField(default=5)
    start_time = models.TimeField(default=datetime.time(9, 0))
    end_time = models.TimeField(default=datetime.time(21, 0))

    def __str__(self):
        return self.name

    def find_rating(self):
        point = self.comment_set.aggregate(Avg('rating'))['rating__avg']
        return point if point is not None else 0.0


class Food(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.CharField(max_length=300)
    image = models.ImageField(upload_to='food-images/', default='images/food.jpg')

    def __str__(self):
        return self.name


class Comment(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return self.comment


class Like(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name


class Booking(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=now)
    start_time = models.TimeField(default=datetime.time(9, 0))
    end_time = models.TimeField(default=datetime.time(11, 0))
    number_of_people = models.IntegerField(default=2)

    def __str__(self):
        return self.restaurant.name


class ThirtyMinuteBookingSlot(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    start_time = models.TimeField(default=datetime.time(9, 0))
    date = models.DateField(default=now)
    free_tables = models.IntegerField(default=5)
    occupied_tables = models.IntegerField(default=0)


class TwoHourBookingSlot(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    start_time = models.TimeField(default=datetime.time(9, 0))
    end_time = models.TimeField(default=datetime.time(11, 0))
    date = models.DateField(default=now)
