from dataclasses import replace

import pandas as pd

from sfp.checks import bootstrap_sharpe, yearly_risk
from sfp.config import load_instruments, load_settings
from sfp.data import load_market
from sfp.portfolio import run_portfolio, total
from sfp.signals import trend_forecast
from sfp.stats import summary_table

settings = load_settings()
instruments = load_instruments()
markets = {code: load_market(i) for code, i in instruments.items()}
capital = max(settings["capital_levels"])
test_period = slice(settings["start_date"], settings["holdout_start"])
holdout_period = slice(settings["holdout_start"], None)


# Daily returns of a portfolio run, as a fraction of capital
def returns_of(results):
    return total(results, "pnl") / capital


# Run the portfolio with some settings changed and return its daily returns
def run(signal=trend_forecast, use_buffer=True, chosen=instruments):
    picked = {code: markets[code] for code in chosen}
    return returns_of(run_portfolio(picked, chosen, capital, settings, signal, use_buffer))


main = run()

print("1. Change one thing at a time (2000 to holdout, $1m)\n")
variants = {
    "main system": main,
    "fast signals only (8/32, 16/64)": run(lambda p: trend_forecast(p, [(8, 32), (16, 64)])),
    "slow signals only (32/128, 64/256)": run(lambda p: trend_forecast(p, [(32, 128), (64, 256)])),
    "single signal (16/64)": run(lambda p: trend_forecast(p, [(16, 64)])),
    "no buffer": run(use_buffer=False),
    "costs doubled": run(chosen={c: replace(i, commission=i.commission * 2, spread=i.spread * 2)
                                 for c, i in instruments.items()}),
}
for sector in sorted({i.sector for i in instruments.values()}):
    without = {c: i for c, i in instruments.items() if i.sector != sector}
    variants[f"without {sector}"] = run(chosen=without)

table = summary_table({name: r[test_period] for name, r in variants.items()}).T
print(table[["yearly return", "Sharpe", "worst drawdown"]].to_string(float_format=lambda x: f"{x:.2f}"))

print("\n2. Could the Sharpe ratio be luck?\n")
low, middle, high = bootstrap_sharpe(main[test_period])
print(f"Shuffling months 1,000 times: 90% of Sharpe ratios fall between {low:.2f} and {high:.2f}")

print("\n3. Did we take the risk we aimed for?\n")
risk = yearly_risk(main[test_period])
print(f"Target {settings['target_annual_vol']:.0%}. Actual yearly risk: average {risk.mean():.0%}, "
      f"lowest {risk.min():.0%} ({risk.idxmin()}), highest {risk.max():.0%} ({risk.idxmax()})")

print("\n4. Held-back data, run once\n")
pd.set_option("display.width", 200)
both = summary_table({"2000 to Mar 2021": main[test_period], "Apr 2021 to Mar 2024": main[holdout_period]})
print(both.T.to_string(float_format=lambda x: f"{x:.2f}"))
yearly = main[holdout_period].groupby(main[holdout_period].index.year).sum()
print("\nHeld-back returns by year: " + ", ".join(f"{y}: {r:.1%}" for y, r in yearly.items()))
