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


class RestrictedHomeView(View):
    def get(self, request, link, pageno):
        keywords = {'country' : -1, 'city' : -1, 'cuisine' : -1}
        print(link)
        link_to_list = link.split("-")
        print(link_to_list)
        filters = {}
        next_exists = True
        for pair in link_to_list:
            keywords[pair.split("=")[0]] = int(pair.split("=")[1])
        if keywords['country'] != -1:
            countryId = keywords['country']
            filters['country'] = get_object_or_404(Country, id=countryId)
        if keywords['city'] != -1:
            cityId = keywords['city']
            filters['city'] = get_object_or_404(City, id=cityId)
        if keywords['cuisine'] != -1:
            cuisineId = keywords['cuisine']
            filters['cuisine'] = get_object_or_404(Cuisine, id=cuisineId)
        restaurants = Restaurant.objects.filter(**filters).order_by('point')
        print(filters)
        if pageno != -1:
            restaurants = restaurants[pageno * 5:pageno * 5 + 5]
        users = User.objects.all()
        if (pageno + 1) * 5 > restaurants.count():
           next_exists = False
        context = {
            'restaurants': restaurants,
            'users': users,
            'pageno': pageno,
            'link': link,
            'next_exists': next_exists
        }
        return render(request, 'home.html', context)

class PrevPageView(View):
    def get(self, request, link, pageno):
        keywords = {'country' : -1, 'city' : -1, 'cuisine' : -1}
        print(link)
        link_to_list = link.split("-")
        print(link_to_list)
        next_exists = True
        filters = {}
        for pair in link_to_list:
            keywords[pair.split("=")[0]] = int(pair.split("=")[1])
        if keywords['country'] != -1:
            countryId = keywords['country']
            filters['country'] = get_object_or_404(Country, id=countryId)
        if keywords['city'] != -1:
            cityId = keywords['city']
            filters['city'] = get_object_or_404(City, id=cityId)
        if keywords['cuisine'] != -1:
            cuisineId = keywords['cuisine']
            filters['cuisine'] = get_object_or_404(Cuisine, id=cuisineId)
        restaurants = Restaurant.objects.filter(**filters).order_by('point')
        print(filters)
        if pageno > 0:
            pageno = pageno - 1
            restaurants = restaurants[pageno * 5:pageno * 5 + 5]
        users = User.objects.all()
        if (pageno + 1) * 5 > restaurants.count():
           next_exists = False
        context = {
            'restaurants': restaurants,
            'users': users,
            'pageno': pageno,
            'link': link,
            'next_exists': next_exists
        }
        return render(request, 'home.html', context)


class NextPageView(View):
    def get(self, request, link, pageno):
        keywords = {'country' : -1, 'city' : -1, 'cuisine' : -1}
        print(link)
        link_to_list = link.split("-")
        print(link_to_list)
        filters = {}
        next_exists = True
        for pair in link_to_list:
            keywords[pair.split("=")[0]] = int(pair.split("=")[1])
        if keywords['country'] != -1:
            countryId = keywords['country']
            filters['country'] = get_object_or_404(Country, id=countryId)
        if keywords['city'] != -1:
            cityId = keywords['city']
            filters['city'] = get_object_or_404(City, id=cityId)
        if keywords['cuisine'] != -1:
            cuisineId = keywords['cuisine']
            filters['cuisine'] = get_object_or_404(Cuisine, id=cuisineId)
        restaurants = Restaurant.objects.filter(**filters).order_by('point')
        print(filters)
        if pageno != -1:
            pageno = pageno + 1
            restaurants = restaurants[pageno * 5:pageno * 5 + 5]
        users = User.objects.all()
        if (pageno + 1) * 5 > restaurants.count():
           next_exists = False
        context = {
            'restaurants': restaurants,
            'users': users,
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
            if form.cleaned_data.get('country') is not None:
                countryId = form.cleaned_data.get('country').id
                link = link + "country=" + str(countryId) + "-"
            if form.cleaned_data.get('city') is not None:
                cityId = form.cleaned_data.get('city').id
                link = link + "city=" + str(cityId) + "-"
            if form.cleaned_data.get('cuisine') is not None:
                cuisineId = form.cleaned_data.get('cuisine').id
                link = link + "cuisine=" + str(cuisineId) + "-"
            link = link[:-1]
            return redirect(f'restrictedhome/{link}/0')
        return render(request, 'searchrestaurant.html', context={'form': form})




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
    def get(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)
        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)
        rating = restaurant.find_rating()
        form = AddCommentForm()
        return render(request, 'restaurantdetail.html', {'liked_comments': liked_comments, 'restaurant': restaurant, 'form': form, 'rating': rating})

    def post(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        form = AddCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.restaurant = restaurant
            comment.user = request.user
            comment.save()
            return redirect('restaurantdetail', id=restaurant.id)
        return render(request, 'restaurantdetail.html', {'restaurant': restaurant, 'form': form})


class LikeUnlikeReviewView(View):
    def post(self, request, id):
        comment = get_object_or_404(Comment, id=id)
        restaurant = get_object_or_404(Restaurant, id=comment.restaurant.id)
        user = request.user
        if user.is_authenticated:
            if Like.objects.filter(user=user, comment=comment).exists():
                Like.objects.filter(user=user, comment=comment).delete()
                messages.success(request, 'You unliked the review.')
                return redirect('restaurantdetail', id=restaurant.id)
            else:
                Like.objects.create(user=user, comment=comment)
                messages.success(request, 'You liked the review.')
                return redirect('restaurantdetail', id=restaurant.id)
        else:
            messages.success(request, 'Log in to like the review.')
            return redirect('restaurantdetail', id=restaurant.id)


class MenuView(View):
    def get(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        return render(request, 'menu.html', {'restaurant': restaurant})


class DeleteCommentFromRestView(View):
    def post(self, request, restId, commentId):
        comment = get_object_or_404(Comment, id=commentId)
        comment.delete()
        return redirect('restaurantdetail', id=restId)


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


class DeleteUserView(View):
    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        logout(request)
        user.delete()
        return redirect('login')
