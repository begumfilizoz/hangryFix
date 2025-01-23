# **HangryFix**

HangryFix is a web app that presents users with restaurants in their desired locations. Users can rate the meals they had in those restaurants. Owners can add their own restaurant to the website for users to view. Based on the reviews they left on the restaurants, the website recommends some other restaurants to the users using a machine learning recommendation system. 
The project originally had a large local database, in which Django's cities_light was imported and web data was scraped to create a large database of renowned restaurants. On GitHub, the project is filled with mockdata to show its essential features. 

---

## **Features**
- User authentication with support for owners and customers.
- Restaurant and cuisine management.
- Booking system with multiple booking slot options.
- Ratings and comments for restaurants.
- Integration with [cities_light](https://github.com/yourlabs/django-cities-light) for cities and countries. (This is not valid at the moment for simplification, it is implemented but the app uses mockdata)

---

## **Setup Instructions**

Follow these steps to set up the project on your local machine.

```bash
# 1. Clone the Repository

# 2. Set Up a Virtual Environment
python3 -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate     # For Windows

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Set Up PostgreSQL
# Ensure PostgreSQL is installed and running.
# Open the PostgreSQL shell and execute the following commands:
CREATE DATABASE hangryfix;
GRANT ALL PRIVILEGES ON DATABASE hangryfix TO <your-postgres-user>;

# Replace <your-postgres-user> with your PostgreSQL username (e.g., postgres in my case).

# 5. Apply Database Migrations
python manage.py makemigrations
python manage.py migrate

# 6. Load Mock Data
python manage.py populate_mock_data

# 7. Run the Development Server
python manage.py runserver

# Visit the application at http://127.0.0.1:8000/.
