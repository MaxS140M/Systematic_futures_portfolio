import pandas as pd

from sfp.data import load_market, roll_dates


# Summarise one market's data so problems are easy to spot
def check_market(instrument):
    df = load_market(instrument)
    change = df["adjusted"].diff()
    normal_size = change.rolling(60).std().shift(1)
    big_jumps = (change.abs() > 8 * normal_size).sum()

    return {
        "code": instrument.code,
        "start": df.index[0].date(),
        "end": df.index[-1].date(),
        "days": len(df),
        "rolls": len(roll_dates(df)),
        "big_jumps": big_jumps,
        "negative_adjusted": (df["adjusted"] <= 0).any(),
    }


# Build a table with one row of checks per market
def quality_report(instruments):
    rows = [check_market(i) for i in instruments.values()]
    return pd.DataFrame(rows).set_index("code")
