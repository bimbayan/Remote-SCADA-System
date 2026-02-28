import streamlit as st
import pandas as pd
import time
import plotly.express as px
import os

st.set_page_config(layout="wide", page_title="Solar SCADA Prototype")

st.title("Solar PV Plant SCADA — Remote Monitoring Prototype")

refresh_s = st.sidebar.number_input("Refresh Interval (seconds)", value=5, min_value=1, max_value=30)

LIVE_FILE = os.path.abspath("data/live/plant_live.csv")

# Auto-refresh
st.experimental_rerun = st.rerun

# Create placeholders
placeholder_kpis = st.empty()
placeholder_table = st.empty()
placeholder_chart = st.empty()
placeholder_alarms = st.empty()

if "history" not in st.session_state:
    st.session_state.history = []

def read_snapshot():
    if not os.path.exists(LIVE_FILE):
        return None
    if os.path.getsize(LIVE_FILE) == 0:          # still zero bytes
        return None
    try:
        return pd.read_csv(LIVE_FILE)
    except pd.errors.EmptyDataError:             # catches 0-col or 0-row
        return None


def update_history(df):
    plant_row = df[df["inverter_id"] == "PLANT_SUMMARY"].iloc[0].to_dict()
    ts = pd.to_datetime(plant_row["ts"], errors="coerce")

    # no more duplicate-ts logic needed
    plant_row["ts"] = ts
    st.session_state.history.append(plant_row)
    st.session_state.history = st.session_state.history[-500:]


def render_kpis(plant):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Plant Power (kW)", f"{plant['P_AC_kW']:.2f}")
    col2.metric("GHI (W/m²)", f"{plant['GHI']:.1f}")
    col3.metric("Ambient Temp (°C)", f"{plant['AmbientTemp_C']:.1f}")
    col4.metric("Total Energy (kWh)", f"{plant['Total_energy_kWh']:.1f}")

def render_chart():
    hist = pd.DataFrame(st.session_state.history)
    if len(hist) < 2:
        st.info("Waiting for more data to plot…")
        return

    hist["ts"] = pd.to_datetime(hist["ts"], errors="coerce")
    latest_p = hist["P_AC_kW"].iloc[-1]

    # ---- auto-zoom exactly what you were double-clicking ----
    delta = latest_p * 0.005                       # 0.5 % micro-window
    now = hist["ts"].iloc[-1]
    xmin = now - pd.Timedelta(minutes=10)

    fig = px.line(
        hist,
        x="ts",
        y="P_AC_kW",
        title="Plant Power Trend (kW) – micro resolution",
        range_x=[xmin, now]
    )

    fig.update_layout(
        yaxis=dict(range=[latest_p - delta, latest_p + delta]),
        uirevision="constant",                     # keep zoom when data updates
        xaxis=dict(tickformat="%H:%M:%S", nticks=8),
        template="plotly_dark",
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

def get_alarms(df):
    alarms = []
    plant = df[df["inverter_id"]=="PLANT_SUMMARY"].iloc[0]
    plant_power = plant["P_AC_kW"]
    invs = df[df["inverter_id"]!="PLANT_SUMMARY"]

    for _, row in invs.iterrows():
        expected = (row["rated_kw"] / plant["rated_kw"]) * plant_power
        if expected > 0 and (row["P_AC_kW"] / expected * 100) < 50:
            alarms.append((row["inverter_id"], row["P_AC_kW"], expected))

    return alarms



df = read_snapshot()

if df is not None:

    numeric = ["P_AC_kW", "GHI", "AmbientTemp_C", "Total_energy_kWh", "rated_kw"]
    for col in numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    plant = df[df["inverter_id"]=="PLANT_SUMMARY"].iloc[0]

    update_history(df)

    with placeholder_kpis:
        render_kpis(plant)

    with placeholder_table:
        st.subheader("Inverter Status")
        st.dataframe(df[df["inverter_id"]!="PLANT_SUMMARY"], height=350)

    with placeholder_chart:
        render_chart()

    alarms = get_alarms(df)
    with placeholder_alarms:
        if alarms:
            st.error(f"{len(alarms)} active alarms")
            st.table(pd.DataFrame(alarms, columns=["Inverter","Actual","Expected"]))
        else:
            st.success("No active alarms")

# Auto-refresh the entire page
time.sleep(refresh_s)
st.experimental_rerun()
