import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from runtime import job_lock, read_status, run_bounded


class RuntimeTests(unittest.TestCase):
    def test_failed_and_timed_out_jobs_preserve_outputs_and_last_success(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def success(stage):
                return [sys.executable, "-c",
                        "from pathlib import Path; import sys; Path(sys.argv[1]).write_text('valid')",
                        str(stage / "predictions.csv")]
            first = run_bounded(success, root, "status.json", timeout=10)
            self.assertEqual(first["state"], "success")
            for code, expected, error in [
                ("import sys; sys.exit(2)", "failed", subprocess.CalledProcessError),
                ("import time; time.sleep(30)", "timeout", subprocess.TimeoutExpired),
            ]:
                with self.assertRaises(error):
                    run_bounded(lambda stage: [sys.executable, "-c", code], root,
                                "status.json", timeout=0.3)
                status = read_status(root / "status.json")
                self.assertEqual(status["state"], expected)
                self.assertEqual(status["last_success_at"], first["last_success_at"])
                self.assertEqual((root / "predictions.csv").read_text(), "valid")
                self.assertFalse(list(root.glob(".run-*")))

    def test_simultaneous_job_rejected_without_changing_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with job_lock(root / ".pipeline.lock"):
                with self.assertRaises(RuntimeError):
                    run_bounded(lambda stage: [], root, "status.json")
            self.assertFalse((root / "status.json").exists())

    def test_invalid_limits_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            for limit in (0, -1, float("nan"), float("inf")):
                with self.assertRaises(ValueError):
                    run_bounded(lambda stage: [], temp, "status.json", limit)

    def test_corrupt_status_is_not_a_success(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "status.json"
            path.write_text("broken")
            self.assertEqual(read_status(path), {})
