# simulator_phase6.py
import os, time, math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# near the top of simulator_phase6.py
import os
PLOT = os.getenv("PLOT")        # set env-var only when you want the window
if PLOT:
    import matplotlib.pyplot as plt
    plt.ion()


# ------------------------------------------------------------------
# 0a.  KEEP LAST N SNAPSHOTS  (so dashboard never waits)
# ------------------------------------------------------------------
def write_snapshot(rows):
    from database import get_engine
    import sqlalchemy as sa
    engine = get_engine()
    df = pd.DataFrame(rows)
    df.to_sql("plant_live", con=engine, if_exists="append", index=False)
    
    # Optional cleanup to keep DB small (keep approx 1000 snapshots for the rolling window)
    try:
        with engine.begin() as con:
            con.execute(sa.text("DELETE FROM plant_live WHERE ts <= strftime('%Y-%m-%dT%H:%M:%S', 'now', '-1 hours')"))
    except Exception:
        pass
# ------------------------------------------------------------------
# 1.  Folders / constants
# ------------------------------------------------------------------
OUT_DIR   = os.path.abspath("data")
LIVE_DIR  = os.path.join(OUT_DIR, "live")
LOG_DIR   = os.path.join(OUT_DIR, "logs")
os.makedirs(LIVE_DIR, exist_ok=True)
os.makedirs(LOG_DIR,  exist_ok=True)

LIVE_FILE  = os.path.join(LIVE_DIR, "plant_live.csv")
ALARM_FILE = os.path.join(LOG_DIR,  "alarms.csv")

INTERVAL_S          = 5
PLANT_CAPACITY_KW   = 500.0
N_INVERTERS         = 5
N_PANELS            = 10
PANELS_PER_INV      = 2
INVERTER_RATED_KW   = PLANT_CAPACITY_KW / N_INVERTERS
PANEL_RATED_KW      = INVERTER_RATED_KW / PANELS_PER_INV
BATTERY_CAPACITY_KWH= 200.0
BATTERY_MAX_C_RATE  = 0.5
BATTERY_ROUNDTRIP_EFF= 0.95
BATTERY_TEMP_COEFF  = 0.005
TRANSFORMER_RATED_KVA= 600.0
np.random.seed(42)

start_time = datetime.now().replace(microsecond=0)

# ------------------------------------------------------------------
# 2.  Hardware objects
# ------------------------------------------------------------------
battery = {
    "soc": 1.0,  # Refreshed battery SOC to 100%
    "capacity_kwh": BATTERY_CAPACITY_KWH,
    "temp_c": 25.0,
    "voltage": 600.0
}

inverters = []
for i in range(N_INVERTERS):
    inverters.append({
        "inverter_id": f"INV-{i+1:02d}",
        "rated_kw": INVERTER_RATED_KW,
        "status": "Running",
        "total_energy_kwh": 0.0,
        "panels": [f"PV-{i*PANELS_PER_INV + j + 1:02d}" for j in range(PANELS_PER_INV)]
    })

panels = [{"panel_id": f"PV-{i+1:02d}", "rated_kw": PANEL_RATED_KW} for i in range(N_PANELS)]

# ------------------------------------------------------------------
# 3.  Alarm logger
# ------------------------------------------------------------------
def raise_alarm(source, severity, message, ts):
    from database import get_engine
    engine = get_engine()
    entry = {"ts": ts.isoformat(), "source": source,
             "severity": severity, "message": message}
    
    # Write to SQL
    df_new = pd.DataFrame([entry])
    
    # Try to check last alarm to prevent duplicate spam
    try:
        last_alarm = pd.read_sql("SELECT source, message FROM alarms ORDER BY ts DESC LIMIT 1", con=engine)
        if not last_alarm.empty:
            if last_alarm.iloc[0]["source"] == source and last_alarm.iloc[0]["message"] == message:
                return
    except Exception:
        pass
        
    df_new.to_sql("alarms", con=engine, if_exists="append", index=False)

# ------------------------------------------------------------------
# 4.  Models
# ------------------------------------------------------------------
def battery_max_power_kw():
    return BATTERY_MAX_C_RATE * battery["capacity_kwh"]

def battery_voltage_from_soc(soc):
    return 480 + 170 * soc

def battery_temp_derating_factor(temp_c):
    return 1.0 if temp_c <= 25 else max(0.6, 1.0 - BATTERY_TEMP_COEFF*(temp_c-25))

def battery_step(charge_power_kw, dt_hours):
    max_p = battery_max_power_kw()
    charge_power_kw = max(-max_p, min(max_p, charge_power_kw))
    derate = battery_temp_derating_factor(battery["temp_c"])
    eff  = math.sqrt(BATTERY_ROUNDTRIP_EFF)
    effective_power = charge_power_kw * derate
    delta_kwh = effective_power * dt_hours * eff
    new_soc = battery["soc"] + delta_kwh / battery["capacity_kwh"]
    new_soc = max(0.01, min(0.99, new_soc))
    battery["soc"] = new_soc
    battery["voltage"] = battery_voltage_from_soc(new_soc)
    return delta_kwh

def transformer_losses_kw(load_kw):
    rated = TRANSFORMER_RATED_KVA
    load_pct = min(1.0, load_kw / rated)
    core_loss = 0.01 * rated
    cu_loss   = 0.01 * rated * (load_pct ** 2)
    return core_loss + cu_loss

def panel_power_from_ghi(ghi, kw):
    p = (ghi / 1000.0) * kw * (0.98 + 0.04 * np.random.randn())
    return max(0, p)

# ------------------------------------------------------------------
# 5.  Real-time plot utilities
# ------------------------------------------------------------------
PLOT_ENABLED = False
line1 = line2 = line3 = None
fig   = None

def init_plot():
    global line1, line2, line3, fig, PLOT_ENABLED
    try:
        import matplotlib.pyplot as plt
        plt.ion()
        fig, ax = plt.subplots(figsize=(7,4))
        ax.set_ylim(-50, 550)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Power (kW) / SOC (%)")
        ax.grid(True)
        line1, = ax.plot([], [], label="Plant AC (kW)", color="tab:green")
        line2, = ax.plot([], [], label="Battery power (kW)", color="tab:blue")
        line3, = ax.plot([], [], label="Battery SOC (%)", color="tab:red")
        ax.legend()
        PLOT_ENABLED = True
        return fig, ax
    except ImportError:
        print("[WARN] matplotlib not found – running head-less")
        return None, None

def update_plot(ax, t_hist, p_hist, b_pwr_hist, soc_hist):
    if not PLOT_ENABLED:
        return
    import matplotlib.pyplot as plt
    line1.set_data(t_hist, p_hist)
    line2.set_data(t_hist, b_pwr_hist)
    line3.set_data(t_hist, soc_hist)
    ax.set_xlim(max(0, t_hist[-1]-300), t_hist[-1]+10)  # rolling 5-min window
    fig.canvas.draw()
    fig.canvas.flush_events()

# ------------------------------------------------------------------
# 6.  Main loop
# ------------------------------------------------------------------
def run_simulator(duration_minutes=999999):
    import fcntl
    import sys
    lock_file = os.path.join(OUT_DIR, "simulator.lock")
    lock_fd = open(lock_file, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Another simulator instance is already running.", flush=True)
        sys.exit(0)

    ts = start_time
    end_ts = ts + timedelta(minutes=duration_minutes)

    # history lists for plotting
    t_hist, p_hist, b_pwr_hist, soc_hist = [], [], [], []
    t0 = time.time()

    fig, ax = init_plot()

    while ts <= end_ts:
        # ---- weather / irradiance ---------------------------------
        hour = ts.hour + ts.minute/60
        day_fraction = max(0, min(1, (hour - 6) / 12))
        base = math.sin(day_fraction * math.pi)
        ghi  = max(0, base * (900 + 60*np.random.randn()) + np.random.normal(0,20))

        # ---- panel DC ---------------------------------------------
        panel_rows = []
        for p in panels:
            dc = panel_power_from_ghi(ghi, p["rated_kw"])
            panel_rows.append({"panel_id": p["panel_id"], "P_DC_kW": round(dc,3)})

        # ---- inverter AC ------------------------------------------
        rows, plant_total_ac, plant_energy_inc = [], 0, 0
        for inv in inverters:
            dc_sum = sum(r["P_DC_kW"] for r in panel_rows if r["panel_id"] in inv["panels"])
            ambient = 20 + 12*base + np.random.normal(0,2)
            temp_factor = 1 - 0.004*max(0, ambient - 25)
            perf = 0.95 + 0.02*np.random.randn()
            ac = dc_sum * temp_factor * perf
            ac = max(0, min(inv["rated_kw"], ac))

            status = "Running"
            if np.random.rand() < 0.002:
                status = "Fault"
                ac = 0
                raise_alarm(inv["inverter_id"], "Critical", "Inverter fault detected", ts)

            inc = ac * (INTERVAL_S/3600)
            inv["total_energy_kwh"] += inc
            plant_total_ac += ac
            plant_energy_inc += inc

            rows.append({
                "ts": ts.isoformat(),
                "inverter_id": inv["inverter_id"],
                "panel_id": ",".join(inv["panels"]),
                "GHI": round(ghi,2),
                "P_DC_kW": round(dc_sum,3),
                "rated_kw": inv["rated_kw"],
                "status": status,
                "AmbientTemp_C": round(ambient,2),
                "P_AC_kW": round(ac,3),
                "Energy_increment_kWh": round(inc,6),
                "Total_energy_kWh": round(inv["total_energy_kwh"],6)
            })

        # ---- battery ----------------------------------------------
        dt = INTERVAL_S / 3600
        net_batt_kw = 0
        if plant_total_ac > 0.9 * PLANT_CAPACITY_KW:
            net_batt_kw = min(battery_max_power_kw(), plant_total_ac - 0.9 * PLANT_CAPACITY_KW)
        elif plant_total_ac < 0.5 * PLANT_CAPACITY_KW:
            if battery["soc"] > 0.01:
                net_batt_kw = -min(battery_max_power_kw(), 0.5*PLANT_CAPACITY_KW - plant_total_ac)
            else:
                net_batt_kw = 0
                
        battery_step(net_batt_kw, dt)
        if net_batt_kw < 0:
            plant_total_ac += abs(net_batt_kw)
            plant_energy_inc += abs(net_batt_kw) * dt

        # ---- transformer ------------------------------------------
        t_loss = transformer_losses_kw(plant_total_ac)
        t_eff  = max(0.85, 1 - t_loss/max(1, plant_total_ac))
        load_pct = (plant_total_ac / TRANSFORMER_RATED_KVA)*100
        if load_pct > 110:
            raise_alarm("TRANSFORMER-01","Critical",f"Transformer overloaded {round(load_pct,2)}%", ts)
        if battery["temp_c"] > 55:
            raise_alarm("BATTERY-01","High",f"Battery temperature high: {battery['temp_c']}", ts)

        # ---- plant summary row ------------------------------------
        plant_row = {
            "ts": ts.isoformat(),
            "inverter_id": "PLANT_SUMMARY",
            "GHI": round(ghi,2),
            "P_DC_kW": round(sum(r["P_DC_kW"] for r in panel_rows),3),
            "rated_kw": PLANT_CAPACITY_KW,
            "status": "Running",
            "AmbientTemp_C": round(ambient,2),
            "P_AC_kW": round(plant_total_ac,3),
            "Energy_increment_kWh": round(plant_energy_inc,6),
            "Total_energy_kWh": round(sum(inv["total_energy_kwh"] for inv in inverters),6),
            "transformer_loss_kw": round(t_loss,3),
            "transformer_eff": round(t_eff,4),
            "battery_soc": round(battery["soc"]*100,2),
            "battery_voltage": round(battery["voltage"],2),
            "battery_temp_c": round(battery["temp_c"],2),
            "battery_power_kw": round(net_batt_kw,3)
        }
        rows.append(plant_row)
        write_snapshot(rows)          # use the circular buffer you defined at the top

        # ---- console print ----------------------------------------
        print(f"[SIM] {ts.isoformat()}  P={plant_total_ac:.2f} kW  SOC={battery['soc']*100:.1f}%")

        # ---- update plot -------------------------------------
        elapsed = time.time() - t0
        t_hist.append(elapsed)
        p_hist.append(plant_total_ac)
        b_pwr_hist.append(net_batt_kw)
        soc_hist.append(battery["soc"]*100)
        if PLOT_ENABLED:
            update_plot(ax, t_hist, p_hist, b_pwr_hist, soc_hist)

        # ---- advance time -----------------------------------------
        ts += timedelta(seconds=INTERVAL_S)
        battery["temp_c"] += np.random.randn()*0.02
        time.sleep(INTERVAL_S)

# ------------------------------------------------------------------
# 7.  Entry point
# ------------------------------------------------------------------
if __name__ == "__main__":
    run_simulator()