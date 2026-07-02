"""Application configuration."""

import os
from enum import Enum
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LIVE_DB = DATA_DIR / "live" / "scada_live.db"
LOG_DB = DATA_DIR / "logs" / "scada_logs.db"

# ── Simulator ────────────────────────────────────────────────────
SIM_INTERVAL_SECONDS = 5
SIM_PLANT_CAPACITY_KW = 1000.0

# ── Database ─────────────────────────────────────────────────────
DB_TIMEOUT_SECONDS = 10

# ── HTTP ─────────────────────────────────────────────────────────
REQUEST_TIMEOUT_SECONDS = 15
USER_AGENT = (
    "RemoteSCADA/1.0 (https://github.com/bimbayan/Remote-SCADA-System)"
)

# ── Time ─────────────────────────────────────────────────────────
TIMEZONE = "UTC"

# ── OpenWeather (for temp/humidity/wind/clouds) ──────────────────
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

# ── Nominatim (geocoding — free, no key needed) ──────────────────
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"

# ── Weather field mapping ────────────────────────────────────────
class WeatherField(Enum):
    TEMPERATURE = "temp"
    HUMIDITY = "humidity"
    WIND_SPEED = "speed"
    CLOUD_COVER = "all"
    IS_DAY = "icon"