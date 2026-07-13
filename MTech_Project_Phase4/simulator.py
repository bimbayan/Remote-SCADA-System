# simulator.py
"""
Simulator for: 5 inverters, 10 panels (2 panels per inverter), small battery.
Writes snapshots to data/live/plant_live.csv every INTERVAL_S seconds.
Each snapshot contains one row per inverter, one row per panel, one plant summary, and one battery row.
"""

import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

# Output config
OUT_DIR = os.path.abspath("data/live")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, "plant_live.csv")
print("Simulator writing to:", OUT_FILE)

# Plant topology
N_INVERTERS = 5
N_PANELS = 10
PANELS_PER_INVERTER = 2   # 10 panels / 5 inverters
assert N_PANELS == N_INVERTERS * PANELS_PER_INVERTER

# Ratings
INVERTER_RATED_KW = 100.0            # AC rating per inverter
PANEL_RATED_KW = INVERTER_RATED_KW / PANELS_PER_INVERTER  # panel rating so 2 panels -> 1 inverter
PLANT_CAPACITY_KW = INVERTER_RATED_KW * N_INVERTERS

# Timing and RNG
INTERVAL_S = 5
np.random.seed(42)

# Small site load so battery can discharge/charge realistically
SITE_LOAD_KW = 300.0

# Battery simple model
BATTERY_CAPACITY_KWH = 500.0         # total usable capacity
BATTERY_MAX_CHARGE_KW = 250.0
BATTERY_MAX_DISCHARGE_KW = 250.0
BATTERY_EFFICIENCY = 0.95            # round-trip approx

# Build panels and assign to inverters
panels = []
for p in range(N_PANELS):
    panels.append({
        "panel_id": f"PV-{p+1:02d}",
        "rated_kw": PANEL_RATED_KW,
    })

inverters = []
for i in range(N_INVERTERS):
    inv_panels = panels[i*PANELS_PER_INVERTER:(i+1)*PANELS_PER_INVERTER]
    inverters.append({
        "inverter_id": f"INV-{i+1:02d}",
        "rated_kw": INVERTER_RATED_KW,
        "panels": inv_panels,
        "status": "Running",
        "total_energy_kwh": 0.0
    })

# Battery state
battery = {
    "soc_kwh": BATTERY_CAPACITY_KWH * 0.5,   # start 50% SOC
    "capacity_kwh": BATTERY_CAPACITY_KWH,
    "status": "Idle"
}

# time
start_time = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

# ---------- helper models ----------
def solar_irradiance(ts):
    """Return realistic GHI (W/m2) for timestamp ts."""
    hour = ts.hour + ts.minute/60 + ts.second/3600
    if hour < 6 or hour > 18:
        return 0.0
    t = (hour - 6) / 12.0  # 0..1
    ghi = 1000.0 * np.sin(np.pi * t)               # bell curve peak ~1000
    ghi += np.random.normal(0, 60)                 # clouds jitter
    return max(0.0, ghi)

def temp_model(ghi):
    """Simple ambient temperature approximated from GHI."""
    return 20 + (ghi / 1000.0) * 15 + np.random.normal(0, 2.0)

def performance_ratio():
    """Random PR around nominal."""
    return np.clip(np.random.normal(0.78, 0.03), 0.65, 0.9)

# ---------- simulation timestep ----------
def simulate_panel(ts, panel):
    """Return panel DC output (kW) at timestamp for a single panel."""
    ghi = solar_irradiance(ts)
    # Panel rated_kw is STC DC rating; simple linear relation
    p_dc_kw = (ghi / 1000.0) * panel["rated_kw"]
    # add small mismatch noise
    p_dc_kw *= (1.0 + np.random.normal(0, 0.02))
    return round(max(0.0, p_dc_kw), 4), round(ghi, 2)

def simulate_inverter(ts, inv):
    """Simulate inverter: sum its panels DC -> apply PR/temp/inverter behavior -> AC (kW)."""
    panel_rows = []
    panel_dc_sum = 0.0
    ghi_vals = []
    temp_vals = []
    for panel in inv["panels"]:
        p_dc, ghi = simulate_panel(ts, panel)
        panel_rows.append({
            "ts": ts.isoformat(),
            "inverter_id": inv["inverter_id"],
            "panel_id": panel["panel_id"],
            "panel_rated_kw": panel["rated_kw"],
            "GHI": ghi,
            "P_DC_kW": p_dc
        })
        panel_dc_sum += p_dc
        ghi_vals.append(ghi)

    # temperature derived from mean GHI
    ambient_temp = temp_model(np.mean(ghi_vals) if ghi_vals else 0.0)
    temp_factor = 1.0 - 0.004 * max(0.0, ambient_temp - 25.0)
    pr = performance_ratio()

    # DC-to-AC mapping: use panel DC sum, PR and temp factor to get AC before clipping
    p_ac_raw = panel_dc_sum * pr * temp_factor
    # limit by inverter AC rating (no grid export limits here)
    p_ac = float(np.clip(p_ac_raw, 0.0, inv["rated_kw"]))

    # small MPPT/inverter jitter
    p_ac *= (1.0 + np.random.normal(0, 0.003))

    # occasional inverter faults
    roll = np.random.rand()
    status = inv["status"]
    if roll < 0.002:
        status = "Fault"
        p_ac = 0.0
    elif roll < 0.01:
        status = "Stopped"
        p_ac = 0.0
    else:
        status = "Running"

    energy_kwh = p_ac * (INTERVAL_S / 3600.0)
    inv["total_energy_kwh"] += energy_kwh
    inv["status"] = status

    inv_row = {
        "ts": ts.isoformat(),
        "inverter_id": inv["inverter_id"],
        "rated_kw": inv["rated_kw"],
        "status": status,
        "GHI": round(np.mean(ghi_vals), 2) if ghi_vals else 0.0,
        "AmbientTemp_C": round(ambient_temp, 2),
        "P_AC_kW": round(p_ac, 3),
        "P_DC_sum_kW": round(panel_dc_sum, 3),
        "Energy_increment_kWh": round(energy_kwh, 6),
        "Total_energy_kWh": round(inv["total_energy_kwh"], 6)
    }

    return panel_rows, inv_row

def battery_step(net_generation_kw):
    """
    net_generation_kw: plant generation available (positive = generation available)
    This function updates battery['soc_kwh'], returns battery_power_kW (positive charging, negative discharging)
    """
    soc = battery["soc_kwh"]
    cap = battery["capacity_kwh"]

    # If generation greater than site load, charge up to max charge power
    if net_generation_kw > 0:
        charge_possible = min(net_generation_kw, BATTERY_MAX_CHARGE_KW)
        charge_kwh = charge_possible * (INTERVAL_S / 3600.0)
        # don't exceed capacity
        charge_kwh = min(charge_kwh, cap - soc)
        battery["soc_kwh"] += charge_kwh * BATTERY_EFFICIENCY
        battery["status"] = "Charging" if charge_kwh > 0 else "Idle"
        return round(charge_possible if charge_kwh > 0 else 0.0, 3)  # positive = charging power
    else:
        # deficit: discharge to meet demand up to max discharge
        deficit_kw = abs(net_generation_kw)
        discharge_possible = min(deficit_kw, BATTERY_MAX_DISCHARGE_KW)
        discharge_kwh = discharge_possible * (INTERVAL_S / 3600.0)
        # don't go below 0
        discharge_kwh = min(discharge_kwh, battery["soc_kwh"])
        battery["soc_kwh"] -= discharge_kwh / BATTERY_EFFICIENCY
        battery["status"] = "Discharging" if discharge_kwh > 0 else "Idle"
        return round(-discharge_possible if discharge_kwh > 0 else 0.0, 3)  # negative = discharging

# ---------- main run loop ----------
def write_snapshot(rows):
    # Write inverter rows + plant summary + battery row + panel rows
    # rows is a dict with keys: "panel_rows" list, "inv_rows" list, plant, battery
    flat = []
    # include panel rows first
    for pr in rows["panel_rows"]:
        flat.append(pr)
    # include inverter rows
    for ir in rows["inv_rows"]:
        flat.append(ir)
    # plant summary
    flat.append(rows["plant"])
    # battery row
    flat.append(rows["battery_row"])
    pd.DataFrame(flat).to_csv(OUT_FILE, index=False)

def run_simulator(duration_minutes=999999):
    ts = start_time
    end_time = ts + timedelta(minutes=duration_minutes)

    while ts <= end_time:
        panel_rows_all = []
        inv_rows_all = []
        total_gen_kw = 0.0

        # per-inverter simulation
        for inv in inverters:
            prs, inv_row = simulate_inverter(ts, inv)
            panel_rows_all.extend(prs)
            inv_rows_all.append(inv_row)
            total_gen_kw += inv_row["P_AC_kW"]

        # simple site load and battery: supply site_load from generation first
        # net_generation = generation - site_load
        net_gen_kw = total_gen_kw - SITE_LOAD_KW

        # battery acts to absorb net_gen_kw positive (charging) or supply deficit (discharging)
        battery_power_kw = battery_step(net_gen_kw)

        # compute final plant export/consumption after battery action
        plant_net_export_kw = total_gen_kw - SITE_LOAD_KW - (battery_power_kw if battery_power_kw > 0 else 0.0) \
                              + (abs(battery_power_kw) if battery_power_kw < 0 else 0.0)

        plant = {
            "ts": ts.isoformat(),
            "inverter_id": "PLANT_SUMMARY",
            "rated_kw": PLANT_CAPACITY_KW,
            "status": "Running",
            "GHI": round(np.mean([p["GHI"] for p in panel_rows_all]) if panel_rows_all else 0.0, 2),
            "AmbientTemp_C": round(np.mean([p.get("AmbientTemp_C", np.nan) for p in inv_rows_all if "AmbientTemp_C" in p]) if inv_rows_all else 0.0, 2),
            "P_AC_kW": round(total_gen_kw, 3),
            "P_net_kW": round(plant_net_export_kw, 3),
            "Site_Load_kW": round(SITE_LOAD_KW, 3),
            "Battery_power_kW": round(battery_power_kw, 3),
            "Battery_SOC_kWh": round(battery["soc_kwh"], 3),
            "Energy_increment_kWh": round(sum([ir["Energy_increment_kWh"] for ir in inv_rows_all]), 6),
            "Total_energy_kWh": round(sum([ir["Total_energy_kWh"] for ir in inv_rows_all]), 6)
        }

        rows = {
            "panel_rows": panel_rows_all,
            "inv_rows": inv_rows_all,
            "plant": plant,
            "battery_row": {
                "ts": ts.isoformat(),
                "inverter_id": "BATTERY",
                "rated_kw": BATTERY_MAX_DISCHARGE_KW,
                "status": battery["status"],
                "GHI": None,
                "AmbientTemp_C": None,
                "P_AC_kW": None,
                "Battery_power_kW": round(battery_power_kw, 3),
                "Battery_SOC_kWh": round(battery["soc_kwh"], 3)
            }
        }

        write_snapshot(rows)
        print(f"[SIM] {ts.isoformat()}  Plant_Gen={plant['P_AC_kW']:.2f}kW  Net={plant['P_net_kW']:.2f}kW  Bat={rows['battery_row']['Battery_power_kW']}kW  SOC={battery['soc_kwh']:.1f}kWh")

        # increment timestamp with small jitter to ensure uniqueness
        ts = ts + timedelta(seconds=INTERVAL_S, milliseconds=int(np.random.randint(1, 300)))
        time.sleep(INTERVAL_S)

if __name__ == "__main__":
    run_simulator()
