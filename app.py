from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if request.method == 'POST':
        return redirect(url_for('feeling'))
    return render_template('create_group.html')

@app.route('/join_group', methods=['GET', 'POST'])
def join_group():
    if request.method == 'POST':
        return redirect(url_for('feeling'))
    return render_template('join_group.html')

@app.route('/feeling', methods=['GET', 'POST'])
def feeling():
    if request.method == 'POST':
        return redirect(url_for('choose_location'))
    return render_template('feeling.html')

@app.route('/choose_location', methods=['GET', 'POST'])
def choose_location():
    if request.method == 'POST':
        selected_restaurant = request.form.get('restaurant')
        session['selected_restaurant'] = selected_restaurant
        return redirect(url_for('vote_winner'))
    return render_template('choose_location.html')

@app.route('/vote_winner', methods=['GET', 'POST'])
def vote_winner():
    selected_restaurant = session.get('selected_restaurant', 'Restaurant A')
    if request.method == 'POST':
        return redirect(url_for('confirmation'))
    return render_template('vote_winner.html', selected_restaurant=selected_restaurant)

@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    if request.method == 'POST':
        return redirect(url_for('home'))
    return render_template('confirmation.html')

if __name__ == '__main__':
    app.run(debug=True)
