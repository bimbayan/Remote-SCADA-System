# sizing_estimator.py
import requests, pandas as pd
import numpy as np

PVGIS_BASE = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"

def fetch_irradiation(lat: float, lon: float, year: int = 2022):
    params = {
        "lat": lat,
        "lon": lon,
        "raddatabase": "PVGIS-ERA5",
        "startyear": year,
        "endyear": year,
        "angle": 0,
        "aspect": 0,
        "pvcalculation": 0,
        "components": 1,
        "outputformat": "json",
    }

    r = requests.get(PVGIS_BASE, params=params, timeout=120)
    r.raise_for_status()

    data = r.json()["outputs"]["hourly"]
    df = pd.DataFrame(data)

    if "G(h)" in df.columns:
        ghi = pd.to_numeric(df["G(h)"], errors="coerce").fillna(0)
    else:
        # components fallback
        cols = ["Gb(i)", "Gd(i)", "Gr(i)", "Int"]
        irradiance_cols = [df[c] for c in cols if c in df.columns]
        ghi = sum(pd.to_numeric(c, errors="coerce").fillna(0) for c in irradiance_cols)

    # PVGIS hourly is always hourly → convert Wh/m2 to kWh/m2
    annual_kwh_m2 = ghi.sum() / 1000  
    return annual_kwh_m2


def size_system(lat, lon,
                target_annual_kwh=None,
                desired_kwp=None,
                module_eff=0.18,
                performance_ratio=0.78,
                cost_per_kwp=450,
                electricity_price=0.08):

    annual_irr = fetch_irradiation(lat, lon)

    specific_yield = annual_irr * performance_ratio  # kWh/kWp/year

    if desired_kwp is not None:
        required_kwp = desired_kwp
        annual_output = specific_yield * required_kwp
    else:
        required_kwp = target_annual_kwh / specific_yield
        annual_output = target_annual_kwh

    area_m2 = required_kwp * (1/module_eff)

    total_cost = required_kwp * cost_per_kwp

    payback = None
    if annual_output * electricity_price > 0:
        payback = total_cost / (annual_output * electricity_price)

    return {
        "annual_irradiation_kwh_m2": round(annual_irr,2),
        "specific_yield_kwh_per_kwp": round(specific_yield,2),
        "required_kwp": round(required_kwp,2),
        "annual_output_kwh": round(annual_output,2),
        "area_m2": round(area_m2,2),
        "total_cost_usd": round(total_cost,2),
        "payback_years": round(payback,2) if payback else None
    }
