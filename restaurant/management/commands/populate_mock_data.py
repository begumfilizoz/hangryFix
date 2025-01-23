import random
from django.core.management.base import BaseCommand
from restaurant.models import *  # Import all models
from cities_light.models import Country, City


class Command(BaseCommand):
    help = "Populate database with mock countries, cities, restaurants, cuisines, foods, users, and reviews."

    def handle(self, *args, **kwargs):
        # 1. Mock Cuisines
        cuisine_data = ["Steakhouse", "Turkish", "Pizza", "French", "Seafood", "Fine Dining", "Bakery", "Cafe", "Mediterranean", "Burgers", "Salad", "Dessert"]
        cuisines = {}
        for cuisine_name in cuisine_data:
            cuisine, _ = Cuisine.objects.get_or_create(name=cuisine_name)
            cuisines[cuisine_name] = cuisine

        # 2. Mock Users
        usernames = ["john_doe", "jane_smith", "foodie101", "critic_x", "dining_enthusiast"]
        users = []
        for username in usernames:
            user, _ = User.objects.get_or_create(username=username, email=f"{username}@example.com")
            users.append(user)

        # 3. Mock Countries and Cities
        mock_countries = {
            "TR": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"],
            "US": ["New York", "Los Angeles", "Chicago", "Houston", "Miami"],
            "FR": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"],
            "DE": ["Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt"],
            "IT": ["Rome", "Milan", "Naples", "Turin", "Florence"],
            "GB": ["London", "Manchester", "Birmingham", "Glasgow", "Edinburgh"],
        }
        countries = {}
        for country_code, city_names in mock_countries.items():
            country, _ = Country.objects.get_or_create(name=country_code, code2=country_code)
            countries[country_code] = country
            for city_name in city_names:
                City.objects.get_or_create(name=city_name, country=country)

        # 4. Mock Restaurants
        mock_restaurants = {
            "TR": [
                {"name": "Nusr-Et Steakhouse", "cuisine": "Steakhouse"},
                {"name": "CZN Burak", "cuisine": "Turkish"},
                {"name": "Meze by Lemon Tree", "cuisine": "Mediterranean"},
                {"name": "Simit Sarayı", "cuisine": "Bakery"},
                {"name": "Tarihi Sultanahmet Köftecisi", "cuisine": "Turkish"},
            ],
            "US": [
                {"name": "Joe's Pizza", "cuisine": "Pizza"},
                {"name": "Shake Shack", "cuisine": "Burgers"},
                {"name": "Sweetgreen", "cuisine": "Salad"},
                {"name": "In-N-Out Burger", "cuisine": "Burgers"},
                {"name": "The Capital Grille", "cuisine": "Steakhouse"},
            ],
            "FR": [
                {"name": "Le Meurice", "cuisine": "French"},
                {"name": "Chez Janou", "cuisine": "French"},
                {"name": "La Palette", "cuisine": "Cafe"},
                {"name": "L'Ambroisie", "cuisine": "Fine Dining"},
                {"name": "Angelina", "cuisine": "Dessert"},
            ],
        }

        for country_code, restaurant_list in mock_restaurants.items():
            country = countries[country_code]
            cities = City.objects.filter(country=country)

            for restaurant_data in restaurant_list:
                # Assign a random city to the restaurant
                city = random.choice(cities)

                # Create restaurant
                restaurant = Restaurant.objects.create(
                    name=restaurant_data["name"],
                    cuisine=cuisines[restaurant_data["cuisine"]],
                    city=city,
                    country=country,
                    point=random.uniform(3.0, 5.0),
                    lat=random.uniform(-90.0, 90.0),
                    lng=random.uniform(-180.0, 180.0),
                )

                # Add mock food items
                for i in range(3):
                    Food.objects.create(
                        restaurant=restaurant,
                        name=f"Dish {i + 1} at {restaurant.name}",
                        price=random.uniform(10.0, 50.0),
                        description=f"Delicious {restaurant.cuisine.name} dish.",
                    )

                # Add comments
                for _ in range(random.randint(3, 7)):
                    Comment.objects.create(
                        restaurant=restaurant,
                        user=random.choice(users),
                        rating=random.uniform(3.0, 5.0),
                        comment=f"Great experience at {restaurant.name}. Loved it!",
                    )

        self.stdout.write("Successfully populated mock data for restaurants, cuisines, foods, and reviews!")
