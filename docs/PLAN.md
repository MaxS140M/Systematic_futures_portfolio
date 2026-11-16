# Plan

## Goal
A trading system for 22 futures markets. It buys markets that have been going up, sells markets
that have been going down, sizes every position so no single market dominates, and is tested on
over 20 years of history with trading costs included.

## How it is built
Each feature works on its own and the next one builds on top of it. After every feature the code
runs, the tests pass, and there is something to look at.

## Done
- **Load data** – download prices for 22 markets, clean them into one row per day, convert to
  USD, find contract rolls, and print a data-quality report.
- **Trend signal** – four moving-average crossovers of different speeds, combined into one
  forecast from -20 (strong sell) to +20 (strong buy). `python scripts/plot_signal.py GOLD` draws
  it for any market.
- **Position sizing** – turns the forecast into whole contracts so every market carries the same
  risk. `python scripts/plot_position.py` shows contracts held at $100k and $1m.
- **Profit and loss** – daily profit from yesterday's position times today's price change, plus
  Sharpe ratio and drawdown. `python scripts/backtest_market.py GOLD` backtests any market.
- **Trading costs** – commission, spread and roll costs, plus a buffer so small wobbles in the
  ideal position don't cause trades. The same script compares before costs, after costs, and
  after costs with the buffer.
- **Whole portfolio** – all 22 markets together, risk split equally across sectors, scaled up by a
  diversification multiplier. `python scripts/backtest_portfolio.py` runs it at $100k and $1m.
- **Results report** – headline numbers, yearly returns, drawdowns, sector contributions and
  behaviour in stock market falls, compared with "always long" and S&P 500 buy-and-hold.
  `python scripts/report.py`.
- **Honesty checks** – change one setting at a time, shuffle months to see the range of luck,
  check actual risk against the target, and run the held-back 2021–2024 data once.
  `python scripts/honesty_checks.py`.

