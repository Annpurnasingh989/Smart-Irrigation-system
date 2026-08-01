import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
import joblib

# Dataset load
data = pd.read_csv("dataset/irrigation_dataset.csv")

# Crop ko number me convert
encoder = LabelEncoder()
data["Crop"] = encoder.fit_transform(data["Crop"])

# Input aur Output
X = data[["Temperature", "Humidity", "Crop"]]
y = data["WaterRequired"]

# Model Train
model = DecisionTreeRegressor()
model.fit(X, y)

# Save Model
joblib.dump(model, "models/irrigation_model.pkl")
joblib.dump(encoder, "models/crop_encoder.pkl")

print("✅ Model Trained Successfully!")