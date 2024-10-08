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
import restaurant
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('meal/', include('restaurant.urls.meal')),
    path('restaurant/', include('restaurant.urls.restaurant')),
    path('user/', include('restaurant.urls.user')),
    path('home/', HomeView.as_view(), name='home'),
    path('', SearchView.as_view(), name='search'),
    path('restricted_home/<int:page_no>/', RestrictedHomeView.as_view(), name='restricted_home'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
