"""Download recent data from intervals.icu and write local CSVs.

Raw JSON  -> data/raw/<today>/      (git-ignored)
Tidy CSVs -> data/processed/        (git-ignored)

    python scripts/sync.py --days 120
"""

import argparse
import sys
from datetime import date, timedelta

from hll.client import IntervalsAPIError, IntervalsClient
from hll.config import PROCESSED_DIR, RAW_DIR, ConfigError, load_settings
from hll.ingest import activities_to_frame, save_json, wellness_to_frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=120, help="days to pull (default 120)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"Cannot sync: {exc}")
        return 1

    client = IntervalsClient(settings.athlete_id, settings.api_key)
    newest = date.today()
    oldest = newest - timedelta(days=args.days)
    try:
        activities = client.activities(oldest, newest)
        wellness = client.wellness(oldest, newest)
    except IntervalsAPIError as exc:
        print(f"Sync failed: {exc}")
        return 1

    raw_dir = RAW_DIR / newest.isoformat()
    save_json(activities, raw_dir / "activities.json")
    save_json(wellness, raw_dir / "wellness.json")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    activities_to_frame(activities).to_csv(PROCESSED_DIR / "activities.csv", index=False)
    wellness_to_frame(wellness).to_csv(PROCESSED_DIR / "wellness.csv", index=False)

    print(f"Synced {len(activities)} activities and {len(wellness)} wellness records "
          f"({args.days} days).")
    print(f"Raw JSON:  {raw_dir.relative_to(raw_dir.parents[2])}")
    print(f"CSV files: {PROCESSED_DIR.relative_to(PROCESSED_DIR.parents[1])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
