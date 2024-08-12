# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Restaurant, Food, User, Comment
from .forms import UserCreationForm, AddRestaurantForm, AddMealForm, AddCommentForm
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg


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
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.point = 0
            restaurant.save()
            return redirect('home')
        return render(request, 'addrestaurant.html', {'form': form})


class RestaurantDetailView(View):
    def get(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        rating = restaurant.find_rating()
        form = AddCommentForm()
        return render(request, 'restaurantdetail.html', {'restaurant': restaurant, 'form': form, 'rating': rating})

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
        return redirect('home')


class AddMealView(View):
    def get(self, request, id):
        form = AddMealForm()
        restaurant = get_object_or_404(Restaurant, id=id)
        return render(request, 'addmeal.html', {'form': form, 'restaurant': restaurant})

    def post(self, request, id):
        form = AddMealForm(request.POST)
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
