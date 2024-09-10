from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.serializers import serialize
from .models import Restaurant, Food, User, Comment, ContactMessage, Like, Cuisine, FavoritesList, Booking, ThirtyMinuteBookingSlot
from .forms import UserCreationForm, AddRestaurantForm, AddMealForm, AddCommentForm, ContactForm, SearchRestaurantForm
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
from .utils import show_favorites


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
    def post(self, request, commentId):
        comment = get_object_or_404(Comment, id=commentId)
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
    def post(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        list = request.user.favorites
        restaurant.favorites.add(list)
        restaurant.save()
        return redirect('restaurantdetail', id=id, pageno=pageno)


class RemoveFromFavoritesView(View):
    def post(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        list = request.user.favorites
        restaurant.favorites.remove(list)
        restaurant.save()
        return redirect('restaurantdetail', id=id, pageno=pageno)


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

        # find the average of the reviews the user left to that restaurant
        aggregated_reviews = high_reviews.values('restaurant_id').annotate(rating=models.Avg('rating'))

        # get the restaurants with the high reviews
        high_rated_restaurants = Restaurant.objects.filter(
            id__in=[review['restaurant_id'] for review in aggregated_reviews])

        # fetch data to feed the model
        high_rated_restaurants_data = Restaurant.objects.filter(id__in=[restaurant.id for restaurant in high_rated_restaurants]).select_related('cuisine').values(
            'id', 'cuisine__name', 'lng', 'lat', 'point'
        )

        # convert the data to pandas dataframe
        df_user = pd.DataFrame(high_rated_restaurants_data)

        # printing for debugging
        print(df_user.columns)
        print(df_user.head())

        # one-hot encoding to convert the cuisine__name field into numeric vectors
        cuisine_encoder = OneHotEncoder(handle_unknown='ignore')
        cuisine_encoder.fit(df_user[['cuisine__name']])
        cuisine_vectors = cuisine_encoder.transform(df_user[['cuisine__name']])
        print(cuisine_vectors)

        # create user profile to find user cuisine preferences
        user_profile_vector = np.mean(cuisine_vectors.toarray(), axis=0)

        # fetch the data of all restaurants to compare to user preferences
        all_restaurants = Restaurant.objects.select_related('cuisine').all().values()
        all_restaurants_data = Restaurant.objects.select_related('cuisine').values(
            'id', 'cuisine__name', 'lng', 'lat', 'point'
        )
        df_all = pd.DataFrame(list(all_restaurants_data))

        # convert cuisines to numeric values again
        all_cuisine_vectors = cuisine_encoder.transform(df_all[['cuisine__name']]).toarray()
        cuisine_similarity = cosine_similarity([user_profile_vector], all_cuisine_vectors)[0]

        # calculate the proximity of user-rated restaurants and a target restaurant
        def calculate_location_similarity(user_restaurants, target_restaurant):
            distances = [geodesic((r['lat'], r['lng']),
                                  (target_restaurant['lat'], target_restaurant['lng'])).kilometers
                         for r in user_restaurants]
            return 1 / (1 + np.mean(distances)) # this is done to ensure that closer distances yield larger
            # similarity scores

        # proximity similarity applied to all restaurants
        location_similarities = np.array([
            calculate_location_similarity(high_rated_restaurants_data, restaurant) for restaurant in
            df_all.to_dict('records')
        ])

        # calculate a combined similarity score and recommend top 5 most similar restaurants
        combined_similarity = 0.7 * cuisine_similarity + 0.3 * location_similarities
        df_all['similarity'] = combined_similarity

        # drop the duplicate restaurant recommendations if the user reviewed the restaurant multiple times
        all_recommendations = df_all.drop_duplicates(subset='id').sort_values(by='similarity', ascending=False).head(5)
        recommended_restaurant_ids = all_recommendations['id'].tolist()
        recommended_restaurants = Restaurant.objects.filter(id__in=recommended_restaurant_ids)
        print(recommended_restaurants.count())
        return render(request, 'restaurantrecommendations.html', {'reviews_exist': reviews_exist, 'recommended_restaurants': recommended_restaurants})