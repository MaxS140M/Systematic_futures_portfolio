import pandas as pd
import pytest

from sfp.config import Instrument
from sfp.sizing import ideal_position, rounded_position, yearly_dollar_risk


# A price that moves exactly 1 point up or down every day
def zigzag_prices(days=500):
    moves = [1 if i % 2 == 0 else -1 for i in range(days)]
    dates = pd.bdate_range("2000-01-01", periods=days)
    return pd.Series(moves, index=dates).cumsum() + 100.0


# 1 point a day x multiplier 50 x fx 2 x 16 should be about $1,600 a year
def test_yearly_dollar_risk():
    instrument = Instrument("TEST", "Test", "equity", 50, "EUR", 1.0, 0.1)
    risk = yearly_dollar_risk(zigzag_prices(), instrument, fx=2.0)
    assert risk.iloc[-1] == pytest.approx(1600, rel=0.05)


# A forecast of 10 with $100k, 20% target and $20k risk per contract means exactly 1 contract
def test_normal_forecast_gives_expected_position():
    assert ideal_position(10, 20_000, 100_000, 0.2) == pytest.approx(1.0)


# A stronger forecast should mean a bigger position
def test_stronger_forecast_means_more_contracts():
    assert ideal_position(20, 20_000, 100_000, 0.2) == pytest.approx(2.0)


# Twice the capital should mean twice the contracts
def test_double_capital_doubles_position():
    assert ideal_position(10, 20_000, 200_000, 0.2) == pytest.approx(2.0)


# A market twice as risky should get half the contracts
def test_riskier_market_gets_fewer_contracts():
    assert ideal_position(10, 40_000, 100_000, 0.2) == pytest.approx(0.5)


# A sell forecast should give a short (negative) position
def test_sell_forecast_gives_short_position():
    assert ideal_position(-10, 20_000, 100_000, 0.2) == pytest.approx(-1.0)


# Positions get rounded to whole contracts
def test_rounding_to_whole_contracts():
    ideal = pd.Series([0.3, 0.7, -1.6, 2.2])
    assert rounded_position(ideal).tolist() == [0, 1, -2, 2]


# Changing future prices must not change past risk estimates (no look-ahead)
def test_risk_only_uses_past_prices():
    instrument = Instrument("TEST", "Test", "equity", 50, "USD", 1.0, 0.1)
    prices = zigzag_prices()
    changed = prices.copy()
    changed.iloc[300:] *= 3

    before = yearly_dollar_risk(prices, instrument, 1.0).iloc[:300]
    after = yearly_dollar_risk(changed, instrument, 1.0).iloc[:300]
    pd.testing.assert_series_equal(before, after)
