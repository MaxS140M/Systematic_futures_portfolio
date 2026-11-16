import pandas as pd
import pytest

from sfp.signals import always_long
from sfp.stats import drawdowns, monthly_skew, sharpe_ratio, yearly_returns


def series(values, start="2020-01-01"):
    return pd.Series(values, index=pd.bdate_range(start, periods=len(values)), dtype=float)


# Up 10%, down 5%, down 5%, up 20%: the falls from the high are 0, 5, 10, 0
def test_drawdowns():
    assert drawdowns(series([0.1, -0.05, -0.05, 0.2])).tolist() == pytest.approx([0, -0.05, -0.1, 0])


# Returns are added up within each calendar year
def test_yearly_returns():
    returns = pd.Series([0.01, 0.02, 0.03], index=pd.to_datetime(["2020-06-01", "2020-07-01", "2021-01-04"]))
    assert yearly_returns(returns).to_dict() == pytest.approx({2020: 0.03, 2021: 0.03})


# Doubling every return doubles the profit and the risk, so the Sharpe ratio stays the same
def test_sharpe_ignores_leverage():
    returns = series([0.01, -0.005, 0.002, 0.004, -0.001])
    assert sharpe_ratio(returns * 2) == pytest.approx(sharpe_ratio(returns))


# Many small losses and one big win should have positive skew
def test_positive_skew():
    months = [-0.01] * 11 + [0.2]
    returns = pd.Series(months, index=pd.date_range("2020-01-31", periods=12, freq="ME"))
    assert monthly_skew(returns) > 0


# The always-long comparison is a constant buy of 10
def test_always_long():
    assert (always_long(series([1, 2, 3])) == 10).all()
