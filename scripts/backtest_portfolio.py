import matplotlib.pyplot as plt
import pandas as pd

from sfp.config import ROOT, load_instruments, load_settings
from sfp.data import load_market
from sfp.portfolio import run_portfolio, total
from sfp.stats import annual_return, annual_volatility, max_drawdown, sharpe_ratio

settings = load_settings()
instruments = load_instruments()
markets = {code: load_market(i) for code, i in instruments.items()}
period = slice(settings["start_date"], settings["holdout_start"])

fig, ax = plt.subplots(figsize=(12, 5))
for capital in settings["capital_levels"]:
    results = run_portfolio(markets, instruments, capital, settings)
    returns = (total(results, "pnl") / capital)[period]
    positions = pd.DataFrame({c: r["position"] for c, r in results.items()})[period]

    print(f"Portfolio with ${capital:,} (after costs):")
    print(f"  yearly return:  {annual_return(returns):.1%}")
    print(f"  yearly risk:    {annual_volatility(returns):.1%}   (target {settings['target_annual_vol']:.0%})")
    print(f"  Sharpe ratio:   {sharpe_ratio(returns):.2f}")
    print(f"  worst drawdown: {max_drawdown(returns):.1%}")
    print(f"  average markets actually held: {(positions != 0).sum(axis=1).mean():.1f} of 22")

    ax.plot(returns.cumsum() * 100, label=f"${capital:,}")

ax.axhline(0, color="grey", linewidth=0.5)
ax.set_title("22-market portfolio: cumulative profit after costs, % of starting capital")
ax.legend()

output = ROOT / "output" / "portfolio.png"
output.parent.mkdir(exist_ok=True)
fig.tight_layout()
fig.savefig(output, dpi=110)
print(f"Saved chart to {output}")
