import sys

import matplotlib.pyplot as plt

from sfp.config import ROOT, load_instruments
from sfp.data import load_market
from sfp.signals import trend_forecast

code = sys.argv[1] if len(sys.argv) > 1 else "CRUDE_W"
start = "2000-01-01"

prices = load_market(load_instruments()[code])["adjusted"]
forecast = trend_forecast(prices)
prices = prices[start:]
forecast = forecast[start:]

fig, (top, bottom) = plt.subplots(2, 1, sharex=True, figsize=(12, 7))
top.plot(prices, color="black", linewidth=0.8)
top.set_title(f"{code} price (adjusted)")

bottom.fill_between(forecast.index, forecast, 0, where=forecast > 0, color="tab:green", label="buy")
bottom.fill_between(forecast.index, forecast, 0, where=forecast < 0, color="tab:red", label="sell")
bottom.set_ylim(-21, 21)
bottom.set_title("Trend forecast (+20 strong buy, -20 strong sell)")
bottom.legend(loc="upper left")

output = ROOT / "output" / f"signal_{code}.png"
output.parent.mkdir(exist_ok=True)
fig.tight_layout()
fig.savefig(output, dpi=110)

print(f"Saved chart to {output}")
print(f"Buy {(forecast > 0).mean():.0%} of days, sell {(forecast < 0).mean():.0%} of days")
print(f"Average forecast size: {forecast.abs().mean():.1f}")
print(f"Forecast on {forecast.index[-1].date()}: {forecast.iloc[-1]:.1f}")
