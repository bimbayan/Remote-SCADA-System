import streamlit as st
import plotly.express as px
import pandas as pd
import time

# --- Page setup ---
st.set_page_config(page_title="AI-Assisted Digital Twin", layout="wide")
st.title("Live Digital Twin Dashboard")

# --- Initialize state ---
if "iteration" not in st.session_state:
    st.session_state.iteration = 0

# --- Start button ---
if st.button("Start Simulation"):
    st.session_state.run = True

# --- Stop button ---
if st.button("Stop Simulation"):
    st.session_state.run = False

# --- Placeholder for chart ---
chart_placeholder = st.empty()

# --- Run simulation if toggled ---
if st.session_state.get("run", False):
    iteration = st.session_state.iteration

    # Create fake (or sensor) data
    df = pd.DataFrame({
        "time": pd.date_range(start="2025-01-01", periods=10, freq="s"),
        "value": [i + iteration for i in range(10)]
    })

    # Make chart
    fig = px.line(df, x="time", y="value", title="Real-time Sensor Data")

    # Give a dynamic key so Streamlit knows each chart is new
    chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"chart_{iteration}")

    # Increment for next cycle
    st.session_state.iteration += 1

    # Now, wait a bit before re-running
    time.sleep(2)

    # This tells Streamlit to re-run the script
    st.rerun()
