from __future__ import annotations

import unittest

import pandas as pd

from src.multimarket import analyze_market


class MultiMarketTests(unittest.TestCase):
    def make_data(self, slope: float, rows: int = 260) -> pd.DataFrame:
        index = pd.date_range("2025-01-01", periods=rows, freq="D")
        close = [100.0 + slope * i + ((i % 9) - 4) * 0.03 for i in range(rows)]
        return pd.DataFrame({"close": close}, index=index)

    def test_analyze_market_returns_snapshot(self) -> None:
        tested, result = analyze_market("TEST", self.make_data(0.25))
        self.assertEqual(result.symbol, "TEST")
        self.assertEqual(result.rows, len(tested))
        self.assertIn(result.radar_signal, {"LONG", "SHORT", "WAIT"})

    def test_declining_market_is_supported(self) -> None:
        _, result = analyze_market("TEST", self.make_data(-0.15))
        self.assertLess(result.latest_close, 100.0)


if __name__ == "__main__":
    unittest.main()
