# Systematic Futures Portfolio

A trading system for 22 futures markets (stock indices, bonds, currencies, energy, metals and
crops). It buys what has been rising, sells what has been falling, and sizes each position so no
market dominates. It is tested on historical data with trading costs included.

See [docs/PLAN.md](docs/PLAN.md) for what is done and what comes next.

## Setup
```bash
python -m venv .venv
.venv/Scripts/activate
pip install -e .
python scripts/download_data.py
python scripts/data_report.py
pytest
```

Data comes from [pysystemtrade](https://github.com/robcarver17/pysystemtrade) (data files only).
