# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.serializers import serialize
from .models import Restaurant, Food, User, Comment, ContactMessage, Like, Cuisine, FavoritesList, ThirtyMinuteBookingSlot, TwoHourBookingSlot, Booking
from .forms import UserCreationForm, AddRestaurantForm, AddMealForm, AddCommentForm, ContactForm, SearchRestaurantForm, BookingForm
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg
from django.http import JsonResponse
from cities_light.models import City, Country
from django.contrib import messages
import folium
from datetime import datetime, timedelta
import math
from django.utils import timezone


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
    def get(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True

        # gets the likes given by the logged in user
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)

        # gets the comments made for that restaurant
        comments = Comment.objects.filter(restaurant=restaurant)

        # checks if there are more comments to be displayed in the next page and takes the first 5 comments based on
        # page no
        if (pageno + 1) * 5 > comments.count():
            next_exists = False
        comments = comments[pageno * 5:pageno * 5 + 5]

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
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno, 'restaurant_in_favorites': restaurant_in_favorites})

    def post(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True

        # gets the likes given by the logged in user
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)

        # checks if there are more comments to be displayed in the next page and takes the first 5 comments based on
        # page no
        if (pageno + 1) * 5 > comments.count():
            next_exists = False
        comments = comments[pageno * 5:pageno * 5 + 5]

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
            return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)

        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno,
                       'restaurant_in_favorites': restaurant_in_favorites})


class PrevRestaurantDetailView(View):
    def get(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True

        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)

        if pageno > 0:
            pageno = pageno - 1
            if (pageno + 1) * 5 > comments.count():
                next_exists = False
            comments = comments[pageno * 5:pageno * 5 + 5]

        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)
        rating = restaurant.find_rating()
        form = AddCommentForm()

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
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno,
                       'restaurant_in_favorites': restaurant_in_favorites})

    def post(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True

        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)

        if pageno > 0:
            pageno = pageno - 1
            if (pageno + 1) * 5 > comments.count():
                next_exists = False
            comments = comments[pageno * 5:pageno * 5 + 5]

        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)
        rating = restaurant.find_rating()
        form = AddCommentForm()

        m = folium.Map(location=[restaurant.lat, restaurant.lng], zoom_start=15)
        folium.Marker([restaurant.lat, restaurant.lng], popup=restaurant.name).add_to(m)
        map_html = m._repr_html_()
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
            return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)

        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno,
                       'restaurant_in_favorites': restaurant_in_favorites})


class NextRestaurantDetailView(View):
    def get(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True

        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)

        if pageno != -1:
            pageno = pageno + 1
            if (pageno + 1) * 5 > comments.count():
                next_exists = False
            comments = comments[pageno * 5:pageno * 5 + 5]

        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)

        rating = restaurant.find_rating()
        form = AddCommentForm()

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
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno,
                       'restaurant_in_favorites': restaurant_in_favorites})
    def post(self, request, id, pageno):
        restaurant = get_object_or_404(Restaurant, id=id)
        next_exists = True
        if request.user.is_authenticated:
            likes = Like.objects.filter(user=request.user)
        comments = Comment.objects.filter(restaurant=restaurant)
        if pageno != -1:
            pageno = pageno + 1
            if (pageno + 1) * 5 > comments.count():
                next_exists = False
            comments = comments[pageno * 5:pageno * 5 + 5]
        liked_comments = []
        if request.user.is_authenticated:
            for like in likes:
                if like.comment in comments:
                    liked_comments.append(like.comment)
        rating = restaurant.find_rating()
        form = AddCommentForm()
        m = folium.Map(location=[restaurant.lat, restaurant.lng], zoom_start=15)
        folium.Marker([restaurant.lat, restaurant.lng], popup=restaurant.name).add_to(m)
        map_html = m._repr_html_()
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
            return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)

        return render(request, 'restaurantdetail.html',
                      {'comments': comments, 'map_html': map_html, 'liked_comments': liked_comments,
                       'restaurant': restaurant, 'form': form,
                       'rating': rating, 'next_exists': next_exists, 'pageno': pageno,
                       'restaurant_in_favorites': restaurant_in_favorites})


# class LikeUnlikeReviewView(View):
#     def post(self, request, id, pageno):
#         comment = get_object_or_404(Comment, id=id)
#         restaurant = get_object_or_404(Restaurant, id=comment.restaurant.id)
#         user = request.user
#         if user.is_authenticated:
#             if Like.objects.filter(user=user, comment=comment).exists():
#                 Like.objects.filter(user=user, comment=comment).delete()
#                 messages.success(request, 'You unliked the review.')
#                 return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)
#             else:
#                 Like.objects.create(user=user, comment=comment)
#                 messages.success(request, 'You liked the review.')
#                 return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)
#         else:
#             messages.success(request, 'Log in to like the review.')
#             return redirect('restaurantdetail', id=restaurant.id, pageno=pageno)


class LikeUnlikeReviewView(View):
    def post(self, request, id, pageno):
        comment = get_object_or_404(Comment, id=id)
        restaurant = get_object_or_404(Restaurant, id=comment.restaurant.id)
        user = request.user

        if user.is_authenticated:
            liked = Like.objects.filter(user=user, comment=comment).exists()

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
                'pageno': pageno
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
    def post(self, request, restId, commentId):
        comment = get_object_or_404(Comment, id=commentId)
        comment.delete()
        return redirect('restaurantdetail', id=restId, pageno=0)


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
                page_valid = True
                if date < timezone.now().date():
                    page_valid = False
                prev_date = date - timedelta(days=1)
                prev_exists = True
                if prev_date < timezone.now().date():
                    prev_exists = False
                number_of_people = form.cleaned_data.get('number_of_people')
                start_time = datetime.combine(date, restaurant.start_time)
                end_time = datetime.combine(date, restaurant.end_time)
                start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
                end_time = timezone.make_aware(end_time, timezone.get_current_timezone())
                start_time = start_time.replace(minute=0, second=0, microsecond=0)
                end_time = end_time.replace(minute=0, second=0, microsecond=0)
                slots = []
                current_time = start_time
                while current_time < end_time:
                    if date > timezone.now().date() or (date == timezone.now().date() and current_time > timezone.now()):
                        slots.append(current_time)
                    current_time = current_time + timedelta(minutes=30)
                available_slots = []
                for slot in slots:
                    booking = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=slot.time(), date=date).first()
                    number_of_tables_required = math.ceil(number_of_people / restaurant.people_per_table)
                    if booking is not None and booking.free_tables > 0:
                        if booking.free_tables >= number_of_tables_required:
                            available_slots.append(slot)
                    elif booking is None:
                        if restaurant.tables >= number_of_tables_required:
                            available_slots.append(slot)
                print(available_slots)
                two_hour_booking_slots = []
                for slot in available_slots:
                    slot2 = slot + timedelta(minutes=30)
                    slot3 = slot2 + timedelta(minutes=30)
                    slot4 = slot3 + timedelta(minutes=30)
                    if slot2 in available_slots and slot3 in available_slots and slot4 in available_slots:
                        two_hour_slot = TwoHourBookingSlot(restaurant=restaurant, start_time=slot.time(), end_time=(slot4 + timedelta(minutes=30)).time(), date=date)
                        two_hour_slot.save()
                        two_hour_booking_slots.append(two_hour_slot)
                count = len(two_hour_booking_slots)
            return render(request, 'slotpick.html', {"page_valid": page_valid, "prev_exists": prev_exists, "count": count, "date": date, "restaurant": restaurant, "two_hour_booking_slots": two_hour_booking_slots, "number_of_people": number_of_people})
        return render(request, 'bookrestaurant.html', {"restaurant": restaurant, "form": form})


class PickSlotView(View):
    def post(self, request, rest_id, slot_id, number):
        restaurant = get_object_or_404(Restaurant, id=rest_id)
        slot = get_object_or_404(TwoHourBookingSlot, id=slot_id)
        booking = Booking(restaurant=restaurant, user=request.user, date=slot.date, start_time=slot.start_time, end_time=slot.end_time, number_of_people=number)
        booking.save()
        start_time = datetime.combine(slot.date, slot.start_time)
        start_time1 = start_time + timedelta(minutes=30)
        start_time2 = start_time1 + timedelta(minutes=30)
        start_time3 = start_time2 + timedelta(minutes=30)
        slot1 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time.time(), date=slot.date).first()
        if slot1 is None:
            slot1 = ThirtyMinuteBookingSlot(restaurant=restaurant, start_time=start_time.time(), date=slot.date, free_tables=restaurant.tables)
        slot2 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time1.time(), date=slot.date).first()
        if slot2 is None:
            slot2 = ThirtyMinuteBookingSlot(free_tables=restaurant.tables, restaurant=restaurant, start_time=start_time1.time(), date=slot.date)
        slot3 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time2.time(), date=slot.date).first()
        if slot3 is None:
            slot3 = ThirtyMinuteBookingSlot(free_tables=restaurant.tables, restaurant=restaurant, start_time=start_time2.time(), date=slot.date)
        slot4 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time3.time(), date=slot.date).first()
        if slot4 is None:
            slot4 = ThirtyMinuteBookingSlot(free_tables=restaurant.tables, restaurant=restaurant, start_time=start_time3.time(), date=slot.date)
        number_of_tables_required = math.ceil(number / restaurant.people_per_table)
        slot1.occupied_tables += number_of_tables_required
        slot2.occupied_tables += number_of_tables_required
        slot3.occupied_tables += number_of_tables_required
        slot4.occupied_tables += number_of_tables_required
        slot1.free_tables -= number_of_tables_required
        slot2.free_tables -= number_of_tables_required
        slot3.free_tables -= number_of_tables_required
        slot4.free_tables -= number_of_tables_required
        slot1.save()
        slot2.save()
        slot3.save()
        slot4.save()
        messages.success(request, "Booking request completed successfully. Check your profile for updates on your request.")
        return redirect('restaurantdetail', id=restaurant.id, pageno=0)


class BookNextDay(View):
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
        start_time = datetime.combine(date, restaurant.start_time)
        end_time = datetime.combine(date, restaurant.end_time)
        start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
        end_time = timezone.make_aware(end_time, timezone.get_current_timezone())
        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        end_time = end_time.replace(minute=0, second=0, microsecond=0)
        slots = []
        current_time = start_time
        while current_time < end_time:
            if date > timezone.now().date() or (date == timezone.now().date() and current_time > timezone.now()):
                slots.append(current_time)
            current_time = current_time + timedelta(minutes=30)
        available_slots = []
        for slot in slots:
            booking = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=slot.time(), date=date).first()
            number_of_tables_required = math.ceil(number_of_people / restaurant.people_per_table)
            if booking is not None and booking.free_tables > 0:
                if booking.free_tables >= number_of_tables_required:
                    available_slots.append(slot)
            elif booking is None:
                if restaurant.tables >= number_of_tables_required:
                    available_slots.append(slot)
        print(available_slots)
        two_hour_booking_slots = []
        for slot in available_slots:
            slot2 = slot + timedelta(minutes=30)
            slot3 = slot2 + timedelta(minutes=30)
            slot4 = slot3 + timedelta(minutes=30)
            if slot2 in available_slots and slot3 in available_slots and slot4 in available_slots:
                two_hour_slot = TwoHourBookingSlot(restaurant=restaurant, start_time=slot.time(), end_time=(slot4 + timedelta(minutes=30)).time(), date=date)
                two_hour_slot.save()
                two_hour_booking_slots.append(two_hour_slot)

        count = len(two_hour_booking_slots)
        return render(request, 'slotpick.html', {"page_valid": page_valid, "prev_exists": prev_exists, "count": count, "date": date, "restaurant": restaurant, "two_hour_booking_slots": two_hour_booking_slots, "number_of_people": number_of_people})


class BookPrevDay(View):
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
        start_time = datetime.combine(date, restaurant.start_time)
        end_time = datetime.combine(date, restaurant.end_time)
        start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
        end_time = timezone.make_aware(end_time, timezone.get_current_timezone())
        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        end_time = end_time.replace(minute=0, second=0, microsecond=0)
        slots = []
        current_time = start_time
        while current_time < end_time:
            if date > timezone.now().date() or (date == timezone.now().date() and current_time > timezone.now()):
                slots.append(current_time)
            current_time = current_time + timedelta(minutes=30)
        available_slots = []
        for slot in slots:
            booking = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=slot.time(), date=date).first()
            number_of_tables_required = math.ceil(number_of_people / restaurant.people_per_table)
            if booking is not None and booking.free_tables > 0:
                if booking.free_tables >= number_of_tables_required:
                    available_slots.append(slot)
            elif booking is None:
                if restaurant.tables >= number_of_tables_required:
                    available_slots.append(slot)
        print(available_slots)
        two_hour_booking_slots = []
        for slot in available_slots:
            slot2 = slot + timedelta(minutes=30)
            slot3 = slot2 + timedelta(minutes=30)
            slot4 = slot3 + timedelta(minutes=30)
            if slot2 in available_slots and slot3 in available_slots and slot4 in available_slots:
                two_hour_slot = TwoHourBookingSlot(restaurant=restaurant, start_time=slot.time(), end_time=(slot4 + timedelta(minutes=30)).time(), date=date)
                two_hour_slot.save()
                two_hour_booking_slots.append(two_hour_slot)
        count = len(two_hour_booking_slots)
        return render(request, 'slotpick.html', {"page_valid": page_valid, "prev_exists": prev_exists, "count": count, "date": date, "restaurant": restaurant, "two_hour_booking_slots": two_hour_booking_slots, "number_of_people": number_of_people})


class DeleteBookingView(View):
    def post(self, request, id):
        booking = get_object_or_404(Booking, id=id)
        restaurant = booking.restaurant
        start_time = datetime.combine(booking.date, booking.start_time)
        start_time1 = start_time + timedelta(minutes=30)
        start_time2 = start_time1 + timedelta(minutes=30)
        start_time3 = start_time2 + timedelta(minutes=30)
        slot1 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time.time(), date=booking.date).first()
        slot2 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time1.time(), date=booking.date).first()
        slot3 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time2.time(), date=booking.date).first()
        slot4 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time3.time(), date=booking.date).first()
        number_of_tables_required = math.ceil(booking.number_of_people / restaurant.people_per_table)
        slot1.occupied_tables -= number_of_tables_required
        slot2.occupied_tables -= number_of_tables_required
        slot3.occupied_tables -= number_of_tables_required
        slot4.occupied_tables -= number_of_tables_required
        slot1.free_tables += number_of_tables_required
        slot2.free_tables += number_of_tables_required
        slot3.free_tables += number_of_tables_required
        slot4.free_tables += number_of_tables_required
        slot1.save()
        slot2.save()
        slot3.save()
        slot4.save()
        booking.delete()
        bookings = Booking.objects.filter(user=request.user).order_by('id')
        count = bookings.count()
        messages.success(request,
                         "Booking request deleted successfully.")
        return render(request, 'userbookings.html', {'count': count, 'bookings': bookings})


class DeleteBookingOwnerView(View):
    def post(self, request, id):
        booking = get_object_or_404(Booking, id=id)
        restaurant = booking.restaurant
        start_time = datetime.combine(booking.date, booking.start_time)
        start_time1 = start_time + timedelta(minutes=30)
        start_time2 = start_time1 + timedelta(minutes=30)
        start_time3 = start_time2 + timedelta(minutes=30)
        slot1 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time.time(), date=booking.date).first()
        slot2 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time1.time(), date=booking.date).first()
        slot3 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time2.time(), date=booking.date).first()
        slot4 = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time3.time(), date=booking.date).first()
        number_of_tables_required = math.ceil(booking.number_of_people / restaurant.people_per_table)
        slot1.occupied_tables -= number_of_tables_required
        slot2.occupied_tables -= number_of_tables_required
        slot3.occupied_tables -= number_of_tables_required
        slot4.occupied_tables -= number_of_tables_required
        slot1.free_tables += number_of_tables_required
        slot2.free_tables += number_of_tables_required
        slot3.free_tables += number_of_tables_required
        slot4.free_tables += number_of_tables_required
        slot1.save()
        slot2.save()
        slot3.save()
        slot4.save()
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
