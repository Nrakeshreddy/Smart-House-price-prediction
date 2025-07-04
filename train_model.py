import pandas as pd
import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

file_path = "C:\\Users\\rakes\\OneDrive\\Documents\\hpp.csv"
data = pd.read_csv(file_path)

numerical_features = ["NumRooms", "SquareFootage"]
categorical_features = ["City", "Street", "Location", "DrainageCondition"]

target_price = "Price"
target_crime = "CrimeRate"
target_employment = "EmploymentRate"

missing_columns = set(numerical_features + categorical_features + [target_price, target_crime, target_employment]) - set(data.columns)
if missing_columns:
    raise ValueError(f"Missing columns in dataset: {missing_columns}")

# Preprocessing pipeline
column_transformer = ColumnTransformer([
    ("num", StandardScaler(), numerical_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
])

# Function to train and save models
def train_and_save_model(X, y, filename, scale_price=False):
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create pipeline
    model = Pipeline([
        ("transformer", column_transformer),
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    # Scale the target price if required
    if scale_price:
        # Apply a scaling factor (e.g., divide by 2 to reduce prices)
        y_train = y_train / 2
        y_test = y_test / 2
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions and evaluate the model
    y_pred = model.predict(X_test)
    
    # Reverse the scaling for the predictions
    if scale_price:
        y_pred = y_pred * 2  # Revert the scaling (multiply by 2)
    
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Model: {filename}, MSE: {mse}, R2 Score: {r2}")
    
    # Save the trained model
    joblib.dump(model, filename)

# Prepare the feature matrix (X) and target vectors (y)
X = data[categorical_features + numerical_features]

# Train and save models
train_and_save_model(X, data[target_price], "house_price_model.pkl", scale_price=True)
train_and_save_model(X, data[target_crime], "crime_rate_model.pkl", scale_price=False)
train_and_save_model(X, data[target_employment], "employment_rate_model.pkl", scale_price=False)

print("All models (Price, Crime Rate, Employment Rate) have been saved successfully.")
