import pandas as pd
import pytest

from sfp.config import Instrument, load_instruments
from sfp.data import load_market, roll_dates


# Write a small fake dataset to a temp folder
@pytest.fixture
def data_dir(tmp_path):
    (tmp_path / "adjusted").mkdir()
    (tmp_path / "multiple").mkdir()
    (tmp_path / "fx").mkdir()

    (tmp_path / "adjusted" / "TEST.csv").write_text(
        "DATETIME,price\n"
        "2020-01-01 23:00,-5.0\n"
        "2020-01-02 14:00,-4.5\n"
        "2020-01-02 23:00,-4.0\n"
        "2020-01-03 23:00,-3.0\n"
    )
    (tmp_path / "multiple" / "TEST.csv").write_text(
        "DATETIME,PRICE,PRICE_CONTRACT\n"
        "2020-01-01 23:00,100,20200300\n"
        "2020-01-02 23:00,101,20200300\n"
        "2020-01-03 23:00,105,20200600\n"
    )
    (tmp_path / "fx" / "EURUSD.csv").write_text(
        "DATETIME,PRICE\n"
        "2019-12-31,1.10\n"
        "2020-01-02,1.20\n"
    )
    return tmp_path


def make_instrument(currency):
    return Instrument("TEST", "Test", "equity", 10, currency, 1.0, 0.1)


# Two prices on the same day should become one: the later one
def test_keeps_last_price_of_each_day(data_dir):
    df = load_market(make_instrument("EUR"), data_dir)
    assert len(df) == 3
    assert df.loc["2020-01-02", "adjusted"] == -4.0


# Negative adjusted prices are normal and must not be thrown away
def test_keeps_negative_adjusted_prices(data_dir):
    df = load_market(make_instrument("EUR"), data_dir)
    assert (df["adjusted"] < 0).all()


# Each day must use the latest FX rate we already knew, never a future one
def test_fx_uses_past_rates_only(data_dir):
    df = load_market(make_instrument("EUR"), data_dir)
    assert df["fx"].tolist() == [1.10, 1.20, 1.20]


# A USD market needs no conversion
def test_usd_market_has_fx_of_one(data_dir):
    df = load_market(make_instrument("USD"), data_dir)
    assert (df["fx"] == 1.0).all()


# The contract changes on 3 Jan, so that is the only roll
def test_finds_roll_dates(data_dir):
    df = load_market(make_instrument("EUR"), data_dir)
    assert list(roll_dates(df)) == [pd.Timestamp("2020-01-03")]


# The real config should have 22 markets across 6 sectors
def test_config_has_22_markets():
    instruments = load_instruments()
    assert len(instruments) == 22
    assert len({i.sector for i in instruments.values()}) == 6
