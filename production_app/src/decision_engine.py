import pandas as pd
import numpy as np

def generate_decisions(df_live):
    """
    Input:
        df_live : latest snapshot dataframe (including PLANT_SUMMARY)
    Output:
        ranked list of decision recommendations
    """

    decisions = []

    plant = df_live[df_live["inverter_id"] == "PLANT_SUMMARY"].iloc[-1]

    plant_power = plant["P_AC_kW"]
    ghi = plant["GHI"]
    rated = plant["rated_kw"]
    battery_soc = plant.get("battery_soc", 50)

    # -------------------------------
    # 1. Underperformance detection
    # -------------------------------
    expected_power = (ghi / 1000) * rated
    if expected_power > 0 and plant_power < 0.8 * expected_power:
        loss_kw = expected_power - plant_power

        decisions.append({
            "action": "Investigate underperformance",
            "reason": "Plant output significantly below irradiance-based expectation",
            "estimated_gain_kw": round(loss_kw, 2),
            "priority_score": loss_kw * 1.5
        })

    # -------------------------------
    # 2. Battery misuse risk
    # -------------------------------
    if battery_soc > 90:
        decisions.append({
            "action": "Reduce battery charging",
            "reason": "Battery SOC high — risk of clipping / accelerated ageing",
            "estimated_gain_kw": 0,
            "priority_score": 40
        })

    if battery_soc < 20:
        decisions.append({
            "action": "Preserve battery",
            "reason": "Battery SOC critically low — reserve for grid events",
            "estimated_gain_kw": 0,
            "priority_score": 50
        })

    # -------------------------------
    # 3. Inverter availability
    # -------------------------------
    inv = df_live[df_live["inverter_id"] != "PLANT_SUMMARY"]

    # Safety: status column may not exist yet
    if "status" in inv.columns:
        down = inv[inv["status"] != "Running"]
    else:
        down = pd.DataFrame()

    if not down.empty:
        lost_kw = down["rated_kw"].sum() if "rated_kw" in down.columns else 0.0
        decisions.append({
            "action": "Dispatch O&M to restore inverter(s)",
            "reason": f"{len(down)} inverter(s) unavailable",
            "estimated_gain_kw": round(lost_kw, 2),
            "priority_score": lost_kw * 2
        })

    # -------------------------------
    # Final ranking
    # -------------------------------
    if not decisions:
        decisions.append({
            "action": "No action required",
            "reason": "Plant operating within optimal envelope",
            "estimated_gain_kw": 0,
            "priority_score": 0
        })

    df_decisions = pd.DataFrame(decisions)
    df_decisions = df_decisions.sort_values(
        by="priority_score", ascending=False
    ).reset_index(drop=True)

    return df_decisions