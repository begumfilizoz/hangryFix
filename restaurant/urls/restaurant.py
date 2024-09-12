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
from django.urls import path, include

from restaurant.views.home_views import (HomeView, RestrictedHomeView, SearchView)
from restaurant.views.restaurant_views import (DeleteBookingOwnerView, DeleteBookingView, BookNextDay, BookPrevDay, PickSlotView, AddRestaurantView, RestaurantDetailView, AddMealView, RemoveMealsView, RemoveMealView, RemoveRestaurantView,
                                               DeleteCommentFromRestView, MenuView, GetCitiesAndCountriesView, LikeUnlikeReviewView, BookingView)
from restaurant.views.user_action_views import (RestaurantRecommendationsView, ApproveBookingView, ManageBookingsRestaurantView, RestaurantsListView, BookingsView, OtherFavoritesView, MakeFavoritesPublicView, MakeFavoritesPrivateView, RemoveFromFavoritesProfileView, AddToFavoritesView, RemoveFromFavoritesView, SignUpView, LogInView, ContactView, ProfileView, LogoutView, DeleteCommentFromProfileView, DeleteUserView, MakeUserOwnerView, OtherProfileView, FavoritesView)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('add_restaurant/', AddRestaurantView.as_view(), name='add_restaurant'),
    path('restaurant/<int:id>/<int:page_no>/', RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('book_a_table/<int:id>/', BookingView.as_view(), name='book_a_table'),
    path('menu/<int:id>/', MenuView.as_view(), name='menu'),
    path('remove_restaurant/<int:res_id>/<int:user_id>/', RemoveRestaurantView.as_view(), name='remove_restaurant'),
    path('delete_comment_from_rest/<int:rest_id>/<int:comment_id>/', DeleteCommentFromRestView.as_view(),
         name='delete_comment_from_rest'),
    path('get_cities_and_countries/', GetCitiesAndCountriesView.as_view(), name='get_cities_and_countries'),
    path('like_unlike_comment/<int:id>/<int:page_no>/', LikeUnlikeReviewView.as_view(), name='like_unlike_comment'),
    path('add_to_favorites/<int:id>/<int:page_no>/', AddToFavoritesView.as_view(), name='add_to_favorites'),
    path('remove_from_favorites/<int:id>/<int:page_no>/', RemoveFromFavoritesView.as_view(), name='remove_from_favorites'),
    path('pick_the_slot/<int:rest_id>/<int:slot_id>/<int:number>/', PickSlotView.as_view(), name='pick_the_slot'),
    path('book_next_day/<int:id>/<str:date>/<int:number>/', BookNextDay.as_view(), name='book_next_day'),
    path('book_prev_day/<int:id>/<str:date>/<int:number>/', BookPrevDay.as_view(), name='book_prev_day'),
    path('your_bookings/', BookingsView.as_view(), name='your_bookings'),
    path('delete_booking/<int:id>/', DeleteBookingView.as_view(), name='delete_booking'),
    path('delete_booking_owner/<int:id>/', DeleteBookingOwnerView.as_view(), name='delete_booking_owner'),
    path('restaurant_list_bookings/', RestaurantsListView.as_view(), name='restaurant_list_bookings'),
    path('manage_bookings/<int:id>/', ManageBookingsRestaurantView.as_view(), name='manage_bookings'),
    path('approve_booking/<int:id>/', ApproveBookingView.as_view(), name='approve_booking'),
    path('restaurant_recommendations/', RestaurantRecommendationsView.as_view(), name='restaurant_recommendations'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
