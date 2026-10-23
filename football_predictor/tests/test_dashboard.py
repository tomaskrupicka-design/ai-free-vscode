from pathlib import Path
import shutil
import tempfile
import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest
from evaluation.backtest import backtest
from evaluation.compare import benchmark
from runtime import write_status

ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copy(ROOT / "dashboard_app.py", self.root)
        self.output = self.root / "output"
        self.output.mkdir()
        matches = pd.DataFrame([
            dict(date="2026-01-01", home_team="A", away_team="B", home_goals=1, away_goals=0),
            dict(date="2026-01-02", home_team="C", away_team="D", home_goals=0, away_goals=0),
        ])
        pd.DataFrame(backtest(matches)).to_csv(self.output / "predictions.csv", index=False)
        pd.DataFrame(benchmark(matches)).to_csv(self.output / "comparison.csv", index=False)

    def app(self):
        return AppTest.from_file(str(self.root / "dashboard_app.py"), default_timeout=15).run()

    def demo(self):
        return self.app().radio[0].set_value("Ukázková data").run()

    def test_filters_model_details_and_csv_export(self):
        app = self.demo()
        self.assertFalse(app.exception)
        app.selectbox[0].set_value("A")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "1")
        app.selectbox[2].set_value("team-goals-v0.3").run()
        self.assertFalse(app.exception)
        details = app.dataframe[1].value
        self.assertEqual(list(details.home_team), ["A"])
        self.assertEqual(list(details.model_version), ["team-goals-v0.3"])
        self.assertEqual(len(app.get("download_button")), 1)

    def test_missing_real_data_and_failed_demo_status(self):
        app = self.app()
        self.assertFalse(app.exception)
        self.assertTrue(any("Nejdřív spusť" in item.value for item in app.warning))
        write_status(self.output / "run_status_demo.json", {
            "state": "timeout", "last_success_at": "2026-10-20T08:00:00+00:00",
            "last_success_files": ["predictions.csv"],
        })
        app = self.demo()
        self.assertFalse(app.exception)
        self.assertTrue(any("Poslední pokus selhal" in item.value for item in app.warning))
        self.assertTrue(any("nepochází" in item.value for item in app.warning))
        self.assertTrue(any("20. 10. 2026 10:00:00" in item.value for item in app.caption))

    def test_original_model_without_comparison(self):
        (self.output / "comparison.csv").unlink()
        app = self.demo()
        app.selectbox[0].set_value("C")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "1")
