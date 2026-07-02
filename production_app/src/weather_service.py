from __future__ import annotations

from typing import Any

import requests

from config import (
    OPEN_METEO_API_URL,
    REQUEST_TIMEOUT_SECONDS,
    TIMEZONE,
    USER_AGENT,
    WeatherField,
)
from models import WeatherSnapshot


class WeatherServiceError(RuntimeError):
    """Raised when weather data cannot be retrieved."""


class WeatherService:
    """
    Fetches weather information from Open-Meteo.

    This service is responsible only for communicating with the upstream
    weather provider and converting responses into WeatherSnapshot objects.
    """

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": USER_AGENT,
            }
        )

    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> WeatherSnapshot:

        payload = self._fetch(
            latitude,
            longitude,
            current=True,
            hourly=False,
        )

        current = payload["current"]

        return WeatherSnapshot(
            timestamp=current["time"],
            ghi_w_m2=float(current.get(WeatherField.GHI.value, 0)),
            temperature_c=float(current.get(WeatherField.TEMPERATURE.value, 0)),
            humidity_pct=float(current.get(WeatherField.HUMIDITY.value, 0)),
            wind_speed_m_s=float(current.get(WeatherField.WIND_SPEED.value, 0)),
            cloud_cover_pct=float(current.get(WeatherField.CLOUD_COVER.value, 0)),
            is_day=bool(current.get(WeatherField.IS_DAY.value, 1)),
        )

    def get_hourly_forecast(
        self,
        latitude: float,
        longitude: float,
    ) -> list[WeatherSnapshot]:

        payload = self._fetch(
            latitude,
            longitude,
            current=False,
            hourly=True,
        )

        hourly = payload["hourly"]

        snapshots: list[WeatherSnapshot] = []

        total = len(hourly["time"])

        for index in range(total):
            snapshots.append(
                WeatherSnapshot(
                    timestamp=hourly["time"][index],
                    ghi_w_m2=float(hourly[WeatherField.GHI.value][index]),
                    temperature_c=float(hourly[WeatherField.TEMPERATURE.value][index]),
                    humidity_pct=float(hourly[WeatherField.HUMIDITY.value][index]),
                    wind_speed_m_s=float(hourly[WeatherField.WIND_SPEED.value][index]),
                    cloud_cover_pct=float(hourly[WeatherField.CLOUD_COVER.value][index]),
                    is_day=True,
                )
            )

        return snapshots

    def _fetch(
        self,
        latitude: float,
        longitude: float,
        *,
        current: bool,
        hourly: bool,
    ) -> dict[str, Any]:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": TIMEZONE,
            "wind_speed_unit": "ms",
        }

        if current:
            params["current"] = ",".join(
                field.value
                for field in [
                    WeatherField.TEMPERATURE,
                    WeatherField.HUMIDITY,
                    WeatherField.CLOUD_COVER,
                    WeatherField.WIND_SPEED,
                    WeatherField.GHI,
                    WeatherField.IS_DAY,
                ]
            )

        if hourly:
            params["forecast_days"] = 7
            params["hourly"] = ",".join(
                field.value
                for field in [
                    WeatherField.TEMPERATURE,
                    WeatherField.HUMIDITY,
                    WeatherField.CLOUD_COVER,
                    WeatherField.WIND_SPEED,
                    WeatherField.GHI,
                ]
            )

        try:
            response = self._session.get(
                OPEN_METEO_API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as exc:
            raise WeatherServiceError(
                "Unable to retrieve weather information."
            ) from exc