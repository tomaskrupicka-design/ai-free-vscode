from pathlib import Path
import pandas as pd

def save_predictions(rows,path):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(rows)
    df.to_csv(path,index=False)
    return df
