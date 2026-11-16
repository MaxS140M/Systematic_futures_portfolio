# Systematic Futures Portfolio

A trading system for 22 futures markets (stock indices, bonds, currencies, energy, metals and
crops). It buys what has been rising, sells what has been falling, and sizes each position so no
market dominates. It is tested on historical data with trading costs included.

**Start here: [notebooks/walkthrough.ipynb](notebooks/walkthrough.ipynb)**, a step-by-step tour
with charts, from raw data to the final held-back test.

## How it works
1. **Signal** – four moving-average crossovers (fast vs slow) combined into a forecast from -20 to +20.
2. **Sizing** – contracts = forecast × capital × 20% risk target ÷ yearly dollar risk of one contract,
   so a calm market gets more contracts than a wild one.
3. **Portfolio** – risk split equally across 6 sectors, then across markets in each sector.
4. **Costs** – commission, half the bid-ask spread, and rolling into the next contract.
5. **No look-ahead** – a position chosen at today's close only earns tomorrow's move. Tests check this.

## Results ($1m, after costs)

| | 2000 – Mar 2021 | Apr 2021 – Mar 2024 (held back) |
|---|---|---|
| Yearly return | 11% | 5% |
| Sharpe ratio | 0.64 | 0.30 |
| Worst drawdown | -40% | -35% |

- Made money in stock market crashes: +50% in 2008, +1.2% on average in months the S&P 500 fell.
- Results hold up when settings change slightly (Sharpe 0.5–0.7), but the held-back period was weaker.
- With $100k most markets need less than one contract, so only ~7 of 22 are held and Sharpe falls to 0.41.

Full numbers: `python scripts/report.py` and `python scripts/honesty_checks.py`. Roadmap: [docs/PLAN.md](docs/PLAN.md).

## Setup
```bash
python -m venv .venv
.venv/Scripts/activate
pip install -e .
python scripts/download_data.py
pytest
```

## Scripts
| Script | What it shows |
|---|---|
| `data_report.py` | Data quality for every market |
| `plot_signal.py CODE` | Price and trend forecast for one market |
| `plot_position.py CODE` | Contracts held at $100k and $1m |
| `backtest_market.py CODE` | Profit before and after costs for one market |
| `backtest_portfolio.py` | All 22 markets together |
| `report.py` | Full results and comparison with simple alternatives |
| `honesty_checks.py` | Sensitivity, luck, risk check and the held-back test |

Charts are saved to `output/`. Data comes from
[pysystemtrade](https://github.com/robcarver17/pysystemtrade) (data files only).
