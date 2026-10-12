"""Check the intervals.icu connection and which FIELDS exist in your data.

Pulls the last 30 days and prints counts only: no values, names or notes.

    python scripts/check_connection.py
"""

import sys
from datetime import date, timedelta

from hll.client import IntervalsAPIError, IntervalsClient
from hll.config import FIELDS, ConfigError, load_settings

DAYS = 30
HINT_WORDS = ("rpe", "watts", "power", "desc", "feel")


def report_fields(label: str, records: list[dict], fields: dict) -> None:
    print(f"\n{label} fields (FIELDS mapping):")
    for name, api_name in fields.items():
        present = any(api_name in r for r in records)
        non_null = sum(r.get(api_name) is not None for r in records)
        status = "present" if present else "MISSING"
        print(f"  {name:<12} -> {api_name:<22} {status:<8} non-null: {non_null}")


def report_candidate_keys(records: list[dict]) -> None:
    keys = sorted({k for r in records for k in r if any(w in k.lower() for w in HINT_WORDS)})
    print(f"\nActivity keys containing {', '.join(HINT_WORDS)}:")
    if not keys:
        print("  (none found)")
    for key in keys:
        non_null = sum(r.get(key) is not None for r in records)
        print(f"  {key:<34} non-null: {non_null}")


def main() -> int:
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"Cannot connect: {exc}")
        return 1

    client = IntervalsClient(settings.athlete_id, settings.api_key)
    newest = date.today()
    oldest = newest - timedelta(days=DAYS)
    try:
        activities = client.activities(oldest, newest)
        wellness = client.wellness(oldest, newest)
    except IntervalsAPIError as exc:
        print(f"Connection failed: {exc}")
        return 1

    print(
        f"Connected. Last {DAYS} days: {len(activities)} activities, "
        f"{len(wellness)} wellness records."
    )
    report_fields("Activity", activities, FIELDS["activities"])
    report_fields("Wellness", wellness, FIELDS["wellness"])
    report_candidate_keys(activities)

    notes_field = FIELDS["activities"]["notes"]
    has_notes = any(r.get(notes_field) for r in activities)
    print(f"\nNotes present: {'yes' if has_notes else 'no'} (text not shown)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
