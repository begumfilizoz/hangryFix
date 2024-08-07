from django.contrib.auth.forms import AuthenticationForm
# Create your views here.
from django.shortcuts import render, redirect
from django.views import View
from .models import Restaurant, Food, User, Comment

class HomeView(View):
    def get(self, request, *args, **kwargs):
        restaurants = Restaurant.objects.all()
        #comments = Comment.objects.all()
        #foods = Food.objects.all()
        users = User.objects.all()
        context = {
            'restaurants': restaurants,
            #'comments': comments,
            #'foods': foods,
            'users': users,
        }
        return render(request, 'home.html', context)

class LogInView(View):
    def get(self, request, *args, **kwargs):
        template_name = 'login.html'
        def get(self, request):
            form = AuthenticationForm()
            return render(request, self.template_name, {'form': form})

