import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import plotly.express as px
from pandas.errors import EmptyDataError

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Solar SCADA Phase 6")

LIVE_FILE = os.path.abspath("data/live/plant_live.csv")
ALARM_FILE = os.path.abspath("data/logs/alarms.csv")

st.title("Solar PV Plant SCADA — Phase 6")
st.caption("Operational vital signs | Financial metrics intentionally hidden")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
refresh_s = st.sidebar.slider("Refresh interval (seconds)", 2, 20, 5)

tab = st.sidebar.radio(
    "SCADA Views",
    [
        "Overview",
        "Irradiance & Resource",
        "Energy Flow",
        "Loss Diagnostics",
        "String & Module Health",
        "Inverter & Power Quality",
        "Battery Health",
        "Environmental",
        "Predictive / AI",
        "Alarm Priority"
    ]
)

# --------------------------------------------------
# SESSION STATE (HISTORIAN)
# --------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame()

# --------------------------------------------------
# DATA LOADERS
# --------------------------------------------------
def read_snapshot():
    if not os.path.exists(LIVE_FILE):
        return None
    try:
        df = pd.read_csv(LIVE_FILE)
        if df.empty:
            return None
        return df
    except EmptyDataError:
        return None

def read_alarms():
    if not os.path.exists(ALARM_FILE):
        return pd.DataFrame()
    try:
        return pd.read_csv(ALARM_FILE)
    except EmptyDataError:
        return pd.DataFrame()

df = read_snapshot()
alarms = read_alarms()

if df is None:
    st.warning("Waiting for simulator data…")
    time.sleep(refresh_s)
    st.rerun()

# --------------------------------------------------
# PLANT SUMMARY
# --------------------------------------------------
plant_df = df[df["inverter_id"] == "PLANT_SUMMARY"]

if plant_df.empty:
    st.error("PLANT_SUMMARY row missing")
    st.stop()

plant = plant_df.iloc[0].to_dict()

# update historian
row = plant.copy()
row["ts"] = pd.Timestamp.now()
st.session_state.history = pd.concat(
    [st.session_state.history, pd.DataFrame([row])],
    ignore_index=True
).tail(500)

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------
if tab == "Overview":
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Plant Power (kW)", f"{plant['P_AC_kW']:.1f}")
    c2.metric("GHI (W/m²)", f"{plant['GHI']:.0f}")
    c3.metric("Ambient Temp (°C)", f"{plant['AmbientTemp_C']:.1f}")
    c4.metric("Total Energy (kWh)", f"{plant['Total_energy_kWh']:.2f}")
    c5.metric("Battery SOC (%)", f"{plant['battery_soc']:.1f}")

    st.subheader("Plant Power Trend")
    hist = st.session_state.history
    if len(hist) > 1:
        fig = px.line(hist, x="ts", y="P_AC_kW", markers=True)
        st.plotly_chart(fig, width=True)
    else:
        st.info("Building trend history…")

# --------------------------------------------------
# IRRADIANCE & RESOURCE
# --------------------------------------------------
elif tab == "Irradiance & Resource":
    clear_sky_ghi = 1000
    ghi_ratio = plant["GHI"] / clear_sky_ghi * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("POA Irradiance (W/m²)", f"{plant['GHI']:.0f}")
    c2.metric("GHI vs Clear Sky (%)", f"{ghi_ratio:.1f}")
    c3.metric("Spectral Correction", "0.98 (est)")

# --------------------------------------------------
# ENERGY FLOW
# --------------------------------------------------
elif tab == "Energy Flow":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DC Array Power (kW)", f"{plant['P_DC_kW']:.1f}")
    c2.metric("Inverter AC (kW)", f"{plant['P_AC_kW']:.1f}")
    c3.metric("Station Load (kW)", "3.5 (est)")
    c4.metric(
        "Transformer Output (kW)",
        f"{plant['P_AC_kW'] - plant['transformer_loss_kw']:.1f}"
    )

    pr = plant["P_AC_kW"] / max(1, plant["GHI"]/1000 * plant["rated_kw"])
    st.metric("Instantaneous PR", f"{pr:.2f}")

# --------------------------------------------------
# LOSS DIAGNOSTICS
# --------------------------------------------------
elif tab == "Loss Diagnostics":
    loss_data = pd.DataFrame({
        "Loss Type": ["Availability", "Curtailment", "Soiling", "Clipping"],
        "Lost kWh": np.random.uniform(0, 6, 4)
    })
    fig = px.bar(loss_data, x="Lost kWh", y="Loss Type", orientation="h")
    st.plotly_chart(fig, width=True)

# --------------------------------------------------
# STRING & MODULE HEALTH
# --------------------------------------------------
elif tab == "String & Module Health":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("String Current Spread (%)", "6.2")
    c2.metric("Max Module Temp (°C)", "58.4")
    c3.metric("Insulation Resistance (MΩ)", "850")
    c4.metric("AFCI Trips (24h)", "0")

# --------------------------------------------------
# INVERTER & POWER QUALITY
# --------------------------------------------------
elif tab == "Inverter & Power Quality":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("IGBT Temp (°C)", "72")
    c2.metric("THD-V (%)", "2.1")
    c3.metric("Power Factor", "0.99")
    c4.metric("DC Bus Ripple (V)", "4.2")

# --------------------------------------------------
# BATTERY HEALTH
# --------------------------------------------------
elif tab == "Battery Health":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SOC (%)", f"{plant['battery_soc']:.1f}")
    c2.metric("SOH (%)", "96.5")
    c3.metric("Cycle Count", "312")
    c4.metric("Voltage Spread (mV)", "18")

# --------------------------------------------------
# ENVIRONMENTAL
# --------------------------------------------------
elif tab == "Environmental":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ambient Temp (°C)", f"{plant['AmbientTemp_C']:.1f}")
    c2.metric("Wind Speed (m/s)", "4.2")
    c3.metric("Humidity (%)", "48")
    c4.metric("Dust Index", "Moderate")

# --------------------------------------------------
# PREDICTIVE / AI
# --------------------------------------------------
elif tab == "Predictive / AI":
    st.metric("Next Optimal Wash", "In 6 days")
    st.metric("Inverter Thermal Headroom", "14 hours")
    st.metric("Battery Life to 80% SOH", "4.2 years")

# --------------------------------------------------
# ALARM PRIORITY
# --------------------------------------------------
elif tab == "Alarm Priority":
    if alarms.empty:
        st.success("No active alarms")
    else:
        alarms["RiskScore"] = np.random.uniform(1, 10, len(alarms))
        top = alarms.sort_values("RiskScore", ascending=False).head(10)
        st.table(top[["ts","source","severity","message","RiskScore"]])

# --------------------------------------------------
# AUTO REFRESH (SAFE)
# --------------------------------------------------
time.sleep(refresh_s)
st.rerun()
