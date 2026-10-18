import unittest
import pandas as pd
from evaluation.compare import benchmark, metrics_table
from models.team_goals import TeamGoalModel

class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.rows = pd.DataFrame([
            {"date": "2026-01-01", "home_team": "A", "away_team": "B",
             "home_goals": 4, "away_goals": 0},
            {"date": "2026-01-01", "home_team": "C", "away_team": "A",
             "home_goals": 0, "away_goals": 2},
            {"date": "2026-01-08", "home_team": "B", "away_team": "A",
             "home_goals": 1, "away_goals": 1},
            {"date": "2026-02-01", "home_team": "A", "away_team": "C",
             "home_goals": 2, "away_goals": 0},
        ])

    def test_three_models_and_metrics(self):
        rows = benchmark(self.rows)
        self.assertEqual(len(rows), 12)
        self.assertEqual(len(metrics_table(rows)), 3)
        for row in rows:
            self.assertAlmostEqual(row["p_home"] + row["p_draw"] +
                                   row["p_away"], 1, places=8)
            self.assertEqual(row["prediction_kind"], "retrospective_backtest")

    def test_same_day_outcomes_not_visible(self):
        first = benchmark(self.rows)
        second = benchmark(self.rows.iloc[[1, 0, 2, 3]])
        def sig(rows):
            return {(r["date"], r["home_team"], r["away_team"], r["model_version"]):
                    tuple(round(r[k], 10) for k in ("p_home", "p_draw", "p_away"))
                    for r in rows}
        self.assertEqual(sig(first), sig(second))

    def test_attack_defence_update(self):
        model = TeamGoalModel()
        before = model.predict("A", "B", "2026-01-01")
        for i in range(10):
            model.update("A", "B", 4, 0, f"2026-01-{i+1:02d}")
        after = model.predict("A", "B", "2026-01-20")
        self.assertGreater(after[0], before[0])
        self.assertLess(after[1], before[1])

if __name__ == "__main__":
    unittest.main()
