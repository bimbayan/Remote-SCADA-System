from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LocationResult:
    """
    Represents a resolved geographical location.
    """

    query: str
    display_name: str

    latitude: float
    longitude: float

    city: str | None
    state: str | None
    country: str


@dataclass(frozen=True, slots=True)
class WeatherSnapshot:
    """
    Represents the environmental conditions at a given instant.
    """

    timestamp: str

    ghi_w_m2: float
    temperature_c: float
    humidity_pct: float
    wind_speed_m_s: float
    cloud_cover_pct: float

    is_day: bool

@dataclass(frozen=True, slots=True)
class PredictionResult:
    dc_power_kw: float
    ac_power_kw: float

    estimated_hourly_energy_kwh: float

    final_yield: float
    reference_yield: float
    performance_ratio: float

    inverter_efficiency_pct: float