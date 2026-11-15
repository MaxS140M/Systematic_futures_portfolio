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

## Next
1. **Trend signal on one market** – a moving-average signal for crude oil that says how strongly
   to be long or short, plotted against the price.
2. **Position size on one market** – turn the signal into a number of contracts using how
   volatile the market is and how much capital we have.
3. **Profit and loss on one market** – daily P&L from those positions, with a test proving we
   never trade on tomorrow's prices.
4. **Trading costs** – subtract commission, spread and roll costs. Compare before and after.
5. **Whole portfolio** – run all 22 markets together, split risk equally across sectors, at $100k
   and $1m.
6. **Results report** – Sharpe ratio, drawdowns, yearly returns and charts, compared with simply
   buying and holding.
7. **Honesty checks** – change the settings slightly and see if results hold up, then run the
   untouched 2021–2024 data once.

## Ideas for later
- A second signal (carry)
- Micro contracts so $100k can hold more markets
- Data after March 2024

## Decisions
- Free data from the pysystemtrade project (data only, our own code). It ends on 28 March 2024.
- Every backtest runs at both $100k and $1m.
- Data from 1 April 2021 onwards is kept aside and only used once, at the end.
