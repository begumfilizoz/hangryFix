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
from urllib.parse import urlencode


class RestrictedHomeView(View):
    def get(self, request, pageno):
        next_exists = True
        filters = {}
        name = request.GET.get('name')
        country_id = request.GET.get('country')
        city_id = request.GET.get('city')
        cuisine_id = request.GET.get('cuisine')
        if country_id:
            filters['country'] = get_object_or_404(Country, id=country_id)
        if city_id:
            filters['city'] = get_object_or_404(City, id=city_id)
        if cuisine_id:
            filters['cuisine'] = get_object_or_404(Cuisine, id=cuisine_id)
        restaurants = Restaurant.objects.filter(**filters)
        if name:
            restaurants = restaurants.filter(name__icontains=name)
        if pageno != -1:
            if (pageno + 1) * 5 > restaurants.count():
                next_exists = False
            restaurants.order_by('id')
            restaurants = restaurants[pageno * 5:pageno * 5 + 5]
        context = {
            'restaurants': restaurants,
            'pageno': pageno,
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
            query_params = {}

            # Fetch the data from the search form and add to query_params
            if form.cleaned_data.get('name'):
                name = form.cleaned_data.get('name')
                query_params['name'] = name

            if form.cleaned_data.get('country'):
                country_id = form.cleaned_data.get('country').id
                query_params['country'] = country_id

            if form.cleaned_data.get('city'):
                city_id = form.cleaned_data.get('city').id
                query_params['city'] = city_id

            if form.cleaned_data.get('cuisine'):
                cuisine_id = form.cleaned_data.get('cuisine').id
                query_params['cuisine'] = cuisine_id

            # Build the query string using urlencode
            if query_params:
                query_string = urlencode(query_params)
            else:
                query_string = "all=1"  # Default if no parameters are selected

            # Redirect to the URL with query parameters
            return redirect(f'/restrictedhome/0/?{query_string}')

        return render(request, 'searchrestaurant.html', context={'form': form})


class HomeView(View):
    def get(self, request, *args, **kwargs):
        restaurants = Restaurant.objects.all()
        context = {
            'restaurants': restaurants,
        }
        return render(request, 'home.html', context)
