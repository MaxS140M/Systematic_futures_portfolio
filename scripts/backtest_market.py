import sys

import matplotlib.pyplot as plt

from sfp.backtest import run_market
from sfp.config import ROOT, load_instruments, load_settings
from sfp.data import load_market
from sfp.stats import annual_return, max_drawdown, sharpe_ratio

code = sys.argv[1] if len(sys.argv) > 1 else "CRUDE_W"
settings = load_settings()
instrument = load_instruments()[code]
market = load_market(instrument)
period = slice(settings["start_date"], settings["holdout_start"])

fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
for ax, capital in zip(axes, settings["capital_levels"]):
    no_buffer = run_market(market, instrument, capital, settings, use_buffer=False)[period]
    buffered = run_market(market, instrument, capital, settings)[period]
    versions = {
        "before costs": no_buffer["gross_pnl"],
        "after costs, no buffer": no_buffer["pnl"],
        "after costs, with buffer": buffered["pnl"],
    }

    print(f"{code} with ${capital:,}:")
    for name, pnl in versions.items():
        returns = pnl / capital
        print(f"  {name:26} return {annual_return(returns):6.1%}   Sharpe {sharpe_ratio(returns):5.2f}"
              f"   worst drawdown {max_drawdown(returns):7.1%}")
        ax.plot(returns.cumsum() * 100, label=name, linewidth=0.9)

    years = len(buffered) / 256
    print(f"  costs per year: no buffer ${no_buffer['costs'].sum() / years:,.0f}, "
          f"with buffer ${buffered['costs'].sum() / years:,.0f}")

    ax.set_title(f"{code} with ${capital:,}")
    ax.set_ylabel("cumulative profit, % of starting capital")
    ax.legend(loc="upper left")

output = ROOT / "output" / f"pnl_{code}.png"
output.parent.mkdir(exist_ok=True)
fig.tight_layout()
fig.savefig(output, dpi=110)
print(f"Saved chart to {output}")
