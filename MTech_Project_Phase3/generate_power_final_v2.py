# generate_power_final_v2.py
import pandas as pd
import numpy as np
import os

# set the plant parameters
PLANT_DC_KWP = 100.0       # PV plant size in kWp
DC_AC_RATIO = 1.2          # typical 1.1–1.3
GAMMA_PDC = -0.0042        # power temp coefficient (/°C)
NOCT_C = 45.0              # °C (Nominal Operating Cell Temp)
INV_EFF = 0.97             # inverter efficiency


src_csv = "data/curated/pvgis_2020_hourly.csv"
if not os.path.exists(src_csv):
    raise FileNotFoundError(f"CSV not found: {src_csv}")

df = pd.read_csv(src_csv)
df.columns = df.columns.str.strip()

# Auto-detect and map columns 
rename_map = {
    "Gb(n)": "DNI",
    "Gb(i)": "DNI",
    "Gd(h)": "DHI",
    "Gd(i)": "DHI",
    "G(h)": "GHI",
    "Gr(i)": "Reflected",
    "T2m": "Temperature",
    "WS10m": "WindSpeed",
    "RH": "RelativeHumidity"
}
for old, new in rename_map.items():
    if old in df.columns:
        df.rename(columns={old: new}, inplace=True)

# If no GHI column exists, compute it from available irradiance
if "GHI" not in df.columns:
    if all(col in df.columns for col in ["DNI", "DHI", "Reflected"]):
        df["GHI"] = df["DNI"] + df["DHI"] + df["Reflected"]
        print("Computed GHI = DNI + DHI + Reflected")
    elif all(col in df.columns for col in ["DNI", "DHI"]):
        df["GHI"] = df["DNI"] + df["DHI"]
        print("Computed GHI = DNI + DHI")
    else:
        raise ValueError(f"No irradiance columns found. Columns: {list(df.columns)}")

# Parse timestamp
if "ts" not in df.columns:
    if "time" in df.columns:
        df["ts"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M", errors="coerce", utc=True)
    else:
        raise ValueError("No timestamp found (expected 'ts' or 'time').")

df = df.dropna(subset=["ts"]).sort_values("ts").reset_index(drop=True)

# Model 
P_AC_RATED = PLANT_DC_KWP / DC_AC_RATIO
df["GHI"] = df["GHI"].clip(lower=0)
df["T_cell"] = df["Temperature"] + ((NOCT_C - 20) / 800) * df["GHI"]
df["P_DC_kW"] = (
    PLANT_DC_KWP * (df["GHI"] / 1000) * (1 + GAMMA_PDC * (df["T_cell"] - 25))
).clip(lower=0)
df["P_AC_kW"] = (df["P_DC_kW"] * INV_EFF).clip(upper=P_AC_RATED)

# Save output
os.makedirs("data/curated", exist_ok=True)
out_csv = "data/curated/pvgis_2020_with_power.csv"
out_parquet = "data/curated/pvgis_2020_with_power.parquet"

df.to_csv(out_csv, index=False)
df.to_parquet(out_parquet, index=False)

print(" Power calculation complete.")
print(f" Saved to {out_csv}")
print(df[["ts", "GHI", "Temperature", "T_cell", "P_DC_kW", "P_AC_kW"]].head())
