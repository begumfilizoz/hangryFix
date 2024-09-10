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
from restaurant.home_views import (HomeView, RestrictedHomeView, SearchView)
from restaurant.restaurant_views import (DeleteBookingOwnerView, DeleteBookingView, BookNextDay, BookPrevDay, PickSlotView, AddRestaurantView, RestaurantDetailView, AddMealView, RemoveMealsView, RemoveMealView, RemoveRestaurantView,
                              DeleteCommentFromRestView, MenuView, GetCitiesAndCountriesView, LikeUnlikeReviewView, BookingView)
from restaurant.user_action_views import (RestaurantRecommendationsView, ApproveBookingView, ManageBookingsRestaurantView, RestaurantsListView, BookingsView,OtherFavoritesView, MakeFavoritesPublicView, MakeFavoritesPrivateView, RemoveFromFavoritesProfileView, AddToFavoritesView, RemoveFromFavoritesView, SignUpView, LogInView, ContactView, ProfileView, LogoutView, DeleteCommentFromProfileView, DeleteUserView, MakeUserOwnerView, OtherProfileView, FavoritesView)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', HomeView.as_view(), name='home'),
    path('', SearchView.as_view(), name='search'),
    path('restrictedhome/<int:pageno>/', RestrictedHomeView.as_view(), name='restrictedhome'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LogInView.as_view(), name='login'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('addrestaurant/', AddRestaurantView.as_view(), name='addrestaurant'),
    path('restaurant/<int:id>/<int:pageno>/', RestaurantDetailView.as_view(), name='restaurantdetail'),
    path('bookatable/<int:id>/', BookingView.as_view(), name='bookatable'),
    path('menu/<int:id>/', MenuView.as_view(), name='menu'),
    path('profile/<int:id>/', ProfileView.as_view(), name='profile'),
    path('otherprofile/<int:id>/', OtherProfileView.as_view(), name='otherprofile'),
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
    path('likeunlikecomment/<int:id>/<int:pageno>/', LikeUnlikeReviewView.as_view(), name='likeunlikecomment'),
    path('addtofavorites/<int:id>/<int:pageno>/', AddToFavoritesView.as_view(), name='addtofavorites'),
    path('removefromfavorites/<int:id>/<int:pageno>/', RemoveFromFavoritesView.as_view(), name='removefromfavorites'),
    path('favorites/<int:id>/<int:page_no>/', FavoritesView.as_view(), name='favorites'),
    path('removefromfavoritesprofile/<int:id>/<int:page_no>/', RemoveFromFavoritesProfileView.as_view(), name='removefromfavoritesprofile'),
    path('make-public/', MakeFavoritesPublicView.as_view(), name='make-public'),
    path('make-private/', MakeFavoritesPrivateView.as_view(), name='make-private'),
    path('other-favorites/<int:id>/<int:page_no>/', OtherFavoritesView.as_view(), name='other-favorites'),
    path('pick-the-slot/<int:rest_id>/<int:slot_id>/<int:number>/', PickSlotView.as_view(), name='pick-the-slot'),
    path('book-next-day/<int:id>/<str:date>/<int:number>/', BookNextDay.as_view(), name='book-next-day'),
    path('book-prev-day/<int:id>/<str:date>/<int:number>/', BookPrevDay.as_view(), name='book-prev-day'),
    path('your-bookings/', BookingsView.as_view(), name='your-bookings'),
    path('delete-booking/<int:id>/', DeleteBookingView.as_view(), name='delete-booking'),
    path('delete-booking-owner/<int:id>/', DeleteBookingOwnerView.as_view(), name='delete-booking-owner'),
    path('restaurant-list-bookings/', RestaurantsListView.as_view(), name='restaurant-list-bookings'),
    path('manage-bookings/<int:id>/', ManageBookingsRestaurantView.as_view(), name='manage-bookings'),
    path('approve-booking/<int:id>/', ApproveBookingView.as_view(), name='approve-booking'),
    path('restaurant-recommendations/', RestaurantRecommendationsView.as_view(), name='restaurant-recommendations'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
