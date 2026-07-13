from __future__ import annotations

import pandas as pd

from decision_engine import generate_decisions

from models import (
    PredictionResult,
    WeatherSnapshot,
)


class RecommendationService:
    """
    Generates operational recommendations based on
    the predicted plant performance.
    """

    def generate(
        self,
        prediction: PredictionResult,
        weather: WeatherSnapshot,
        plant_capacity_kw: float,
    ) -> pd.DataFrame:

        plant_summary = {
            "inverter_id": "PLANT_SUMMARY",
            "P_AC_kW": prediction.ac_power_kw,
            "GHI": weather.ghi_w_m2,
            "rated_kw": plant_capacity_kw,
            "battery_soc": 60,
        }

        df = pd.DataFrame([plant_summary])

        return generate_decisions(df)