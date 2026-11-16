import numpy as np
import pandas as pd
import pytest

from sfp.config import Instrument
from sfp.portfolio import market_weights, run_portfolio, total

INSTRUMENTS = {
    "A": Instrument("A", "A", "equity", 10, "USD", 1.0, 0.1),
    "B": Instrument("B", "B", "equity", 10, "USD", 1.0, 0.1),
    "C": Instrument("C", "C", "bond", 10, "USD", 1.0, 0.1),
}
DATES = pd.bdate_range("2000-01-01", periods=3)


# Two sectors: each gets half; the two equity markets split their half
def test_equal_weights_by_sector():
    forecasts = pd.DataFrame({"A": [1.0] * 3, "B": [1.0] * 3, "C": [1.0] * 3}, index=DATES)
    weights = market_weights(forecasts, INSTRUMENTS)
    assert weights.iloc[0].tolist() == [0.25, 0.25, 0.5]


# Before market B has data, market A gets the whole equity half
def test_missing_market_gives_its_share_to_its_sector():
    forecasts = pd.DataFrame({"A": [1.0] * 3, "B": [np.nan, 1, 1], "C": [1.0] * 3}, index=DATES)
    weights = market_weights(forecasts, INSTRUMENTS)
    assert weights.iloc[0].tolist() == [0.5, 0, 0.5]


# Before any bond has data, equities get all the risk
def test_missing_sector_gives_its_share_to_other_sectors():
    forecasts = pd.DataFrame({"A": [1.0] * 3, "B": [1.0] * 3, "C": [np.nan, 1, 1]}, index=DATES)
    weights = market_weights(forecasts, INSTRUMENTS)
    assert weights.iloc[0].tolist() == [0.5, 0.5, 0]


# A market closed for a holiday keeps its weight, so the others don't jump for one day
def test_holiday_does_not_change_weights():
    forecasts = pd.DataFrame({"A": [1.0, 1, 1], "B": [1.0, np.nan, 1], "C": [1.0] * 3}, index=DATES)
    weights = market_weights(forecasts, INSTRUMENTS)
    assert weights.iloc[1].tolist() == [0.25, 0.25, 0.5]


# Weights always add up to 1 on days with any data
def test_weights_add_up_to_one():
    forecasts = pd.DataFrame({"A": [1.0, 1, 1], "B": [np.nan, 1, 1], "C": [np.nan, np.nan, 1]},
                             index=DATES)
    assert market_weights(forecasts, INSTRUMENTS).sum(axis=1).tolist() == pytest.approx([1, 1, 1])


SETTINGS = {"target_annual_vol": 0.2, "buffer": 0.1, "diversification_multiplier": 2.0}


# Three fake markets; market C skips every 7th day like a market with different holidays
def fake_markets():
    rng = np.random.default_rng(0)
    dates = pd.bdate_range("2000-01-01", periods=1500)
    markets = {}
    for code in INSTRUMENTS:
        prices = 100 + rng.normal(0, 1, 1500).cumsum()
        markets[code] = pd.DataFrame({"adjusted": prices, "fx": 1.0, "contract": 1}, index=dates)
    markets["C"] = markets["C"].iloc[::7]
    return markets


# Portfolio profit is the sum of each market's profit
def test_portfolio_total_is_sum_of_markets():
    results = run_portfolio(fake_markets(), INSTRUMENTS, 10_000_000, SETTINGS)
    by_hand = pd.concat([r["pnl"] for r in results.values()], axis=1).fillna(0).sum(axis=1)
    pd.testing.assert_series_equal(total(results, "pnl"), by_hand)


# Each market's results only contain days that market actually traded
def test_markets_keep_their_own_trading_days():
    markets = fake_markets()
    results = run_portfolio(markets, INSTRUMENTS, 10_000_000, SETTINGS)
    for code in markets:
        assert results[code].index.equals(markets[code].index)
