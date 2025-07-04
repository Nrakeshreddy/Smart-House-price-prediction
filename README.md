# Smart-House-price-prediction
# 🏠 Smart House Price Prediction

This is a Flask-based web application that predicts:
-  House Price
-  Crime Rate
-  Employment Rate

based on user input like City, Location, Number of Rooms, etc.

---

## 🔧 Technologies Used

- Python 3
- Flask
- MySQL
- HTML, CSS, Jinja2 Templates
- Scikit-Learn (machine learning models)
- Joblib (model saving/loading)

---

##  Project Structure

├── app.py
├── train_model.py
├── templates/
│ ├── index.html
│ ├── login.html
│ ├── signup.html
│ └── welcome.html
├── column_transformer.pkl
├── crime_rate_model.pkl
├── employment_rate_model.pkl
├── house_price_model.pkl
├── house_price_model_pipeline.pkl
├── requirements.txt
├── .gitignore

---

## ⚙️ Setup Instructions

###  Clone the Repo
git clone https://github.com/Nrakeshreddy/Smart-House-price-prediction.git
cd Smart-House-price-prediction

Create a Virtual Environment (Optional but Recommended)
python -m venv venv
venv\Scripts\activate   # For Windows
# source venv/bin/activate  # For Linux/Mac

Install Requirements
pip install -r requirements.txt

Set Up MySQL Database
Create a database named house_price_db
Create a table users:
sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255)
);

Run the App
python app.py
Open browser at:
📍 http://127.0.0.1:5000

🔐 Features
User signup, login, and logout
Predictions based on dropdown and numeric inputs
Auto-filled default values

💼 Models Included
The following models are pre-trained and included in .pkl format:
house_price_model.pkl
crime_rate_model.pkl
employment_rate_model.pkl
