from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
import pvlib
import requests

from config import (
    OPENWEATHER_API_KEY,
    OPENWEATHER_API_URL,
    REQUEST_TIMEOUT_SECONDS,
    USER_AGENT,
)
from models import WeatherSnapshot


class WeatherServiceError(RuntimeError):
    """Raised when weather data cannot be retrieved."""


class WeatherService:
    """
    Hybrid weather service:
    - GHI computed locally via pvlib Ineichen-Perez clear-sky model (no API)
    - Temperature, humidity, wind, clouds from OpenWeather (free tier)
    - 100% reliable — never fails due to external API issues
    """

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": USER_AGENT})

    # ──────────────────────────────────────────────────────────────
    #  PUBLIC API
    # ──────────────────────────────────────────────────────────────

    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        altitude: float = 0.0,
    ) -> WeatherSnapshot:
        """
        Returns a WeatherSnapshot for the given coordinates.

        GHI is computed locally via pvlib clear-sky model.
        Meteorological data comes from OpenWeather Current API.
        """
        now = datetime.now(timezone.utc)

        # 1. Compute GHI locally — NEVER fails, NO API call
        ghi = self._compute_clear_sky_ghi(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            timestamp=now,
        )

        # 2. Fetch temp/humidity/wind/clouds from OpenWeather
        #    If this fails, we fall back to reasonable defaults
        try:
            weather_data = self._fetch_openweather(latitude, longitude)
        except Exception:
            weather_data = self._fallback_weather(latitude, longitude, now)

        return WeatherSnapshot(
            timestamp=now.isoformat(),
            ghi_w_m2=ghi,
            temperature_c=weather_data["temperature_c"],
            humidity_pct=weather_data["humidity_pct"],
            wind_speed_m_s=weather_data["wind_speed_m_s"],
            cloud_cover_pct=weather_data["cloud_cover_pct"],
            is_day=weather_data["is_day"],
        )

    def get_hourly_forecast(
        self,
        latitude: float,
        longitude: float,
        altitude: float = 0.0,
    ) -> list[WeatherSnapshot]:
        """
        Returns 24 hourly snapshots.

        GHI computed locally for each hour.
        Temp/humidity/wind/clouds from OpenWeather forecast.
        """
        now = datetime.now(timezone.utc)
        snapshots: list[WeatherSnapshot] = []

        # Try OpenWeather forecast; fall back to current weather repeated
        try:
            forecast_data = self._fetch_openweather_forecast(latitude, longitude)
        except Exception:
            forecast_data = []

        for hour_offset in range(24):
            hour_time = now.replace(minute=0, second=0, microsecond=0)
            hour_time = hour_time + pd.Timedelta(hours=hour_offset)

            ghi = self._compute_clear_sky_ghi(
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                timestamp=hour_time,
            )

            if hour_offset < len(forecast_data):
                wd = forecast_data[hour_offset]
            else:
                wd = self._fallback_weather(latitude, longitude, hour_time)

            snapshots.append(
                WeatherSnapshot(
                    timestamp=hour_time.isoformat(),
                    ghi_w_m2=ghi,
                    temperature_c=wd["temperature_c"],
                    humidity_pct=wd["humidity_pct"],
                    wind_speed_m_s=wd["wind_speed_m_s"],
                    cloud_cover_pct=wd["cloud_cover_pct"],
                    is_day=wd["is_day"],
                )
            )

        return snapshots

    # ──────────────────────────────────────────────────────────────
    #  DAILY FORECAST (Open‑Meteo) – used for the 7‑day outlook
    # ──────────────────────────────────────────────────────────────
    def get_daily_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
    ) -> list[dict]:
        """
        Returns a list of daily forecasts for the next *days* days.
        Each dict contains:
            - date (str, ISO format)
            - ghi_w_m2 (float)   – average irradiance over the day
            - temp_c (float)     – average temperature (°C)
            - sunrise (str)      – ISO time
            - sunset (str)       – ISO time
        Uses the free Open‑Meteo API (no key required).
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset,shortwave_radiation_sum",
            "timezone": "auto",
            "forecast_days": days,
        }
        try:
            resp = self._session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            # Return an empty list on failure; the caller can handle it.
            print(f"[WeatherService] Daily forecast failed: {exc}")
            return []

        daily = data.get("daily", {})
        times = daily.get("time", [])
        tmax = daily.get("temperature_2m_max", [])
        tmin = daily.get("temperature_2m_min", [])
        sunrise = daily.get("sunrise", [])   # Fixed: was sunset
        sunset = daily.get("sunset", [])     # Fixed: was sunset
        rad_sum = daily.get("shortwave_radiation_sum", [])

        out = []
        for i, date_str in enumerate(times[:days]):
            # Convert radiation sum (MJ/m2/day) to average W/m2
            rad_mj = rad_sum[i] if i < len(rad_sum) else 0.0
            ghi_w_m2 = rad_mj * 1_000_000 / (24 * 3600)  # = rad_mj * 11.574074...
            # Average temperature
            t_max = tmax[i] if i < len(tmax) else None
            t_min = tmin[i] if i < len(tmin) else None
            if t_max is not None and t_min is not None:
                temp_c = (t_max + t_min) / 2.0
            else:
                temp_c = 20.0  # fallback

            out.append({
                "date": date_str,
                "ghi_w_m2": round(ghi_w_m2, 2),
                "temp_c": round(temp_c, 1),
                "sunrise": sunrise[i] if i < len(sunrise) else "",
                "sunset": sunset[i] if i < len(sunset) else "",
            })
        return out

    # ──────────────────────────────────────────────────────────────
    #  GHI COMPUTATION — pvlib clear-sky (NO API, 100% reliable)
    # ──────────────────────────────────────────────────────────────

    def _compute_clear_sky_ghi(
        self,
        latitude: float,
        longitude: float,
        altitude: float,
        timestamp: datetime,
    ) -> float:
        """
        Compute clear-sky GHI using pvlib's Ineichen-Perez model.

        This requires ONLY:
            - latitude, longitude, altitude
            - timestamp

        No API calls. No keys. No rate limits. 100% reliable.

        The Ineichen-Perez model is the standard clear-sky model
        used in solar forecasting research (Reno et al., SAND2012-2389).
        """
        # Create a single-point DatetimeIndex for pvlib
        times = pd.DatetimeIndex([timestamp], tz="UTC")

        # Build pvlib Location object
        location = pvlib.location.Location(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            tz="UTC",
        )

        # Compute clear-sky irradiance
        # Default model='ineichen' uses climatological Linke turbidity
        # from global lookup tables — no user input needed
        clearsky_df = location.get_clearsky(times, model="ineichen")

        ghi = float(clearsky_df["ghi"].iloc[0])

        # Ensure non-negative (nighttime returns 0)
        return max(ghi, 0.0)

    # ──────────────────────────────────────────────────────────────
    #  OPENWEATHER API — temp, humidity, wind, clouds
    # ──────────────────────────────────────────────────────────────

    def _fetch_openweather(
        self,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        """Fetch current weather from OpenWeather."""
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        }

        response = self._session.get(
            OPENWEATHER_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "temperature_c": float(data["main"]["temp"]),
            "humidity_pct": float(data["main"]["humidity"]),
            "wind_speed_m_s": float(data["wind"]["speed"]),
            "cloud_cover_pct": float(data["clouds"]["all"]),
            "is_day": data.get("weather", [{}])[0].get("icon", "").endswith("d"),
        }

    def _fetch_openweather_forecast(
        self,
        latitude: float,
        longitude: float,
    ) -> list[dict[str, Any]]:
        """Fetch 5-day / 3-hour forecast from OpenWeather."""
        url = OPENWEATHER_API_URL.replace("weather", "forecast")
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        }

        response = self._session.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()

        result = []
        for item in data.get("list", [])[:8]:  # next 24h (3h intervals)
            result.append({
                "temperature_c": float(item["main"]["temp"]),
                "humidity_pct": float(item["main"]["humidity"]),
                "wind_speed_m_s": float(item["wind"]["speed"]),
                "cloud_cover_pct": float(item["clouds"]["all"]),
                "is_day": item.get("weather", [{}])[0].get("icon", "").endswith("d"),
            })

        return result

    # ──────────────────────────────────────────────────────────────
    #  FALLBACK — never let the Predictor crash
    # ──────────────────────────────────────────────────────────────

    def _fallback_weather(
        self,
        latitude: float,
        longitude: float,
        timestamp: datetime,
    ) -> dict[str, Any]:
        """
        Return reasonable default weather values.

        Used when OpenWeather is unavailable. GHI is still computed
        locally via pvlib, so the only missing data is meteorological.
        """
        # Determine if it's daytime based on solar elevation
        is_day = self._is_daytime(latitude, longitude, timestamp)

        # Season-aware temperature estimate for India-ish latitudes
        month = timestamp.month
        if month in [12, 1, 2]:      # Winter
            temp = 22.0
            humidity = 55.0
        elif month in [3, 4, 5]:     # Summer
            temp = 35.0
            humidity = 40.0
        elif month in [6, 7, 8, 9]:  # Monsoon
            temp = 30.0
            humidity = 75.0
        else:                        # Post-monsoon
            temp = 28.0
            humidity = 65.0

        return {
            "temperature_c": temp,
            "humidity_pct": humidity,
            "wind_speed_m_s": 3.5,
            "cloud_cover_pct": 20.0 if is_day else 0.0,
            "is_day": is_day,
        }

    def _is_daytime(
        self,
        latitude: float,
        longitude: float,
        timestamp: datetime,
    ) -> bool:
        """Check if sun is above horizon at given time/location."""
        times = pd.DatetimeIndex([timestamp], tz="UTC")
        solpos = pvlib.solarposition.get_solarposition(
            times, latitude, longitude
        )
        elevation = float(solpos["apparent_elevation"].iloc[0])
        return elevation > 0