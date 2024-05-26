import requests
from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
app = Flask(__name__)
app.secret_key = 'supersecretkey'

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

def fetch_top_cuisines(city_name, radius, api_key):
    lat, lon = get_coordinates(city_name, api_key)
    if lat is None or lon is None:
        print(f"Failed to get coordinates for {city_name}")
        return []
    
    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'places.types,places.rating'
    }
    payload = {
        "includedTypes": ["restaurant"],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lon
                },
                "radius": float(radius)
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(data)
        cuisines = set()
        sorted_results = sorted(data['places'], key=lambda x: x.get('rating', 0), reverse=True)
        for place in sorted_results:
            if len(cuisines) >= 4:
                break
            for type in place['types']:
                if type != 'restaurant' and type not in cuisines:
                    cuisines.add(type)
        print(f"Cuisines found: {list(cuisines)}")
        return list(cuisines)
    else:
        print(f"Error fetching places: {response.json().get('error_message', 'Unknown error')}")
        return []

@app.route('/')
def home():
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
        feeling = request.form.get('feeling')
        price = request.form.get('price')
        group = session.get('group')
        username = session.get('username')
        session['feeling'] = feeling
        session['price'] = price
        if group and username:
            return redirect(url_for('choose_location'))
    location = session.get('location', '')
    radius = request.args.get('radius', 1500)  # Default radius to 1500 meters if not provided
    cuisines = fetch_top_cuisines(location, radius, API_KEY) if location else []
    return render_template('feeling.html', cuisines=cuisines, radius=radius)

@app.route('/choose_location')
def choose_location():
    price = session.get('price')
    cuisine = session.get('cuisine')
    images = []
    if price and cuisine:
        image_dir = os.path.join('static', cuisine)
        for i in ['A', 'B', 'C']:
            image_path = f'res-{price}-{cuisine}-{i}.jpg'
            if os.path.exists(os.path.join(image_dir, image_path)):
                images.append(os.path.join(cuisine, image_path))
            else:
                image_path = f'res-{price}-{cuisine}-{i}.jpeg'
                if os.path.exists(os.path.join(image_dir, image_path)):
                    images.append(os.path.join(cuisine, image_path))
                else:
                    image_path = f'res-{price}-{cuisine}-{i}.webp'
                    if os.path.exists(os.path.join(image_dir, image_path)):
                        images.append(os.path.join(cuisine, image_path))
    return render_template('choose_location.html', images=images)


@app.route('/vote_winner', methods=['GET', 'POST'])
def vote_winner():
    selected_restaurant = session.get('selected_restaurant', 'None')
    if request.method == 'POST':
        winner = request.form.get('winner')
        session['winner'] = winner
        return redirect(url_for('confirmation'))
    return render_template('vote_winner.html', selected_restaurant=selected_restaurant)

@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    selected_restaurant = session.get('winner', 'Unknown')
    location = session.get('location')
    if request.method == 'POST':
        return redirect(url_for('home'))
    return render_template('confirmation.html', selected_restaurant=selected_restaurant, location=location)

if __name__ == '__main__':
    app.run(debug=True)
