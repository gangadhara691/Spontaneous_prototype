from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

iframes = {
    "Jap": '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d25909.81818687059!2d139.6906253743164!3d35.7329253!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x60188d76e2611ec9%3A0xd19caad64db229b!2sEthnic%20Dining%20Japan!5e0!3m2!1sen!2sjp!4v1717904340665!5m2!1sen!2sjp" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>',
    "Chi": '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d25919.10833882084!2d139.7346936743164!3d35.7043603!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x60188c1e29c7090f%3A0x12b845ef4f1b4000!2sChinese%20restaurant!5e0!3m2!1sen!2sjp!4v1717904378592!5m2!1sen!2sjp" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>',
    "Ind": '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d51833.337741465264!2d139.64331384863277!3d35.711863!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x60188dba5a343af7%3A0x85ae75672843498a!2sMughal%20Halal%20Indian%20restaurant!5e0!3m2!1sen!2sjp!4v1717904451294!5m2!1sen!2sjp" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>',
    "Wes": '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d51833.346873008595!2d139.643313797727!3d35.711848959028885!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x60188cc09fa1f559%3A0x94b6232057cc6728!2sWestern-style%20Restaurant%20Le%20Rire!5e0!3m2!1sen!2sjp!4v1717904496328!5m2!1sen!2sjp" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
}

# Load restaurant details from JSON
# with open('restaurant_details.json', 'r') as f:
#     restaurant_details = json.load(f)
def load_res(json_file):
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
    return config
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
restaurant_details = load_res('restaurant_details.json')
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
            session['your_name'] = your_name
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
                session['your_name'] = your_name
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
    print(restaurant_details)
    print(f"Price: {price}, Cuisine: {cuisine}")  # Debugging print statement
    print(f"Sample of restaurant_details: {list(restaurant_details.items())[:5]}")  # Debugging print statement
    for name, details in restaurant_details.items():
        details["name"] = name
        # if not os.path.exists("static/"+details["image"]):
        #     details["image"] = "/home/ganga008/Spontaneous_prototype/static/"+details["image"]
    # Filter the restaurants based on the selected price and cuisine
    if price == '¥¥¥¥':
        price = '¥¥¥'
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
        first_preference = request.form.get('preference1')
        second_preference = request.form.get('preference2')
        session['first_preference'] = first_preference
        session['second_preference'] = second_preference
        print(f"First preference: {first_preference}, Second preference: {second_preference}")
        return redirect(url_for('confirmation'))

    selected_restaurant = session.get('selected_restaurant')
    selected_restaurant_details = restaurant_details.get(selected_restaurant, {})
    print(f"Selected restaurant: {selected_restaurant}, Details: {selected_restaurant_details}")
    # Randomly select other restaurants excluding the selected one
    
        # print(name, details)
    other_restaurants = [details for name, details in restaurant_details.items() if name != selected_restaurant]
    # other_restaurants = {name: details for name, details in restaurant_details.items() if name != selected_restaurant}

    print(f"Other restaurants: {other_restaurants}")
    random.shuffle(other_restaurants)
    other_restaurants = other_restaurants[:3]

    return render_template('vote_winner.html', selected_restaurant=selected_restaurant_details, other_restaurants=other_restaurants)

import random

# Sample reviews and ratings
sample_reviews = [
    ("John Doe", "Great place! Loved the food.", 5),
    ("Jane Smith", "Nice ambiance but a bit pricey.", 4),
    ("Alice Johnson", "The service was excellent!", 5),
    ("Bob Brown", "Food was okay, not the best I've had.", 3),
    ("Charlie Davis", "Would definitely visit again.", 4)
]

def generate_random_reviews():
    return random.sample(sample_reviews, k=3)  # Generate 3 random reviews for each restaurant

@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    if request.method == 'POST':
        return redirect(url_for('home'))

    # Retrieve preferences from session
    first_preference = session.get('first_preference', 'Unknown')
    second_preference = session.get('second_preference', 'Unknown')
    selected_restaurant = session.get('selected_restaurant')
    selected_restaurant_details = restaurant_details.get(selected_restaurant, {})

    # Example: Mock vote counts using the selected and other restaurants
    vote_counts = {
        first_preference: {'first_preference': 20, 'second_preference': 10},
        second_preference: {'first_preference': 7, 'second_preference': 3},
    }

    # Randomly select one restaurant from other_restaurants for the third rank
    other_restaurants = [details for name, details in restaurant_details.items() if name not in [first_preference, second_preference]]
    random_third_restaurant = random.choice(other_restaurants)
    random_third_restaurant_name = random_third_restaurant['name']
    vote_counts[random_third_restaurant_name] = {'first_preference': 5, 'second_preference': 2}

    # Calculate total votes for percentage calculation
    total_votes = sum(v['first_preference'] + v['second_preference'] for v in vote_counts.values())

    # Sort the restaurants based on vote counts
    sorted_restaurants = sorted(vote_counts.items(), key=lambda item: (item[1]['first_preference'], item[1]['second_preference']), reverse=True)

    # Assign ranks to the top 3 restaurants
    top_3_restaurants = {
        "Rank 1 ": (sorted_restaurants[0][0], sorted_restaurants[0][1]),
        "Rank 2 ": (sorted_restaurants[1][0], sorted_restaurants[1][1]),
        "Rank 3 ": (sorted_restaurants[2][0], sorted_restaurants[2][1]),
    }

    return render_template('confirmation.html', top_3_restaurants=top_3_restaurants, restaurant_details=restaurant_details, total_votes=total_votes,iframes=iframes)

if __name__ == '__main__':
    app.run(debug=True)
