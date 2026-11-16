import numpy as np
import pandas as pd
import pytest

from sfp.backtest import run_market
from sfp.config import Instrument
from sfp.pnl import daily_pnl
from sfp.stats import annual_return, max_drawdown

INSTRUMENT = Instrument("TEST", "Test", "equity", 10, "USD", 1.0, 0.1)
SETTINGS = {"target_annual_vol": 0.2, "buffer": 0.1}


def series(values):
    return pd.Series(values, index=pd.bdate_range("2020-01-01", periods=len(values)), dtype=float)


# Holding 1 contract while the price rises by 2 with multiplier 10 earns $20
def test_long_position_earns_price_rise():
    pnl = daily_pnl(series([1, 1]), series([100, 102]), INSTRUMENT, 1.0)
    assert pnl.iloc[1] == 20


# Holding a short position earns money when the price falls
def test_short_position_earns_price_fall():
    pnl = daily_pnl(series([-1, -1]), series([100, 98]), INSTRUMENT, 1.0)
    assert pnl.iloc[1] == 20


# A position bought today must not earn today's move, only tomorrow's
def test_new_position_does_not_earn_same_day_move():
    pnl = daily_pnl(series([0, 1, 1]), series([100, 110, 111]), INSTRUMENT, 1.0)
    assert pnl.tolist()[1:] == [0, 10]


# Profit in a foreign currency is converted to dollars
def test_profit_converted_with_fx():
    pnl = daily_pnl(series([1, 1]), series([100, 102]), INSTRUMENT, 1.5)
    assert pnl.iloc[1] == 30


# Make a fake market from random prices
def fake_market(days=2000, seed=0):
    rng = np.random.default_rng(seed)
    prices = series(100 + rng.normal(0, 1, days).cumsum())
    contracts = [202000 + i // 60 for i in range(days)]
    return pd.DataFrame({"adjusted": prices, "fx": 1.0, "contract": contracts})


# Changing future prices must not change past profits (no look-ahead anywhere in the chain)
def test_backtest_only_uses_past_prices():
    market = fake_market()
    changed = market.copy()
    changed.iloc[1500:, 0] += 500

    before = run_market(market, INSTRUMENT, 1_000_000, SETTINGS)["pnl"].iloc[:1500]
    after = run_market(changed, INSTRUMENT, 1_000_000, SETTINGS)["pnl"].iloc[:1500]
    pd.testing.assert_series_equal(before, after)


# Earning 0.1% every day is about 25.6% a year
def test_annual_return():
    assert annual_return(series([0.001] * 10)) == pytest.approx(0.256)


# Up 10%, down 5%, down 5%, up 20%: the biggest fall from a high is 10%
def test_max_drawdown():
    assert max_drawdown(series([0.1, -0.05, -0.05, 0.2])) == pytest.approx(-0.1)
