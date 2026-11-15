from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw"


@dataclass
class Instrument:
    code: str
    name: str
    sector: str
    multiplier: float
    currency: str
    commission: float
    spread: float


# Read instruments.yaml and return a dict of code -> Instrument
def load_instruments():
    raw = yaml.safe_load((ROOT / "config" / "instruments.yaml").read_text())
    instruments = {}
    for sector, markets in raw.items():
        for code, info in markets.items():
            instruments[code] = Instrument(code=code, sector=sector, **info)
    return instruments


# Read backtest.yaml and return it as a dict
def load_settings():
    return yaml.safe_load((ROOT / "config" / "backtest.yaml").read_text())
