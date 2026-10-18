"""Date-decayed team attack/defence strengths from past full-time goals.

These are estimated goals, NOT observed xG measurements.
All updates must run AFTER predictions for the entire fixture date.
"""
from datetime import date, datetime


class TeamGoalModel:
    def __init__(self, home_prior=1.45, away_prior=1.15,
                 team_prior_games=12.0, league_prior_games=60.0,
                 half_life_days=365.0):
        self.home_prior = float(home_prior)
        self.away_prior = float(away_prior)
        self.team_prior_games = float(team_prior_games)
        self.league_prior_games = float(league_prior_games)
        self.half_life_days = float(half_life_days)
        self.teams = {}
        self.league = {"home_goals": 0.0, "away_goals": 0.0,
                       "games": 0.0, "as_of": None}

    @staticmethod
    def as_date(value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value)[:10])

    def _decay(self, stats, at_date):
        at_date = self.as_date(at_date)
        previous = stats.get("as_of")
        if previous is None:
            stats["as_of"] = at_date
            return
        days = (at_date - previous).days
        if days < 0:
            raise ValueError("Matches must be processed chronologically")
        factor = 2 ** (-days / self.half_life_days)
        for field in stats:
            if field != "as_of":
                stats[field] *= factor
        stats["as_of"] = at_date

    def _get(self, team, at_date):
        if team not in self.teams:
            self.teams[team] = {"attack": 0.0, "defence": 0.0,
                                "games": 0.0, "as_of": None}
        self._decay(self.teams[team], at_date)
        return self.teams[team]

    def predict(self, home, away, at_date):
        self._decay(self.league, at_date)
        h, a = self._get(home, at_date), self._get(away, at_date)
        games = self.league["games"]
        base_home = (self.league_prior_games * self.home_prior +
                     self.league["home_goals"]) / (self.league_prior_games + games)
        base_away = (self.league_prior_games * self.away_prior +
                     self.league["away_goals"]) / (self.league_prior_games + games)

        def factor(stats, field):
            return (self.team_prior_games + stats[field]) / (
                self.team_prior_games + stats["games"])

        home_goals = base_home * factor(h, "attack") * factor(a, "defence")
        away_goals = base_away * factor(a, "attack") * factor(h, "defence")
        return max(0.2, min(4.5, home_goals)), max(0.2, min(4.5, away_goals))

    def update(self, home, away, home_goals, away_goals, at_date):
        h, a = self._get(home, at_date), self._get(away, at_date)
        h["attack"] += home_goals / self.home_prior
        h["defence"] += away_goals / self.away_prior
        a["attack"] += away_goals / self.away_prior
        a["defence"] += home_goals / self.home_prior
        h["games"] += 1.0
        a["games"] += 1.0
        self._decay(self.league, at_date)
        self.league["home_goals"] += home_goals
        self.league["away_goals"] += away_goals
        self.league["games"] += 1.0
