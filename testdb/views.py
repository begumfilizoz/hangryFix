# Create your views here.
from django.shortcuts import render, redirect
from django.views import View
from .models import Restaurant, Food, User, Comment
from .forms import UserCreationForm, AddRestaurantForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm



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

class ContactView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'contact.html')
class SignUpView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
        return render(request, 'signup.html', {'form': form})


class LogInView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            print("is valid")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                print("weird")
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password')
                print(form.errors)
        return render(request, 'login.html', {'form': form})

class AddRestaurantView(View):
    def get(self, request):
        form = AddRestaurantForm()
        return render(request, 'addrestaurant.html', {'form': form})

    def post(self, request):
        form = AddRestaurantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        return render(request, 'addrestaurant.html', {'form': form})