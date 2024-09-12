# Create your views here.
from urllib.parse import urlencode

from cities_light.models import City, Country
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from restaurant.forms import SearchRestaurantForm
from restaurant.models import Restaurant, Cuisine


class RestrictedHomeView(View):
    def get(self, request, page_no):
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
        if page_no != -1:
            if (page_no + 1) * 5 > restaurants.count():
                next_exists = False
            restaurants.order_by('id')
            restaurants = restaurants[page_no * 5:page_no * 5 + 5]
        context = {
            'restaurants': restaurants,
            'page_no': page_no,
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
            return redirect(f'/restricted_home/0/?{query_string}')

        return render(request, 'searchrestaurant.html', context={'form': form})


class HomeView(View):
    def get(self, request, *args, **kwargs):
        restaurants = Restaurant.objects.all()
        context = {
            'restaurants': restaurants,
        }
        return render(request, 'home.html', context)
