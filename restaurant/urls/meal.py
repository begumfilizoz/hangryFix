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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from restaurant.views.restaurant_views import (
    AddMealView, RemoveMealsView,
    RemoveMealView,
)

urlpatterns = [
    path('add_meal/<int:id>/', AddMealView.as_view(), name='add_meal'),
    path('remove_meals/<int:id>/', RemoveMealsView.as_view(), name='remove_meals'),
    path('remove_meal/<int:food_id>/<int:res_id>/', RemoveMealView.as_view(), name='remove_meal'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
