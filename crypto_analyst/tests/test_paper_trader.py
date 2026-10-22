import unittest
import pandas as pd
from simulation.paper_trader import SimulationSettings, simulate_ema_history
from data.binance_public import closed_candles


def demo_candles(n=150):
    # Purpose-built example dataset, NOT observed financial history.
    prices = [100 + (i * 0.3 if i < n // 2 else (n - i) * 0.35) for i in range(n)]
    return pd.DataFrame({
        "open_time": pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC"),
        "open": prices,
        "close": prices,
        "high": [p + 1 for p in prices],
        "low": [p - 1 for p in prices],
    })


class HistoricalSimulationTests(unittest.TestCase):
    def test_requires_enough_history(self):
        with self.assertRaises(ValueError):
            simulate_ema_history(demo_candles(30))

    def test_no_leverage_or_negative_cash(self):
        result = simulate_ema_history(demo_candles())
        curve = result["equity_curve"]
        self.assertTrue((curve["cash"] >= -0.00001).all())
        self.assertTrue((curve["units"] >= 0).all())
        self.assertTrue((curve["simulated_portfolio"] > 0).all())
        self.assertGreaterEqual(result["summary"]["hypothetical_entries"], 1)

    def test_present_candle_close_cannot_affect_present_open_event(self):
        base = demo_candles()
        altered = base.copy()
        altered.loc[len(altered) - 1, "close"] = 1.0  # Different same-bar close.
        a = simulate_ema_history(base)["events"]
        b = simulate_ema_history(altered)["events"]
        self.assertEqual(a.to_dict("records"), b.to_dict("records"))

    def test_costs_are_not_ignored(self):
        candles = demo_candles()
        zero = simulate_ema_history(candles, SimulationSettings(fee_bps=0, slippage_bps=0))
        cost = simulate_ema_history(candles, SimulationSettings(fee_bps=10, slippage_bps=5))
        self.assertLessEqual(cost["summary"]["ending_demo_value"],
                             zero["summary"]["ending_demo_value"])
        self.assertGreater(cost["summary"]["fees_demo_units"], 0)

    def test_exclude_incomplete_candle(self):
        df = demo_candles(3)
        df["close_time"] = (df["open_time"].astype("int64") // 1_000_000) + 3_599_999
        filtered = closed_candles(df, as_of="2026-01-01T02:30:00Z")
        self.assertEqual(len(filtered), 2)


if __name__ == "__main__":
    unittest.main()
