import sys

import matplotlib.pyplot as plt

from sfp.config import ROOT, load_instruments, load_settings
from sfp.data import load_market
from sfp.signals import trend_forecast
from sfp.sizing import ideal_position, rounded_position, yearly_dollar_risk

code = sys.argv[1] if len(sys.argv) > 1 else "CRUDE_W"
start = "2000-01-01"
settings = load_settings()
instrument = load_instruments()[code]

market = load_market(instrument)
forecast = trend_forecast(market["adjusted"])
risk = yearly_dollar_risk(market["adjusted"], instrument, market["fx"])
forecast = forecast[start:]
risk = risk[start:]

capitals = settings["capital_levels"]
fig, axes = plt.subplots(len(capitals) + 1, 1, sharex=True, figsize=(12, 9))

axes[0].plot(forecast, color="black", linewidth=0.7)
axes[0].axhline(0, color="grey", linewidth=0.5)
axes[0].set_title(f"{code} forecast")

for ax, capital in zip(axes[1:], capitals):
    ideal = ideal_position(forecast, risk, capital, settings["target_annual_vol"])
    rounded = rounded_position(ideal)

    ax.plot(ideal, color="tab:blue", linewidth=0.7, label="ideal")
    ax.plot(rounded, color="tab:orange", linewidth=1, label="rounded (what we hold)")
    ax.axhline(0, color="grey", linewidth=0.5)
    ax.set_title(f"Contracts held with ${capital:,}")
    ax.legend(loc="upper left")

    print(f"${capital:,} with all the money in {code}:")
    print(f"  average size: {ideal.abs().mean():.2f} contracts")
    print(f"  days holding nothing: {(rounded == 0).mean():.0%}")
    print(f"  average rounding error: {(rounded - ideal).abs().mean():.2f} contracts")

    share = ideal / 22
    print(f"  if it only got 1/22 of the money: average {share.abs().mean():.2f} contracts, "
          f"holding nothing {(rounded_position(share) == 0).mean():.0%} of days")

output = ROOT / "output" / f"position_{code}.png"
output.parent.mkdir(exist_ok=True)
fig.tight_layout()
fig.savefig(output, dpi=110)
print(f"Saved chart to {output}")
