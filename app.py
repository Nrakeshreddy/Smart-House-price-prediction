from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import joblib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  
# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  
app.config['MYSQL_DB'] = 'house_price_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Load models
price_model = joblib.load("house_price_model.pkl")
crime_model = joblib.load("crime_rate_model.pkl")
employment_model = joblib.load("employment_rate_model.pkl")

# Load dataset
csv_path = "C:\\Users\\rakes\\OneDrive\\Documents\\hpp.csv"
data = pd.read_csv(csv_path)

# Dropdown values
cities = sorted(data["City"].dropna().unique().tolist())
streets = sorted(data["Street"].dropna().unique().tolist())
locations = sorted(data["Location"].dropna().unique().tolist())
drainages = sorted(data["DrainageCondition"].dropna().unique().tolist())

# Default values
default_values = {
    "NumRooms": int(data["NumRooms"].median()),
    "SquareFootage": float(data["SquareFootage"].median()),
    "City": data["City"].mode()[0],
    "Street": data["Street"].mode()[0],
    "Location": data["Location"].mode()[0],
    "DrainageCondition": data["DrainageCondition"].mode()[0],
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('welcome'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def welcome():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('welcome.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not all([name, email, password]):
            return "All fields are required", 400

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return "Email already exists. Please login.", 409

        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, hashed_password))
        mysql.connection.commit()

        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        session['user_id'] = user['id']
        session['username'] = user['name']
        session['email'] = user['email']
        cur.close()

        return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['email'] = user['email']
            return redirect(url_for('home'))
        else:
            return "Invalid email or password", 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))

@app.route('/home')
@login_required
def home():
    return render_template('index.html', cities=cities, streets=streets,
                           locations=locations, drainages=drainages)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        input_data = request.get_json()

        # Use default values if some features are missing in the input data
        for feature in default_values:
            if feature not in input_data or pd.isna(input_data[feature]) or input_data[feature] == "":
                input_data[feature] = default_values[feature]

        input_df = pd.DataFrame([input_data])

        # Predict house price
        price = round(price_model.predict(input_df)[0], 2)

        # Predict crime rate and employment rate
        crime = round(crime_model.predict(input_df)[0], 2)
        employment = round(employment_model.predict(input_df)[0], 2)

        prediction = {
            "predicted_price": f"{price:,}",
            "predicted_crime": crime,
            "predicted_employment": employment
        }

        return jsonify(prediction)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
