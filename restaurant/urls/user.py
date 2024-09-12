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

from restaurant.views.user_action_views import (RestaurantRecommendationsView, ApproveBookingView, ManageBookingsRestaurantView, RestaurantsListView, BookingsView, OtherFavoritesView, MakeFavoritesPublicView, MakeFavoritesPrivateView, RemoveFromFavoritesProfileView, AddToFavoritesView, RemoveFromFavoritesView, SignUpView, LogInView, ContactView, ProfileView, LogoutView, DeleteCommentFromProfileView, DeleteUserView, MakeUserOwnerView, OtherProfileView, FavoritesView)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LogInView.as_view(), name='login'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('profile/<int:id>/', ProfileView.as_view(), name='profile'),
    path('other_profile/<int:id>/', OtherProfileView.as_view(), name='other_profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete_comment_from_profile/<int:comment_id>/', DeleteCommentFromProfileView.as_view(),
         name='delete_comment_from_profile'),
    path('delete_user/', DeleteUserView.as_view(), name='delete_user'),
    path('make_user_an_owner/', MakeUserOwnerView.as_view(), name='make_user_owner'),
    path('favorites/<int:id>/<int:page_no>/', FavoritesView.as_view(), name='favorites'),
    path('remove_from_favorites_profile/<int:id>/<int:page_no>/', RemoveFromFavoritesProfileView.as_view(), name='remove_from_favorites_profile'),
    path('make_public/', MakeFavoritesPublicView.as_view(), name='make_public'),
    path('make_private/', MakeFavoritesPrivateView.as_view(), name='make_private'),
    path('other_favorites/<int:id>/<int:page_no>/', OtherFavoritesView.as_view(), name='other_favorites'),
   ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
