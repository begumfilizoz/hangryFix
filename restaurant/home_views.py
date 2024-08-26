# Create your views here.
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


class RestrictedHomeView(View):
    def get(self, request, link, pageno):
        next_exists = True
        if link == "all":
            restaurants = Restaurant.objects.all()
        else:
            keywords = {'country': -1, 'city': -1, 'cuisine': -1}
            print(link)
            link_to_list = link.split("-")
            print(link_to_list)
            filters = {}
            name = ""
            name_exists = False
            for pair in link_to_list:
                if pair.split("=")[0] == "name":
                    name_exists = True
                    name = pair.split("=")[1]
                else:
                    keywords[pair.split("=")[0]] = int(pair.split("=")[1])
            if keywords['country'] != -1:
                country_id = keywords['country']
                filters['country'] = get_object_or_404(Country, id=country_id)
            if keywords['city'] != -1:
                city_id = keywords['city']
                filters['city'] = get_object_or_404(City, id=city_id)
            if keywords['cuisine'] != -1:
                cuisine_id = keywords['cuisine']
                filters['cuisine'] = get_object_or_404(Cuisine, id=cuisine_id)
            restaurants = Restaurant.objects.filter(**filters)
            if name_exists:
                restaurants = restaurants.filter(name__icontains=name)
            print(filters)
        if pageno != -1:
            if (pageno + 1) * 5 > restaurants.count():
                next_exists = False
            restaurants = restaurants[pageno * 5:pageno * 5 + 5]
        context = {
            'restaurants': restaurants,
            'pageno': pageno,
            'link': link,
            'next_exists': next_exists
        }
        return render(request, 'home.html', context)


class PrevPageView(View):
    def get(self, request, link, pageno):
        next_exists = True
        if link == "all":
            restaurants = Restaurant.objects.all()
        else:
            keywords = {'country': -1, 'city': -1, 'cuisine': -1}
            print(link)
            link_to_list = link.split("-")
            print(link_to_list)
            filters = {}
            name = ""
            name_exists = False
            for pair in link_to_list:
                if pair.split("=")[0] == "name":
                    name_exists = True
                    name = pair.split("=")[1]
                else:
                    keywords[pair.split("=")[0]] = int(pair.split("=")[1])
            if keywords['country'] != -1:
                country_id = keywords['country']
                filters['country'] = get_object_or_404(Country, id=country_id)
            if keywords['city'] != -1:
                city_id = keywords['city']
                filters['city'] = get_object_or_404(City, id=city_id)
            if keywords['cuisine'] != -1:
                cuisine_id = keywords['cuisine']
                filters['cuisine'] = get_object_or_404(Cuisine, id=cuisine_id)
            restaurants = Restaurant.objects.filter(**filters)
            if name_exists:
                restaurants = restaurants.filter(name__icontains=name)
            print(filters)
        if pageno > 0:
            pageno = pageno - 1
            if (pageno + 1) * 5 > restaurants.count():
                next_exists = False
            restaurants = restaurants[pageno * 5:pageno * 5 + 5]
        context = {
            'restaurants': restaurants,
            'pageno': pageno,
            'link': link,
            'next_exists': next_exists
        }
        return render(request, 'home.html', context)


class NextPageView(View):
    def get(self, request, link, pageno):
        next_exists = True
        if link == "all":
            restaurants = Restaurant.objects.all()
        else:
            keywords = {'country': -1, 'city': -1, 'cuisine': -1}
            print(link)
            link_to_list = link.split("-")
            print(link_to_list)
            filters = {}
            next_exists = True
            name = ""
            name_exists = False
            for pair in link_to_list:
                if pair.split("=")[0] == "name":
                    name_exists = True
                    name = pair.split("=")[1]
                else:
                    keywords[pair.split("=")[0]] = int(pair.split("=")[1])
            if keywords['country'] != -1:
                country_id = keywords['country']
                filters['country'] = get_object_or_404(Country, id=country_id)
            if keywords['city'] != -1:
                city_id = keywords['city']
                filters['city'] = get_object_or_404(City, id=city_id)
            if keywords['cuisine'] != -1:
                cuisine_id = keywords['cuisine']
                filters['cuisine'] = get_object_or_404(Cuisine, id=cuisine_id)
            restaurants = Restaurant.objects.filter(**filters)
            if name_exists:
                restaurants = restaurants.filter(name__icontains=name)
            print(filters)
        if pageno != -1:
            pageno = pageno + 1
            if (pageno + 1) * 5 > restaurants.count():
                next_exists = False
            restaurants = restaurants[pageno * 5:pageno * 5 + 5]
        context = {
            'restaurants': restaurants,
            'pageno': pageno,
            'link': link,
            'next_exists': next_exists
        }
        return render(request, 'home.html', context)


class SearchView(View):
    def get(self, request):
        form = SearchRestaurantForm()
        return render(request, 'searchrestaurant.html', context={'form': form})

    def post(self, request):
        form = SearchRestaurantForm(request.POST)
        if form.is_valid():
            link = ""
            if form.cleaned_data.get('name') is not None:
                name = form.cleaned_data.get('name')
                link = link + "name=" + str(name) + "-"
            if form.cleaned_data.get('country') is not None:
                country_id = form.cleaned_data.get('country').id
                link = link + "country=" + str(country_id) + "-"
            if form.cleaned_data.get('city') is not None:
                city_id = form.cleaned_data.get('city').id
                link = link + "city=" + str(city_id) + "-"
            if form.cleaned_data.get('cuisine') is not None:
                cuisine_id = form.cleaned_data.get('cuisine').id
                link = link + "cuisine=" + str(cuisine_id) + "-"
            if link != "":
                link = link[:-1]
            else:
                link = "all"
            return redirect(f'restrictedhome/{link}/0')
        return render(request, 'searchrestaurant.html', context={'form': form})


class HomeView(View):
    def get(self, request, *args, **kwargs):
        restaurants = Restaurant.objects.all()
        context = {
            'restaurants': restaurants,
        }
        return render(request, 'home.html', context)
