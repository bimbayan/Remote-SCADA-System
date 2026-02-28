import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from pandas.errors import EmptyDataError
from datetime import datetime

#from decision_engine import generate_decisions


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Remote Solar SCADA System",
    layout="wide"
)

# =========================================================
# PATH RESOLUTION (NO GUESSWORK)
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LIVE_FILE = os.path.join(BASE_DIR, "data", "live", "plant_live.csv")
ALARM_FILE = os.path.join(BASE_DIR, "data", "logs", "alarms.csv")
# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("SCADA Status")
st.sidebar.markdown(f"📁 Data path:\n`{BASE_DIR}`") 

# =========================================================
# DATA LOADERS (THIS IS THE HEART)
# =========================================================
@st.cache_data(ttl=5)
def load_live_data():
    if not os.path.exists(LIVE_FILE):
        return None

    try:
        df = pd.read_csv(LIVE_FILE)
        if df.empty:
            return None

        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.dropna(subset=["ts"])
        return df

    except EmptyDataError:
        return None


@st.cache_data(ttl=5)
def load_alarms():
    if not os.path.exists(ALARM_FILE):
        return pd.DataFrame()

    try:
        df = pd.read_csv(ALARM_FILE)
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        return df.dropna(subset=["ts"])
    except EmptyDataError:
        return pd.DataFrame()


df = load_live_data()
alarms = load_alarms()

# =========================================================
# HEADER
# =========================================================
st.title("Remote SCADA System")


st.markdown(
    f"🕒 **Last refresh:** `{datetime.now().strftime('%H:%M:%S')}`"
)

if df is None:
    st.warning("Waiting for simulator data…")
    st.stop()

# =========================================================
# PLANT SUMMARY ROW
# =========================================================
plant_rows = df[df["inverter_id"] == "PLANT_SUMMARY"]

if plant_rows.empty:
    st.error("PLANT_SUMMARY row not found. Simulator issue.")
    st.stop()

plant = plant_rows.iloc[-1]
trend_df = plant_rows.sort_values("ts")

# =========================================================
# TABS (CHROME-STYLE)
# =========================================================
tabs = st.tabs([
    "Overview","Irradiance","Energy Flow","Losses","DC Health",
    "Inverter Health","Battery","Environment","Predictive",
    "Alarm Priority","Decision Intelligence"
])


# =========================================================
# OVERVIEW
# =========================================================
with tabs[0]:
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Plant Power (kW)", f"{plant['P_AC_kW']:.1f}")
    c2.metric("GHI (W/m²)", f"{plant['GHI']:.0f}")
    c3.metric("Ambient Temp (°C)", f"{plant['AmbientTemp_C']:.1f}")
    c4.metric("Total Energy (kWh)", f"{plant['Total_energy_kWh']:.2f}")
    c5.metric("Battery SOC (%)", f"{plant['battery_soc']:.1f}")

    st.subheader("Plant Output Trend")

    if len(trend_df) < 2:
        st.info("Trend building… need more samples.")
    else:
        fig = px.line(
            trend_df,
            x="ts",
            y="P_AC_kW",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Power (kW)",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# IRRADIANCE
# =========================================================
with tabs[1]:
    clear_sky = 1000
    ratio = plant["GHI"] / clear_sky * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("POA Irradiance (W/m²)", f"{plant['GHI']:.0f}")
    c2.metric("GHI vs Clear Sky (%)", f"{ratio:.1f}")
    c3.metric("Spectral Factor", "0.98")

# =========================================================
# ENERGY FLOW
# =========================================================
with tabs[2]:
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("DC Array Power (kW)", f"{plant['P_DC_kW']:.1f}")
    c2.metric("Inverter AC (kW)", f"{plant['P_AC_kW']:.1f}")
    c3.metric("Station Load (kW)", "3.5")

    loss = plant.get("transformer_loss_kw", 0)
    c4.metric("Export @ POI (kW)", f"{plant['P_AC_kW'] - loss:.1f}")

    pr = plant["P_AC_kW"] / max(1, plant["GHI"] / 1000 * plant["rated_kw"])
    st.metric("Instantaneous PR", f"{pr:.2f}")

# =========================================================
# LOSSES
# =========================================================
with tabs[3]:
    loss_df = pd.DataFrame({
        "Loss Type": ["Availability", "Curtailment", "Soiling", "Clipping"],
        "Lost kWh": np.random.uniform(1, 10, 4)
    })

    fig = px.bar(loss_df, x="Lost kWh", y="Loss Type", orientation="h")
    st.plotly_chart(fig, use_container_width=True)


# DC HEALTH

with tabs[4]:
    cols = st.columns(4)
    cols[0].metric("String Spread (%)", "6.1")
    cols[1].metric("Max Module Temp (°C)", "57.8")
    cols[2].metric("Insulation (MΩ)", "840")
    cols[3].metric("AFCI Trips", "0")


# INVERTER HEALTH

with tabs[5]:
    cols = st.columns(4)
    cols[0].metric("IGBT Temp (°C)", "71")
    cols[1].metric("THD-V (%)", "2.0")
    cols[2].metric("Power Factor", "0.99")
    cols[3].metric("DC Bus Ripple (V)", "4.1")


# BATTERY

with tabs[6]:
    cols = st.columns(4)
    cols[0].metric("SOC (%)", f"{plant['battery_soc']:.1f}")
    cols[1].metric("SOH (%)", "96.4")
    cols[2].metric("Cycles", "318")
    cols[3].metric("Cell ΔV (mV)", "17")


# ENVIRONMENT

with tabs[7]:
    cols = st.columns(4)
    cols[0].metric("Temp (°C)", f"{plant['AmbientTemp_C']:.1f}")
    cols[1].metric("Wind (m/s)", "4.1")
    cols[2].metric("Humidity (%)", "49")
    cols[3].metric("Dust", "Moderate")

# =========================================================
# PREDICTIVE
# =========================================================
with tabs[8]:
    st.metric("Next Wash", "6 days")
    st.metric("Thermal Headroom", "13 h")
    st.metric("Battery Life to 80% SOH", "4.1 years")

# =========================================================
# ALARMS
# =========================================================
with tabs[9]:
    if alarms.empty:
        st.success("No active alarms")
    else:
        alarms["RiskScore"] = np.random.uniform(1, 10, len(alarms))
        st.dataframe(
            alarms.sort_values("RiskScore", ascending=False).head(10),
            use_container_width=True
        )
    st.markdown("⚠️ Alarm priority is based on a simulated risk score for demonstration purposes only.")    

##
#with tabs[10]:
  #  st.subheader("Decision Intelligence — What to do next")

 #   decisions = generate_decisions(df_live)

  #  for i, row in decisions.iterrows():
  #      st.markdown(f"""
  #      ### {i+1}. {row['action']}
  #      **Why:** {row['reason']}  
  #      **Estimated gain:** {row['estimated_gain_kw']} kW  
  #      **Priority score:** {row['priority_score']}
  #      """)


#formulae logic, basic equations logic explanation in the final report 
