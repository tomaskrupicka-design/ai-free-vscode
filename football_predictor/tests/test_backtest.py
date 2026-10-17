import unittest
import pandas as pd
from evaluation.backtest import backtest

class BacktestTests(unittest.TestCase):
    def test_no_same_day_future_information(self):
        one=pd.DataFrame([
            dict(date="2026-01-01",home_team="A",away_team="B",home_goals=4,away_goals=0),
            dict(date="2026-01-01",home_team="B",away_team="A",home_goals=0,away_goals=3),
        ])
        two=one.iloc[::-1].reset_index(drop=True)
        a=backtest(one)
        b=backtest(two)
        def probs(rows):
            return { (r["home_team"],r["away_team"]):tuple(round(r[k],10) for k in ("p_home","p_draw","p_away")) for r in rows }
        self.assertEqual(probs(a),probs(b))
        for row in a:
            self.assertAlmostEqual(row["p_home"]+row["p_draw"]+row["p_away"],1.0,places=8)
            self.assertEqual(row["prediction_kind"],"retrospective_backtest")

if __name__ == "__main__":
    unittest.main()
