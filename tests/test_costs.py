import pandas as pd
import pytest

from sfp.config import Instrument
from sfp.costs import contracts_traded, cost_per_contract, daily_costs
from sfp.sizing import buffered_position

INSTRUMENT = Instrument("TEST", "Test", "equity", 10, "USD", 2.0, 0.5)


def series(values):
    return pd.Series(values, index=pd.bdate_range("2020-01-01", periods=len(values)), dtype=float)


# Commission $2 plus spread 0.5 points x multiplier 10 = $7 per contract
def test_cost_per_contract():
    assert cost_per_contract(INSTRUMENT, 1.0) == 7.0


# Going from 0 to 3 to 1 contracts means trading 3 then 2
def test_contracts_traded_from_position_changes():
    traded = contracts_traded(series([0, 3, 1]), roll_days=[])
    assert traded.tolist() == [0, 3, 2]


# On a roll day, holding 2 contracts means selling 2 old and buying 2 new
def test_roll_day_trades_twice_the_position():
    position = series([2, 2, 2])
    traded = contracts_traded(position, roll_days=[position.index[2]])
    assert traded.tolist() == [0, 0, 4]


# Trading 3 contracts at $7 each costs $21
def test_daily_costs():
    costs = daily_costs(series([0, 3]), [], INSTRUMENT, 1.0)
    assert costs.iloc[1] == pytest.approx(21.0)


# Small wobbles inside the buffer should not cause trades
def test_buffer_ignores_small_moves():
    ideal = series([3.0, 3.3, 2.7, 3.2])
    held = buffered_position(ideal, series([0.4] * 4))
    assert held.tolist() == [3, 3, 3, 3]


# A big move outside the buffer should trade to the edge of the buffer
def test_buffer_trades_big_moves():
    ideal = series([5.0, 5.2, 10.0])
    held = buffered_position(ideal, series([1.0] * 3))
    assert held.tolist() == [4, 4, 9]


# Without a buffer, an ideal hovering around 1.5 flips every day; with one it stays put
def test_buffer_reduces_trading():
    ideal = series([1.4, 1.6] * 50)
    rounded = ideal.round()
    buffered = buffered_position(ideal, series([0.3] * 100))
    assert contracts_traded(buffered, []).sum() < contracts_traded(rounded, []).sum()
