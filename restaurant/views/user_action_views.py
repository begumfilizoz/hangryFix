from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.serializers import serialize
from restaurant.models import RestaurantRecommendations, Restaurant, Food, User, Comment, ContactMessage, Like, Cuisine, FavoritesList, Booking, ThirtyMinuteBookingSlot
from restaurant.forms import UserCreationForm, AddRestaurantForm, AddMealForm, AddCommentForm, ContactForm, SearchRestaurantForm
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg
from django.http import JsonResponse
from cities_light.models import City, Country
from django.contrib import messages
import folium, math
from django.utils import timezone
from datetime import datetime, timedelta
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
from geopy.distance import geodesic
import numpy as np
import pandas as pd
from restaurant.utils import show_favorites


class SignUpView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            favorites_list = FavoritesList()
            favorites_list.save()
            user.favorites = favorites_list
            user.save()
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
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return redirect('profile', id=request.user.id)


class ProfileView(View):
    def get(self, request, id):
        requested_user = get_object_or_404(User, id=id)
        restaurants = Restaurant.objects.filter(owner=requested_user)
        comments = Comment.objects.filter(user=requested_user)
        if not request.user.is_authenticated:
            return redirect('login')
        return render(request, 'profile.html',
                      {'requested_user': requested_user, 'restaurants': restaurants, 'comments': comments, 'id': id})


class AddToFavoritesView(View):
    def post(self, request, id, page_no):
        restaurant = get_object_or_404(Restaurant, id=id)
        list = request.user.favorites
        restaurant.favorites.add(list)
        restaurant.save()
        return redirect('restaurant_detail', id=id, page_no=page_no)


class RemoveFromFavoritesView(View):
    def post(self, request, id, page_no):
        restaurant = get_object_or_404(Restaurant, id=id)
        list = request.user.favorites
        restaurant.favorites.remove(list)
        restaurant.save()
        return redirect('restaurant_detail', id=id, page_no=page_no)


class RemoveFromFavoritesProfileView(View):
    def post(self, request, id, page_no):
        restaurant = get_object_or_404(Restaurant, id=id)
        list = request.user.favorites
        restaurant.favorites.remove(list)
        restaurant.save()
        return redirect('favorites', id=request.user.id, page_no=page_no)


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('login')


class MakeFavoritesPublicView(View):
    def post(self, request):
        request.user.favorites_is_private = False
        request.user.save()
        return redirect('favorites', id=request.user.id, page_no=0)


class MakeFavoritesPrivateView(View):
    def post(self, request):
        request.user.favorites_is_private = True
        request.user.save()
        return redirect('favorites', id=request.user.id, page_no=0)


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


class OtherProfileView(View):
    def get(self, request, id):
        other_user = get_object_or_404(User, id=id)
        return render(request, 'otherprofile.html', {'other_user': other_user})


class FavoritesView(View):
    def get(self, request, id, page_no):
        requested_user = get_object_or_404(User, id=id)
        favorites_list = request.user.favorites
        count, restaurants, next_exists, page_no = show_favorites(favorites_list, page_no)
        return render(request, 'favorites.html',
                      {'restaurants': restaurants, 'requested_user': requested_user, 'next_exists': next_exists,
                       'page_no': page_no, 'count': count})


class OtherFavoritesView(View):
    def get(self, request, id, page_no):
        requested_user = get_object_or_404(User, id=id)
        favorites_list = requested_user.favorites
        count, restaurants, next_exists, page_no = show_favorites(favorites_list, page_no)
        return render(request, 'other-favorites.html',
                      {'restaurants': restaurants, 'requested_user': requested_user, 'next_exists': next_exists,
                       'page_no': page_no, 'count': count})


class BookingsView(View):
    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).order_by('id')
        for booking in bookings:
            if booking.date < timezone.now().date():
                booking.delete()
        bookings.order_by('id')
        count = bookings.count()
        return render(request, 'userbookings.html', {'count': count, 'bookings': bookings})


class RestaurantsListView(View):
    def get(self, request):
        restaurants = Restaurant.objects.filter(owner=request.user).order_by('id')
        return render(request, 'restaurantlist.html', {'restaurants': restaurants})


class ManageBookingsRestaurantView(View):
    def get(self, request, id):
        restaurant = Restaurant.objects.get(id=id)
        requested_user = request.user
        bookings = Booking.objects.filter(restaurant=restaurant).order_by('id')
        for booking in bookings:
            if booking.date < timezone.now().date():
                booking.delete()
        bookings.order_by('id')
        count = bookings.count()
        return render(request, 'bookingslist.html', {'count': count, 'restaurant': restaurant, 'bookings': bookings, 'requested_user': requested_user})


class ApproveBookingView(View):
    def post(self, request, id):
        booking = Booking.objects.get(id=id)
        booking.approved = True
        booking.save()
        messages.success(request, 'Booking approved')
        restaurant = booking.restaurant
        requested_user = request.user
        bookings = Booking.objects.filter(restaurant=restaurant).order_by('id')
        for booking in bookings:
            if booking.date < timezone.now().date():
                booking.delete()
        bookings.order_by('id')
        count = bookings.count()
        return render(request, 'bookingslist.html',
                      {'count': count, 'restaurant': restaurant, 'bookings': bookings, 'requested_user': requested_user})


class RestaurantRecommendationsView(View):
    def get(self, request):
        user = request.user
        # fetch the high reviews of the logged in user
        high_reviews = Comment.objects.filter(user=user, rating__gte=4).select_related('restaurant')

        # bool to alert the template if there are no reviews to use
        reviews_exist = True
        if not high_reviews.exists():
            reviews_exist = False

        # get the recommended restaurants from the database
        recommendations = RestaurantRecommendations.objects.filter(user_id=user.id)
        recommended_restaurants = []
        for recommendation in recommendations:
            recommended_restaurants.append(Restaurant.objects.get(id=recommendation.restaurant_id))
        return render(request, 'restaurantrecommendations.html', {'reviews_exist': reviews_exist, 'recommended_restaurants': recommended_restaurants})