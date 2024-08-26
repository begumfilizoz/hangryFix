# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.serializers import serialize
from .models import Restaurant, Food, User, Comment, ContactMessage, Like, Cuisine, FavoritesList
from .forms import UserCreationForm, AddRestaurantForm, AddMealForm, AddCommentForm, ContactForm, SearchRestaurantForm, BookingForm
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg
from django.http import JsonResponse
from cities_light.models import City, Country
from django.contrib import messages
import folium


class AddRestaurantView(View):
    def get(self, request):
        form = AddRestaurantForm()
        return render(request, 'addrestaurant.html', {'form': form})

    def post(self, request):
        form = AddRestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.point = 0
            restaurant.save()
            return redirect('search')
        return render(request, 'addrestaurant.html', {'form': form})


class GetCitiesAndCountriesView(View):
    def get(self, request):
        country_id = request.GET.get('country_id')
        cities = City.objects.filter(country_id=country_id)
        cities_data = list(cities.values('id', 'name'))
        return JsonResponse(cities_data, safe=False)


class RestaurantDetailView(View):
    def get(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)
        if (pageno + 1) * 5 > comments.count():
            next_exists = False
        comments = comments[pageno * 5:pageno * 5 + 5]
        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)
        rating = restaurant.find_rating()
        form = AddCommentForm()
        m = folium.Map(location=[restaurant.lat, restaurant.lng], zoom_start=15)
        folium.Marker([restaurant.lat, restaurant.lng], popup=restaurant.name).add_to(m)
        map_html = m._repr_html_()
        if request.user.favorites in restaurant.favorites.all():
            restaurant_in_favorites = True
        else:
            restaurant_in_favorites = False
        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno, 'restaurant_in_favorites': restaurant_in_favorites})

    def post(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)
        if (pageno + 1) * 5 > comments.count():
            next_exists = False
        comments = comments[pageno * 5:pageno * 5 + 5]
        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)
        rating = restaurant.find_rating()
        form = AddCommentForm()
        m = folium.Map(location=[restaurant.lat, restaurant.lng], zoom_start=15)
        folium.Marker([restaurant.lat, restaurant.lng], popup=restaurant.name).add_to(m)
        map_html = m._repr_html_()
        form = AddCommentForm(request.POST)
        if request.user.favorites in restaurant.favorites.all():
            restaurant_in_favorites = True
        else:
            restaurant_in_favorites = False
        if form.is_valid():
            comment = form.save(commit=False)
            comment.restaurant = restaurant
            comment.user = request.user
            comment.save()
            rating = restaurant.find_rating()
            restaurant.point = rating
            restaurant.save()
            return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)

        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno,
                       'restaurant_in_favorites': restaurant_in_favorites})


class PrevRestaurantDetailView(View):
    def get(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)
        if pageno > 0:
            pageno = pageno - 1
            if (pageno + 1) * 5 > comments.count():
                next_exists = False
            comments = comments[pageno * 5:pageno * 5 + 5]
        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)
        rating = restaurant.find_rating()
        form = AddCommentForm()
        m = folium.Map(location=[restaurant.lat, restaurant.lng], zoom_start=15)
        folium.Marker([restaurant.lat, restaurant.lng], popup=restaurant.name).add_to(m)
        map_html = m._repr_html_()
        if request.user.favorites in restaurant.favorites.all():
            restaurant_in_favorites = True
        else:
            restaurant_in_favorites = False
        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno,
                       'restaurant_in_favorites': restaurant_in_favorites})

    def post(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)
        if pageno > 0:
            pageno = pageno - 1
            if (pageno + 1) * 5 > comments.count():
                next_exists = False
            comments = comments[pageno * 5:pageno * 5 + 5]
        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)
        rating = restaurant.find_rating()
        form = AddCommentForm()
        m = folium.Map(location=[restaurant.lat, restaurant.lng], zoom_start=15)
        folium.Marker([restaurant.lat, restaurant.lng], popup=restaurant.name).add_to(m)
        map_html = m._repr_html_()
        form = AddCommentForm(request.POST)
        if request.user.favorites in restaurant.favorites.all():
            restaurant_in_favorites = True
        else:
            restaurant_in_favorites = False
        if form.is_valid():
            comment = form.save(commit=False)
            comment.restaurant = restaurant
            comment.user = request.user
            comment.save()
            rating = restaurant.find_rating()
            restaurant.point = rating
            restaurant.save()
            return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)

        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno,
                       'restaurant_in_favorites': restaurant_in_favorites})


class NextRestaurantDetailView(View):
    def get(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)
        if pageno != -1:
            pageno = pageno + 1
            if (pageno + 1) * 5 > comments.count():
                next_exists = False
            comments = comments[pageno * 5:pageno * 5 + 5]
        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)
        rating = restaurant.find_rating()
        form = AddCommentForm()
        m = folium.Map(location=[restaurant.lat, restaurant.lng], zoom_start=15)
        folium.Marker([restaurant.lat, restaurant.lng], popup=restaurant.name).add_to(m)
        map_html = m._repr_html_()
        if request.user.favorites in restaurant.favorites.all():
            restaurant_in_favorites = True
        else:
            restaurant_in_favorites = False
        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno,
                       'restaurant_in_favorites': restaurant_in_favorites})
    def post(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)
        if pageno != -1:
            pageno = pageno + 1
            if (pageno + 1) * 5 > comments.count():
                next_exists = False
            comments = comments[pageno * 5:pageno * 5 + 5]
        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)
        rating = restaurant.find_rating()
        form = AddCommentForm()
        m = folium.Map(location=[restaurant.lat, restaurant.lng], zoom_start=15)
        folium.Marker([restaurant.lat, restaurant.lng], popup=restaurant.name).add_to(m)
        map_html = m._repr_html_()
        form = AddCommentForm(request.POST)
        if request.user.favorites in restaurant.favorites.all():
            restaurant_in_favorites = True
        else:
            restaurant_in_favorites = False
        if form.is_valid():
            comment = form.save(commit=False)
            comment.restaurant = restaurant
            comment.user = request.user
            comment.save()
            rating = restaurant.find_rating()
            restaurant.point = rating
            restaurant.save()
            return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)

        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno,
                       'restaurant_in_favorites': restaurant_in_favorites})


class LikeUnlikeReviewView(View):
    def post(self, request, id, pageno):
        comment = get_object_or_404(Comment, id=id)
        restaurant = get_object_or_404(Restaurant, id=comment.restaurant.id)
        user = request.user
        if user.is_authenticated:
            if Like.objects.filter(user=user, comment=comment).exists():
                Like.objects.filter(user=user, comment=comment).delete()
                messages.success(request, 'You unliked the review.')
                return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)
            else:
                Like.objects.create(user=user, comment=comment)
                messages.success(request, 'You liked the review.')
                return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)
        else:
            messages.success(request, 'Log in to like the review.')
            return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)


class MenuView(View):
    def get(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        return render(request, 'menu.html', {'restaurant': restaurant})


class DeleteCommentFromRestView(View):
    def post(self, request, restId, commentId):
        comment = get_object_or_404(Comment, id=commentId)
        comment.delete()
        return redirect('restaurantdetail', id=restId, pageno=0)


class AddMealView(View):
    def get(self, request, id):
        form = AddMealForm()
        restaurant = get_object_or_404(Restaurant, id=id)
        return render(request, 'addmeal.html', {'form': form, 'restaurant': restaurant})

    def post(self, request, id):
        form = AddMealForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = get_object_or_404(Restaurant, id=id)
            meal = form.save(commit=False)
            meal.restaurant = restaurant
            meal.save()
            user_id = request.user.id
            return redirect('profile', id=user_id)
        return render(request, 'addmeal.html', {'form': form, 'id': id})


class RemoveMealsView(View):
    def get(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        return render(request, 'removemeals.html', {'restaurant': restaurant})


class RemoveMealView(View):
    def post(self, request, foodId, resId):
        food = get_object_or_404(Food, id=foodId)
        food.delete()
        return redirect('removemeals', id=resId)


class RemoveRestaurantView(View):
    def post(self, request, resId, userId):
        restaurant = get_object_or_404(Restaurant, id=resId)
        restaurant.delete()
        return redirect('profile', id=userId)


class BookingView(View):
    def get(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        form = BookingForm(restaurant=restaurant)
        return render(request, 'bookrestaurant.html', {"restaurant": restaurant, "form": form})

    def post(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        form = BookingForm(request.POST, restaurant=restaurant)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.restaurant = restaurant
            booking.user = request.user
            booking.save()
            messages.success(request, 'You successfully booked the restaurant.')
            return redirect('restaurantdetail', id=restaurant.id, pageno=0)
        return render(request, 'bookrestaurant.html', {"restaurant": restaurant, "form": form})
