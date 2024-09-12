from django.core.management.base import BaseCommand
from django.db import models
from restaurant.models import Restaurant, RestaurantRecommendations, Food, User, Comment, ContactMessage, Like, Cuisine, FavoritesList, Booking, ThirtyMinuteBookingSlot
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
from geopy.distance import geodesic
from django.db.models import Avg
import numpy as np
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):
        RestaurantRecommendations.objects.all().delete()
        for user in User.objects.all():
            # fetch the high reviews of the logged in user
            high_reviews = Comment.objects.filter(user=user, rating__gte=4).select_related('restaurant')

            # bool to alert the template if there are no reviews to use
            reviews_exist = True
            if not high_reviews.exists():
                reviews_exist = False

            # find the average of the reviews the user left to that restaurant
            aggregated_reviews = high_reviews.values('restaurant_id').annotate(rating=models.Avg('rating'))

            # get the restaurants with the high reviews
            high_rated_restaurants = Restaurant.objects.filter(
                id__in=[review['restaurant_id'] for review in aggregated_reviews])

            # fetch data to feed the model
            high_rated_restaurants_data = Restaurant.objects.filter(
                id__in=[restaurant.id for restaurant in high_rated_restaurants]).select_related('cuisine').values(
                'id', 'cuisine__name', 'lng', 'lat', 'point'
            )

            # convert the data to pandas dataframe
            df_user = pd.DataFrame(high_rated_restaurants_data)

            # printing for debugging
            print(df_user.columns)
            print(df_user.head())

            # one-hot encoding to convert the cuisine__name field into numeric vectors
            cuisine_encoder = OneHotEncoder(handle_unknown='ignore')
            cuisine_encoder.fit(df_user[['cuisine__name']])
            cuisine_vectors = cuisine_encoder.transform(df_user[['cuisine__name']])
            print(cuisine_vectors)

            # create user profile to find user cuisine preferences
            user_profile_vector = np.mean(cuisine_vectors.toarray(), axis=0)

            # fetch the data of all restaurants to compare to user preferences
            all_restaurants = Restaurant.objects.select_related('cuisine').all().values()
            all_restaurants_data = Restaurant.objects.select_related('cuisine').values(
                'id', 'cuisine__name', 'lng', 'lat', 'point'
            )
            df_all = pd.DataFrame(list(all_restaurants_data))

            # convert cuisines to numeric values again
            all_cuisine_vectors = cuisine_encoder.transform(df_all[['cuisine__name']]).toarray()
            cuisine_similarity = cosine_similarity([user_profile_vector], all_cuisine_vectors)[0]

            # calculate the proximity of user-rated restaurants and a target restaurant
            def calculate_location_similarity(user_restaurants, target_restaurant):
                distances = [geodesic((r['lat'], r['lng']),
                                      (target_restaurant['lat'], target_restaurant['lng'])).kilometers
                             for r in user_restaurants]
                return 1 / (1 + np.mean(distances))  # this is done to ensure that closer distances yield larger
                # similarity scores

            # proximity similarity applied to all restaurants
            location_similarities = np.array([
                calculate_location_similarity(high_rated_restaurants_data, restaurant) for restaurant in
                df_all.to_dict('records')
            ])

            # calculate a combined similarity score and recommend top 5 most similar restaurants
            combined_similarity = 0.7 * cuisine_similarity + 0.3 * location_similarities
            df_all['similarity'] = combined_similarity

            # drop the duplicate restaurant recommendations if the user reviewed the restaurant multiple times
            all_recommendations = df_all.drop_duplicates(subset='id').sort_values(by='similarity',
                                                                                  ascending=False).head(5)
            recommended_restaurant_ids = all_recommendations['id'].tolist()
            recommended_restaurants = Restaurant.objects.filter(id__in=recommended_restaurant_ids)
            for restaurant in recommended_restaurants:
                recommendation = RestaurantRecommendations(restaurant_id=restaurant.id, user_id=user.id)
                recommendation.save()