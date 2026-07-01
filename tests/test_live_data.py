import unittest
from unittest.mock import Mock

import pandas as pd

from MTech_Project_Phase7.live_data import (
    build_forecast_telemetry,
    build_live_snapshot,
    estimate_ac_power_kw,
    fetch_live_environment,
)


class LiveDataTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "current": {
                "time": "2026-06-30T12:00",
                "temperature_2m": 32.0,
                "relative_humidity_2m": 65,
                "cloud_cover": 40,
                "wind_speed_10m": 3.2,
                "shortwave_radiation": 800.0,
                "is_day": 1,
            },
            "hourly": {
                "time": ["2026-06-30T12:00", "2026-06-30T13:00"],
                "temperature_2m": [32.0, 33.0],
                "relative_humidity_2m": [65, 62],
                "cloud_cover": [40, 35],
                "wind_speed_10m": [3.2, 3.5],
                "shortwave_radiation": [800.0, 750.0],
            },
        }

    def fake_session(self):
        response = Mock()
        response.json.return_value = self.payload
        response.raise_for_status.return_value = None
        response.url = "https://api.open-meteo.com/v1/forecast?test=true"
        session = Mock()
        session.get.return_value = response
        return session

    def test_fetch_and_transform(self):
        data = fetch_live_environment(session=self.fake_session())
        forecast = build_forecast_telemetry(data)
        snapshot = build_live_snapshot(data)
        self.assertEqual(len(forecast), 2)
        self.assertEqual(len(snapshot), 6)
        self.assertEqual(snapshot.iloc[-1]["inverter_id"], "PLANT_SUMMARY")
        self.assertTrue((forecast["Estimated_AC_kW"] >= 0).all())

    def test_power_model_bounds(self):
        self.assertEqual(estimate_ac_power_kw(0.0, 25.0), 0.0)
        self.assertLessEqual(estimate_ac_power_kw(2000.0, 25.0), 500.0)

    def test_power_model_handles_series(self):
        result = estimate_ac_power_kw(pd.Series([0.0, 1000.0]), pd.Series([25.0, 35.0]))
        self.assertEqual(len(result), 2)
        self.assertGreater(result.iloc[1], result.iloc[0])


if __name__ == "__main__":
    unittest.main()

