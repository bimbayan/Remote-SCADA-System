from __future__ import annotations

import numpy as np

from models import (
    PredictionResult,
    WeatherSnapshot,
)

# ------------------------------------------------------------------
# PV Model Constants
# ------------------------------------------------------------------

REFERENCE_CELL_TEMPERATURE_C = 25.0
REFERENCE_AMBIENT_TEMPERATURE_C = 20.0
NOCT_C = 45.0

TEMPERATURE_COEFFICIENT = 0.0042

INVERTER_EFFICIENCY = 0.97

MIN_TEMPERATURE_FACTOR = 0.75


class PredictionService:
    """
    Predicts PV plant output from weather conditions.
    """

    def predict(
        self,
        weather: WeatherSnapshot,
        plant_capacity_kw: float,
    ) -> PredictionResult:

        # --------------------------------------------------------------
        # Cell Temperature (NOCT Model)
        # --------------------------------------------------------------

        cell_temperature = (
            weather.temperature_c
            + (NOCT_C - REFERENCE_AMBIENT_TEMPERATURE_C)
            / 800.0
            * weather.ghi_w_m2
        )

        # --------------------------------------------------------------
        # Temperature Derating
        # --------------------------------------------------------------

        temperature_factor = np.clip(
            1.0
            - TEMPERATURE_COEFFICIENT
            * max(cell_temperature - REFERENCE_CELL_TEMPERATURE_C, 0.0),
            MIN_TEMPERATURE_FACTOR,
            1.0,
        )

        # --------------------------------------------------------------
        # DC Power
        # --------------------------------------------------------------

        dc_power = (
            plant_capacity_kw
            * weather.ghi_w_m2
            / 1000.0
            * temperature_factor
        )

        # --------------------------------------------------------------
        # AC Power
        # --------------------------------------------------------------

        ac_power = min(
            dc_power * INVERTER_EFFICIENCY,
            plant_capacity_kw,
        )

        # --------------------------------------------------------------
        # Hourly Energy
        # --------------------------------------------------------------

        forecast_interval_hours = 1.0

        hourly_energy = ac_power * forecast_interval_hours

        # --------------------------------------------------------------
        # IEC 61724 Performance Ratio
        # --------------------------------------------------------------

        reference_yield = (
            weather.ghi_w_m2
            / 1000.0
        ) * forecast_interval_hours

        final_yield = (
            hourly_energy
            / plant_capacity_kw
        )

        if reference_yield > 0:
            performance_ratio = final_yield / reference_yield
        else:
            performance_ratio = 0.0

        return PredictionResult(
            dc_power_kw=round(dc_power, 2),
            ac_power_kw=round(ac_power, 2),
            estimated_hourly_energy_kwh=round(hourly_energy, 2),
            final_yield=round(final_yield, 4),
            reference_yield=round(reference_yield, 4),
            performance_ratio=round(performance_ratio, 3),
            inverter_efficiency_pct=round(
                INVERTER_EFFICIENCY * 100,
                1,
            ),
        )