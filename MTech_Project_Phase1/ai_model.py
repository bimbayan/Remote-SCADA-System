import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Load dataset
df = pd.read_csv("sensor_data.csv")

# Features and target
X = df[["temperature", "irradiance"]]
y = df["power"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
joblib.dump(model, "power_model.pkl")
print("Model trained and saved as power_model.pkl")
