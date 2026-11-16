import pandas as pd

from sfp.signals import daily_volatility

DAYS_PER_YEAR = 256


# How many dollars one contract typically gains or loses in a year
def yearly_dollar_risk(prices, instrument, fx):
    return daily_volatility(prices) * instrument.multiplier * fx * DAYS_PER_YEAR ** 0.5


# Ideal number of contracts (can be a fraction) for a forecast and an amount of capital
def ideal_position(forecast, risk_per_contract, capital, target_vol, weight=1.0):
    return (forecast / 10) * capital * target_vol * weight / risk_per_contract


# Round the ideal position to whole contracts, since fractions can't be traded
def rounded_position(ideal):
    return ideal.round()


# Whole contracts, but only trade when the ideal moves more than the buffer away from what we hold
def buffered_position(ideal, buffer_size):
    held = 0
    positions = []
    for want, buffer in zip(ideal, buffer_size):
        if pd.notna(want) and pd.notna(buffer):
            if want > held + buffer:
                held = round(want - buffer)
            elif want < held - buffer:
                held = round(want + buffer)
        positions.append(held)
    return pd.Series(positions, index=ideal.index, dtype=float)
