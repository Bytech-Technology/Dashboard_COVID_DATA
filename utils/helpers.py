import pandas as pd
from pathlib import Path

CSV_PATH = "data/dataset.csv"

def human_format(num):
    try:
        num = float(num)
    except Exception:
        return str(num)
    magnitude = 0
    units = ['', 'K', 'M', 'B', 'T']
    while abs(num) >= 1000 and magnitude < len(units) - 1:
        magnitude += 1
        num /= 1000.0
    if magnitude == 0:
        return f"{int(num):,}"
    return f"{num:.1f}{units[magnitude]}"

def load_data(path=CSV_PATH):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found at {path}")
    df = pd.read_csv(p)
    for col in df.select_dtypes(include=['number']).columns:
        df[col] = df[col].fillna(0)
    return df
