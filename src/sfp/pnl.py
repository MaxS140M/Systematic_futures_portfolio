# Daily profit in dollars: the position held since yesterday times today's price change
def daily_pnl(position, prices, instrument, fx):
    return position.shift(1) * prices.diff() * instrument.multiplier * fx
