"""Remote Solar SCADA dashboard backed by a real environmental API."""

from __future__ import annotations

import math
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from MTech_Project_Phase7.live_data import (
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
    LiveDataError,
    build_forecast_telemetry,
    build_live_snapshot,
    fetch_live_environment,
)


st.set_page_config(page_title="Remote Solar SCADA", page_icon="☀️", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALARM_FILE = os.path.join(BASE_DIR, "data", "logs", "alarms.csv")


@st.cache_data(ttl=300, show_spinner="Calling Open-Meteo…")
def load_api_data(latitude: float, longitude: float):
    return fetch_live_environment(latitude, longitude)


@st.cache_data(ttl=30)
def load_alarms() -> pd.DataFrame:
    if not os.path.exists(ALARM_FILE):
        return pd.DataFrame()
    try:
        alarms = pd.read_csv(ALARM_FILE)
        alarms["ts"] = pd.to_datetime(alarms["ts"], errors="coerce")
        return alarms.dropna(subset=["ts"])
    except (pd.errors.EmptyDataError, KeyError):
        return pd.DataFrame()


st.title("Remote Solar SCADA System")
st.caption("Live environmental API • transparent PV digital twin • paginated telemetry explorer")

st.sidebar.header("Plant connection")
latitude = st.sidebar.number_input("Latitude", -90.0, 90.0, DEFAULT_LATITUDE, format="%.4f")
longitude = st.sidebar.number_input("Longitude", -180.0, 180.0, DEFAULT_LONGITUDE, format="%.4f")
if st.sidebar.button("Refresh upstream API", use_container_width=True):
    load_api_data.clear()

try:
    api_data = load_api_data(latitude, longitude)
    snapshot = build_live_snapshot(api_data)
    forecast = build_forecast_telemetry(api_data)
    upstream_ok = True
except LiveDataError as exc:
    upstream_ok = False
    st.error(f"Live source unavailable: {exc}")
    st.info("The dashboard has stopped instead of silently presenting stale data as live.")
    st.stop()

plant = snapshot[snapshot["inverter_id"] == "PLANT_SUMMARY"].iloc[-1]
inverters = snapshot[snapshot["inverter_id"] != "PLANT_SUMMARY"]

st.sidebar.success("● API connected" if upstream_ok else "● API offline")
st.sidebar.metric("HTTP response", f"{api_data.response_ms} ms")
st.sidebar.caption(f"Fetched {api_data.fetched_at.strftime('%d %b %Y, %H:%M:%S %Z')}")
st.sidebar.caption("Weather/irradiance: current model conditions or forecasts from Open-Meteo. Plant equipment: modelled.")
st.sidebar.markdown("[Weather data by Open-Meteo.com](https://open-meteo.com/)")

overview_tab, equipment_tab, explorer_tab, intelligence_tab, alarms_tab = st.tabs(
    ["Overview", "Equipment", "API Data Explorer", "Decision Intelligence", "Alarms"]
)

with overview_tab:
    st.subheader("Current operating picture")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Modelled plant power", f"{plant['P_AC_kW']:.1f} kW")
    c2.metric("Current API GHI", f"{plant['GHI']:.0f} W/m²")
    c3.metric("Current API ambient", f"{plant['AmbientTemp_C']:.1f} °C")
    c4.metric("Current API wind", f"{plant['wind_speed_m_s']:.1f} m/s")
    c5.metric("Modelled battery SOC", f"{plant['battery_soc']:.1f}%")

    chart_data = forecast.head(48)
    fig = px.line(
        chart_data,
        x="time",
        y=["Estimated_AC_kW", "GHI_W_m2"],
        title="Next 48 hours: modelled AC power and upstream irradiance",
    )
    fig.update_layout(hovermode="x unified", legend_title_text="Signal")
    st.plotly_chart(fig, use_container_width=True)
    st.info(
        "Data lineage: Open-Meteo supplies environmental conditions. AC power is calculated "
        "from irradiance, cell-temperature derating and 97% conversion efficiency."
    )

with equipment_tab:
    st.subheader("Inverter digital twin")
    equipment_view = inverters[
        ["ts", "inverter_id", "status", "rated_kw", "P_DC_kW", "P_AC_kW", "data_class"]
    ].copy()
    equipment_view[["P_DC_kW", "P_AC_kW"]] = equipment_view[["P_DC_kW", "P_AC_kW"]].round(2)
    st.dataframe(equipment_view, use_container_width=True, hide_index=True)
    st.caption("These are deterministic model outputs, not measurements from a connected field RTU.")

with explorer_tab:
    st.subheader("Paginated upstream telemetry")
    st.code(f"GET {api_data.endpoint}", language=None)
    a, b, c = st.columns(3)
    page_size = a.selectbox("Records per page", [10, 20, 25, 50], index=1)
    total_records = len(forecast)
    total_pages = max(1, math.ceil(total_records / page_size))
    page = int(b.number_input("Page", 1, total_pages, 1, step=1))
    b.caption(f"of {total_pages} pages")
    c.metric("Upstream records", total_records)

    start = (page - 1) * page_size
    end = min(start + page_size, total_records)
    page_df = forecast.iloc[start:end].copy()
    numeric_cols = page_df.select_dtypes(include="number").columns
    page_df[numeric_cols] = page_df[numeric_cols].round(2)
    st.dataframe(page_df, use_container_width=True, hide_index=True)
    st.caption(f"Showing records {start + 1}–{end} of {total_records} • page {page}/{total_pages}")

    with st.expander("API provenance and response metadata"):
        st.json(
            {
                "provider": api_data.source,
                "transport": "HTTPS / JSON",
                "authentication": "No API key required",
                "response_time_ms": api_data.response_ms,
                "cache_ttl_seconds": 300,
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "upstream_granularity": "current conditions + hourly forecast",
            }
        )

with intelligence_tab:
    st.subheader("Rule-based operating recommendations")
    expected = max(1.0, plant["GHI"] / 1000.0 * plant["rated_kw"])
    performance_ratio = plant["P_AC_kW"] / expected
    if plant["GHI"] < 20:
        st.success("Night/low-irradiance state: keep inverters in standby and preserve battery reserve.")
    elif performance_ratio < 0.75:
        st.warning("Modelled performance ratio is below 0.75; inspect temperature and conversion losses.")
    else:
        st.success(f"Modelled performance ratio is {performance_ratio:.2f}; no intervention indicated.")
    if plant["battery_soc"] > 80:
        st.info("Battery reserve is high; enable export or flexible loads if site policy permits.")
    st.caption("Recommendations are explainable rules, not autonomous control commands.")

with alarms_tab:
    alarms = load_alarms()
    st.subheader("Simulator alarm history")
    if alarms.empty:
        st.success("No recorded simulator alarms")
    else:
        severity_score = {"Critical": 3, "High": 2, "Medium": 1}
        alarms["priority"] = alarms["severity"].map(severity_score).fillna(0)
        st.dataframe(
            alarms.sort_values(["priority", "ts"], ascending=False).head(50),
            use_container_width=True,
            hide_index=True,
        )
    st.caption("Alarm records originate from the local simulator and are labelled separately from API data.")
