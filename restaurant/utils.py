from datetime import datetime, timedelta
import math
from django.utils import timezone
from .models import Restaurant, Food, User, Comment, ContactMessage, Like, Cuisine, FavoritesList, \
    ThirtyMinuteBookingSlot, TwoHourBookingSlot, Booking
from .forms import UserCreationForm, AddRestaurantForm, AddMealForm, AddCommentForm, ContactForm, SearchRestaurantForm, \
    BookingForm


def create_booking_slots(date, restaurant, number_of_people):
    # fetch info and round the times to the correct format
    start_time = datetime.combine(date, restaurant.start_time)
    end_time = datetime.combine(date, restaurant.end_time)
    start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
    end_time = timezone.make_aware(end_time, timezone.get_current_timezone())
    start_time = start_time.replace(minute=0, second=0, microsecond=0)
    end_time = end_time.replace(minute=0, second=0, microsecond=0)
    slots = []
    current_time = start_time

    # separate the period to 30-minute slots
    while current_time < end_time:
        if date > timezone.now().date() or (date == timezone.now().date() and current_time > timezone.now()):
            slots.append(current_time)
        current_time = current_time + timedelta(minutes=30)
    available_slots = []

    # if there are available tables in the slots, append them to the list
    for slot in slots:
        booking = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=slot.time(),
                                                         date=date).first()
        number_of_tables_required = math.ceil(number_of_people / restaurant.people_per_table)
        if booking is not None and booking.free_tables > 0:
            if booking.free_tables >= number_of_tables_required:
                available_slots.append(slot)
        elif booking is None:
            if restaurant.tables >= number_of_tables_required:
                available_slots.append(slot)
    print(available_slots)
    two_hour_booking_slots = []

    # check if there are 2-hour availabilities in the slots' list, if so, append to show them
    for slot in available_slots:
        slot2 = slot + timedelta(minutes=30)
        slot3 = slot2 + timedelta(minutes=30)
        slot4 = slot3 + timedelta(minutes=30)
        if slot2 in available_slots and slot3 in available_slots and slot4 in available_slots:
            two_hour_slot = TwoHourBookingSlot(restaurant=restaurant, start_time=slot.time(),
                                               end_time=(slot4 + timedelta(minutes=30)).time(), date=date)
            two_hour_slot.save()
            two_hour_booking_slots.append(two_hour_slot)
    count = len(two_hour_booking_slots)
    return count, two_hour_booking_slots


def process_slots(restaurant, booking):
    # find the slots to be altered
    start_time = datetime.combine(booking.date, booking.start_time)
    slots = []
    for i in range(4):
        slot = ThirtyMinuteBookingSlot.objects.filter(restaurant=restaurant, start_time=start_time.time(),
                                                      date=booking.date).first()
        slots.append(slot)
        start_time = start_time + timedelta(minutes=30)

    # save the slots and delete the booking
    number_of_tables_required = math.ceil(booking.number_of_people / restaurant.people_per_table)
    for slot in slots:
        slot.occupied_tables -= number_of_tables_required
        slot.free_tables += number_of_tables_required
        slot.save()


def show_favorites(favorites_list, page_no):
    next_exists = True
    if favorites_list:
        restaurants = Restaurant.objects.filter(favorites=favorites_list).order_by('id')
    else:
        restaurants = Restaurant.objects.none()
    print(restaurants)
    if page_no != -1:
        if (page_no + 1) * 5 > restaurants.count():
            next_exists = False
        print(page_no)
        count = restaurants.count()
        restaurants = restaurants[page_no * 5:page_no * 5 + 5]
    return count, restaurants, next_exists, page_no