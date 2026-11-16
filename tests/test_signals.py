import numpy as np
import pandas as pd

from sfp.signals import ewmac, scale_forecast, trend_forecast


# Make a random daily price series with an optional upward or downward drift
def random_prices(drift=0.0, days=2000, seed=0):
    rng = np.random.default_rng(seed)
    moves = rng.normal(drift, 1, days)
    dates = pd.bdate_range("2000-01-01", periods=days)
    return pd.Series(100 + moves.cumsum(), index=dates)


# A price that keeps rising should end with a buy forecast
def test_rising_price_gives_buy():
    assert trend_forecast(random_prices(drift=0.3)).iloc[-1] > 0


# A price that keeps falling should end with a sell forecast
def test_falling_price_gives_sell():
    assert trend_forecast(random_prices(drift=-0.3)).iloc[-1] < 0


# The forecast must never go beyond +/-20
def test_forecast_is_capped():
    forecast = trend_forecast(random_prices(drift=1.0)).dropna()
    assert forecast.between(-20, 20).all()


# After scaling, the average size of the forecast should be close to 10
def test_average_forecast_size_is_about_10():
    forecast = scale_forecast(ewmac(random_prices(), 16, 64)).dropna()
    assert 8 < forecast.abs().mean() < 12


# Changing future prices must not change past forecasts (no look-ahead)
def test_forecast_only_uses_past_prices():
    prices = random_prices()
    changed = prices.copy()
    changed.iloc[1500:] += 500

    before = trend_forecast(prices).iloc[:1500]
    after = trend_forecast(changed).iloc[:1500]
    pd.testing.assert_series_equal(before, after)
