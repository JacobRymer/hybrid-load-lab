"""Settings, paths and field-name mapping.

Secrets are read from a local ``.env`` file (never committed). Nothing is
loaded at import time, so tests and demo mode work without a ``.env``.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

# Local-only folders (all git-ignored).
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Committed folder for charts made from synthetic data only.
DOCS_IMG_DIR = PROJECT_ROOT / "docs" / "img"

REQUIRED_VARS = ("INTERVALS_API_KEY", "ATHLETE_ID")

# Logical name -> intervals.icu field name.
# UNVERIFIED: these are best guesses. Run scripts/check_connection.py to see
# which fields are present in your data, then correct them here.
FIELDS = {
    "activities": {
        "start_date": "start_date_local",
        "name": "name",
        "type": "type",
        "load": "icu_training_load",
        "avg_hr": "average_heartrate",
        "rpe": "icu_rpe",
        "avg_power": "icu_average_watts",
        "notes": "description",
    },
    "wellness": {
        "hrv": "hrv",
        "resting_hr": "restingHR",
        "sleep_secs": "sleepSecs",
        "ctl": "ctl",
        "atl": "atl",
    },
}


class ConfigError(RuntimeError):
    """Raised when required settings are missing."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    athlete_id: str

    def __repr__(self) -> str:
        # Keep the key out of logs and tracebacks.
        return "Settings(api_key='***', athlete_id='***')"


def load_settings(env_file: Path = ENV_FILE) -> Settings:
    """Load settings from ``env_file`` (if present) and the environment.

    Raises ConfigError naming every missing variable.
    """
    if env_file.exists():
        load_dotenv(env_file)

    missing = [name for name in REQUIRED_VARS if not os.getenv(name, "").strip()]
    if missing:
        hint = (
            "Copy .env.example to .env and fill in the values."
            if not env_file.exists()
            else "Add the missing values to your .env file."
        )
        raise ConfigError(f"Missing setting(s): {', '.join(missing)}. {hint}")

    return Settings(
        api_key=os.environ["INTERVALS_API_KEY"].strip(),
        athlete_id=os.environ["ATHLETE_ID"].strip(),
    )
