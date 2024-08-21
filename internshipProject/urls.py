"""
URL configuration for internshipProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from restaurant.home_views import (HomeView, RestrictedHomeView, SearchView, NextPageView, PrevPageView)
from restaurant.restaurant_views import (AddRestaurantView, RestaurantDetailView, AddMealView, RemoveMealsView, RemoveMealView, RemoveRestaurantView,
                              DeleteCommentFromRestView, MenuView, GetCitiesAndCountriesView, LikeUnlikeReviewView)
from restaurant.user_action_views import (SignUpView, LogInView, ContactView, ProfileView, LogoutView, DeleteCommentFromProfileView, DeleteUserView, MakeUserOwnerView)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', HomeView.as_view(), name='home'),
    path('', SearchView.as_view(), name='search'),
    path('restrictedhome/<str:link>/<int:pageno>/', RestrictedHomeView.as_view(), name='restrictedhome'),
    path('nextpage/<str:link>/<int:pageno>', NextPageView.as_view(), name='nextpage'),
    path('prevpage/<str:link>/<int:pageno>', PrevPageView.as_view(), name='prevpage'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LogInView.as_view(), name='login'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('addrestaurant/', AddRestaurantView.as_view(), name='addrestaurant'),
    path('restaurant/<int:id>/', RestaurantDetailView.as_view(), name='restaurantdetail'),
    path('menu/<int:id>/', MenuView.as_view(), name='menu'),
    path('profile/<int:id>/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('addmeal/<int:id>/', AddMealView.as_view(), name='addmeal'),
    path('removemeals/<int:id>/', RemoveMealsView.as_view(), name='removemeals'),
    path('removemeal/<int:foodId>/<int:resId>/', RemoveMealView.as_view(), name='removemeal'),
    path('removerestaurant/<int:resId>/<int:userId>/', RemoveRestaurantView.as_view(), name='removerestaurant'),
    path('deletecommentfromrest/<int:restId>/<int:commentId>/', DeleteCommentFromRestView.as_view(),
         name='deletecommentfromrest'),
    path('deletecommentfromprofile/<int:commentId>/', DeleteCommentFromProfileView.as_view(),
         name='deletecommentfromprofile'),
    path('deleteuser/', DeleteUserView.as_view(), name='deleteuser'),
    path('makeuseranowner/', MakeUserOwnerView.as_view(), name='makeuserowner'),
    path('getcitiesandcountries/', GetCitiesAndCountriesView.as_view(), name='getcitiesandcountries'),
    path('likeunlikecomment/<int:id>/', LikeUnlikeReviewView.as_view(), name='likeunlikecomment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
