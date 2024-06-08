from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Load restaurant details from JSON
with open('restaurant_details.json', 'r') as f:
    restaurant_details = json.load(f)

# Function to load API keys from a JSON file
def load_api_keys(json_file):
    # First, check if the file exists in the current directory
    if os.path.exists(json_file):
        file_path = json_file
    # If not, check the specified path
    elif os.path.exists(os.path.join('/home/ganga008/Spontaneous_prototype', json_file)):
        file_path = os.path.join('/home/ganga008/Spontaneous_prototype', json_file)
    else:
        raise FileNotFoundError(f"API keys file {json_file} not found in the current directory or /home/ganga008/Spontaneous_prototype/")
    
    with open(file_path, 'r') as file:
        config = json.load(file)
    print(f"Loaded API keys from {file_path}")
    return config['API_KEY'], config['OPENAI_API_KEY']

# Load the API keys
API_KEY, OPENAI_API_KEY = load_api_keys('api.json')

# In-memory storage for user interests and locations
rooms = {}

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

    print(f"Price: {price}, Cuisine: {cuisine}")  # Debugging print statement
    print(f"Sample of restaurant_details: {list(restaurant_details.items())[:5]}")  # Debugging print statement

    # Filter the restaurants based on the selected price and cuisine
    filtered_restaurants = [
        {**details, 'name': name} for name, details in restaurant_details.items() 
        if details['price'] == price and details['cuisine'].lower() == cuisine.lower()[0:3]
    ]

    print(f"Filtered restaurants: {filtered_restaurants}")  # Debugging print statement

    # Sort the filtered restaurants by rating in descending order
    filtered_restaurants.sort(key=lambda x: x['rating'], reverse=True)

    return render_template('choose_location.html', location=location, price=price, cuisine=cuisine, images=filtered_restaurants)

@app.route('/vote_winner', methods=['GET', 'POST'])
def vote_winner():
    if request.method == 'POST':
        first_preference = request.form.get('first_preference')
        second_preference = request.form.get('second_preference')
        session['first_preference'] = first_preference
        session['second_preference'] = second_preference
        return redirect(url_for('confirmation'))

    selected_restaurant = session.get('selected_restaurant')
    selected_restaurant_details = restaurant_details.get(selected_restaurant, {})

    # Randomly select other restaurants excluding the selected one
    other_restaurants = [details for name, details in restaurant_details.items() if name != selected_restaurant]
    random.shuffle(other_restaurants)
    other_restaurants = other_restaurants[:3]

    return render_template('vote_winner.html', selected_restaurant=selected_restaurant_details, other_restaurants=other_restaurants)

@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    selected_restaurant = session.get('first_preference', 'Unknown')
    location = session.get('location')
    if request.method == 'POST':
        return redirect(url_for('home'))

    # Example votes data, replace with actual voting data
    votes_data = {
        'Restaurant 1': {'first_preference': 12, 'second_preference': 5},
        'Restaurant 2': {'first_preference': 19, 'second_preference': 3},
        'Restaurant 3': {'first_preference': 3, 'second_preference': 2}
    }

    return render_template('confirmation.html', selected_restaurant=selected_restaurant, location=location, votes_data=votes_data)

if __name__ == '__main__':
    app.run(debug=True)
