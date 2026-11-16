import pandas as pd

from sfp.costs import daily_costs
from sfp.data import roll_dates
from sfp.pnl import daily_pnl
from sfp.signals import trend_forecast
from sfp.sizing import buffered_position, ideal_position, rounded_position, yearly_dollar_risk


# Run the system on one market and return a daily table of forecast, position, profit and costs
def run_market(market, instrument, capital, settings, weight=1.0, use_buffer=True,
               signal=trend_forecast):
    prices = market["adjusted"]
    forecast = signal(prices)
    risk = yearly_dollar_risk(prices, instrument, market["fx"])
    target_vol = settings["target_annual_vol"]
    ideal = ideal_position(forecast, risk, capital, target_vol, weight)

    if use_buffer:
        normal_position = ideal_position(10, risk, capital, target_vol, weight)
        position = buffered_position(ideal, settings["buffer"] * normal_position)
    else:
        position = rounded_position(ideal).fillna(0)

    gross = daily_pnl(position, prices, instrument, market["fx"]).fillna(0)
    costs = daily_costs(position, roll_dates(market), instrument, market["fx"])
    return pd.DataFrame({
        "forecast": forecast,
        "position": position,
        "gross_pnl": gross,
        "costs": costs,
        "pnl": gross - costs,
    })
