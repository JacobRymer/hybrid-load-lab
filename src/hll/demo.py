"""Seeded synthetic training data for demos and tests.

Nothing here comes from a real athlete. The 16-week block has a simple
weekly pattern, a gradual build, a deload week and a one-week load spike,
so the charts have something to show. Columns match
data/processed/activities.csv.
"""

import numpy as np
import pandas as pd

from hll.ingest import ACTIVITY_COLUMNS

WEEKS = 16
DEMO_START = "2000-01-03"  # an arbitrary Monday, clearly not a real date range
DELOAD_WEEK = 9  # 1-based week numbers
SPIKE_WEEK = 13

# (day of week 0=Mon, session type, typical load, typical avg HR, typical RPE)
WEEKLY_PLAN = [
    (0, "WeightTraining", 45, 120, 6),  # sleds, lunges, strength
    (1, "Run", 70, 155, 7),  # intervals
    (3, "Workout", 85, 160, 8),  # HYROX-style stations + running
    (4, "Run", 40, 135, 4),  # easy run
    (5, "Run", 95, 148, 6),  # long run
]


def week_multiplier(week: int) -> float:
    """Gradual build (+3% a week), a deload and a spike."""
    if week == DELOAD_WEEK:
        return 0.55
    if week == SPIKE_WEEK:
        return 1.7
    return 1.0 + 0.03 * (week - 1)


def make_demo_activities(seed: int = 42, weeks: int = WEEKS) -> pd.DataFrame:
    """Synthetic activities with the same columns as the processed CSV."""
    rng = np.random.default_rng(seed)
    start = pd.Timestamp(DEMO_START)
    rows = []
    for week in range(1, weeks + 1):
        scale = week_multiplier(week)
        for weekday, session_type, load, hr, rpe in WEEKLY_PLAN:
            day = start + pd.Timedelta(days=7 * (week - 1) + weekday, hours=7)
            noise = rng.normal(1.0, 0.12)
            rows.append(
                {
                    "id": f"demo-{len(rows) + 1:03d}",
                    "start_date": day,
                    "name": f"Synthetic {session_type}",
                    "type": session_type,
                    "load": round(max(load * scale * noise, 5.0), 1),
                    "avg_hr": round(hr + rng.normal(0, 4)),
                    "rpe": int(np.clip(round(rpe + rng.normal(0, 1) + (scale - 1) * 2), 1, 10)),
                    "avg_power": np.nan,
                    "notes": "",
                }
            )
    return pd.DataFrame(rows, columns=ACTIVITY_COLUMNS)
