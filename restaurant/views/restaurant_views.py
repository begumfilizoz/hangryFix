# Create your views here.
import math
from datetime import datetime, timedelta

import folium
from cities_light.models import City
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import View

from restaurant.forms import AddRestaurantForm, AddMealForm, AddCommentForm, BookingForm
from restaurant.models import Restaurant, Food, Comment, Like, ThirtyMinuteBookingSlot, TwoHourBookingSlot, Booking
from restaurant.utils import create_booking_slots, process_slots


class AddRestaurantView(View):
    def get(self, request):
        form = AddRestaurantForm()
        return render(request, 'addrestaurant.html', {'form': form})

    def post(self, request):
        form = AddRestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            # saves the restaurant to the database
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.point = 0
            restaurant.save()
            return redirect('search')
        return render(request, 'addrestaurant.html', {'form': form})


class GetCitiesAndCountriesView(View):
    def get(self, request):
        # returns the cities that are in a particular country
        country_id = request.GET.get('country_id')
        cities = City.objects.filter(country_id=country_id)
        cities_data = list(cities.values('id', 'name'))
        return JsonResponse(cities_data, safe=False)


class RestaurantDetailView(View):
    def get(self, request, id, page_no):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True

        # gets the likes given by the logged in user
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)

        # gets the comments made for that restaurant
        comments = Comment.objects.filter(restaurant=restaurant)

        # checks if there are more comments to be displayed in the next page and takes the first 5 comments based on
        # page no
        if (page_no + 1) * 5 > comments.count():
            next_exists = False
        comments = comments[page_no * 5:page_no * 5 + 5]

        # finds the comments liked by that user for this restaurant
        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)

        rating = restaurant.find_rating()
        form = AddCommentForm()

        # shows the location of the restaurant on the map
        m = folium.Map(location=[restaurant.lat, restaurant.lng], zoom_start=15)
        folium.Marker([restaurant.lat, restaurant.lng], popup=restaurant.name).add_to(m)
        map_html = m._repr_html_()

        if request.user.is_authenticated and request.user.favorites in restaurant.favorites.all():
            restaurant_in_favorites = True
        else:
            restaurant_in_favorites = False
        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'page_no': page_no,
                       'restaurant_in_favorites': restaurant_in_favorites})

    def post(self, request, id, page_no):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True

        # gets the likes given by the logged in user
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)

        # checks if there are more comments to be displayed in the next page and takes the first 5 comments based on
        # page no
        if (page_no + 1) * 5 > comments.count():
            next_exists = False
        comments = comments[page_no * 5:page_no * 5 + 5]

        # finds the comments liked by that user for this restaurant
        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)

        rating = restaurant.find_rating()
        form = AddCommentForm()

        # shows the location of the restaurant on the map
        m = folium.Map(location=[restaurant.lat, restaurant.lng], zoom_start=15)
        folium.Marker([restaurant.lat, restaurant.lng], popup=restaurant.name).add_to(m)
        map_html = m._repr_html_()

        # gets the form data and saves comment
        form = AddCommentForm(request.POST)
        if request.user.is_authenticated and request.user.favorites in restaurant.favorites.all():
            restaurant_in_favorites = True
        else:
            restaurant_in_favorites = False
        if form.is_valid():
            comment = form.save(commit=False)
            comment.restaurant = restaurant
            comment.user = request.user
            comment.save()
            rating = restaurant.find_rating()
            restaurant.point = rating
            restaurant.save()
            return redirect('restaurant_detail', id=restaurant.id, page_no=page_no)

        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'page_no': page_no,
                       'restaurant_in_favorites': restaurant_in_favorites})


class LikeUnlikeReviewView(View):
    def post(self, request, id, page_no):
        comment = get_object_or_404(Comment, id=id)
        restaurant = get_object_or_404(Restaurant, id=comment.restaurant.id)
        user = request.user

        if user.is_authenticated:
            liked = Like.objects.filter(user=user, comment=comment).exists()

            # figure out whether to show "like" or "unlike" button
            if liked:
                Like.objects.filter(user=user, comment=comment).delete()
                message = 'You unliked the review.'
                liked = False
            else:
                Like.objects.create(user=user, comment=comment)
                message = 'You liked the review.'
                liked = True

            response_data = {
                'success': True,
                'message': message,
                'liked': liked,
                'restaurant_id': restaurant.id,
                'page_no': page_no
            }
            return JsonResponse(response_data)
        else:
            response_data = {
                'success': False,
                'message': 'Log in to like the review.'
            }
            return JsonResponse(response_data)


class MenuView(View):
    def get(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        return render(request, 'menu.html', {'restaurant': restaurant})


class DeleteCommentFromRestView(View):
    def post(self, request, rest_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return redirect('restaurant_detail', id=rest_id, page_no=0)


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
    def post(self, request, food_id, res_id):
        food = get_object_or_404(Food, id=food_id)
        food.delete()
        return redirect('remove_meals', id=res_id)


class RemoveRestaurantView(View):
    def post(self, request, res_id, user_id):
        restaurant = get_object_or_404(Restaurant, id=res_id)
        restaurant.delete()
        return redirect('profile', id=user_id)


class BookingView(View):
    def get(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        form = BookingForm()
        return render(request, 'bookrestaurant.html', {"restaurant": restaurant, "form": form})

    def post(self, request, id):
        restaurant = get_object_or_404(Restaurant, id=id)
        form = BookingForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['date'] is not None and form.cleaned_data['number_of_people'] is not None:
                date = form.cleaned_data.get('date')

                # check if the date selected is today or after today
                page_valid = True
                if date < timezone.now().date():
                    page_valid = False

                # check if the date before today is valid
                prev_date = date - timedelta(days=1)
                prev_exists = True
                if prev_date < timezone.now().date():
                    prev_exists = False

                # fetch info and create slots
                number_of_people = form.cleaned_data.get('number_of_people')
                count, two_hour_booking_slots = create_booking_slots(date, restaurant, number_of_people)
            return render(request, 'slotpick.html',
                          {"page_valid": page_valid, "prev_exists": prev_exists, "count": count, "date": date,
                           "restaurant": restaurant, "two_hour_booking_slots": two_hour_booking_slots,
                           "number_of_people": number_of_people})
        return render(request, 'bookrestaurant.html', {"restaurant": restaurant, "form": form})


class PickSlotView(View):
    def post(self, request, rest_id, slot_id, number):
        # fetch the data to save the booking
        restaurant = get_object_or_404(Restaurant, id=rest_id)
        slot = get_object_or_404(TwoHourBookingSlot, id=slot_id)
        booking = Booking(restaurant=restaurant, user=request.user, date=slot.date, start_time=slot.start_time,
                          end_time=slot.end_time, number_of_people=number)
        booking.save()

        # set the 30-minute slots to be altered
        # if the slots already exist (meaning that they have been booked before) just decrease the number of available
        # tables, otherwise create new slots and then decrease the available tables
        start_time = datetime.combine(slot.date, slot.start_time)
        slots = []
        for i in range(4):
            slot1 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time.time(),
                                                          date=slot.date).first()
            if slot1 is None:
                slot1 = ThirtyMinuteBookingSlot(restaurant=restaurant, start_time=start_time.time(), date=slot.date,
                                               free_tables=restaurant.tables)
            slots.append(slot1)
            start_time = start_time + timedelta(minutes=30)

        # increase occupied tables, decrease free tables and save the slots
        number_of_tables_required = math.ceil(number / restaurant.people_per_table)
        for slot1 in slots:
            slot1.occupied_tables += number_of_tables_required
            slot1.free_tables -= number_of_tables_required
            slot1.save()

        messages.success(request,
                         "Booking request completed successfully. Check your profile for updates on your request.")
        return redirect('restaurant_detail', id=restaurant.id, page_no=0)


class BookNextDay(View):  # same as BookingView, however this shows the next day
    def post(self, request, id, date, number):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_date = datetime.strptime(date, "%Y-%m-%d").date()
        date = next_date + timedelta(days=1)
        page_valid = True

        if date < timezone.now().date():
            page_valid = False
        prev_date = date - timedelta(days=1)
        prev_exists = True
        if prev_date < timezone.now().date():
            prev_exists = False
        number_of_people = number
        count, two_hour_booking_slots = create_booking_slots(date, restaurant, number_of_people)
        return render(request, 'slotpick.html',
                      {"page_valid": page_valid, "prev_exists": prev_exists, "count": count, "date": date,
                       "restaurant": restaurant, "two_hour_booking_slots": two_hour_booking_slots,
                       "number_of_people": number_of_people})


class BookPrevDay(View):  # same as BookingView, however this shows the previous day
    def post(self, request, id, date, number):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_date = datetime.strptime(date, "%Y-%m-%d").date()
        date = next_date - timedelta(days=1)
        page_valid = True
        if date < timezone.now().date():
            page_valid = False
        prev_date = date - timedelta(days=1)
        prev_exists = True
        if prev_date < timezone.now().date():
            prev_exists = False
        number_of_people = number
        count, two_hour_booking_slots = create_booking_slots(date, restaurant, number_of_people)
        return render(request, 'slotpick.html',
                      {"page_valid": page_valid, "prev_exists": prev_exists, "count": count, "date": date,
                       "restaurant": restaurant, "two_hour_booking_slots": two_hour_booking_slots,
                       "number_of_people": number_of_people})


class DeleteBookingView(View):
    def post(self, request, id):
        # fetch data
        booking = get_object_or_404(Booking, id=id)
        restaurant = booking.restaurant
        start_time = datetime.combine(booking.date, booking.start_time)
        process_slots(restaurant, booking)
        booking.delete()
        bookings = Booking.objects.filter(user=request.user).order_by('id')
        count = bookings.count()
        messages.success(request,
                         "Booking request deleted successfully.")
        return render(request, 'userbookings.html', {'count': count, 'bookings': bookings})


class DeleteBookingOwnerView(View):

    # same as DeleteBookingView, but for the owner to cancel bookings
    def post(self, request, id):
        booking = get_object_or_404(Booking, id=id)
        restaurant = booking.restaurant
        process_slots(restaurant, booking)
        restaurant = booking.restaurant
        booking.delete()
        bookings = Booking.objects.filter(restaurant=restaurant).order_by('id')
        requested_user = request.user
        count = bookings.count()
        messages.success(request,
                         "Booking request deleted successfully.")
        return render(request, 'bookingslist.html',
                      {'count': count, 'restaurant': restaurant, 'bookings': bookings,
                       'requested_user': requested_user})

