import pandas as pd

from sfp.config import DATA_DIR


# Read a price CSV and keep only the last price of each day
def read_daily_csv(path):
    df = pd.read_csv(path, parse_dates=["DATETIME"])
    df["date"] = df["DATETIME"].dt.normalize()
    return df.groupby("date").last().drop(columns="DATETIME")


# Load one market: adjusted price, current contract price and name, and the FX rate to USD
def load_market(instrument, data_dir=DATA_DIR):
    adjusted = read_daily_csv(data_dir / "adjusted" / f"{instrument.code}.csv")
    multiple = read_daily_csv(data_dir / "multiple" / f"{instrument.code}.csv")

    df = pd.DataFrame({
        "adjusted": adjusted["price"],
        "price": multiple["PRICE"],
        "contract": multiple["PRICE_CONTRACT"],
    }).dropna()
    df["contract"] = df["contract"].astype(int)

    if instrument.currency == "USD":
        df["fx"] = 1.0
    else:
        fx = read_daily_csv(data_dir / "fx" / f"{instrument.currency}USD.csv")["PRICE"]
        df["fx"] = fx.reindex(df.index, method="ffill")

    return df.dropna()


# Return the dates where we switched from one contract to the next
def roll_dates(df):
    changed = df["contract"] != df["contract"].shift()
    return df.index[changed][1:]
