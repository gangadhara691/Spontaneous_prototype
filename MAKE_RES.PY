import json
import random
import numpy as np

# List of image paths
image_paths = [
    "chi/res-1-chi-A.jpg", "chi/res-1-chi-B.jpg", "chi/res-1-chi-C.jpg",
    "chi/res-2-chi-A.jpg", "chi/res-2-chi-B.jpeg", "chi/res-2-chi-C.jpg",
    "chi/res-3-chi-A.jpg", "chi/res-3-chi-B.jpg", "chi/res-3-chi-C.jpg",
    "ind/res-1-ind-A.png", "ind/res-1-ind-B.jpg", "ind/res-1-ind-C.jpg",
    "ind/res-2-ind-A.webp", "ind/res-2-ind-B.jpg", "ind/res-2-ind-C.jpg",
    "ind/res-3-ind-A.jpg", "ind/res-3-ind-B.jpg", "ind/res-3-ind-C.jpg",
    "jap/res-1-jap-A.jpg", "jap/res-1-jap-B.webp", "jap/res-1-jap-C.jpg",
    "jap/res-2-jap-A.webp", "jap/res-2-jap-B.webp", "jap/res-2-jap-C.webp",
    "jap/res-3-jap-A.jpg", "jap/res-3-jap-B.jpeg", "jap/res-3-jap-C.jpg",
    "wes/res-1-wes-A.jpg", "wes/res-1-wes-B.jpg", "wes/res-1-wes-C.webp",
    "wes/res-2-wes-A.jpg", "wes/res-2-wes-B.jpg", "wes/res-2-wes-C.jpg",
    "wes/res-3-wes-A.jpg", "wes/res-3-wes-B.jpg", "wes/res-3-wes-C.jpeg"
]

# Define the base structure for restaurant details
base_details = {
    'distance': '',
    'rating': 0.0,
    'discount': '',
    'seats': '',
    'price': '',
    'cuisine': '',
    'image': ''
}

# Discounts and price mapping
discounts = {
    '1': 'Enjoy 5% off all beverages for dine-in customers only!',
    '2': 'Enjoy 10% off on all orders above ¥5000!',
    '3': 'Get a free dessert with every meal!'
}

# Function to generate random rating
def generate_random_rating():
    return round(random.uniform(3.5, 4.99), 1)

# Function to generate random seat availability
def generate_random_seats():
    gen = np.random.choice(['Limited seating', 'Many seats available'],1,p=[0.7,0.3])
    print(gen)
    return gen[0]

# Initialize the master dictionary
restaurant_details = {}

# Loop through image paths and populate the dictionary
for path in image_paths:
    parts = path.split('/')
    cuisine, file_name = parts[0], parts[1]
    details = file_name.split('-')
    price, cuisine_code, identifier_with_ext = details[1], details[2], details[3]
    identifier = "RESTAURENT-"+cuisine.capitalize()+"-"+identifier_with_ext.split('.')[0]+"-"+str(price)
    
    restaurant_details[identifier] = base_details.copy()
    restaurant_details[identifier]['distance'] = f'{random.randint(300, 1000)}m'
    restaurant_details[identifier]['rating'] = generate_random_rating()
    restaurant_details[identifier]['discount'] = discounts[price]
    restaurant_details[identifier]['seats'] = generate_random_seats()
    restaurant_details[identifier]['price'] = '¥' * int(price)
    restaurant_details[identifier]['cuisine'] = cuisine.capitalize()
    restaurant_details[identifier]['image'] = path

# Save the dictionary to a JSON file
with open('restaurant_details.json', 'w') as json_file:
    json.dump(restaurant_details, json_file, indent=2)

print("Master dictionary saved to 'restaurant_details.json'")
