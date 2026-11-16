import numpy as np
import pandas as pd

from sfp.checks import bootstrap_sharpe, yearly_risk


def random_returns(mean, days=2560, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2000-01-01", periods=days)
    return pd.Series(rng.normal(mean, 0.01, days), index=dates)


# A strategy with a real edge should have its whole likely range above zero
def test_bootstrap_range_above_zero_for_real_edge():
    low, middle, high = bootstrap_sharpe(random_returns(0.002), runs=200)
    assert 0 < low < middle < high


# A strategy with no edge should have a range that includes zero
def test_bootstrap_range_includes_zero_for_no_edge():
    low, _, high = bootstrap_sharpe(random_returns(0.0), runs=200)
    assert low < 0 < high


# Daily moves of 1% are about 16% a year
def test_yearly_risk():
    risk = yearly_risk(random_returns(0.0))
    assert 0.15 < risk.mean() < 0.17
