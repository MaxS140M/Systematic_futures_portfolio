import numpy as np
import pandas as pd

from sfp.stats import sharpe_ratio


# Range of Sharpe ratios we could have seen by luck: shuffle whole months many times
def bootstrap_sharpe(returns, runs=1000, seed=0):
    rng = np.random.default_rng(seed)
    months = [m for _, m in returns.groupby([returns.index.year, returns.index.month])]
    sharpes = []
    for _ in range(runs):
        picked = rng.integers(0, len(months), len(months))
        sample = pd.concat([months[i] for i in picked], ignore_index=True)
        sharpes.append(sharpe_ratio(sample))
    return np.percentile(sharpes, [5, 50, 95])


# Actual risk taken in each calendar year
def yearly_risk(returns):
    return returns.groupby(returns.index.year).std() * 16
