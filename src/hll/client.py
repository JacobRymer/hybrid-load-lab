"""Minimal client for the intervals.icu REST API.

Authentication is HTTP basic auth with the literal username "API_KEY" and
your personal API key as the password. The key is never logged or printed.
"""

from datetime import date

import requests

BASE_URL = "https://intervals.icu/api/v1"
TIMEOUT_SECONDS = 30

_STATUS_MESSAGES = {
    401: "Authentication failed (401). Check INTERVALS_API_KEY in your .env file.",
    403: "Access denied (403). Check that the API key belongs to this athlete.",
    404: "Not found (404). Check ATHLETE_ID in your .env file.",
}


class IntervalsAPIError(RuntimeError):
    """Raised for API errors, with a message that never includes the key."""


class IntervalsClient:
    def __init__(self, athlete_id: str, api_key: str, base_url: str = BASE_URL):
        self.athlete_id = athlete_id
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = ("API_KEY", api_key)
        self.session.headers["Accept"] = "application/json"

    def __repr__(self) -> str:
        return "IntervalsClient(athlete_id='***', api_key='***')"

    def activities(self, oldest: date, newest: date) -> list[dict]:
        """Activities between two dates (inclusive)."""
        return self._get_range("activities", oldest, newest)

    def wellness(self, oldest: date, newest: date) -> list[dict]:
        """Daily wellness records between two dates (inclusive)."""
        return self._get_range("wellness", oldest, newest)

    def _get_range(self, endpoint: str, oldest: date, newest: date) -> list[dict]:
        url = f"{self.base_url}/athlete/{self.athlete_id}/{endpoint}"
        params = {"oldest": oldest.isoformat(), "newest": newest.isoformat()}
        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            raise IntervalsAPIError(
                f"Could not reach intervals.icu ({type(exc).__name__})."
            ) from None

        if response.status_code in _STATUS_MESSAGES:
            raise IntervalsAPIError(_STATUS_MESSAGES[response.status_code])
        if not response.ok:
            raise IntervalsAPIError(
                f"intervals.icu returned HTTP {response.status_code} for /{endpoint}."
            )
        return response.json()
