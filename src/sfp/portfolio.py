import pandas as pd

from sfp.backtest import run_market
from sfp.signals import trend_forecast


# Each day, split risk equally across sectors, then equally across markets in a sector that have started trading
def market_weights(forecasts, instruments):
    has_forecast = forecasts.ffill().notna().astype(float)
    sectors = pd.Series({code: instruments[code].sector for code in forecasts.columns})

    markets_in_sector = has_forecast.T.groupby(sectors).transform("sum").T
    live_sectors = (has_forecast.T.groupby(sectors).sum() > 0).sum()

    weights = has_forecast / markets_in_sector
    return weights.div(live_sectors, axis=0).fillna(0)


# Run every market with its share of the capital and return daily profit per market
def run_portfolio(markets, instruments, capital, settings, signal=trend_forecast, use_buffer=True):
    forecasts = pd.DataFrame({code: signal(m["adjusted"]) for code, m in markets.items()})
    weights = market_weights(forecasts, instruments) * settings["diversification_multiplier"]

    results = {}
    for code, market in markets.items():
        weight = weights[code].reindex(market.index)
        results[code] = run_market(market, instruments[code], capital, settings,
                                   weight, use_buffer, signal)
    return results


# Add up one column (like "pnl") across all markets into a single daily series
def total(results, column):
    return pd.DataFrame({code: r[column] for code, r in results.items()}).fillna(0).sum(axis=1)
