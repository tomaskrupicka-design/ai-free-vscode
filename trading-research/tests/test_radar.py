from __future__ import annotations

import unittest

import pandas as pd

from src.radar import add_radar_score, latest_radar_snapshot
from src.regime import add_market_regime


class RadarTests(unittest.TestCase):
    def make_data(self, rising: bool = True, rows: int = 260) -> pd.DataFrame:
        index = pd.date_range("2025-01-01", periods=rows, freq="D")
        if rising:
            close = [100.0 + i * 0.35 for i in range(rows)]
        else:
            close = [200.0 - i * 0.35 for i in range(rows)]
        return pd.DataFrame({"close": close}, index=index)

    def prepare(self, rising: bool) -> pd.DataFrame:
        data = self.make_data(rising=rising)
        return add_market_regime(
            data,
            fast_window=20,
            slow_window=100,
            vol_window=20,
        )

    def test_score_is_bounded(self) -> None:
        radar = add_radar_score(self.prepare(True))
        self.assertTrue((radar["radar_score"] <= 100).all())
        self.assertTrue((radar["radar_score"] >= -100).all())

    def test_rising_market_has_non_negative_latest_score(self) -> None:
        radar = add_radar_score(self.prepare(True))
        self.assertGreaterEqual(float(radar["radar_score"].iloc[-1]), 0.0)

    def test_falling_market_has_non_positive_latest_score(self) -> None:
        radar = add_radar_score(self.prepare(False))
        self.assertLessEqual(float(radar["radar_score"].iloc[-1]), 0.0)

    def test_snapshot_contains_explanation(self) -> None:
        radar = add_radar_score(self.prepare(True))
        snap = latest_radar_snapshot(radar)
        self.assertIn(snap["signal"], {"LONG", "SHORT", "WAIT"})
        self.assertIn("components", snap)
        self.assertIn("reason", snap)


if __name__ == "__main__":
    unittest.main()
