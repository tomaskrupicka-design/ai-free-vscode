import math

def pmf(k,lam):
    return math.exp(-lam)*lam**k/math.factorial(k)

def result_probabilities(home_xg,away_xg,max_goals=8):
    out={"home":0.0,"draw":0.0,"away":0.0}
    for h in range(max_goals+1):
        for a in range(max_goals+1):
            p=pmf(h,home_xg)*pmf(a,away_xg)
            out["home" if h>a else "draw" if h==a else "away"]+=p
    total=sum(out.values())
    return {k:v/total for k,v in out.items()}
