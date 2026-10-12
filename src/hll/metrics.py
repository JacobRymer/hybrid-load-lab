"""Reference training-load metrics.

All functions take a daily load series: one value per calendar day, rest
days as 0 (see ``daily_load``). "Load" here is the watch-derived number
(e.g. intervals.icu training load), i.e. a heart-rate-based mechanical load
proxy, not a measure of neuromuscular fatigue.

The acute:chronic (A:C) ratio is descriptive: it shows how the last week
compares with the recent norm. It is not an injury-risk score.

Ratios are left empty (NaN) until a full chronic window (28 days) exists.
They are never filled with a default such as 1.0.
"""

import numpy as np
import pandas as pd

ACUTE_DAYS = 7
CHRONIC_DAYS = 28


def daily_load(
    activities: pd.DataFrame,
    date_col: str = "start_date",
    load_col: str = "load",
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> pd.Series:
    """Total load per calendar day, with rest days filled as 0.

    Several sessions on one day are summed. Missing load values count as 0.
    The range runs from ``start`` (default: first activity) to ``end``
    (default: last activity).
    """
    days = pd.to_datetime(activities[date_col]).dt.normalize()
    loads = pd.to_numeric(activities[load_col], errors="coerce").fillna(0)
    totals = loads.groupby(days).sum()

    start = pd.Timestamp(start) if start is not None else totals.index.min()
    end = pd.Timestamp(end) if end is not None else totals.index.max()
    full_range = pd.date_range(start, end, freq="D", name="date")
    return totals.reindex(full_range, fill_value=0.0).astype(float).rename("load")


def _safe_ratio(acute: pd.Series, chronic: pd.Series) -> pd.Series:
    """acute / chronic, NaN where chronic is 0 or missing."""
    return (acute / chronic.replace(0, np.nan)).rename("acwr")


def acwr_rolling(
    daily: pd.Series, acute: int = ACUTE_DAYS, chronic: int = CHRONIC_DAYS
) -> pd.DataFrame:
    """Rolling-average A:C ratio.

    acute   = mean load over the last ``acute`` days (from day 7)
    chronic = mean load over the last ``chronic`` days (from day 28)
    acwr    = acute / chronic (from day 28)
    """
    acute_avg = daily.rolling(acute, min_periods=acute).mean()
    chronic_avg = daily.rolling(chronic, min_periods=chronic).mean()
    return pd.DataFrame(
        {"acute": acute_avg, "chronic": chronic_avg, "acwr": _safe_ratio(acute_avg, chronic_avg)}
    )


def acwr_ewma(
    daily: pd.Series, acute: int = ACUTE_DAYS, chronic: int = CHRONIC_DAYS
) -> pd.DataFrame:
    """Exponentially weighted A:C ratio.

    Each day: ewma_today = load_today * a + ewma_yesterday * (1 - a),
    with a = 2 / (N + 1), seeded with the first day's load.
    Recent days count more than older ones, unlike a plain rolling mean.
    All three columns are NaN until ``chronic`` days of data exist.
    """
    acute_ewma = daily.ewm(alpha=2 / (acute + 1), adjust=False).mean()
    chronic_ewma = daily.ewm(alpha=2 / (chronic + 1), adjust=False).mean()

    enough_data = np.arange(len(daily)) >= chronic - 1
    acute_ewma = acute_ewma.where(enough_data)
    chronic_ewma = chronic_ewma.where(enough_data)
    return pd.DataFrame(
        {
            "acute": acute_ewma,
            "chronic": chronic_ewma,
            "acwr": _safe_ratio(acute_ewma, chronic_ewma),
        }
    )


def monotony_strain(daily: pd.Series, window: int = ACUTE_DAYS) -> pd.DataFrame:
    """Weekly training monotony and strain.

    monotony = mean daily load / standard deviation of daily load (sample SD)
    strain   = total weekly load * monotony

    Both use a rolling ``window``-day window and start once it is full.
    Monotony is NaN when every day in the window has the same load (SD = 0).
    """
    mean = daily.rolling(window, min_periods=window).mean()
    sd = daily.rolling(window, min_periods=window).std()
    total = daily.rolling(window, min_periods=window).sum()
    monotony = mean / sd.replace(0, np.nan)
    return pd.DataFrame({"monotony": monotony, "strain": total * monotony})
