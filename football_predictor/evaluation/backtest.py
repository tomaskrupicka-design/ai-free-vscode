from models.elo import EloModel
from models.poisson import result_probabilities
from evaluation.metrics import brier,log_loss

def outcome(hg,ag): return "home" if hg>ag else "draw" if hg==ag else "away"

def backtest(matches):
    elo=EloModel(); rows=[]
    for _,m in matches.sort_values("date").iterrows():
        strength=elo.expected_home(m.home_team,m.away_team)
        hxg=max(.25,.85+1.10*strength); axg=max(.20,.70+1.10*(1-strength))
        p=result_probabilities(hxg,axg)
        actual=outcome(int(m.home_goals),int(m.away_goals))
        rows.append({"date":str(m.date.date()),"home_team":m.home_team,"away_team":m.away_team,
          "home_xg":round(hxg,3),"away_xg":round(axg,3),"p_home":p["home"],"p_draw":p["draw"],
          "p_away":p["away"],"actual":actual,"brier":brier(p,actual),"log_loss":log_loss(p,actual)})
        result=1 if m.home_goals>m.away_goals else 0 if m.home_goals==m.away_goals else -1
        elo.update(m.home_team,m.away_team,result)
    return rows
