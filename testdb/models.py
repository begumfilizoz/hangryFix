from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    point = models.FloatField()
    city = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Food(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.CharField(max_length=300)
    def __str__(self):
        return self.name

class User(AbstractUser):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.username

class Comment(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField()
    def __str__(self):
        return self.comment