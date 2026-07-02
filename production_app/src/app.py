import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_autorefresh import st_autorefresh

from location_service import LocationService
from weather_service import WeatherService
from prediction_service import PredictionService
from recommendation_service import RecommendationService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from database import get_engine


st.set_page_config(page_title="PV SCADA UI", layout="wide", initial_sidebar_state="expanded")

# CUSTOM CSS FOR INDUSTRIAL LOOK
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    /* Global Font */
    * {
        font-family: 'Inter', sans-serif !important;
    }

    /* Hide Streamlit Header & Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Remove Top Padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Main Background */
    .stApp { background-color: #0a0a0f; color: #f0f0f5; }
    
    /* Panel Containers */
    div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #141419;
        border: 1px solid #1f1f28 !important;
        border-radius: 6px;
    }
    
    /* Headers */
    h1, h2, h3 { color: #f0f0f5 !important; font-family: 'Inter', sans-serif !important; font-weight: 600;}
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #f0f0f5 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #8b8b9a !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0a0a0f !important;
        border-right: 1px solid #1f1f28;
    }
    
    /* Force Sidebar Radio Text Color */
    [data-testid="stSidebar"] .stRadio p, [data-testid="stSidebar"] .stRadio label {
        color: #f0f0f5 !important;
        font-size: 14px !important;
    }
    
    /* Fix Sidebar Buttons (e.g. Logout) */
    [data-testid="stSidebar"] button {
        background-color: #141419 !important;
        color: #f0f0f5 !important;
        border: 1px solid #2a2a35 !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: #1f1f28 !important;
        border-color: #00d4aa !important;
    }
    
    .panel-title {
        background-color: #1f1f28;
        padding: 5px 10px;
        font-size: 12px;
        font-weight: 600;
        color: #f0f0f5;
        text-align: center;
        border-bottom: 1px solid #2a2a35;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* LED Indicators */
    .led-green {
        height: 12px; width: 12px;
        background-color: #00d4aa;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 5px #00d4aa;
        margin-right: 5px;
    }
    .led-red {
        height: 12px; width: 12px;
        background-color: #ff4757;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 5px #ff4757;
        margin-right: 5px;
    }
    .led-amber {
        height: 12px; width: 12px;
        background-color: #ffb800;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 5px #ffb800;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# AUTHENTICATION
# =========================================================
with open(os.path.join(BASE_DIR, 'src', 'config.yaml')) as file:
    config = yaml.load(file, Loader=SafeLoader)

admin_password_hash = os.environ.get("ADMIN_PASSWORD_HASH")
if admin_password_hash:
    config['credentials']['usernames']['admin']['password'] = admin_password_hash

cookie_key = os.environ.get("COOKIE_KEY")
if cookie_key:
    config['cookie']['key'] = cookie_key

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state.get("authentication_status") is False:
    st.error('Username/password is incorrect')
    st.stop()
elif st.session_state.get("authentication_status") is None:
    st.warning('Please enter your username and password to access the SCADA system')
    st.stop()

st_autorefresh(interval=5000, limit=None, key="scada_dashboard_refresh")

# =========================================================
# DATA LOADERS
# =========================================================
def load_live_data():
    engine = get_engine()
    try:
        df = pd.read_sql("SELECT * FROM plant_live ORDER BY ts DESC LIMIT 300", con=engine)
        if df.empty: return None
        df = df.sort_values("ts").reset_index(drop=True)
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        return df.dropna(subset=["ts"])
    except Exception as e:
        import traceback
        st.error(f"load_live_data error:\n```\n{traceback.format_exc()}\n```")
        return None

# Load data — autorefresh handles retry every 5 seconds
df = load_live_data()

authenticator.logout('Logout', 'sidebar', key="logout_btn")

# SIDEBAR NAV
st.sidebar.markdown(f"**User:** admin <br/> **Time:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "⚙️ Plant Control", "🏠 Home", "🗺️ Overview", "🏢 Substation", "🔔 Alarm", "📈 Trend", "🔌 Utilities", "🔮 Predictor"],
    label_visibility="collapsed")

# ── Sidebar Alarm Ticker ────────────────────────────────────
st.sidebar.markdown("---")
try:
    _sidebar_alarms = pd.read_sql(
        "SELECT ts, source, severity, message FROM alarms ORDER BY ts DESC LIMIT 3",
        con=get_engine()
    )
    if _sidebar_alarms.empty:
        st.sidebar.markdown("<div style='font-size:11px; color:#00d4aa; padding:4px 6px;'>✅ No active alarms</div>", unsafe_allow_html=True)
    else:
        _sev_c = {"Critical": "#ff4757", "High": "#ffb800", "Warning": "#3b82f6", "Info": "#8b8b9a"}
        st.sidebar.markdown("<div style='font-size:10px; color:#8b8b9a; text-transform:uppercase; letter-spacing:0.5px; padding:4px 6px; margin-bottom:2px;'>🚨 Latest Alarms</div>", unsafe_allow_html=True)
        for _, _al in _sidebar_alarms.iterrows():
            _c = _sev_c.get(_al.get("severity", "Info"), "#8b8b9a")
            st.sidebar.markdown(
                f"<div style='font-size:10px; padding:4px 6px; border-left:3px solid {_c}; margin-bottom:3px; background:#141419; border-radius:0 4px 4px 0;'>"
                f"<span style='color:{_c}; font-weight:700;'>{_al.get('severity','?')}</span> "
                f"<span style='color:#8b8b9a;'>{_al.get('source','?')}</span><br/>"
                f"<span style='color:#ccc; font-size:9px;'>{str(_al.get('message',''))[:40]}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
except Exception:
    pass

if df is None:
    # Show diagnostic info to debug why data is missing
    import sqlalchemy as sa
    diag = []
    try:
        _eng = get_engine()
        from database import DB_PATH
        diag.append(f"**DB Path:** `{DB_PATH}`")
        diag.append(f"**DB exists:** `{os.path.exists(DB_PATH)}`")
        with _eng.connect() as _conn:
            tables = _conn.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
            diag.append(f"**Tables:** `{[t[0] for t in tables]}`")
            for t in tables:
                cnt = _conn.execute(sa.text(f"SELECT count(*) FROM [{t[0]}]")).scalar()
                diag.append(f"  - `{t[0]}`: **{cnt}** rows")
            if any(t[0] == 'plant_live' for t in tables):
                sample = _conn.execute(sa.text("SELECT ts, inverter_id FROM plant_live ORDER BY rowid DESC LIMIT 3")).fetchall()
                diag.append(f"**Latest plant_live rows:** `{sample}`")
    except Exception as ex:
        diag.append(f"**Diagnostic error:** `{ex}`")
    st.warning("Waiting for simulator data...")
    st.code("\n".join(diag))
    st.stop()

plant_rows = df[df["inverter_id"] == "PLANT_SUMMARY"]
if plant_rows.empty:
    st.error("PLANT_SUMMARY row not found.")
    st.stop()

plant = plant_rows.iloc[-1]
trend_df = plant_rows.sort_values("ts")

# =========================================================
# UTILS FOR PLOTS
# =========================================================
PLOT_LAYOUT = dict(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=10, b=10),
    font=dict(color="#8b8b9a", family="Inter, sans-serif")
)

if menu == "📊 Dashboard":
    _p_ac_live = plant['P_AC_kW']
    st.markdown(f"""
        <div style="background-color:#141419; padding:10px 20px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; border: 1px solid #1f1f28; margin-bottom:15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <div style="font-weight:bold; letter-spacing:1px; text-transform:uppercase; font-size:16px; color:#f0f0f5;">Remote SCADA — Live Dashboard</div>
            <div style="font-size:13px; color:#8b8b9a;">Plant Status: <span class="led-green" style="margin-left:5px; margin-right:5px;"></span> <span style="color:#00d4aa; font-weight:600;">RUNNING</span> <span style="margin: 0 15px; color:#2a2a35;">|</span> Grid Code: <span style="color:#f0f0f5; font-weight:600;">IEC 61727</span> <span style="margin: 0 15px; color:#2a2a35;">|</span> <span style="font-family:monospace; color:#f0f0f5;">{_p_ac_live:.1f} kW</span></div>
        </div>
    """, unsafe_allow_html=True)

    # ── Row 1: KPI strip ──────────────────────────────────────────
    d1, d2, d3, d4, d5 = st.columns(5)
    p_out  = plant['P_AC_kW']
    max_p  = plant['rated_kw']
    load_p = round(p_out / max(1, max_p) * 100, 1)
    lc     = "#00d4aa" if load_p >= 70 else ("#ffb800" if load_p >= 30 else "#ff4757")
    def dash_kpi(col, lbl, val, unit, color="#f0f0f5"):
        col.markdown(f"""<div style='background:#141419; border:1px solid #1f1f28; border-radius:6px; padding:12px 8px; text-align:center;'>
            <div style='font-size:10px; color:#8b8b9a; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:5px;'>{lbl}</div>
            <div style='font-size:20px; font-weight:700; color:{color}; font-family:monospace;'>{val}</div>
            <div style='font-size:10px; color:#8b8b9a; margin-top:3px;'>{unit}</div>
        </div>""", unsafe_allow_html=True)
    dash_kpi(d1, "AC Power",    f"{p_out:.1f}",                      "kW",   lc)
    dash_kpi(d2, "Load Factor", f"{load_p:.1f}",                    "%",    lc)
    dash_kpi(d3, "Energy Today",f"{plant['Total_energy_kWh']:.1f}", "kWh",  "#3b82f6")
    dash_kpi(d4, "Irradiance",  f"{plant['GHI']:.0f}",              "W/m²", "#ffb800")
    dash_kpi(d5, "Batt. SOC",   f"{plant.get('battery_soc',50):.1f}","%",  "#a78bfa")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Row 2: Meter donut + Generation bar ───────────────────────
    r1c1, r1c2 = st.columns([1, 1])

    with r1c1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">METER — POI</div>', unsafe_allow_html=True)
            c_donut, c_metrics = st.columns([1, 1])
            with c_donut:
                st.markdown("<div style='text-align:center; color:#8b8b9a; font-size:12px; margin-bottom:-8px; font-weight:600;'>Total Output Active Power</div>", unsafe_allow_html=True)
                fig = go.Figure(go.Pie(
                    values=[p_out, max(0, max_p - p_out)],
                    hole=0.75, textinfo="none",
                    marker=dict(colors=[lc, "#1f1f28"])
                ))
                fig.update_layout(**PLOT_LAYOUT, showlegend=False, height=190,
                    annotations=[dict(text=f"<b>{p_out:.1f}</b><br>kW", font_size=22, font_color="#f0f0f5", showarrow=False)])
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f"<div style='text-align:center; color:#8b8b9a; font-size:12px; margin-top:-8px; padding-bottom:15px;'>Frequency 50.07 Hz</div>", unsafe_allow_html=True)
            with c_metrics:
                inv_running = df[df["inverter_id"].str.startswith("INV")].groupby("inverter_id").last()
                n_run = int((inv_running["status"] == "Running").sum()) if not inv_running.empty else 0
                st.markdown(f"""
                <div style='font-size:13px; line-height:2; padding:0 10px;'>
                    <div style='display:flex; justify-content:space-between;'><span style='color:#8b8b9a;'>Reactive Power</span><span style='color:#f0f0f5; font-family:monospace; font-weight:700;'>0.11 MVAr</span></div>
                    <div style='display:flex; justify-content:space-between;'><span style='color:#8b8b9a;'>Power Factor</span><span style='color:#f0f0f5; font-family:monospace; font-weight:700;'>1.00</span></div>
                    <div style='display:flex; justify-content:space-between;'><span style='color:#8b8b9a;'>Voltage</span><span style='color:#f0f0f5; font-family:monospace; font-weight:700;'>112.7 kV</span></div>
                </div>
                <hr style='border-color:#1f1f28; margin:8px 0;'>
                <div style='font-size:12px; line-height:1.9; padding:0 10px; padding-bottom:12px;'>
                    <div><span class='led-green'></span> POI Online</div>
                    <div><span class='led-green'></span> DataServer 2 OK</div>
                    <div><span class='led-red'></span> DataServer 1 Offline</div>
                    <hr style='border-color:#1f1f28; margin:6px 0;'>
                    <div style='display:flex; justify-content:space-between;'><span style='color:#8b8b9a;'>Inverters Online</span><span style='color:#00d4aa; font-weight:700; font-family:monospace;'>{n_run} / 5</span></div>
                    <div style='display:flex; justify-content:space-between;'><span style='color:#8b8b9a;'>SCB Online</span><span style='color:#00d4aa; font-weight:700; font-family:monospace;'>10 / 10</span></div>
                </div>
                """, unsafe_allow_html=True)

    with r1c2:
        with st.container(border=True):
            st.markdown(f'<div class="panel-title">TOTAL GENERATION &nbsp;<span style="float:right; font-weight:400; color:#8b8b9a;">today: {plant["Total_energy_kWh"]:.1f} kWh</span></div>', unsafe_allow_html=True)
            current_hour = datetime.now().hour
            hours = list(range(24))
            gen = []
            for h in hours:
                if 6 <= h <= 18 and h <= current_hour:
                    peak = max_p * max(0, np.sin((h-6)/12*np.pi))
                    gen.append(round(peak * (0.88 + 0.12*np.random.rand()) * (5/3600), 2))
                else:
                    gen.append(0)
            fig2 = px.bar(x=hours, y=gen, color_discrete_sequence=["#3b82f6"])
            fig2.update_layout(**PLOT_LAYOUT, height=215, xaxis_title="Hour", yaxis_title="kWh")
            fig2.update_xaxes(showgrid=False, tickvals=list(range(0, 24, 2)))
            fig2.update_yaxes(showgrid=True, gridcolor='#1f1f28')
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    # ── Row 3: Power/Irradiance trend + Weather ───────────────────
    r2c1, r2c2 = st.columns([1, 1])

    with r2c1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">POWER / IRRADIANCE TREND</div>', unsafe_allow_html=True)
            if len(trend_df) >= 2:
                from plotly.subplots import make_subplots
                fig3 = make_subplots(specs=[[{"secondary_y": True}]])
                fig3.add_trace(go.Scatter(x=trend_df["ts"], y=trend_df["P_AC_kW"], name="AC Power",
                    line=dict(color="#00d4aa", width=2), fill="tozeroy", fillcolor="rgba(0,212,170,0.06)"), secondary_y=False)
                fig3.add_trace(go.Scatter(x=trend_df["ts"], y=trend_df["GHI"], name="GHI",
                    line=dict(color="#ffb800", width=1.5, dash="dot")), secondary_y=True)
                fig3.update_layout(**PLOT_LAYOUT, height=215, legend=dict(
                    orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=10, color="#8b8b9a")
                ))
                fig3.update_xaxes(showgrid=False)
                fig3.update_yaxes(showgrid=True, gridcolor='#1f1f28', secondary_y=False)
                fig3.update_yaxes(showgrid=False, secondary_y=True)
                st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Gathering trend data...")

    with r2c2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">CURRENT WEATHER</div>', unsafe_allow_html=True)
            wc1, wc2, wc3 = st.columns(3)
            def w_card(col, icon, label, val, unit):
                col.markdown(f"""<div style='text-align:center; padding:10px 4px; border:1px solid #1f1f28; border-radius:6px; background:#0a0a0f; margin:3px;'>
                    <div style='font-size:22px; margin-bottom:3px;'>{icon}</div>
                    <div style='font-size:10px; color:#8b8b9a; text-transform:uppercase; margin-bottom:3px;'>{label}</div>
                    <div style='font-size:18px; font-weight:700; color:#f0f0f5; font-family:monospace;'>{val}</div>
                    <div style='font-size:10px; color:#8b8b9a;'>{unit}</div>
                </div>""", unsafe_allow_html=True)
            w_card(wc1, "☀️", "Irradiance", f"{plant['GHI']:.0f}", "W/m²")
            w_card(wc2, "🌡️", "Amb. Temp", f"{plant['AmbientTemp_C']:.1f}", "°C")
            w_card(wc3, "🏭", "PV Temp", f"{plant['AmbientTemp_C']+20:.1f}", "°C")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            wc4, wc5, wc6 = st.columns(3)
            w_card(wc4, "💨", "Wind", "4.3", "m/s")
            w_card(wc5, "🧭", "Dir", "254", "°")
            w_card(wc6, "💧", "Humidity", "34.2", "%")

    # ── Row 4: SLD + Comms ────────────────────────────────────────
    r3c1, r3c2 = st.columns([1.3, 1])

    with r3c1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">SINGLE LINE DIAGRAM</div>', unsafe_allow_html=True)
            inv_latest = df[df["inverter_id"].str.startswith("INV")].sort_values("ts").groupby("inverter_id").last().reset_index()
            inv_cards = ""
            for i in range(1, 6):
                inv_id = f"INV-{i:02d}"
                if not inv_latest.empty and inv_id in inv_latest["inverter_id"].values:
                    r = inv_latest[inv_latest["inverter_id"] == inv_id].iloc[0]
                    s = r.get("status", "Running")
                    sc = "#00d4aa" if s == "Running" else "#ff4757"
                    led = "led-green" if s == "Running" else "led-red"
                    inv_cards += f"<div style='border:1px solid {sc}; padding:8px 6px; border-radius:4px; background:#0a0a0f; text-align:center; min-width:90px;'><div style='font-size:10px; color:#8b8b9a; font-weight:600; margin-bottom:4px;'>{inv_id}</div><div style='font-size:14px; font-weight:700; color:#f0f0f5; font-family:monospace;'>{r['P_AC_kW']:.0f} kW</div><div style='font-size:10px; margin-top:4px;'><span class='{led}'></span>{s}</div></div>"
                else:
                    inv_cards += f"<div style='border:1px solid #2a2a35; padding:8px 6px; border-radius:4px; background:#0a0a0f; text-align:center; min-width:90px; opacity:0.5;'><div style='font-size:10px; color:#8b8b9a; font-weight:600; margin-bottom:4px;'>{inv_id}</div><div style='font-size:14px; font-weight:700; color:#f0f0f5; font-family:monospace;'>--- kW</div><div style='font-size:10px; margin-top:4px; color:#8b8b9a;'>N/A</div></div>"
            st.markdown(f"""
            <div style='background:#050505; padding:16px; border-radius:5px; border:1px solid #1f1f28; font-size:12px; font-family:monospace; text-align:center;'>
                <div style='color:#3b82f6; font-weight:bold; margin-bottom:6px;'>⚡ 110kV GRID</div>
                <div style='color:#333;'>│</div>
                <div style='border:1px solid #ffb800; display:inline-block; padding:4px 20px; border-radius:3px; color:#ffb800; margin:4px 0;'>TX-01 &nbsp;110kV/33kV &nbsp;600KVA</div>
                <div style='color:#333;'>│</div>
                <div style='border:1px solid #3b82f6; display:inline-block; padding:4px 20px; border-radius:3px; color:#8b8b9a; margin:4px 0;'>RMU &nbsp; CB-1 CB-2 ■ CLOSED</div>
                <div style='color:#333; margin-bottom:8px;'>──────────────────────</div>
                <div style='display:flex; justify-content:center; gap:10px; flex-wrap:wrap;'>{inv_cards}</div>
            </div>
            """, unsafe_allow_html=True)

    with r3c2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">COMMUNICATION DIAGNOSTICS</div>', unsafe_allow_html=True)
            comms_d = [
                ("Modbus TCP", "Inverter-01..05", "Online",  "~13ms", "green"),
                ("IEC 61850",  "RMU-BCU-01",      "Online",  "8ms",   "green"),
                ("DNP3",       "Weather Stn",     "Online",  "25ms",  "green"),
                ("Modbus RTU", "DataServer-1",    "Offline", "—",     "red"),
                ("WebSocket",  "Streamlit Cloud", "Online",  "<5ms",  "green"),
            ]
            st.markdown("""
            <table style='width:100%; font-size:12px; border-collapse:collapse; color:#f0f0f5;'>
                <tr style='color:#8b8b9a; border-bottom:2px solid #2a2a35;'>
                    <th style='padding:8px; text-align:left;'>Protocol</th>
                    <th style='padding:8px; text-align:left;'>Device</th>
                    <th style='padding:8px; text-align:left;'>Status</th>
                    <th style='padding:8px; text-align:right;'>Lat.</th>
                </tr>
            """ + "".join([
                f"<tr style='border-bottom:1px solid #1f1f28; background:{'#0a0a0f' if i % 2 == 0 else '#141419'}'>"
                f"<td style='padding:8px; font-family:monospace; color:#8b8b9a;'>{c[0]}</td>"
                f"<td style='padding:8px; font-weight:600;'>{c[1]}</td>"
                f"<td style='padding:8px;'><span class='led-{c[4]}'></span> {c[2]}</td>"
                f"<td style='padding:8px; text-align:right; font-family:monospace; color:#8b8b9a;'>{c[3]}</td>"
                f"</tr>"
                for i, c in enumerate(comms_d)
            ]) + """</table>
            <div style='margin-top:12px; padding-top:10px; border-top:1px dashed #2a2a35; font-size:11px; color:#8b8b9a; display:flex; justify-content:space-between; align-items:center;'>
                <span>System Pipeline:</span>
                <span style='color:#00d4aa; background:#002200; padding:3px 8px; border-radius:3px; border:1px solid #005500; font-family:monospace; font-weight:bold;'>● WSS CONNECTED (99.9%)</span>
            </div>
            """, unsafe_allow_html=True)

elif menu == "⚙️ Plant Control":
    st.markdown("""
        <div style="background-color:#141419; padding:10px 20px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; border: 1px solid #1f1f28; margin-bottom:15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <div style="font-weight:bold; letter-spacing:1px; text-transform:uppercase; font-size:16px; color:#f0f0f5;">Remote SCADA — Plant Control</div>
            <div style="font-size:13px; color:#8b8b9a;">Setpoint · Ramp Rate · Frequency Droop · Control Mode</div>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.2, 1.2])
    
    with c1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">POWER PLANT CONTROL</div>', unsafe_allow_html=True)
            # Placeholder for satellite image
            st.markdown('<div style="background:#1f1f28; height:120px; display:flex; align-items:center; justify-content:center; color:#8b8b9a; font-size:12px; border-radius:4px;">Satellite View Placeholder</div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            if len(trend_df) >= 2:
                fig_p = px.line(trend_df, x="ts", y="P_AC_kW")
                fig_p.update_traces(line_color="#999999")
                fig_p.update_layout(**PLOT_LAYOUT, height=130, xaxis_visible=False, yaxis_visible=False)
                st.plotly_chart(fig_p, use_container_width=True, config={'displayModeBar': False})
        
        with st.container(border=True):
            st.markdown('<div class="panel-title">POI</div>', unsafe_allow_html=True)
            st.markdown("""
            <table style="width:100%; font-size:11px; border-collapse: collapse; color:#f0f0f5;">
                <tr><td style="padding:4px; border:1px solid #2a2a35; background:#1f1f28; text-align:left; color:#8b8b9a;">Active Power Rating (kW)</td><td style="padding:4px; border:1px solid #2a2a35; text-align:right; font-weight:bold; color:#f0f0f5;">500</td></tr>
                <tr><td style="padding:4px; border:1px solid #2a2a35; background:#1f1f28; text-align:left; color:#8b8b9a;">Reactive Power Rating (kVAr)</td><td style="padding:4px; border:1px solid #2a2a35; text-align:right; font-weight:bold; color:#f0f0f5;">200</td></tr>
                <tr><td style="padding:4px; border:1px solid #2a2a35; background:#141419; text-align:left; color:#8b8b9a;">Active Power (kW)</td><td style="padding:4px; border:1px solid #2a2a35; text-align:right; font-weight:bold; color:#8b8b9a; font-family:monospace;">""" + str(plant['P_AC_kW']) + """</td></tr>
                <tr><td style="padding:4px; border:1px solid #2a2a35; background:#141419; text-align:left; color:#8b8b9a;">Reactive Power (kVAr)</td><td style="padding:4px; border:1px solid #2a2a35; text-align:right; font-weight:bold; color:#8b8b9a; font-family:monospace;">-10.5</td></tr>
                <tr><td style="padding:4px; border:1px solid #2a2a35; background:#141419; text-align:left; color:#8b8b9a;">Power Factor</td><td style="padding:4px; border:1px solid #2a2a35; text-align:right; font-weight:bold; color:#8b8b9a; font-family:monospace;">0.99</td></tr>
                <tr><td style="padding:4px; border:1px solid #2a2a35; background:#141419; text-align:left; color:#8b8b9a;">Voltage (kV)</td><td style="padding:4px; border:1px solid #2a2a35; text-align:right; font-weight:bold; color:#8b8b9a; font-family:monospace;">114.04</td></tr>
                <tr><td style="padding:4px; border:1px solid #2a2a35; background:#141419; text-align:left; color:#8b8b9a;">Frequency (Hz)</td><td style="padding:4px; border:1px solid #2a2a35; text-align:right; font-weight:bold; color:#8b8b9a; font-family:monospace;">50.1</td></tr>
            </table>
            """, unsafe_allow_html=True)
            
    with c2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">CONTROL MODE</div>', unsafe_allow_html=True)
            st.markdown("""
            <table style="width:100%; text-align:center; font-size:11px; color:#f0f0f5; border-collapse: collapse;">
                <tr style="color:#8b8b9a; border-bottom:1px solid #2a2a35;"><th style="padding:4px; text-align:left; font-weight:600;">MODE</th><th style="padding:4px; font-weight:600;">Active</th><th style="padding:4px; font-weight:600;">Input</th><th style="padding:4px;"></th></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Active Power Ctrl</td><td style="color:#00d4aa; font-weight:bold;">No Ramp</td><td><select style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; padding:2px; font-size:9px; width:100%; border-radius:2px;"><option>No Ramp</option></select></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Reactive Power Ctrl</td><td style="color:#00d4aa; font-weight:bold;">PF</td><td><select style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; padding:2px; font-size:9px; width:100%; border-radius:2px;"><option>OFF</option></select></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
            </table>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown('<div class="panel-title">RAMP RATE CONTROL</div>', unsafe_allow_html=True)
            st.markdown("""
            <table style="width:100%; text-align:center; font-size:11px; color:#f0f0f5; border-collapse: collapse;">
                <tr style="color:#8b8b9a; border-bottom:1px solid #2a2a35;"><th style="padding:4px; text-align:left; font-weight:600;">RAMP RATE</th><th style="padding:4px; font-weight:600;">Active</th><th style="padding:4px; font-weight:600;">Input</th><th style="padding:4px;"></th></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Active Power (kW)</td><td style="color:#00d4aa; font-weight:bold;">5000</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:30px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Reactive Pwr (kVAr)</td><td style="color:#00d4aa; font-weight:bold;">0</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:30px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Interval (s)</td><td style="color:#00d4aa; font-weight:bold;">5</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:30px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
            </table>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown('<div class="panel-title">SETPOINT</div>', unsafe_allow_html=True)
            st.markdown("""
            <table style="width:100%; text-align:center; font-size:11px; color:#f0f0f5; border-collapse: collapse;">
                <tr style="color:#8b8b9a; border-bottom:1px solid #2a2a35;"><th style="padding:4px; text-align:left; font-weight:600;">SETPOINT</th><th style="padding:4px; font-weight:600;">Active</th><th style="padding:4px; font-weight:600;">Input</th><th style="padding:4px;"></th></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Active Pwr (kW)</td><td style="color:#00d4aa; font-weight:bold;">145000</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:40px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">React Pwr (kVAr)</td><td style="color:#00d4aa; font-weight:bold;">10000</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:40px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Power Factor</td><td style="color:#00d4aa; font-weight:bold;">1</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:40px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Voltage (kV)</td><td style="color:#00d4aa; font-weight:bold;">114.5</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:40px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
            </table>
            """, unsafe_allow_html=True)
            
    with c3:
        with st.container(border=True):
            st.markdown('<div class="panel-title">PLANT CONTROL</div>', unsafe_allow_html=True)
            cr1, cr2 = st.columns(2)
            cr1.markdown("<button style='width:100%; padding:10px; background:#141419; color:#f0f0f5; border:1px solid #2a2a35; border-radius:4px; font-weight:600; text-transform:uppercase;'><span class='led-red'></span> Start Plant</button>", unsafe_allow_html=True)
            cr2.markdown("<button style='width:100%; padding:10px; background:#141419; color:#f0f0f5; border:1px solid #2a2a35; border-radius:4px; font-weight:600; text-transform:uppercase;'><span class='led-red'></span> Stop Plant</button>", unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown('<div class="panel-title">ALARM SIGNALS</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style='font-size:12px; display:flex; justify-content:space-between; padding:10px; color:#8b8b9a; line-height:2; background:#0a0a0f; border-radius:4px;'>
                <div>
                    <span class='led-red'></span> POI Online<br>
                    <span class='led-red'></span> P Control Changed<br>
                    <span class='led-red'></span> Q Control Changed<br>
                    <span class='led-red'></span> Spare
                </div>
                <div>
                    <span class='led-red'></span> P Out Of Range<br>
                    <span class='led-red'></span> Q Out Of Range<br>
                    <span class='led-red'></span> Pf Out Of Range<br>
                    <span class='led-red'></span> V Out Of Range
                </div>
                <div>
                    <span class='led-red'></span> P Control ON<br>
                    <span class='led-red'></span> Q Control ON<br>
                    <span class='led-red'></span> PF Control ON<br>
                    <span class='led-red'></span> V Control ON
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown('<div class="panel-title">FREQ. DROOP PARAMETERS</div>', unsafe_allow_html=True)
            st.markdown("""
            <table style="width:100%; text-align:center; font-size:11px; color:#f0f0f5; border-collapse: collapse;">
                <tr style="color:#8b8b9a; border-bottom:1px solid #2a2a35;"><th style="padding:4px; text-align:left; font-weight:600;">PARAMETERS</th><th style="padding:4px; font-weight:600;">Active</th><th style="padding:4px; font-weight:600;">Input</th><th style="padding:4px;"></th></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Freq Droop 1 (%)</td><td style="color:#00d4aa; font-weight:bold;">0</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:30px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Freq Droop 2 (%)</td><td style="color:#00d4aa; font-weight:bold;">5</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:30px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">High Limit (Hz)</td><td style="color:#f0f0f5; font-weight:bold;">52</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:30px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
                <tr><td style="padding:4px; background:#1f1f28; border:1px solid #2a2a35; text-align:left; color:#8b8b9a;">Low Limit (Hz)</td><td style="color:#f0f0f5; font-weight:bold;">47</td><td><input type="text" value="0" style="background:#0a0a0f; color:#f0f0f5; border:1px solid #3b82f6; text-align:center; width:30px; font-size:10px; border-radius:2px;"></td><td><button style="background:#2a2a35; color:#f0f0f5; border:none; padding:2px 6px; border-radius:2px; cursor:pointer; font-size:9px; width:100%;">Set</button></td></tr>
            </table>
            """, unsafe_allow_html=True)


# =========================================================
# HOME PAGE
# =========================================================
elif menu == "🏠 Home":
    _now_ts = datetime.now()
    st.markdown(f"""
        <div style="background-color:#141419; padding:10px 20px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; border: 1px solid #1f1f28; margin-bottom:15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <div style="font-weight:bold; letter-spacing:1px; text-transform:uppercase; font-size:16px; color:#f0f0f5;">Remote SCADA — Plant Executive Summary</div>
            <div style="font-size:12px; color:#8b8b9a;">Last refresh: <span style="color:#f0f0f5; font-family:monospace;">{_now_ts.strftime('%H:%M:%S')}</span> &nbsp;|&nbsp; {_now_ts.strftime('%d %b %Y')}</div>
        </div>
    """, unsafe_allow_html=True)

    # ── Compute KPIs ─────────────────────────────────────────────
    energy_today = plant['Total_energy_kWh']
    rated_kw     = plant['rated_kw']
    p_ac         = plant['P_AC_kW']
    ghi          = plant['GHI']
    pr_ratio     = round((p_ac / max(1, ghi / 1000 * rated_kw)) * 100, 1) if ghi > 0 else 0
    cuf          = round((p_ac / max(1, rated_kw)) * 100, 1)
    co2_avoided  = round(energy_today * 0.82, 1)

    # Plant Uptime % — hours generating / daylight hours today
    _sunrise, _sunset = 6, 18
    _daylight_h = max(1, _sunset - _sunrise)
    _current_h  = _now_ts.hour
    _generating_h = max(0, min(_current_h, _sunset) - _sunrise)
    uptime_pct  = round(_generating_h / _daylight_h * 100, 1)

    # Load color
    _lc = "#00d4aa" if cuf >= 60 else ("#ffb800" if cuf >= 30 else "#ff4757")

    # ── KPI Strip ────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    def kpi_card(col, label, value, unit, color, icon=""):
        col.markdown(f"""
        <div style='background:#141419; border:1px solid #1f1f28; border-top:3px solid {color}; border-radius:6px; padding:14px 10px; text-align:center;'>
            <div style='font-size:18px; margin-bottom:4px;'>{icon}</div>
            <div style='font-size:10px; color:#8b8b9a; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;'>{label}</div>
            <div style='font-size:22px; font-weight:700; color:{color}; font-family:monospace; letter-spacing:-0.5px;'>{value}</div>
            <div style='font-size:10px; color:#8b8b9a; margin-top:4px;'>{unit}</div>
        </div>
        """, unsafe_allow_html=True)

    kpi_card(k1, "Today Energy",   f"{energy_today:.1f}", "kWh",    "#3b82f6",  "⚡")
    kpi_card(k2, "Plant Uptime",   f"{uptime_pct:.0f}",   "% today","#6366f1",  "⏱️")
    kpi_card(k3, "Live AC Power",  f"{p_ac:.1f}",         "kW",     _lc,        "🔋")
    kpi_card(k4, "Perf. Ratio",    f"{pr_ratio:.1f}",     "%",      "#00d4aa",  "📊")
    kpi_card(k5, "CUF",            f"{cuf:.1f}",          "%",      "#ffb800",  "☀️")
    kpi_card(k6, "CO₂ Avoided",    f"{co2_avoided:.1f}",  "kg",     "#22c55e",  "🌿")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Row 2: Hourly Generation + Inverter Fleet ─────────────────
    h1, h2 = st.columns([1.5, 1])

    with h1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">HOURLY GENERATION PROFILE — TODAY vs. TARGET</div>', unsafe_allow_html=True)
            current_hour = _now_ts.hour
            hours = list(range(24))
            gen_sim, target_sim = [], []
            for h in hours:
                if 6 <= h <= 18:
                    peak   = rated_kw * max(0, np.sin((h - 6) / 12 * np.pi))
                    target = round(peak * (5 / 3600), 3)
                    actual = round(peak * (0.85 + 0.12 * np.random.rand()) * (5 / 3600), 3) if h <= current_hour else 0
                    gen_sim.append(max(0, actual))
                    target_sim.append(target)
                else:
                    gen_sim.append(0)
                    target_sim.append(0)
            fig_h = go.Figure()
            fig_h.add_trace(go.Bar(x=hours, y=gen_sim, name="Actual", marker_color="#3b82f6", opacity=0.85))
            fig_h.add_trace(go.Scatter(x=hours, y=target_sim, name="Target", mode="lines",
                                       line=dict(color="#ffb800", width=1.5, dash="dot")))
            fig_h.update_layout(**PLOT_LAYOUT, height=230, xaxis_title="Hour", yaxis_title="kWh",
                                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                                            font=dict(size=10, color="#8b8b9a")))
            fig_h.update_xaxes(showgrid=False, tickvals=list(range(0, 24, 2)))
            fig_h.update_yaxes(showgrid=True, gridcolor="#1f1f28")
            st.plotly_chart(fig_h, use_container_width=True, config={'displayModeBar': False})

    with h2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">INVERTER FLEET HEALTH</div>', unsafe_allow_html=True)
            inv_df = df[df["inverter_id"].str.startswith("INV")].sort_values("ts").groupby("inverter_id").last().reset_index()
            if not inv_df.empty:
                for _, row in inv_df.iterrows():
                    status  = row.get("status", "Running")
                    color   = "#00d4aa" if status == "Running" else "#ff4757"
                    led_cls = "led-green" if status == "Running" else "led-red"
                    eff     = round(row['P_AC_kW'] / max(0.1, row['P_DC_kW']) * 100, 1) if row['P_DC_kW'] > 0 else 0
                    load_p  = round(row['P_AC_kW'] / max(0.1, row['rated_kw']) * 100, 1)
                    bar_c   = "#00d4aa" if load_p >= 60 else ("#ffb800" if load_p >= 30 else "#ff4757")
                    st.markdown(f"""
                    <div style='padding:7px 6px; border-bottom:1px solid #1f1f28; font-size:12px;'>
                        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>
                            <span style='font-weight:700; color:#f0f0f5; width:60px;'>{row['inverter_id']}</span>
                            <span><span class='{led_cls}'></span><span style='color:{color}; font-size:11px;'>{status}</span></span>
                            <span style='color:#f0f0f5; font-family:monospace; font-weight:700;'>{row['P_AC_kW']:.1f} kW</span>
                            <span style='background:{bar_c}22; color:{bar_c}; border:1px solid {bar_c}55; border-radius:3px; padding:1px 5px; font-size:10px; font-weight:700;'>eff {eff:.0f}%</span>
                        </div>
                        <div style='background:#0a0a0f; border-radius:2px; height:4px;'>
                            <div style='background:{bar_c}; height:4px; width:{min(100,load_p):.0f}%; border-radius:2px;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Awaiting inverter data...")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Row 3: Live AC Sparkline + PR Trend ──────────────────────
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">LIVE AC POWER — 30 MIN ROLLING</div>', unsafe_allow_html=True)
            if len(trend_df) >= 2:
                from plotly.subplots import make_subplots as _msp
                _fig_sp = _msp(specs=[[{"secondary_y": True}]])
                _fig_sp.add_trace(go.Scatter(
                    x=trend_df["ts"], y=trend_df["P_AC_kW"], name="AC Power",
                    line=dict(color=_lc, width=2), fill="tozeroy",
                    fillcolor=f"rgba({'0,212,170' if _lc=='#00d4aa' else '255,183,0' if _lc=='#ffb800' else '255,71,87'},0.08)"
                ), secondary_y=False)
                _fig_sp.add_trace(go.Scatter(
                    x=trend_df["ts"], y=trend_df["GHI"], name="GHI",
                    line=dict(color="#ffb800", width=1, dash="dot")
                ), secondary_y=True)
                _fig_sp.update_layout(**PLOT_LAYOUT, height=195,
                    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=9, color="#8b8b9a")))
                _fig_sp.update_xaxes(showgrid=False)
                _fig_sp.update_yaxes(showgrid=True, gridcolor="#1f1f28", secondary_y=False)
                _fig_sp.update_yaxes(showgrid=False, secondary_y=True)
                st.plotly_chart(_fig_sp, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Collecting data...")

    with r3c2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">PERFORMANCE RATIO TREND</div>', unsafe_allow_html=True)
            if len(trend_df) >= 2 and trend_df["GHI"].max() > 0:
                _pr_series = np.where(
                    trend_df["GHI"] > 10,
                    (trend_df["P_AC_kW"] / (trend_df["GHI"] / 1000 * rated_kw) * 100).clip(0, 120),
                    np.nan
                )
                _fig_pr = go.Figure()
                _fig_pr.add_trace(go.Scatter(
                    x=trend_df["ts"], y=_pr_series, name="PR %",
                    line=dict(color="#00d4aa", width=2), fill="tozeroy",
                    fillcolor="rgba(0,212,170,0.07)"
                ))
                _fig_pr.add_hline(y=80, line_dash="dot", line_color="#ffb800",
                                  annotation_text="Target 80%", annotation_font_color="#ffb800",
                                  annotation_font_size=10)
                _fig_pr.update_layout(**PLOT_LAYOUT, height=195,
                    yaxis=dict(range=[0, 110]))
                _fig_pr.update_xaxes(showgrid=False)
                _fig_pr.update_yaxes(showgrid=True, gridcolor="#1f1f28", title_text="PR %")
                st.plotly_chart(_fig_pr, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Collecting data...")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Status Bar (replaces redundant summary strip) ────────────
    try:
        _alarm_cnt = pd.read_sql("SELECT COUNT(*) as cnt FROM alarms", con=get_engine()).iloc[0]['cnt']
    except Exception:
        _alarm_cnt = 0
    _inv_run   = df[df["inverter_id"].str.startswith("INV")].groupby("inverter_id").last()
    _n_run     = int((_inv_run["status"] == "Running").sum()) if not _inv_run.empty else 0
    _batt_soc  = plant.get("battery_soc", 50)
    _batt_mode = "Charging" if plant.get("battery_power_kw", 0) > 0 else ("Discharging" if plant.get("battery_power_kw", 0) < 0 else "Idle")
    _alarm_col = "#ff4757" if _alarm_cnt > 5 else ("#ffb800" if _alarm_cnt > 0 else "#00d4aa")

    st.markdown(f"""
    <div style='background:#141419; border:1px solid #1f1f28; border-radius:6px; padding:10px 20px;
                display:flex; justify-content:space-around; align-items:center; font-size:12px;'>
        <span><span class='led-green'></span> <span style='color:#8b8b9a;'>Inverters</span> <span style='color:#00d4aa; font-weight:700; font-family:monospace;'>{_n_run}/5 Online</span></span>
        <span style='color:#2a2a35;'>|</span>
        <span><span style='color:#8b8b9a;'>Alarms</span> <span style='color:{_alarm_col}; font-weight:700; font-family:monospace;'>{_alarm_cnt} Active</span></span>
        <span style='color:#2a2a35;'>|</span>
        <span><span style='color:#8b8b9a;'>Battery</span> <span style='color:#3b82f6; font-weight:700; font-family:monospace;'>{_batt_soc:.1f}% — {_batt_mode}</span></span>
        <span style='color:#2a2a35;'>|</span>
        <span><span style='color:#8b8b9a;'>Mode</span> <span style='color:#00d4aa; font-weight:700;'>AUTO</span></span>
        <span style='color:#2a2a35;'>|</span>
        <span><span class='led-green'></span> <span style='color:#8b8b9a;'>Grid</span> <span style='color:#00d4aa; font-weight:700;'>CONNECTED</span></span>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# OVERVIEW PAGE
# =========================================================
elif menu == "🗺️ Overview":
    st.markdown("""
        <div style="background-color:#141419; padding:10px 20px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; border: 1px solid #1f1f28; margin-bottom:15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <div style="font-weight:bold; letter-spacing:1px; text-transform:uppercase; font-size:16px; color:#f0f0f5;">Remote SCADA — Plant Overview</div>
            <div style="font-size:13px; color:#8b8b9a;">Inverter Block Status &amp; String Layout</div>
        </div>
    """, unsafe_allow_html=True)

    # Total plant live bar
    p_ac   = plant['P_AC_kW']
    rated  = plant['rated_kw']
    pct    = min(100, round(p_ac / max(1, rated) * 100, 1))
    bar_color = "#00d4aa" if pct >= 70 else ("#ffb800" if pct >= 30 else "#ff4757")

    with st.container(border=True):
        st.markdown('<div class="panel-title">PLANT TOTAL OUTPUT</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style='padding:8px 0;'>
            <div style='display:flex; justify-content:space-between; margin-bottom:6px; font-size:13px;'>
                <span style='color:#8b8b9a;'>Total AC Output</span>
                <span style='color:#f0f0f5; font-weight:700; font-family:monospace;'>{p_ac:.1f} kW / {rated:.0f} kW rated</span>
                <span style='color:{bar_color}; font-weight:700;'>{pct}%</span>
            </div>
            <div style='background:#1f1f28; border-radius:4px; height:16px; width:100%;'>
                <div style='background:{bar_color}; height:16px; width:{pct}%; border-radius:4px; box-shadow:0 0 8px {bar_color}55; transition:width 0.5s;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Inverter block cards
    st.markdown('<div class="panel-title" style="font-size:12px; color:#8b8b9a; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">INVERTER STATIONS</div>', unsafe_allow_html=True)
    inv_latest = df[df["inverter_id"].str.startswith("INV")].sort_values("ts").groupby("inverter_id").last().reset_index()

    inv_cols = st.columns(5)
    for idx, col in enumerate(inv_cols):
        inv_id = f"INV-{idx+1:02d}"
        if not inv_latest.empty and inv_id in inv_latest["inverter_id"].values:
            row = inv_latest[inv_latest["inverter_id"] == inv_id].iloc[0]
            status  = row.get("status", "Running")
            ac_kw   = row['P_AC_kW']
            dc_kw   = row['P_DC_kW']
            eff     = round(ac_kw / max(0.1, dc_kw) * 100, 1) if dc_kw > 0 else 0
            rated_inv = row['rated_kw']
            load_pct  = round(ac_kw / max(0.1, rated_inv) * 100, 1)
            is_fault  = status == "Fault"
            border_c  = "#ff4757" if is_fault else ("#ffb800" if load_pct < 30 else "#00d4aa")
            led       = "led-red" if is_fault else "led-green"
            status_c  = "#ff4757" if is_fault else "#00d4aa"
        else:
            status = "N/A"; ac_kw = dc_kw = eff = load_pct = 0; rated_inv = 100
            border_c = "#2a2a35"; led = "led-amber"; status_c = "#ffb800"; is_fault = False

        with col:
            st.markdown(f"""
            <div style='background:#141419; border:1px solid {border_c}; border-radius:8px; padding:16px 12px; text-align:center; box-shadow: 0 0 12px {border_c}22;'>
                <div style='font-size:12px; color:#8b8b9a; font-weight:600; margin-bottom:8px;'>{inv_id}</div>
                <div style='margin-bottom:8px;'><span class='{led}'></span><span style='color:{status_c}; font-size:12px; font-weight:600;'>{status}</span></div>
                <div style='font-size:22px; font-weight:700; color:#f0f0f5; font-family:monospace; margin-bottom:4px;'>{ac_kw:.1f}</div>
                <div style='font-size:11px; color:#8b8b9a; margin-bottom:10px;'>kW AC Output</div>
                <div style='background:#1f1f28; border-radius:3px; height:6px; width:100%; margin-bottom:8px;'>
                    <div style='background:{border_c}; height:6px; width:{min(100,load_pct)}%; border-radius:3px;'></div>
                </div>
                <div style='font-size:11px; color:#8b8b9a; display:flex; justify-content:space-between;'>
                    <span>DC: {dc_kw:.1f} kW</span>
                    <span>Eff: {eff:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # SCB / Panel String Status
    with st.container(border=True):
        st.markdown('<div class="panel-title">STRING / SCB STATUS (10 STRINGS)</div>', unsafe_allow_html=True)
        panel_data = df[df["inverter_id"].str.startswith("INV")].sort_values('ts').groupby("inverter_id").last().reset_index()
        scb_cols = st.columns(10)
        for i, scb_col in enumerate(scb_cols):
            inv_idx = i // 2
            inv_id  = f"INV-{inv_idx+1:02d}"
            if not panel_data.empty and inv_id in panel_data["inverter_id"].values:
                inv_row    = panel_data[panel_data["inverter_id"] == inv_id].iloc[0]
                pv_pwr     = inv_row["P_DC_kW"] / 2  # 2 panels per inverter
                rated_pv   = inv_row["rated_kw"] / 2
                pv_pct     = round(pv_pwr / max(0.1, rated_pv) * 100, 1)
                scb_color  = "#00d4aa" if pv_pct >= 70 else ("#ffb800" if pv_pct >= 20 else "#ff4757")
                scb_status = "Normal" if pv_pct >= 70 else ("Derated" if pv_pct >= 20 else "Fault")
            else:
                pv_pwr = 0; pv_pct = 0; scb_color = "#2a2a35"; scb_status = "N/A"

            scb_col.markdown(f"""
            <div style='background:#141419; border:1px solid {scb_color}; border-radius:6px; padding:8px 4px; text-align:center; margin-bottom:4px;'>
                <div style='font-size:10px; color:#8b8b9a; font-weight:600;'>PV-{i+1:02d}</div>
                <div style='font-size:14px; font-weight:700; color:{scb_color}; font-family:monospace;'>{pv_pwr:.1f}</div>
                <div style='font-size:9px; color:#8b8b9a;'>kW</div>
                <div style='font-size:9px; color:{scb_color}; margin-top:3px;'>{scb_status}</div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# SUBSTATION PAGE
# =========================================================
elif menu == "🏢 Substation":
    st.markdown("""
        <div style="background-color:#141419; padding:10px 20px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; border: 1px solid #1f1f28; margin-bottom:15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <div style="font-weight:bold; letter-spacing:1px; text-transform:uppercase; font-size:16px; color:#f0f0f5;">Remote SCADA — Substation &amp; HV/MV</div>
            <div style="font-size:13px; color:#8b8b9a;">Transformer · RMU · Protection Relays</div>
        </div>
    """, unsafe_allow_html=True)

    tx_loss   = plant.get("transformer_loss_kw", 5.0)
    tx_eff    = plant.get("transformer_eff", 0.97)
    load_pct  = round(plant['P_AC_kW'] / 600 * 100, 1)  # 600 KVA rated
    tx_load_c = "#ff4757" if load_pct > 95 else ("#ffb800" if load_pct > 80 else "#00d4aa")

    sub1, sub2 = st.columns([1.2, 1])

    with sub1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">MAIN STEP-UP TRANSFORMER — TX-01 (600 KVA, 33kV/110kV)</div>', unsafe_allow_html=True)
            t1, t2, t3 = st.columns(3)
            def tx_metric(col, label, val, unit, color="#f0f0f5"):
                col.markdown(f"""
                <div style='text-align:center; padding:12px 6px; border:1px solid #1f1f28; border-radius:6px; background:#0a0a0f; margin:4px;'>
                    <div style='font-size:10px; color:#8b8b9a; text-transform:uppercase; margin-bottom:6px;'>{label}</div>
                    <div style='font-size:22px; font-weight:700; color:{color}; font-family:monospace;'>{val}</div>
                    <div style='font-size:10px; color:#8b8b9a; margin-top:2px;'>{unit}</div>
                </div>""", unsafe_allow_html=True)
            tx_metric(t1, "Load Factor",  f"{load_pct:.1f}", "%", tx_load_c)
            tx_metric(t2, "Efficiency",   f"{tx_eff*100:.2f}", "%", "#00d4aa")
            tx_metric(t3, "Core Losses",  f"{tx_loss:.1f}", "kW", "#ffb800")

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background:#0a0a0f; border-radius:6px; padding:10px 14px; border:1px solid #1f1f28;'>
                <div style='font-size:11px; color:#8b8b9a; margin-bottom:6px; font-weight:600;'>TRANSFORMER LOAD</div>
                <div style='background:#1f1f28; border-radius:4px; height:14px; width:100%;'>
                    <div style='background:{tx_load_c}; height:14px; width:{min(100,load_pct)}%; border-radius:4px; box-shadow:0 0 8px {tx_load_c}55;'></div>
                </div>
                <div style='display:flex; justify-content:space-between; font-size:10px; color:#8b8b9a; margin-top:4px;'>
                    <span>0%</span><span style='color:{tx_load_c}; font-weight:700;'>{load_pct}%</span><span>100%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="panel-title">GRID MEASUREMENTS — HV/MV</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <table style="width:100%; font-size:13px; border-collapse:collapse; color:#f0f0f5;">
                <tr style="color:#8b8b9a; border-bottom:2px solid #2a2a35;">
                    <th style="padding:8px; text-align:left; font-weight:600;">Parameter</th>
                    <th style="padding:8px; text-align:center; font-weight:600;">HV Side (110kV)</th>
                    <th style="padding:8px; text-align:center; font-weight:600;">MV Side (33kV)</th>
                </tr>
                <tr style="border-bottom:1px solid #1f1f28; background:#0a0a0f;">
                    <td style="padding:8px; color:#8b8b9a;">Voltage</td>
                    <td style="padding:8px; text-align:center; font-family:monospace; font-weight:700;">112.7 kV</td>
                    <td style="padding:8px; text-align:center; font-family:monospace; font-weight:700;">33.4 kV</td>
                </tr>
                <tr style="border-bottom:1px solid #1f1f28;">
                    <td style="padding:8px; color:#8b8b9a;">Current</td>
                    <td style="padding:8px; text-align:center; font-family:monospace; font-weight:700;">{plant['P_AC_kW']/112.7:.1f} A</td>
                    <td style="padding:8px; text-align:center; font-family:monospace; font-weight:700;">{plant['P_AC_kW']/33.4:.1f} A</td>
                </tr>
                <tr style="border-bottom:1px solid #1f1f28; background:#0a0a0f;">
                    <td style="padding:8px; color:#8b8b9a;">Active Power</td>
                    <td style="padding:8px; text-align:center; font-family:monospace; font-weight:700;">{plant['P_AC_kW']:.1f} kW</td>
                    <td style="padding:8px; text-align:center; font-family:monospace; font-weight:700;">{plant['P_AC_kW'] + tx_loss:.1f} kW</td>
                </tr>
                <tr style="border-bottom:1px solid #1f1f28;">
                    <td style="padding:8px; color:#8b8b9a;">Power Factor</td>
                    <td style="padding:8px; text-align:center; font-family:monospace; font-weight:700;">0.99</td>
                    <td style="padding:8px; text-align:center; font-family:monospace; font-weight:700;">0.98</td>
                </tr>
                <tr style="background:#0a0a0f;">
                    <td style="padding:8px; color:#8b8b9a;">Frequency</td>
                    <td style="padding:8px; text-align:center; font-family:monospace; font-weight:700;">50.07 Hz</td>
                    <td style="padding:8px; text-align:center; font-family:monospace; font-weight:700;">50.07 Hz</td>
                </tr>
            </table>
            """, unsafe_allow_html=True)

    with sub2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">RMU / CIRCUIT BREAKER STATUS</div>', unsafe_allow_html=True)
            breakers = [
                ("CB-1 (Grid Incomer)", "Closed", "green"),
                ("CB-2 (TX Primary)",   "Closed", "green"),
                ("CB-3 (MV Bus)",       "Closed", "green"),
                ("CB-4 (Feeder 1)",     "Open",   "amber"),
                ("EB-5 (Earthing)",     "Open",   "amber"),
            ]
            for name, state, color in breakers:
                led_c = f"led-{color}"
                sc    = "#00d4aa" if state == "Closed" else "#ffb800"
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; align-items:center; padding:10px 8px; border-bottom:1px solid #1f1f28; font-size:13px;'>
                    <span style='color:#8b8b9a;'>{name}</span>
                    <span><span class='{led_c}'></span> <b style='color:{sc};'>{state}</b></span>
                </div>
                """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="panel-title">PROTECTION RELAYS</div>', unsafe_allow_html=True)
            relays = [
                ("50/51 — Overcurrent (OCEF)",   "Normal", "green"),
                ("87T  — Differential TX",        "Normal", "green"),
                ("27/59 — Under/Over Voltage",    "Normal", "green"),
                ("81  — Under/Over Frequency",    "Normal", "green"),
                ("67  — Directional Overcurrent", "Normal", "green"),
                ("64  — Earth Fault REF",         "Normal", "green"),
            ]
            for name, state, color in relays:
                led_c = f"led-{color}"
                sc    = "#00d4aa"
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; align-items:center; padding:8px 8px; border-bottom:1px solid #1f1f28; font-size:12px;'>
                    <span style='color:#8b8b9a;'>{name}</span>
                    <span><span class='{led_c}'></span> <b style='color:{sc};'>{state}</b></span>
                </div>
                """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="panel-title">SINGLE LINE DIAGRAM</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background:#050505; padding:16px; border-radius:5px; text-align:center; font-size:12px; color:#aaa; font-family:monospace;'>
                <div style='color:#3b82f6; font-weight:bold; margin-bottom:8px;'>⚡ 110kV GRID</div>
                <div style='color:#444;'>│</div>
                <div style='border:1px solid #3b82f6; display:inline-block; padding:4px 16px; border-radius:3px; color:#8b8b9a; margin:4px 0;'>CB-1 ■ CLOSED</div>
                <div style='color:#444;'>│</div>
                <div style='border:1px solid #ffb800; display:inline-block; padding:4px 16px; border-radius:3px; color:#ffb800; margin:4px 0;'>TX-01  110kV/33kV  600KVA</div>
                <div style='color:#444;'>│</div>
                <div style='border:1px solid #3b82f6; display:inline-block; padding:4px 16px; border-radius:3px; color:#8b8b9a; margin:4px 0;'>RMU  CB-2 CB-3 ■ CLOSED</div>
                <div style='color:#444;'>─────────────────</div>
                <div style='display:flex; justify-content:center; gap:16px; margin-top:4px;'>
                    <div style='border:1px solid #00d4aa; padding:4px 8px; border-radius:3px; color:#00d4aa;'>INV-01<br/>{plant['P_AC_kW']/5:.0f}kW</div>
                    <div style='border:1px solid #00d4aa; padding:4px 8px; border-radius:3px; color:#00d4aa;'>INV-02<br/>{plant['P_AC_kW']/5:.0f}kW</div>
                    <div style='border:1px solid #00d4aa; padding:4px 8px; border-radius:3px; color:#00d4aa;'>INV-03<br/>{plant['P_AC_kW']/5:.0f}kW</div>
                    <div style='border:1px solid #00d4aa; padding:4px 8px; border-radius:3px; color:#00d4aa;'>INV-04<br/>{plant['P_AC_kW']/5:.0f}kW</div>
                    <div style='border:1px solid #00d4aa; padding:4px 8px; border-radius:3px; color:#00d4aa;'>INV-05<br/>{plant['P_AC_kW']/5:.0f}kW</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# ALARM PAGE
# =========================================================
elif menu == "🔔 Alarm":
    st.markdown("""
        <div style="background-color:#141419; padding:10px 20px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; border: 1px solid #1f1f28; margin-bottom:15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <div style="font-weight:bold; letter-spacing:1px; text-transform:uppercase; font-size:16px; color:#f0f0f5;">Remote SCADA — Alarm Management</div>
            <div style="font-size:13px; color:#8b8b9a;">Live Fault &amp; Event Log</div>
        </div>
    """, unsafe_allow_html=True)

    @st.cache_data(ttl=5)
    def load_alarms():
        try:
            df_a = pd.read_sql("SELECT * FROM alarms ORDER BY ts DESC LIMIT 500", con=get_engine())
            if df_a.empty: return pd.DataFrame(columns=["ts","source","severity","message"])
            df_a["ts"] = pd.to_datetime(df_a["ts"], errors="coerce")
            return df_a.dropna(subset=["ts"])
        except Exception:
            return pd.DataFrame(columns=["ts","source","severity","message"])

    alarms_df = load_alarms()

    # Summary counts
    sev_map = {"Critical": 0, "High": 0, "Warning": 0, "Info": 0}
    if not alarms_df.empty:
        for sev in sev_map:
            sev_map[sev] = int((alarms_df["severity"] == sev).sum())

    a1, a2, a3, a4 = st.columns(4)
    def alarm_badge(col, label, count, color):
        col.markdown(f"""
        <div style='background:#141419; border:1px solid {color}; border-radius:6px; padding:14px; text-align:center; box-shadow:0 0 8px {color}33;'>
            <div style='font-size:11px; color:#8b8b9a; text-transform:uppercase; margin-bottom:6px;'>{label}</div>
            <div style='font-size:32px; font-weight:700; color:{color}; font-family:monospace;'>{count}</div>
        </div>""", unsafe_allow_html=True)

    alarm_badge(a1, "Critical", sev_map["Critical"], "#ff4757")
    alarm_badge(a2, "High",     sev_map["High"],     "#ffb800")
    alarm_badge(a3, "Warning",  sev_map["Warning"],  "#3b82f6")
    alarm_badge(a4, "Info",     sev_map["Info"],     "#8b8b9a")

    st.markdown("<br>", unsafe_allow_html=True)

    al1, al2 = st.columns([3, 1])
    with al1:
        sev_filter = st.selectbox("Filter by Severity", ["All", "Critical", "High", "Warning", "Info"], label_visibility="collapsed")
    with al2:
        st.markdown(f"<div style='text-align:right; color:#8b8b9a; font-size:12px; padding-top:8px;'>Total: {len(alarms_df)} events</div>", unsafe_allow_html=True)

    filtered = alarms_df if sev_filter == "All" else alarms_df[alarms_df["severity"] == sev_filter]

    with st.container(border=True):
        st.markdown('<div class="panel-title">ACTIVE ALARM LOG</div>', unsafe_allow_html=True)

        if filtered.empty:
            st.markdown("""
            <div style='text-align:center; padding:40px; color:#00d4aa;'>
                <div style='font-size:32px; margin-bottom:10px;'>✅</div>
                <div style='font-size:16px; font-weight:600;'>No Active Alarms</div>
                <div style='font-size:13px; color:#8b8b9a; margin-top:6px;'>All systems operating normally</div>
            </div>""", unsafe_allow_html=True)
        else:
            sev_colors = {"Critical": "#ff4757", "High": "#ffb800", "Warning": "#3b82f6", "Info": "#8b8b9a"}
            st.markdown("""
            <table style="width:100%; font-size:12px; border-collapse:collapse; color:#f0f0f5;">
                <tr style="color:#8b8b9a; border-bottom:2px solid #2a2a35;">
                    <th style="padding:8px; text-align:left; font-weight:600; width:160px;">Timestamp</th>
                    <th style="padding:8px; text-align:left; font-weight:600; width:120px;">Source</th>
                    <th style="padding:8px; text-align:left; font-weight:600; width:90px;">Severity</th>
                    <th style="padding:8px; text-align:left; font-weight:600;">Message</th>
                </tr>
            """ + "".join([
                f"""<tr style="border-bottom:1px solid #1f1f28; background:{'#0a0a0f' if i%2==0 else '#141419'};">
                    <td style="padding:8px; font-family:monospace; color:#8b8b9a;">{str(row['ts'])[:19]}</td>
                    <td style="padding:8px; font-weight:600; color:#f0f0f5;">{row['source']}</td>
                    <td style="padding:8px;"><span style="color:{sev_colors.get(row['severity'],'#8b8b9a')}; font-weight:700;">{row['severity']}</span></td>
                    <td style="padding:8px; color:#ccc;">{row['message']}</td>
                </tr>"""
                for i, (_, row) in enumerate(filtered.head(50).iterrows())
            ]) + "</table>", unsafe_allow_html=True)

    # Alarm frequency chart
    if not alarms_df.empty:
        with st.container(border=True):
            st.markdown('<div class="panel-title">ALARM FREQUENCY (LAST 24H)</div>', unsafe_allow_html=True)
            alarms_df["hour"] = alarms_df["ts"].dt.floor("h")
            alarm_hist = alarms_df.groupby("hour").size().reset_index(name="count")
            fig_al = px.bar(alarm_hist, x="hour", y="count", color_discrete_sequence=["#ff4757"])
            fig_al.update_layout(**PLOT_LAYOUT, height=160, xaxis_title="", yaxis_title="Events")
            fig_al.update_xaxes(showgrid=False)
            fig_al.update_yaxes(showgrid=True, gridcolor="#1f1f28")
            st.plotly_chart(fig_al, use_container_width=True, config={'displayModeBar': False})


# =========================================================
# TREND PAGE
# =========================================================
elif menu == "📈 Trend":
    st.markdown("""
        <div style="background-color:#141419; padding:10px 20px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; border: 1px solid #1f1f28; margin-bottom:15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <div style="font-weight:bold; letter-spacing:1px; text-transform:uppercase; font-size:16px; color:#f0f0f5;">Remote SCADA — Trend Analysis</div>
            <div style="font-size:13px; color:#8b8b9a;">Historical Time-Series Explorer</div>
        </div>
    """, unsafe_allow_html=True)

    PARAM_MAP = {
        "AC Power (kW)":           ("P_AC_kW",           "#00d4aa"),
        "DC Power (kW)":           ("P_DC_kW",           "#3b82f6"),
        "Irradiance GHI (W/m²)":   ("GHI",               "#ffb800"),
        "Performance Ratio (%)":   ("_pr_computed",      "#22c55e"),
        "Ambient Temp (°C)":       ("AmbientTemp_C",     "#ff4757"),
        "Battery SOC (%)":         ("battery_soc",       "#a78bfa"),
        "Battery Voltage (V)":     ("battery_voltage",   "#38bdf8"),
        "Battery Power (kW)":      ("battery_power_kw",  "#fb923c"),
        "Transformer Eff (%)":     ("transformer_eff",   "#34d399"),
    }

    tc1, tc2, tc3 = st.columns([2, 1, 1])
    with tc1:
        selected_params = st.multiselect(
            "Parameters",
            list(PARAM_MAP.keys()),
            default=["AC Power (kW)", "Irradiance GHI (W/m²)"],
            label_visibility="visible"
        )
    with tc2:
        inv_choice = st.selectbox("Inverter", ["All (Plant)"] + [f"INV-{i:02d}" for i in range(1,6)], label_visibility="visible")
    with tc3:
        time_range = st.selectbox("Time Window", ["Last 5 min", "Last 15 min", "Last 30 min", "Last 1 hour"], label_visibility="visible")

    time_map = {"Last 5 min": 60, "Last 15 min": 180, "Last 30 min": 360, "Last 1 hour": 720}
    n_rows = time_map.get(time_range, 180)

    @st.cache_data(ttl=5)
    def load_trend_data(n, inv_id):
        query = f"SELECT * FROM plant_live WHERE inverter_id = '{inv_id}' ORDER BY ts DESC LIMIT {n}"
        try:
            d = pd.read_sql(query, con=get_engine())
            if d.empty: return None
            d["ts"] = pd.to_datetime(d["ts"], errors="coerce")
            return d.sort_values("ts").dropna(subset=["ts"])
        except Exception:
            return None

    inv_id_query = "PLANT_SUMMARY" if inv_choice == "All (Plant)" else inv_choice
    trend_data = load_trend_data(n_rows, inv_id_query)

    if not selected_params:
        st.info("Select at least one parameter above.")
    elif trend_data is None or trend_data.empty:
        st.warning("No trend data available yet. Wait a few seconds...")
    else:
        # Compute PR column on-the-fly for trend
        if "_pr_computed" not in trend_data.columns:
            _rated_kw_t = plant['rated_kw']
            trend_data = trend_data.copy()
            trend_data["_pr_computed"] = np.where(
                trend_data["GHI"] > 10,
                (trend_data["P_AC_kW"] / (_rated_kw_t * trend_data["GHI"] / 1000) * 100).clip(0, 120),
                np.nan
            )

        from plotly.subplots import make_subplots
        fig_t = make_subplots(specs=[[{"secondary_y": True}]])

        _sec_cols = {"_pr_computed", "AmbientTemp_C", "battery_soc", "battery_voltage", "transformer_eff"}
        primary_params   = [p for p in selected_params if PARAM_MAP[p][0] not in _sec_cols]
        secondary_params = [p for p in selected_params if PARAM_MAP[p][0] in _sec_cols]

        for param in primary_params:
            col, color = PARAM_MAP[param]
            if col in trend_data.columns:
                fig_t.add_trace(go.Scatter(x=trend_data["ts"], y=trend_data[col], name=param,
                                           line=dict(color=color, width=1.5), mode="lines"), secondary_y=False)
        for param in secondary_params:
            col, color = PARAM_MAP[param]
            if col in trend_data.columns:
                mult = 100 if col == "transformer_eff" else 1
                fig_t.add_trace(go.Scatter(x=trend_data["ts"], y=trend_data[col]*mult, name=param,
                                           line=dict(color=color, width=1.5, dash="dot"), mode="lines"), secondary_y=True)

        fig_t.update_layout(**PLOT_LAYOUT, height=380, legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11, color="#8b8b9a")
        ))
        fig_t.update_xaxes(showgrid=False)
        fig_t.update_yaxes(showgrid=True, gridcolor="#1f1f28", secondary_y=False)
        fig_t.update_yaxes(showgrid=False, secondary_y=True)

        with st.container(border=True):
            st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': True})

        with st.expander("📋 Raw Data Table"):
            cols_to_show = ["ts"] + [PARAM_MAP[p][0] for p in selected_params if PARAM_MAP[p][0] in trend_data.columns]
            st.dataframe(
                trend_data[cols_to_show].tail(50).sort_values("ts", ascending=False).reset_index(drop=True),
                use_container_width=True, height=220
            )


# =========================================================
# UTILITIES PAGE
# =========================================================
elif menu == "🔌 Utilities":
    st.markdown("""
        <div style="background-color:#141419; padding:10px 20px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; border: 1px solid #1f1f28; margin-bottom:15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <div style="font-weight:bold; letter-spacing:1px; text-transform:uppercase; font-size:16px; color:#f0f0f5;">Remote SCADA — Utilities</div>
            <div style="font-size:13px; color:#8b8b9a;">Battery ESS · Weather Station · System Diagnostics</div>
        </div>
    """, unsafe_allow_html=True)

    batt_soc   = plant.get("battery_soc", 50.0)
    batt_volt  = plant.get("battery_voltage", 600.0)
    batt_temp  = plant.get("battery_temp_c", 25.0)
    batt_pwr   = plant.get("battery_power_kw", 0.0)
    batt_mode  = "Charging" if batt_pwr > 0 else ("Discharging" if batt_pwr < 0 else "Idle")
    batt_color = "#3b82f6" if batt_pwr > 0 else ("#ff4757" if batt_pwr < 0 else "#8b8b9a")

    u1, u2 = st.columns([1, 1])

    with u1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">BATTERY ENERGY STORAGE SYSTEM (ESS)</div>', unsafe_allow_html=True)
            b_donut, b_info = st.columns([1, 1])
            with b_donut:
                soc_color = "#00d4aa" if batt_soc > 50 else ("#ffb800" if batt_soc > 20 else "#ff4757")
                fig_soc = go.Figure(go.Pie(
                    values=[batt_soc, 100 - batt_soc],
                    hole=0.72,
                    textinfo="none",
                    marker=dict(colors=[soc_color, "#1f1f28"])
                ))
                fig_soc.update_layout(**PLOT_LAYOUT, showlegend=False, height=200,
                    annotations=[dict(text=f"<b>{batt_soc:.1f}%</b><br>SOC", font_size=18, font_color="#f0f0f5", showarrow=False)]
                )
                st.plotly_chart(fig_soc, use_container_width=True, config={'displayModeBar': False})

            with b_info:
                st.markdown(f"""
                <div style='font-size:13px; line-height:2.2;'>
                    <div style='display:flex; justify-content:space-between;'>
                        <span style='color:#8b8b9a;'>Voltage</span>
                        <span style='color:#f0f0f5; font-weight:700; font-family:monospace;'>{batt_volt:.1f} V</span>
                    </div>
                    <div style='display:flex; justify-content:space-between;'>
                        <span style='color:#8b8b9a;'>Temperature</span>
                        <span style='color:{"#ff4757" if batt_temp > 45 else "#f0f0f5"}; font-weight:700; font-family:monospace;'>{batt_temp:.1f} °C</span>
                    </div>
                    <div style='display:flex; justify-content:space-between;'>
                        <span style='color:#8b8b9a;'>Power</span>
                        <span style='color:{batt_color}; font-weight:700; font-family:monospace;'>{abs(batt_pwr):.1f} kW</span>
                    </div>
                    <div style='display:flex; justify-content:space-between;'>
                        <span style='color:#8b8b9a;'>Mode</span>
                        <span style='color:{batt_color}; font-weight:700;'>{batt_mode}</span>
                    </div>
                    <div style='display:flex; justify-content:space-between;'>
                        <span style='color:#8b8b9a;'>Capacity</span>
                        <span style='color:#f0f0f5; font-weight:700; font-family:monospace;'>200 kWh</span>
                    </div>
                    <div style='display:flex; justify-content:space-between;'>
                        <span style='color:#8b8b9a;'>Max C-Rate</span>
                        <span style='color:#f0f0f5; font-weight:700; font-family:monospace;'>0.5C / 100 kW</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Battery Cycle Statistics
        with st.container(border=True):
            st.markdown('<div class="panel-title">BATTERY CYCLE STATISTICS</div>', unsafe_allow_html=True)
            try:
                _batt_hist_cyc = pd.read_sql(
                    "SELECT battery_power_kw FROM plant_live WHERE inverter_id='PLANT_SUMMARY' ORDER BY ts DESC LIMIT 1440",
                    con=get_engine()
                )
                if not _batt_hist_cyc.empty:
                    _pwr = _batt_hist_cyc["battery_power_kw"].values
                    _sign_changes = int(np.sum(np.diff(np.sign(_pwr)) != 0))
                    _cycles_today = round(_sign_changes / 2, 1)
                    _energy_thru  = round(float(np.abs(_pwr[_pwr > 0]).sum()) * (5 / 3600), 1)  # kWh throughput (5s intervals)
                    _dod_avg      = round(float(np.abs(np.diff(_batt_hist_cyc['battery_power_kw'].cumsum().values)[:10]).mean()), 1) if len(_pwr)>10 else 0
                else:
                    _cycles_today = _energy_thru = 0
            except Exception:
                _cycles_today = _energy_thru = 0
            _bc1, _bc2, _bc3 = st.columns(3)
            for _col, _lbl, _val, _unit, _clr in [
                (_bc1, "Cycles Today",    f"{_cycles_today:.1f}",  "charge/discharge", "#3b82f6"),
                (_bc2, "Energy Thruput",  f"{_energy_thru:.1f}",   "kWh (today)",      "#fb923c"),
                (_bc3, "Est. Life",       "6,200",                  "cycles at 0.5C",   "#22c55e"),
            ]:
                _col.markdown(f"""
                <div style='text-align:center; padding:10px 4px;'>
                    <div style='font-size:10px; color:#8b8b9a; text-transform:uppercase; margin-bottom:5px;'>{_lbl}</div>
                    <div style='font-size:20px; font-weight:700; color:{_clr}; font-family:monospace;'>{_val}</div>
                    <div style='font-size:10px; color:#8b8b9a; margin-top:3px;'>{_unit}</div>
                </div>""", unsafe_allow_html=True)

        # Battery SOC trend
        with st.container(border=True):
            st.markdown('<div class="panel-title">BATTERY SOC TREND</div>', unsafe_allow_html=True)
            @st.cache_data(ttl=5)
            def load_batt_trend():
                try:
                    d = pd.read_sql("SELECT ts, battery_soc, battery_power_kw FROM plant_live WHERE inverter_id='PLANT_SUMMARY' ORDER BY ts DESC LIMIT 180", con=get_engine())
                    d["ts"] = pd.to_datetime(d["ts"])
                    return d.sort_values("ts")
                except Exception:
                    return None
            batt_hist = load_batt_trend()
            if batt_hist is not None and len(batt_hist) >= 2:
                from plotly.subplots import make_subplots
                fig_batt = make_subplots(specs=[[{"secondary_y": True}]])
                fig_batt.add_trace(go.Scatter(x=batt_hist["ts"], y=batt_hist["battery_soc"], name="SOC %",
                                              line=dict(color="#3b82f6", width=2), fill="tozeroy",
                                              fillcolor="rgba(59,130,246,0.1)"), secondary_y=False)
                fig_batt.add_trace(go.Scatter(x=batt_hist["ts"], y=batt_hist["battery_power_kw"], name="Power kW",
                                              line=dict(color="#fb923c", width=1.5, dash="dot")), secondary_y=True)
                fig_batt.update_layout(**PLOT_LAYOUT, height=180)
                fig_batt.update_xaxes(showgrid=False)
                fig_batt.update_yaxes(showgrid=True, gridcolor="#1f1f28", secondary_y=False)
                fig_batt.update_yaxes(showgrid=False, secondary_y=True)
                st.plotly_chart(fig_batt, use_container_width=True, config={'displayModeBar': False})

    with u2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">WEATHER STATION — WS-01</div>', unsafe_allow_html=True)
            ghi     = plant['GHI']
            amb     = plant['AmbientTemp_C']
            pv_temp = amb + 20

            wf1, wf2, wf3 = st.columns(3)
            def weather_card(col, icon, label, val, unit):
                col.markdown(f"""
                <div style='text-align:center; padding:12px 4px; border:1px solid #1f1f28; border-radius:6px; background:#0a0a0f; margin:3px;'>
                    <div style='font-size:24px; margin-bottom:4px;'>{icon}</div>
                    <div style='font-size:10px; color:#8b8b9a; text-transform:uppercase; margin-bottom:4px;'>{label}</div>
                    <div style='font-size:18px; font-weight:700; color:#f0f0f5; font-family:monospace;'>{val}</div>
                    <div style='font-size:10px; color:#8b8b9a;'>{unit}</div>
                </div>""", unsafe_allow_html=True)

            weather_card(wf1, "☀️", "Irradiance",  f"{ghi:.0f}",   "W/m²")
            weather_card(wf2, "🌡️", "Ambient",     f"{amb:.1f}",   "°C")
            weather_card(wf3, "🏭", "PV Temp",     f"{pv_temp:.1f}", "°C")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            wf4, wf5, wf6 = st.columns(3)
            weather_card(wf4, "💨", "Wind Speed",  "4.3",  "m/s")
            weather_card(wf5, "🧭", "Wind Dir",    "254",  "°")
            weather_card(wf6, "💧", "Humidity",    "34.2", "%")

        with st.container(border=True):
            st.markdown('<div class="panel-title">COMMUNICATION DIAGNOSTICS</div>', unsafe_allow_html=True)
            comms = [
                ("Modbus TCP", "Inverter-01", "Online",  "12ms",  "green"),
                ("Modbus TCP", "Inverter-02", "Online",  "14ms",  "green"),
                ("Modbus TCP", "Inverter-03", "Online",  "13ms",  "green"),
                ("Modbus TCP", "Inverter-04", "Online",  "11ms",  "green"),
                ("Modbus TCP", "Inverter-05", "Online",  "15ms",  "green"),
                ("IEC 61850",  "RMU-BCU-01",  "Online",  "8ms",   "green"),
                ("DNP3",       "Weather Stn", "Online",  "25ms",  "green"),
                ("Modbus RTU", "DataServer-1","Offline", "—",     "red"),
            ]
            st.markdown("""
            <table style="width:100%; font-size:12px; border-collapse:collapse; color:#f0f0f5;">
                <tr style="color:#8b8b9a; border-bottom:2px solid #2a2a35;">
                    <th style="padding:6px; text-align:left;">Protocol</th>
                    <th style="padding:6px; text-align:left;">Device</th>
                    <th style="padding:6px; text-align:left;">Status</th>
                    <th style="padding:6px; text-align:right;">Latency</th>
                </tr>
            """ + "".join([
                f"""<tr style="border-bottom:1px solid #1f1f28; background:{'#0a0a0f' if i%2==0 else '#141419'};">
                    <td style="padding:6px; font-family:monospace; color:#8b8b9a;">{c[0]}</td>
                    <td style="padding:6px; font-weight:600;">{c[1]}</td>
                    <td style="padding:6px;"><span class="led-{c[4]}"></span> {c[2]}</td>
                    <td style="padding:6px; text-align:right; font-family:monospace; color:#8b8b9a;">{c[3]}</td>
                </tr>"""
                for i, c in enumerate(comms)
            ]) + "</table>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="panel-title">SYSTEM INFORMATION</div>', unsafe_allow_html=True)
            try:
                db_count = pd.read_sql("SELECT COUNT(*) as cnt FROM plant_live", con=get_engine()).iloc[0]['cnt']
            except Exception:
                db_count = "N/A"
            last_ts = str(plant.get("ts", df["ts"].max()))[:19] if "ts" in plant.index else "N/A"
            sys_info = [
                ("App Version",        "v3.0 — Phase 7"),
                ("Streamlit Version",  "1.x"),
                ("Database",           "SQLite (WAL mode)"),
                ("Last Data Point",    str(df["ts"].max())[:19]),
                ("Total DB Records",   str(db_count)),
                ("Plant Capacity",     "500 kW"),
                ("N Inverters",        "5 × 100 kW"),
                ("Battery Capacity",   "200 kWh / 0.5C"),
                ("Grid Code",          "IEC 61727"),
                ("Protocol Layer",     "Modbus TCP / IEC 61850"),
            ]
            for key, val in sys_info:
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; padding:5px 6px; border-bottom:1px solid #1f1f28; font-size:12px;'>
                    <span style='color:#8b8b9a;'>{key}</span>
                    <span style='color:#f0f0f5; font-weight:600; font-family:monospace;'>{val}</span>
                </div>""", unsafe_allow_html=True)

elif menu == "🔮 Predictor":

    st.title("🔮 Solar Power Predictor")

    st.markdown(
        """
        Predict the expected power generation of a solar plant
        using live weather data for any location.
        """
    )

    location_service = LocationService()
    weather_service = WeatherService()
    prediction_service = PredictionService()
    recommendation_service = RecommendationService()

    location_name = st.text_input(
        "Location",
        placeholder="Example: Kolkata, Delhi, IIT Kharagpur, Chennai..."
    )

    plant_capacity = st.number_input(
        "Plant Capacity (kW)",
        min_value=1.0,
        value=500.0,
        step=10.0,
    )

    if st.button("Predict Power"):

        if not location_name.strip():
            st.warning("Please enter a location.")
            st.stop()

        with st.spinner("Fetching weather..."):

            location = location_service.resolve(location_name)

            weather = weather_service.get_current_weather(
                
                latitude=location.latitude,
                longitude=location.longitude,
           )

            prediction = prediction_service.predict(
                weather=weather,
                plant_capacity_kw=plant_capacity,
            )

            recommendations = recommendation_service.generate(
                
                prediction,
                weather,
                plant_capacity,
            )

        st.success(f"Location: {location.display_name}")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Irradiance",
            f"{weather.ghi_w_m2:.0f} W/m²",
        )

        c2.metric(
            "Temperature",
            f"{weather.temperature_c:.1f} °C",
        )

        c3.metric(
            "Predicted AC Power",
            f"{prediction.ac_power_kw:.2f} kW",
        )

        c4.metric(
            "Performance Ratio",
            f"{prediction.performance_ratio:.3f}",
        )

        st.subheader("Weather Conditions")

        st.dataframe(
            {
                "Parameter": [
                    "Relative Humidity",
                    "Cloud Cover",
                    "Wind Speed",
                ],
                "Value": [
                    f"{weather.relative_humidity_pct} %",
                    f"{weather.cloud_cover_pct} %",
                    f"{weather.wind_speed_m_s} m/s",
                ],
            },
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Prediction")

        st.dataframe(
            {
                "Metric": [
                    "Predicted DC Power",
                    "Predicted AC Power",
                    "Estimated Hourly Energy",
                    "Performance Ratio",
                    "Inverter Efficiency",
                ],
                "Value": [
                    f"{prediction.dc_power_kw:.2f} kW",
                    f"{prediction.ac_power_kw:.2f} kW",
                    f"{prediction.estimated_hourly_energy_kwh:.2f} kWh",
                    f"{prediction.performance_ratio:.3f}",
                    f"{prediction.inverter_efficiency_pct:.1f} %",
                ],
            },
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Recommendations")
        st.dataframe(
            
            recommendations,
            use_container_width=True,
            hide_index=True,
        )