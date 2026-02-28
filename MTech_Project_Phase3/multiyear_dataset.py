# build_dataset_multi_year.py
import os
import requests
import pandas as pd
import numpy as np


# CONFIG

LAT, LON = 23.0, 88.5
YEARS = range(2018, 2024)
BASE_URL = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"

# PV model parameters
PLANT_DC_KWP = 100.0
DC_AC_RATIO = 1.2
GAMMA_PDC = -0.0042
NOCT_C = 45.0
INV_EFF = 0.97

os.makedirs("data/curated/multi_year", exist_ok=True)
frames = []


# LOOP THROUGH YEARS

for year in YEARS:
    print(f" Downloading {year} data...")
    params = {
        "lat": LAT,
        "lon": LON,
        "raddatabase": "PVGIS-ERA5",
        "startyear": year,
        "endyear": year,
        "angle": 0,
        "aspect": 0,
        "pvcalculation": 0,
        "components": 1,        # ensures Gb(i), Gd(i), Gr(i)
        "outputformat": "json"
    }

    r = requests.get(BASE_URL, params=params, timeout=180)
    if r.status_code != 200:
        print(f"Failed for {year}: {r.status_code}")
        continue

    data = r.json()["outputs"]["hourly"]
    df = pd.DataFrame(data)

    # Parse time
    df["ts"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M", errors="coerce", utc=True)
    df = df.dropna(subset=["ts"])

    # Rename columns
    rename_map = {
        "Gb(n)": "DNI", "Gb(i)": "DNI",
        "Gd(h)": "DHI", "Gd(i)": "DHI",
        "Gr(i)": "Reflected",
        "T2m": "Temperature",
        "WS10m": "WindSpeed",
        "RH": "RelativeHumidity"
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # Compute GHI if missing
    if "GHI" not in df.columns:
        cols = [c for c in ["DNI", "DHI", "Reflected"] if c in df.columns]
        if len(cols) >= 2:
            df["GHI"] = df[cols].sum(axis=1)
        else:
            raise ValueError(f"No irradiance columns found for {year}: {df.columns}")

    # --- Power model ---
    P_AC_RATED = PLANT_DC_KWP / DC_AC_RATIO
    df["GHI"] = df["GHI"].clip(lower=0)
    df["Temperature"] = df["Temperature"].astype(float)
    df["T_cell"] = df["Temperature"] + ((NOCT_C - 20) / 800) * df["GHI"]
    df["P_DC_kW"] = (
        PLANT_DC_KWP * (df["GHI"] / 1000) * (1 + GAMMA_PDC * (df["T_cell"] - 25))
    ).clip(lower=0)
    df["P_AC_kW"] = (df["P_DC_kW"] * INV_EFF).clip(upper=P_AC_RATED)

    df["Year"] = year
    frames.append(df[["ts", "Year", "GHI", "Temperature", "WindSpeed", "P_AC_kW"]])

    print(f" {year} complete → {len(df)} records")


# MERGE ALL YEARS

if not frames:
    raise RuntimeError("No yearly data was downloaded successfully.")

big = pd.concat(frames, ignore_index=True).sort_values("ts")
out_csv = "data/curated/multi_year/pvgis_2018_2023_with_power.csv"
out_parq = "data/curated/multi_year/pvgis_2018_2023_with_power.parquet"

big.to_csv(out_csv, index=False)
big.to_parquet(out_parq, index=False)

print("\n🎉 Multi-year dataset ready!")
print("📁", out_csv)
print(big.head())
print(f"🧾 Total records: {len(big):,}")
