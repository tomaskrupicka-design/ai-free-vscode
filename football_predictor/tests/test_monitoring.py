import unittest
import pandas as pd
from evaluation.monitoring import calibration, rolling_error, monthly_error


def sample_rows():
    return pd.DataFrame([
        {"date": "2026-01-01", "home_team": "A", "away_team": "B",
         "model_version": model, "actual": actual,
         "p_home": ph, "p_draw": .20, "p_away": 0.80 - ph,
         "brier": error, "log_loss": error + .25,
         "prediction_kind": "retrospective_backtest"}
        for model, actual, ph, error in [
            ("old", "home", .60, .4), ("new", "home", .70, .3),
            ("old", "away", .40, .8), ("new", "away", .20, .6)]
    ])


class MonitoringTests(unittest.TestCase):
    def test_rolling_is_separate_by_model(self):
        result = rolling_error(sample_rows(), window=2)
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(float(result.loc[result.model_version == "old", "rolling_brier"].iloc[0]), .6)
        self.assertAlmostEqual(float(result.loc[result.model_version == "new", "rolling_brier"].iloc[0]), .45)
        self.assertTrue((result.matches_seen == 2).all())

    def test_calibration_probability_and_frequency(self):
        result = calibration(sample_rows(), outcome="home", bins=5)
        self.assertEqual(int(result.n.sum()), 4)
        self.assertTrue(result.predicted_probability.between(0, 1).all())
        self.assertTrue(result.observed_frequency.between(0, 1).all())

    def test_monthly_aggregation(self):
        result = monthly_error(sample_rows())
        self.assertEqual(result.matches.sum(), 4)
        self.assertEqual(len(result), 2)

    def test_rejects_nonhistorical_or_invalid_probabilities(self):
        rows = sample_rows()
        rows.loc[0, "prediction_kind"] = "pre_match"
        with self.assertRaises(ValueError):
            rolling_error(rows)
        rows = sample_rows()
        rows.loc[0, "p_home"] = 1.4
        with self.assertRaises(ValueError):
            calibration(rows)

    def test_empty_with_columns(self):
        result = rolling_error(sample_rows().iloc[:0])
        self.assertTrue(result.empty)


if __name__ == "__main__":
    unittest.main()
