import pandas as pd


# Dollar cost of trading one contract: broker commission plus losing half the bid-ask spread
def cost_per_contract(instrument, fx):
    return (instrument.commission + instrument.spread * instrument.multiplier) * fx


# Contracts traded each day: changes in position plus closing and reopening everything on roll days
def contracts_traded(position, roll_days):
    changes = position.diff().abs().fillna(0)
    is_roll_day = pd.Series(position.index.isin(roll_days), index=position.index)
    rolls = 2 * position.shift(1).abs().fillna(0) * is_roll_day
    return changes + rolls


# Dollar cost of all trading each day
def daily_costs(position, roll_days, instrument, fx):
    return contracts_traded(position, roll_days) * cost_per_contract(instrument, fx)
