import streamlit as st
import pickle
import pandas as pd

# Load trained model
with open("trainedmodel.pkl", "rb") as f:
    model = pickle.load(f)

st.title("M.Tech Project Dashboard - Phase 2")
st.write("Upload your CSV to make predictions")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    if "Output" in data.columns:
        data = data.drop(columns = ["Output"])
    st.write("### Uploaded Data", data.head())

    if st.button("Predict"):
        predictions = model.predict(data)
        st.write("### Predictions", predictions)
