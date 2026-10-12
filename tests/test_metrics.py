"""Tests for hll.metrics. Expected values are worked out by hand in comments.

All data here is synthetic.
"""

import math

import numpy as np
import pandas as pd
import pytest

from hll.demo import make_demo_activities
from hll.ingest import ACTIVITY_COLUMNS
from hll.metrics import acwr_ewma, acwr_rolling, daily_load, monotony_strain


def series(values: list[float], start: str = "2000-01-03") -> pd.Series:
    """Daily load series starting on a fixed synthetic date."""
    index = pd.date_range(start, periods=len(values), freq="D", name="date")
    return pd.Series(values, index=index, dtype=float, name="load")


# --- daily_load ------------------------------------------------------------


def test_daily_load_sums_same_day_and_zero_fills_rest_days():
    activities = pd.DataFrame(
        {
            "start_date": ["2000-01-03 07:00", "2000-01-03 18:00", "2000-01-05 09:00"],
            "load": [40, 60, 80],
        }
    )
    result = daily_load(activities)
    # Day 1: 40 + 60 = 100. Day 2: rest -> 0. Day 3: 80.
    assert result.tolist() == [100.0, 0.0, 80.0]
    assert list(result.index.day) == [3, 4, 5]


def test_daily_load_treats_missing_load_as_zero_and_respects_range():
    activities = pd.DataFrame({"start_date": ["2000-01-04"], "load": [None]})
    result = daily_load(activities, start="2000-01-03", end="2000-01-05")
    assert result.tolist() == [0.0, 0.0, 0.0]


# --- acwr_rolling ----------------------------------------------------------


def test_acwr_rolling_is_empty_before_28_days():
    result = acwr_rolling(series([100] * 28))
    assert result["acwr"].iloc[:27].isna().all()
    # Acute (7-day) average exists from day 7.
    assert result["acute"].iloc[:6].isna().all()
    assert result["acute"].iloc[6] == 100


def test_acwr_rolling_constant_load_gives_one():
    result = acwr_rolling(series([100] * 28))
    # acute = 700 / 7 = 100, chronic = 2800 / 28 = 100 -> 1.0
    assert result["acwr"].iloc[27] == pytest.approx(1.0)


def test_acwr_rolling_spike_after_rest():
    # 21 rest days then 7 days at 100.
    result = acwr_rolling(series([0] * 21 + [100] * 7))
    # acute = 700 / 7 = 100; chronic = 700 / 28 = 25; ratio = 100 / 25 = 4.0
    last = result.iloc[-1]
    assert last["acute"] == pytest.approx(100)
    assert last["chronic"] == pytest.approx(25)
    assert last["acwr"] == pytest.approx(4.0)


def test_acwr_rolling_zero_chronic_gives_nan_not_error():
    result = acwr_rolling(series([0] * 28))
    assert math.isnan(result["acwr"].iloc[-1])


# --- acwr_ewma -------------------------------------------------------------


def test_acwr_ewma_is_empty_before_28_days():
    result = acwr_ewma(series([100] * 30))
    assert result.iloc[:27].isna().all().all()
    assert result["acwr"].iloc[27:].notna().all()


def test_acwr_ewma_constant_load_gives_one():
    # Seeded with the first value, a constant series has a constant EWMA.
    result = acwr_ewma(series([100] * 28))
    assert result["acwr"].iloc[-1] == pytest.approx(1.0)


def test_acwr_ewma_single_step_after_rest():
    # 27 rest days then one day at 100. Both EWMAs are 0 until day 28.
    # acute   a = 2/8  = 0.25    -> 100 * 0.25   = 25
    # chronic a = 2/29 = 0.06897 -> 100 * 2 / 29 = 6.8966
    # ratio = 25 / (200 / 29) = 3.625
    last = acwr_ewma(series([0] * 27 + [100])).iloc[-1]
    assert last["acute"] == pytest.approx(25)
    assert last["chronic"] == pytest.approx(200 / 29)
    assert last["acwr"] == pytest.approx(3.625)


# --- monotony_strain -------------------------------------------------------


def test_monotony_and_strain_hand_calculated():
    # Week: 100, 0, 100, 0, 100, 0, 100 -> total 400, mean 400/7 = 57.143
    # Deviations: +42.857 (x4), -57.143 (x3)
    # Sum of squares = 4 * 1836.73 + 3 * 3265.31 = 17142.86
    # Sample SD = sqrt(17142.86 / 6) = 53.452
    # Monotony = 57.143 / 53.452 = 1.0690; strain = 400 * 1.0690 = 427.62
    result = monotony_strain(series([100, 0, 100, 0, 100, 0, 100])).iloc[-1]
    assert result["monotony"] == pytest.approx(1.0690, abs=1e-4)
    assert result["strain"] == pytest.approx(427.62, abs=1e-2)


def test_monotony_is_nan_when_every_day_is_the_same():
    result = monotony_strain(series([50] * 7))
    assert np.isnan(result["monotony"].iloc[-1])


def test_monotony_needs_a_full_week():
    result = monotony_strain(series([10, 20, 30, 40, 50, 60]))
    assert result["monotony"].isna().all()


# --- demo data -------------------------------------------------------------


def test_demo_data_matches_processed_columns_and_is_reproducible():
    first = make_demo_activities(seed=1)
    second = make_demo_activities(seed=1)
    assert list(first.columns) == ACTIVITY_COLUMNS
    pd.testing.assert_frame_equal(first, second)
    days = daily_load(first)
    assert len(days) >= 16 * 7 - 7  # roughly 16 weeks
