import datetime as dt
import unittest
from data.openfootball import parse_matches

class OpenFootballTests(unittest.TestCase):
    def test_skips_upcoming_and_unsupported_score(self):
        today=dt.date(2026,10,18)
        doc={"matches":[
            {"date":"2026-10-10","team1":"A","team2":"B","score":{"ft":[2,1]}},
            {"date":"2026-10-18","team1":"B","team2":"A","score":{"ft":[1,0]}},
            {"date":"2026-10-12","team1":"A","team2":"C"},
            {"date":"2026-10-11","team1":"A","team2":"B","score":[0,0]}
        ]}
        rows=parse_matches(doc, "2026-27", today=today)
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]["home_goals"],2)
        self.assertEqual(rows[1]["away_goals"],0)

if __name__ == "__main__":
    unittest.main()
