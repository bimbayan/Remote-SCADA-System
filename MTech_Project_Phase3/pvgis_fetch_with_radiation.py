# pvgis_fetch_with_radiation.py
import os
import requests
import pandas as pd

lat, lon = 23.0, 88.5
url = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"

params = {
    "lat": lat,
    "lon": lon,
    "raddatabase": "PVGIS-ERA5",   # global dataset
    "startyear": 2020,
    "endyear": 2020,
    "angle": 0,
    "aspect": 0,
    "pvcalculation": 0,
    "outputformat": "json",
    # 👇 this ensures we actually get irradiance data
    "components": 1,               # include G(h), Gb(n), Gd(h)
}

print("Requesting PVGIS data...")
r = requests.get(url, params=params, timeout=180)
print("STATUS:", r.status_code)
r.raise_for_status()

data = r.json()["outputs"]["hourly"]
df = pd.DataFrame(data)

print("Columns received:", df.columns.tolist()[:10])

# Parse timestamps
df["ts"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M", errors="coerce", utc=True)
df = df.dropna(subset=["ts"]).sort_values("ts").reset_index(drop=True)

# Save raw file
os.makedirs("data/curated", exist_ok=True)
df.to_csv("data/curated/pvgis_2020_hourly.csv", index=False)
print("Data with irradiance saved → data/curated/pvgis_2020_hourly.csv")
