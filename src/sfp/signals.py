import pandas as pd

SPEEDS = [(8, 32), (16, 64), (32, 128), (64, 256)]


# How much the price typically moves in one day, in price points
def daily_volatility(prices, span=35):
    return prices.diff().ewm(span=span, min_periods=10).std()


# Fast moving average minus slow moving average, divided by volatility so every market is comparable
def ewmac(prices, fast, slow):
    fast_average = prices.ewm(span=fast, min_periods=fast).mean()
    slow_average = prices.ewm(span=slow, min_periods=slow).mean()
    return (fast_average - slow_average) / daily_volatility(prices)


# Rescale a signal so its average size is 10 (using only past data) and cap it at +/-20
def scale_forecast(raw, target=10, cap=20):
    average_size = raw.abs().expanding(min_periods=250).mean()
    return (raw * target / average_size).clip(-cap, cap)


# A forecast that always says "normal-sized buy", used as a comparison with no trend signal
def always_long(prices):
    return pd.Series(10.0, index=prices.index)


# Combine moving-average signals of several speeds into one forecast between -20 and +20
def trend_forecast(prices, speeds=SPEEDS):
    forecasts = [scale_forecast(ewmac(prices, fast, slow)) for fast, slow in speeds]
    combined = pd.concat(forecasts, axis=1).mean(axis=1)
    return scale_forecast(combined)
