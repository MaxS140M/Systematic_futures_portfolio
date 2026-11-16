import matplotlib.pyplot as plt
import pandas as pd

from sfp.config import ROOT, load_instruments, load_settings
from sfp.data import load_market
from sfp.portfolio import run_portfolio, total
from sfp.signals import always_long
from sfp.stats import drawdowns, summary_table, yearly_returns

settings = load_settings()
instruments = load_instruments()
markets = {code: load_market(i) for code, i in instruments.items()}
period = slice(settings["start_date"], settings["holdout_start"])
capital = max(settings["capital_levels"])
output = ROOT / "output"
output.mkdir(exist_ok=True)


# Daily returns of a portfolio as a fraction of capital, within the test period
def portfolio_returns(results, cap, column="pnl"):
    return (total(results, column) / cap)[period]


trend = {cap: run_portfolio(markets, instruments, cap, settings) for cap in settings["capital_levels"]}
long_only = run_portfolio(markets, instruments, capital, settings, signal=always_long)
sp500 = markets["SP500"]
sp500_returns = (sp500["adjusted"].diff() / sp500["price"].shift(1))[period].fillna(0)

returns = {
    "trend $100k": portfolio_returns(trend[100_000], 100_000),
    "trend $1m": portfolio_returns(trend[capital], capital),
    "trend $1m before costs": portfolio_returns(trend[capital], capital, "gross_pnl"),
    "always long $1m": portfolio_returns(long_only, capital),
    "S&P 500 buy and hold": sp500_returns,
}
main = returns["trend $1m"]

pd.set_option("display.width", 200)
print(f"Results {settings['start_date']} to {settings['holdout_start']}\n")
print(summary_table(returns).T.to_string(float_format=lambda x: f"{x:.2f}"))

yearly = pd.DataFrame({
    "trend $1m": yearly_returns(main),
    "S&P 500": yearly_returns(returns["S&P 500 buy and hold"]),
})
print("\nYearly returns:")
print(yearly.to_string(float_format=lambda x: f"{x:.1%}"))

sectors = pd.Series({code: i.sector for code, i in instruments.items()})
by_market = pd.DataFrame({code: r["pnl"] for code, r in trend[capital].items()})[period]
by_sector = by_market.T.groupby(sectors).sum().T.fillna(0).sum() / capital
years = len(main) / 256
print("\nAverage yearly return from each sector:")
print((by_sector / years).sort_values(ascending=False).to_string(float_format=lambda x: f"{x:.1%}"))

monthly = pd.DataFrame({"trend": main, "sp500": returns["S&P 500 buy and hold"]}).resample("ME").sum()
down_months = monthly[monthly["sp500"] < 0]
print(f"\nCorrelation with S&P 500 (monthly): {monthly.corr().iloc[0, 1]:.2f}")
print(f"In months the S&P 500 fell, trend made {down_months['trend'].mean():.1%} on average "
      f"(S&P: {down_months['sp500'].mean():.1%})")

costs = (total(trend[capital], "costs") / capital)[period]
print(f"Costs: {costs.sum() / years:.2%} of capital per year")

fig, axes = plt.subplots(3, 1, figsize=(12, 12))
for name in ["trend $1m", "trend $100k", "always long $1m", "S&P 500 buy and hold"]:
    axes[0].plot(returns[name].cumsum() * 100, label=name, linewidth=0.9)
axes[0].set_title("Cumulative profit, % of starting capital (after costs)")
axes[0].legend(loc="upper left")

axes[1].fill_between(main.index, drawdowns(main) * 100, 0, color="tab:red")
axes[1].set_title("Trend $1m: fall from previous high, % of starting capital")

yearly.mul(100).plot.bar(ax=axes[2], width=0.8)
axes[2].axhline(0, color="black", linewidth=0.5)
axes[2].set_title("Yearly returns, %")

fig.tight_layout()
fig.savefig(output / "report.png", dpi=110)
print(f"\nSaved chart to {output / 'report.png'}")
