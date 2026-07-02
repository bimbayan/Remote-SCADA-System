from __future__ import annotations

from enum import Enum

# ============================================================
# API Endpoints
# ============================================================

OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"

PVGIS_API_URL = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"

NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"

# ============================================================
# Application Configuration
# ============================================================

DEFAULT_LATITUDE = 23.0
DEFAULT_LONGITUDE = 88.5

DEFAULT_PLANT_CAPACITY_KW = 500.0
DEFAULT_INVERTER_COUNT = 5

REQUEST_TIMEOUT_SECONDS = 15
CACHE_TTL_SECONDS = 300

TIMEZONE = "Asia/Kolkata"

USER_AGENT = "Remote-SCADA-MTech/1.0"

# ============================================================
# Open-Meteo Weather Fields
# ============================================================

class WeatherField(str, Enum):
    TEMPERATURE = "temperature_2m"
    HUMIDITY = "relative_humidity_2m"
    CLOUD_COVER = "cloud_cover"
    WIND_SPEED = "wind_speed_10m"
    GHI = "shortwave_radiation"
    IS_DAY = "is_day"

# ============================================================
# Equipment Status
# ============================================================

class InverterStatus(str, Enum):
    RUNNING = "Running"
    STANDBY = "Standby"

# ============================================================
# Data Classification
# ============================================================

class DataClassification(str, Enum):
    MODELLED_EQUIPMENT = "MODELLED_EQUIPMENT"
    MODELLED_FROM_LIVE_WEATHER = "MODELLED_FROM_LIVE_WEATHER"