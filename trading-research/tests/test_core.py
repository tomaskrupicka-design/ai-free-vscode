from __future__ import annotations

import unittest

import pandas as pd

from src.backtest import run_backtest
from src.regime import add_market_regime
from src.signals import add_trend_signal


class TradingResearchCoreTests(unittest.TestCase):
    def make_data(self, rows: int = 240) -> pd.DataFrame:
        index = pd.date_range("2025-01-01", periods=rows, freq="D")
        close = pd.Series(
            [100.0 + i * 0.25 + ((i % 11) - 5) * 0.05 for i in range(rows)],
            index=index,
        )
        return pd.DataFrame({"close": close})

    def test_signal_values_are_bounded(self) -> None:
        data = add_trend_signal(self.make_data(), fast_window=10, slow_window=40)
        self.assertTrue(set(data["signal"].unique()).issubset({-1, 0, 1}))

    def test_regime_columns_exist(self) -> None:
        data = add_market_regime(
            self.make_data(), fast_window=10, slow_window=40, vol_window=10
        )
        self.assertIn("trend_regime", data.columns)
        self.assertIn("vol_regime", data.columns)

    def test_backtest_uses_previous_bar_signal(self) -> None:
        data = self.make_data()
        data["signal"] = 1
        tested, result = run_backtest(data)
        self.assertEqual(float(tested["position"].iloc[0]), 0.0)
        self.assertGreaterEqual(result.position_changes, 1)
        self.assertEqual(len(result.equity_curve), len(data))


if __name__ == "__main__":
    unittest.main()
