from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.serializers import serialize
from .models import Restaurant, Food, User, Comment, ContactMessage, Like, Cuisine, FavoritesList
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


class PrevFavoritesView(View):
    def get(self, request, id, page_no):
        requested_user = get_object_or_404(User, id=id)
        favorites_list = request.user.favorites
        next_exists = True
        if favorites_list:
            restaurants = Restaurant.objects.filter(favorites=favorites_list).order_by('id')
        else:
            restaurants = Restaurant.objects.none()
        if page_no > 0:
            page_no = page_no - 1
            if (page_no + 1) * 5 > restaurants.count():
                next_exists = False
            print(page_no)
            count = restaurants.count()
            restaurants = restaurants[page_no * 5:page_no * 5 + 5]
        return render(request, 'favorites.html',
                      {'restaurants': restaurants, 'requested_user': requested_user, 'next_exists': next_exists,
                       'page_no': page_no, 'count': count})


class NextFavoritesView(View):
    def get(self, request, id, page_no):
        requested_user = get_object_or_404(User, id=id)
        favorites_list = request.user.favorites
        next_exists = True
        if favorites_list:
            restaurants = Restaurant.objects.filter(favorites=favorites_list).order_by('id')
        else:
            restaurants = Restaurant.objects.none()
        print(restaurants)
        if page_no != -1:
            page_no = page_no + 1
            if (page_no + 1) * 5 > restaurants.count():
                next_exists = False
            print(page_no)
            count = restaurants.count()
            restaurants = restaurants[page_no * 5:page_no * 5 + 5]
        return render(request, 'favorites.html',
                      {'restaurants': restaurants, 'requested_user': requested_user, 'next_exists': next_exists,
                       'page_no': page_no, 'count': count})


class FavoritesView(View):
    def get(self, request, id, page_no):
        requested_user = get_object_or_404(User, id=id)
        favorites_list = request.user.favorites
        next_exists = True
        if favorites_list:
            restaurants = Restaurant.objects.filter(favorites=favorites_list).order_by('id')
        else:
            restaurants = Restaurant.objects.none()
        print(restaurants)
        if page_no != -1:
            if (page_no + 1) * 5 > restaurants.count():
                next_exists = False
            print(page_no)
            count = restaurants.count()
            restaurants = restaurants[page_no * 5:page_no * 5 + 5]
        return render(request, 'favorites.html',
                      {'restaurants': restaurants, 'requested_user': requested_user, 'next_exists': next_exists,
                       'page_no': page_no, 'count': count})


class OtherPrevFavoritesView(View):
    def get(self, request, id, page_no):
        requested_user = get_object_or_404(User, id=id)
        favorites_list = requested_user.favorites
        next_exists = True
        if favorites_list:
            restaurants = Restaurant.objects.filter(favorites=favorites_list).order_by('id')
        else:
            restaurants = Restaurant.objects.none()
        if page_no > 0:
            page_no = page_no - 1
            if (page_no + 1) * 5 > restaurants.count():
                next_exists = False
            print(page_no)
            count = restaurants.count()
            restaurants = restaurants[page_no * 5:page_no * 5 + 5]
        return render(request, 'other-favorites.html',
                      {'restaurants': restaurants, 'requested_user': requested_user, 'next_exists': next_exists,
                       'page_no': page_no, 'count': count})


class OtherNextFavoritesView(View):
    def get(self, request, id, page_no):
        requested_user = get_object_or_404(User, id=id)
        favorites_list = requested_user.favorites
        next_exists = True
        if favorites_list:
            restaurants = Restaurant.objects.filter(favorites=favorites_list).order_by('id')
        else:
            restaurants = Restaurant.objects.none()
        print(restaurants)
        if page_no != -1:
            page_no = page_no + 1
            if (page_no + 1) * 5 > restaurants.count():
                next_exists = False
            print(page_no)
            count = restaurants.count()
            restaurants = restaurants[page_no * 5:page_no * 5 + 5]
        return render(request, 'other-favorites.html',
                      {'restaurants': restaurants, 'requested_user': requested_user, 'next_exists': next_exists,
                       'page_no': page_no, 'count': count})


class OtherFavoritesView(View):
    def get(self, request, id, page_no):
        requested_user = get_object_or_404(User, id=id)
        favorites_list = requested_user.favorites
        next_exists = True
        if favorites_list:
            restaurants = Restaurant.objects.filter(favorites=favorites_list).order_by('id')
        else:
            restaurants = Restaurant.objects.none()
        print(restaurants)
        if page_no != -1:
            if (page_no + 1) * 5 > restaurants.count():
                next_exists = False
            print(page_no)
            count = restaurants.count()
            restaurants = restaurants[page_no * 5:page_no * 5 + 5]
        return render(request, 'other-favorites.html',
                      {'restaurants': restaurants, 'requested_user': requested_user, 'next_exists': next_exists,
                       'page_no': page_no, 'count': count})
