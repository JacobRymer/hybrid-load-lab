"""Turn raw intervals.icu JSON into tidy tables using the FIELDS mapping."""

import json
from pathlib import Path

import pandas as pd

from hll.config import FIELDS

# Column order for data/processed/activities.csv (and the synthetic demo data).
ACTIVITY_COLUMNS = ["id", *FIELDS["activities"]]
WELLNESS_COLUMNS = ["date", *FIELDS["wellness"]]


def activities_to_frame(raw: list[dict], fields: dict = FIELDS["activities"]) -> pd.DataFrame:
    """One row per activity, keeping the intervals.icu activity id.

    Fields missing from the API response become empty (NaN) columns.
    """
    rows = [
        {"id": item.get("id"), **{name: item.get(api) for name, api in fields.items()}}
        for item in raw
    ]
    df = pd.DataFrame(rows, columns=["id", *fields])
    df["start_date"] = pd.to_datetime(df["start_date"])
    return df.sort_values("start_date").reset_index(drop=True)


def wellness_to_frame(raw: list[dict], fields: dict = FIELDS["wellness"]) -> pd.DataFrame:
    """One row per day. intervals.icu uses the date (YYYY-MM-DD) as the record id."""
    rows = [
        {"date": item.get("id"), **{name: item.get(api) for name, api in fields.items()}}
        for item in raw
    ]
    df = pd.DataFrame(rows, columns=["date", *fields])
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def save_json(data: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_activities_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["start_date"])
