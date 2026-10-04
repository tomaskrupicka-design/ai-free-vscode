from __future__ import annotations

import unittest

from src.yahoo_data import YAHOO_FUTURES, download_history


class YahooDataTests(unittest.TestCase):
    def test_expected_research_symbols_exist(self) -> None:
        self.assertEqual(
            YAHOO_FUTURES,
            {
                "ES": "ES=F",
                "NQ": "NQ=F",
                "GC": "GC=F",
                "CL": "CL=F",
            },
        )

    def test_unknown_symbol_is_rejected_before_network_call(self) -> None:
        with self.assertRaises(ValueError):
            download_history("UNKNOWN")


if __name__ == "__main__":
    unittest.main()
