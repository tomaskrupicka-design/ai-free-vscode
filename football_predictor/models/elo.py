class EloModel:
    def __init__(self, initial=1500.0, k=20.0, home_advantage=60.0):
        self.initial=initial; self.k=k; self.home_advantage=home_advantage; self.ratings={}
    def rating(self, team): return self.ratings.get(team,self.initial)
    def expected_home(self, home, away):
        return 1/(1+10**((self.rating(away)-(self.rating(home)+self.home_advantage))/400))
    def update(self, home, away, result):
        expected=self.expected_home(home,away)
        score=1.0 if result>0 else 0.5 if result==0 else 0.0
        change=self.k*(score-expected)
        self.ratings[home]=self.rating(home)+change
        self.ratings[away]=self.rating(away)-change
