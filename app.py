from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Mapping for price and cuisine
price_mapping = {
    '¥': '1',
    '¥¥': '2',
    '¥¥¥': '3'
}

cuisine_mapping = {
    'Indian': 'ind',
    'Western': 'wes',
    'Japanese': 'jap',
    'Chinese': 'chi'
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if request.method == 'POST':
        session['group_name'] = request.form.get('group_name')
        session['your_name'] = request.form.get('your_name')
        session['location'] = request.form.get('location')
        return redirect(url_for('feeling'))
    return render_template('create_group.html')

@app.route('/join_group', methods=['GET', 'POST'])
def join_group():
    if request.method == 'POST':
        session['your_name'] = request.form.get('your_name')
        session['location'] = request.form.get('location')
        return redirect(url_for('feeling'))
    return render_template('join_group.html')

@app.route('/feeling', methods=['GET', 'POST'])
def feeling():
    if request.method == 'POST':
        feeling = request.form.get('feeling')
        price = request.form.get('price')
        session['feeling'] = feeling
        session['price'] = price
        return redirect(url_for('choose_location'))
    return render_template('feeling.html')

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
    
    images = []
    if mapped_price and mapped_cuisine:
        image_dir = os.path.join('static', mapped_cuisine).replace("\\","/")
        for i in ['A', 'B', 'C']:
            for ext in ['jpg', 'jpeg', 'webp']:
                image_path = f'res-{mapped_price}-{mapped_cuisine}-{i}.{ext}'
                print(image_dir,image_path)
                if os.path.exists(os.path.join(image_dir, image_path)):
                    images.append((f'{mapped_cuisine}/{image_path}', restaurant_ratings[i], i))
                    break
                else:
                    images.append((f'/home/ganga008/Spontaneous_prototype/static/{mapped_cuisine}/{image_path}', restaurant_ratings[i], i))
        print(images)
    
    # Sort images by rating
    images.sort(key=lambda x: x[1], reverse=True)

    return render_template('choose_location.html', location=location, price=price, cuisine=cuisine, images=images)

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
