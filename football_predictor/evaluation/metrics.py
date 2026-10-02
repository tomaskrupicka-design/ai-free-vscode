import math

def brier(p,actual):
    y={"home":0.0,"draw":0.0,"away":0.0}; y[actual]=1.0
    return sum((p[k]-y[k])**2 for k in y)

def log_loss(p,actual,eps=1e-15):
    return -math.log(max(p[actual],eps))
