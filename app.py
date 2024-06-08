from flask import Flask, render_template, request, redirect, url_for, session
import os
import requests
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Mapping for price and cuisine
price_mapping = {
    '¥': '1',
    '¥¥': '2',
    '¥¥¥': '3',
    '¥¥¥¥': '3'
}

cuisine_mapping = {
    'Indian': 'ind',
    'Western': 'wes',
    'Japanese': 'jap',
    'Chinese': 'chi'
}

# Function to load API keys from a JSON file
def load_api_keys(json_file):
    with open(json_file, 'r') as file:
        config = json.load(file)
    print(f"Loaded API keys")
    return config['API_KEY'], config['OPENAI_API_KEY']

# Load the API keys
API_KEY, OPENAI_API_KEY = load_api_keys('api.json')

# In-memory storage for user interests and locations
rooms = {}

def get_coordinates(city_name, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']['location']
            print(f"Coordinates for {city_name}: {location}")
            return location['lat'], location['lng']
        else:
            print(f"Error: No results found for city: {city_name}")
            return None, None
    else:
        print(f"Error fetching coordinates: {response.json().get('error_message', 'Unknown error')}")
        return None, None

# Add below unchanged line:
def map_price_to_symbol(price):
    if price < 3000:
        return '¥'
    elif 3000 <= price < 6000:
        return '¥¥'
    elif 6000 <= price < 10000:
        return '¥¥¥'
    else:
        return '¥¥¥¥'
    
@app.route('/')
def home():
    session['group_name'] = request.form.get('group_name')
    return render_template('home.html')

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if request.method == 'POST':
        group_name = request.form.get('group_name')
        your_name = request.form.get('your_name')
        location = request.form.get('location')
        print(f"Creating group: {group_name} with username: {your_name} and location: {location}")
        if group_name and your_name and location:
            session['group'] = group_name
            session['username'] = your_name
            session['location'] = location
            if group_name not in rooms:
                rooms[group_name] = {"location": location, "users": {}}
            if your_name not in rooms[group_name]["users"]:
                rooms[group_name]["users"][your_name] = []
            return redirect(url_for('feeling'))
    return render_template('create_group.html', api_key=API_KEY)

@app.route('/join_group', methods=['GET', 'POST'])
def join_group():
    if request.method == 'POST':
        group_name = request.form.get('group_name')
        your_name = request.form.get('your_name')
        location = request.form.get('location')
        print(f"Joining group: {group_name} with username: {your_name}")
        if group_name in rooms:
            if your_name not in rooms[group_name]["users"]:
                rooms[group_name]["users"][your_name] = []
                session['group'] = group_name
                session['username'] = your_name
                session['location'] = location
                return redirect(url_for('feeling'))
            else:
                return "User already in the group.", 400
        else:
            return "Group does not exist.", 404
    group_name = request.args.get('group_name')
    return render_template('join_group.html', api_key=API_KEY, group_name=group_name)

@app.route('/feeling', methods=['GET', 'POST'])
def feeling():
    if request.method == 'POST':
        action = request.form.get('action')
        feeling = request.form.get('feeling')
        price = request.form.get('price')
        session['feeling'] = feeling
        session['price'] = map_price_to_symbol(int(price))
        session['pricenum'] = price
        print(session)
        if action == 'feeling_alt':
            return redirect(url_for('feeling_alt'))
        return redirect(url_for('choose_location'))
    return render_template('feeling.html')

@app.route('/feeling_alt', methods=['GET', 'POST'])
def feeling_alt():
    if request.method == 'POST':
        feeling = request.form.get('feeling') or request.form.get('other_choice')
        print(f"Received feeling: {feeling}")  # Debugging print statement
        price = request.form.get('priceValue')
        print(f"Received price: {price}")  # Debugging print statement
        session['feeling'] = feeling
        session['price'] = map_price_to_symbol(int(price))
        return redirect(url_for('choose_location'))
    return render_template('feeling_alt.html')

@app.route('/choose_location', methods=['GET', 'POST'])
def choose_location():
    if request.method == 'POST':
        selected_restaurant = request.form.get('restaurant')
        session['selected_restaurant'] = selected_restaurant
        return redirect(url_for('vote_winner'))
    
    location = session.get('location')
    price = session.get('price')
    cuisine = session.get('feeling')

    mapped_price = price_mapping.get(price, '1')  # Default to '1' if not found
    mapped_cuisine = cuisine_mapping.get(cuisine, 'chi')  # Default to 'chi' if not found

    # Example ratings, replace with actual logic to fetch ratings
    restaurant_ratings = {
        'A': 4.5,
        'B': 4.2,
        'C': 4.0
    }

    restaurant_distances = {
        'A': '500m',
        'B': '1km',
        'C': '300m'
    }

    # Reverse mapping for price symbols
    price_mapping_reverse = {
        '1': '¥',
        '2': '¥¥',
        '3': '¥¥¥'
    }

    restaurant_seat_availability = {
        'A': 'Limited seating',
        'B': 'Limited seating',
        'C': 'Many seats available'
    }
    
    images = []
    if mapped_price and mapped_cuisine:
        image_dir = os.path.join('static', mapped_cuisine).replace("\\","/")
        for i in ['A', 'B', 'C']:
            for ext in ['jpg', 'jpeg', 'webp']:
                image_path = f'res-{mapped_price}-{mapped_cuisine}-{i}.{ext}'
                print(image_dir,image_path)
                if os.path.exists(os.path.join(image_dir, image_path)):
                    images.append((f'{mapped_cuisine}/{image_path}', restaurant_ratings[i], i, restaurant_distances[i], price))
                    break
                elif os.path.exists(os.path.join("/home/ganga008/Spontaneous_prototype/"+image_dir, image_path)):
                    images.append((f'{mapped_cuisine}/{image_path}', restaurant_ratings[i], i, restaurant_distances[i], price))
        print(images)
    
    # Sort images by rating
    images.sort(key=lambda x: x[1], reverse=True)

    return render_template('choose_location.html', location=location, price=price, cuisine=cuisine, images=images, restaurant_seat_availability=restaurant_seat_availability, restaurant_distances=restaurant_distances)

@app.route('/vote_winner', methods=['GET', 'POST'])
def vote_winner():
    if request.method == 'POST':
        winner = request.form.get('winner')
        session['winner'] = winner
        return redirect(url_for('confirmation'))

    selected_restaurant = session.get('selected_restaurant')
    print(session)
    restaurant_details = {
        'Restaurant A': {
            'distance': '500m',
            'rating': '4.5',
            'discount': 'Enjoy 5% off all beverages for dine-in customers only!'
        },
        'Restaurant B': {
            'distance': '300m',
            'rating': '4.2',
            'discount': 'Enjoy 10% off on all orders above ¥5000!'
        },
        'Restaurant C': {
            'distance': '500m',
            'rating': '4.8',
            'discount': 'Get a free dessert with every meal!'
        },
        'Restaurant D': {
            'distance': '400m',
            'rating': '4.6',
            'discount': 'Get a free appetizer with any meal!'
        },
        'Restaurant E': {
            'distance': '350m',
            'rating': '4.7',
            'discount': 'Enjoy 15% off on weekends!'
        }
    }

    selected_restaurant_details = restaurant_details.get(selected_restaurant, {})
    other_restaurants = [
        restaurant_details['Restaurant D'],
        restaurant_details['Restaurant E']
    ]

    return render_template('vote_winner.html', selected_restaurant=selected_restaurant, selected_restaurant_details=selected_restaurant_details, other_restaurants=other_restaurants)

@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    selected_restaurant = session.get('winner', 'Unknown')
    location = session.get('location')
    if request.method == 'POST':
        return redirect(url_for('home'))
    return render_template('confirmation.html', selected_restaurant=selected_restaurant, location=location)

if __name__ == '__main__':
    app.run(debug=True)
