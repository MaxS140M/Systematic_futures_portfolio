import pandas as pd

DAYS_PER_YEAR = 256


# Average yearly return as a fraction of capital
def annual_return(returns):
    return returns.mean() * DAYS_PER_YEAR


# Typical yearly up-and-down of returns
def annual_volatility(returns):
    return returns.std() * DAYS_PER_YEAR ** 0.5


# Return per unit of risk: higher is better, above 0.5 is decent for one strategy
def sharpe_ratio(returns):
    return annual_return(returns) / annual_volatility(returns)


# Fall from the previous high on every day, as a fraction of capital
def drawdowns(returns):
    curve = returns.cumsum()
    return curve - curve.cummax()


# Biggest fall from a previous high, as a fraction of capital
def max_drawdown(returns):
    return drawdowns(returns).min()


# Skew of monthly returns: positive means occasional big wins, negative means occasional big losses
def monthly_skew(returns):
    return returns.resample("ME").sum().skew()


# Total return in each calendar year
def yearly_returns(returns):
    yearly = returns.groupby(returns.index.year).sum()
    yearly.index.name = "year"
    return yearly


# All the headline numbers in one dict
def summary(returns):
    return {
        "yearly return": annual_return(returns),
        "yearly risk": annual_volatility(returns),
        "Sharpe": sharpe_ratio(returns),
        "worst drawdown": max_drawdown(returns),
        "monthly skew": monthly_skew(returns),
    }


# Summaries for several return series side by side
def summary_table(named_returns):
    return pd.DataFrame({name: summary(r) for name, r in named_returns.items()})
