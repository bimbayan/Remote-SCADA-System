"""Live environmental data adapter and transparent solar-plant model.

Open-Meteo supplies current model conditions and forecasts. The equipment
values are explicitly modelled because this project has no physical PLC, RTU
or inverter connected to it yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd
import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_LATITUDE = 23.0
DEFAULT_LONGITUDE = 88.5
PLANT_CAPACITY_KW = 500.0
INVERTER_COUNT = 5

CURRENT_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "cloud_cover",
    "wind_speed_10m",
    "shortwave_radiation",
    "is_day",
]
HOURLY_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "cloud_cover",
    "wind_speed_10m",
    "shortwave_radiation",
]


class LiveDataError(RuntimeError):
    """Raised when the upstream data cannot be retrieved or validated."""


@dataclass(frozen=True)
class ApiTelemetry:
    current: dict[str, Any]
    forecast: pd.DataFrame
    endpoint: str
    response_ms: int
    fetched_at: pd.Timestamp
    source: str = "Open-Meteo Forecast API"


def _request_params(latitude: float, longitude: float) -> dict[str, Any]:
    return {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(CURRENT_FIELDS),
        "hourly": ",".join(HOURLY_FIELDS),
        "forecast_days": 7,
        "timezone": "Asia/Kolkata",
        "wind_speed_unit": "ms",
    }


def fetch_live_environment(
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
    timeout_s: int = 15,
    session: requests.Session | None = None,
) -> ApiTelemetry:
    """Fetch current conditions plus seven days of hourly forecast data."""

    client = session or requests.Session()
    started = perf_counter()
    try:
        response = client.get(
            OPEN_METEO_URL,
            params=_request_params(latitude, longitude),
            timeout=timeout_s,
            headers={"User-Agent": "Remote-SCADA-MTech/1.0"},
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise LiveDataError(f"Open-Meteo request failed: {exc}") from exc

    response_ms = round((perf_counter() - started) * 1000)
    current = payload.get("current")
    hourly = payload.get("hourly")
    if not isinstance(current, dict) or not isinstance(hourly, dict):
        raise LiveDataError("Open-Meteo response omitted current or hourly data")

    try:
        forecast = pd.DataFrame(hourly)
        forecast["time"] = pd.to_datetime(forecast["time"], errors="raise")
    except (ValueError, TypeError) as exc:
        raise LiveDataError(f"Open-Meteo response schema was invalid: {exc}") from exc

    response_url = getattr(response, "url", OPEN_METEO_URL)
    return ApiTelemetry(
        current=current,
        forecast=forecast,
        endpoint=response_url,
        response_ms=response_ms,
        fetched_at=pd.Timestamp.now(tz="Asia/Kolkata"),
    )


def estimate_ac_power_kw(
    ghi_w_m2: pd.Series | float,
    ambient_temp_c: pd.Series | float,
    capacity_kw: float = PLANT_CAPACITY_KW,
) -> pd.Series | float:
    """Estimate AC output using irradiance, temperature derating and losses."""

    cell_temp_c = ambient_temp_c + (45.0 - 20.0) / 800.0 * ghi_w_m2
    temperature_factor = np.clip(1.0 - 0.0042 * np.maximum(cell_temp_c - 25.0, 0.0), 0.75, 1.0)
    dc_kw = capacity_kw * np.maximum(ghi_w_m2, 0.0) / 1000.0 * temperature_factor
    return np.clip(dc_kw * 0.97, 0.0, capacity_kw)


def build_forecast_telemetry(api_data: ApiTelemetry) -> pd.DataFrame:
    """Convert the upstream hourly response into modelled plant telemetry."""

    df = api_data.forecast.rename(
        columns={
            "shortwave_radiation": "GHI_W_m2",
            "temperature_2m": "AmbientTemp_C",
            "relative_humidity_2m": "Humidity_pct",
            "cloud_cover": "CloudCover_pct",
            "wind_speed_10m": "WindSpeed_m_s",
        }
    ).copy()
    df["Estimated_AC_kW"] = estimate_ac_power_kw(df["GHI_W_m2"], df["AmbientTemp_C"])
    df["Estimated_Energy_kWh"] = df["Estimated_AC_kW"]
    df.insert(0, "record_id", [f"WX-{i:04d}" for i in range(1, len(df) + 1)])
    return df


def build_live_snapshot(api_data: ApiTelemetry) -> pd.DataFrame:
    """Build deterministic equipment rows from the current real environment."""

    current = api_data.current
    timestamp = pd.to_datetime(current["time"])
    ghi = float(current.get("shortwave_radiation", 0.0) or 0.0)
    temperature = float(current.get("temperature_2m", 25.0) or 25.0)
    plant_ac = float(estimate_ac_power_kw(ghi, temperature))

    # A stable seed prevents equipment values jumping during Streamlit reruns.
    seed = int(timestamp.strftime("%Y%m%d%H%M")) % (2**32 - 1)
    rng = np.random.default_rng(seed)
    shares = np.clip(rng.normal(1.0, 0.018, INVERTER_COUNT), 0.94, 1.04)
    shares = shares / shares.sum()

    rows: list[dict[str, Any]] = []
    for index, share in enumerate(shares, start=1):
        inverter_ac = plant_ac * float(share)
        rows.append(
            {
                "ts": timestamp,
                "inverter_id": f"INV-{index:02d}",
                "status": "Running" if current.get("is_day", 1) else "Standby",
                "rated_kw": PLANT_CAPACITY_KW / INVERTER_COUNT,
                "GHI": ghi,
                "AmbientTemp_C": temperature,
                "P_DC_kW": inverter_ac / 0.97,
                "P_AC_kW": inverter_ac,
                "data_class": "MODELLED_EQUIPMENT",
            }
        )

    rows.append(
        {
            "ts": timestamp,
            "inverter_id": "PLANT_SUMMARY",
            "status": "Running" if current.get("is_day", 1) else "Standby",
            "rated_kw": PLANT_CAPACITY_KW,
            "GHI": ghi,
            "AmbientTemp_C": temperature,
            "P_DC_kW": plant_ac / 0.97,
            "P_AC_kW": plant_ac,
            "battery_soc": float(np.clip(35.0 + ghi * 0.035, 35.0, 85.0)),
            "humidity_pct": current.get("relative_humidity_2m"),
            "cloud_cover_pct": current.get("cloud_cover"),
            "wind_speed_m_s": current.get("wind_speed_10m"),
            "data_class": "MODELLED_FROM_LIVE_WEATHER",
        }
    )
    return pd.DataFrame(rows)
