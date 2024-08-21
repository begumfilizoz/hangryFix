from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.serializers import serialize
from .models import Restaurant, Food, User, Comment, ContactMessage, Like, Cuisine
from .forms import UserCreationForm, AddRestaurantForm, AddMealForm, AddCommentForm, ContactForm, SearchRestaurantForm
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg
from django.http import JsonResponse
from cities_light.models import City, Country
from django.contrib import messages
import folium


class SignUpView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('search')
        return render(request, 'signup.html', {'form': form})


class ContactView(View):
    def get(self, request):
        form = ContactForm()
        return render(request, 'contact.html', {'form': form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('search')
        return render(request, 'contact.html', {'form': form})


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
                return redirect('search')
            else:
                form.add_error(None, 'Invalid username or password')
                print(form.errors)
        return render(request, 'login.html', {'form': form})


class DeleteCommentFromProfileView(View):
    def post(self, request, commentId):
        comment = get_object_or_404(Comment, id=commentId)
        comment.delete()
        return redirect('profile', id=request.user.id)


class ProfileView(View):
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        restaurants = Restaurant.objects.filter(owner=user)
        comments = Comment.objects.filter(user=user)
        if not request.user.is_authenticated:
            return redirect('login')
        return render(request, 'profile.html', {'user': user, 'restaurants': restaurants, 'comments': comments})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('login')


class MakeUserOwnerView(View):
    def post(self, request):
        request.user.isOwner = True
        request.user.save()
        return redirect('profile', id=request.user.id)


class DeleteUserView(View):
    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        logout(request)
        user.delete()
        return redirect('login')
