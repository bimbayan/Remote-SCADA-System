# we start with a simple linear regression model, after testing it we'll update it to XGBoost or something else

import pandas as pd
import streamlit as slt 
import os 
import joblib 
import numpy as np

from sklearn.linear_model import LinearRegression 
from sklearn.model_selection import train_test_split 
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error



#this section loads data 
data_path = "data/curated/multi_year/pvgis_2018_2023_with_power.csv"

df = pd.read_csv(data_path)
df = df.dropna(subset=["GHI", "Temperature", "WindSpeed", "P_AC_kW"])
df = df[df["GHI"] > 20]


#this section sets the features 

X = df[["GHI", "Temperature", "WindSpeed"]]
y = df[["P_AC_kW"]]

# this following section is for the test and train split 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = LinearRegression()
model.fit(X_train, y_train)

#the following section will evaluate the model 

y_pred = model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mape = mean_absolute_percentage_error(y_test, y_pred) * 100 

print ("Model has been trained.")
print(f"RMSE: {rmse:.3f} kW")
print(f"MAPE: {mape:.2f}%")

#the following section will now save the model

os.makedirs("model", exist_ok = True)
joblib.dump(model, "model/solar_power_predictor.pkl")
print("Model has been saved.")

