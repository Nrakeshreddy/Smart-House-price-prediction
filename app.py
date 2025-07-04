from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import joblib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ── MySQL (Railway) configuration via Render env vars ─────────────
app.config["MYSQL_HOST"]     = os.environ.get("MYSQL_HOST")
app.config["MYSQL_USER"]     = os.environ.get("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
app.config["MYSQL_DB"]       = os.environ.get("MYSQL_DB")
app.config["MYSQL_PORT"]     = int(os.environ.get("MYSQL_PORT", 40167))
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# ── Load models ───────────────────────────────────────────────────
price_model      = joblib.load("house_price_model.pkl")
crime_model      = joblib.load("crime_rate_model.pkl")
employment_model = joblib.load("employment_rate_model.pkl")

# ── Load dataset for dropdowns ────────────────────────────────────
data = pd.read_csv("hpp.csv")
cities     = sorted(data["City"].dropna().unique())
streets    = sorted(data["Street"].dropna().unique())
locations  = sorted(data["Location"].dropna().unique())
drainages  = sorted(data["DrainageCondition"].dropna().unique())

default_values = {
    "NumRooms"         : int(data["NumRooms"].median()),
    "SquareFootage"    : float(data["SquareFootage"].median()),
    "City"             : data["City"].mode()[0],
    "Street"           : data["Street"].mode()[0],
    "Location"         : data["Location"].mode()[0],
    "DrainageCondition": data["DrainageCondition"].mode()[0],
}

# ── Auth helpers ──────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("welcome"))
        return f(*args, **kwargs)
    return decorated

# ── Routes ────────────────────────────────────────────────────────
@app.route("/")
def welcome():
    if "username" in session:
        return redirect(url_for("home"))
    return render_template("welcome.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name  = request.form["name"]
        email = request.form["email"]
        pwd   = request.form["password"]

        if not all([name, email, pwd]):
            return "All fields are required", 400

        hashed = generate_password_hash(pwd)
        cur    = mysql.connection.cursor()
        cur.execute("SELECT 1 FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            return "Email already exists.", 409

        cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name,email,hashed))
        mysql.connection.commit()
        cur.execute("SELECT id,name,email FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        session.update({"user_id":user["id"], "username":user["name"], "email":user["email"]})
        cur.close()
        return redirect(url_for("home"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pwd   = request.form["password"]
        cur   = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user  = cur.fetchone()
        cur.close()
        if user and check_password_hash(user["password"], pwd):
            session.update({"user_id":user["id"], "username":user["name"], "email":user["email"]})
            return redirect(url_for("home"))
        return "Invalid email or password", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))

@app.route("/home")
@login_required
def home():
    return render_template("index.html", cities=cities, streets=streets,
                           locations=locations, drainages=drainages)

@app.route("/predict", methods=["POST"])
@login_required
def predict():
    try:
        input_data = request.get_json() or {}
        for k, v in default_values.items():
            if not input_data.get(k):
                input_data[k] = v
        df = pd.DataFrame([input_data])
        prediction = {
            "predicted_price"     : f"{round(price_model.predict(df)[0],2):,}",
            "predicted_crime"     : round(crime_model.predict(df)[0],2),
            "predicted_employment": round(employment_model.predict(df)[0],2)
        }
        return jsonify(prediction)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Entry point for Render ────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
