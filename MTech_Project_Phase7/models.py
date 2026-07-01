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
    timestamp: str

    ghi_w_m2: float
    temperature_c: float
    humidity_pct: float
    wind_speed_m_s: float
    cloud_cover_pct: float

    is_day: bool

@dataclass(frozen=True, slots=True)
class PredictionResult:
    """
    Represents the output of the PV prediction engine.
    """

    dc_power_kw: float
    ac_power_kw: float

    estimated_energy_kwh: float

    performance_ratio: float
    plant_efficiency: float