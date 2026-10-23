import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pandas as pd
from database.supabase_sync import sync
from evaluation.backtest import backtest


class SyncTests(unittest.TestCase):
    def test_repeat_sync_and_retry_after_partial_failure_keep_logical_row_counts(self):
        """Exercise request construction with a stateful in-memory PostgREST transport.

        This is not an integration test of the deployed database's constraints.
        """
        matches = pd.DataFrame([
            dict(date="2026-01-01", home_team="A", away_team="B", home_goals=1,
                 away_goals=0, source_match_key="fixture:1", source="fixture", season="2025-26"),
            dict(date="2026-01-02", home_team="C", away_team="D", home_goals=0,
                 away_goals=0, source_match_key="fixture:2", source="fixture", season="2025-26"),
        ])
        predictions = pd.DataFrame(backtest(matches))
        tables = {"matches": {}, "predictions": {}}
        fail = [True]
        def transport(request, timeout):
            parsed = urlparse(request.full_url)
            table = parsed.path.rsplit("/", 1)[-1]
            conflict = parse_qs(parsed.query)["on_conflict"][0]
            self.assertEqual(conflict, "source_match_key" if table == "matches"
                             else "match_id,model_version,prediction_kind")
            self.assertIn("resolution=merge-duplicates", request.get_header("Prefer"))
            self.assertGreater(timeout, 0)
            if table == "predictions" and len(tables["predictions"]) == 1 and fail[0]:
                fail[0] = False
                raise TimeoutError("simulated response lost after one prediction batch")
            result = []
            for row in json.loads(request.data):
                key = tuple(row[column] for column in conflict.split(","))
                previous = tables[table].get(key)
                row["id"] = previous["id"] if previous else len(tables[table]) + 1
                tables[table][key] = row
                result.append(row)
            return io.BytesIO(json.dumps(result).encode())
        with patch.dict(os.environ, {"SUPABASE_URL": "https://fixture.invalid",
                                    "SUPABASE_SERVICE_ROLE_KEY": "fixture-only"}), \
                patch("database.supabase_sync.urlopen", side_effect=transport):
            with self.assertRaises(TimeoutError):
                sync(predictions, matches, batch_size=1)
            for _ in range(2):
                self.assertEqual(sync(predictions, matches, batch_size=1), (2, 2))
            changed = predictions.copy()
            changed.loc[0, "brier"] = 0.123
            sync(changed, matches, batch_size=1)
        self.assertEqual(len(tables["matches"]), 2)
        self.assertEqual(len(tables["predictions"]), 2)
        self.assertEqual(next(iter(tables["predictions"].values()))["brier"], 0.123)
