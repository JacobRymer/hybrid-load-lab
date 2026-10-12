# Changelog

All notable changes to this project are listed here.

## [0.1.0] - in development

### Added
- Project scaffold: conda environment, src-layout package `hll`, MIT licence.
- intervals.icu client (basic auth, clear 401/403/404 errors) and `FIELDS` mapping (unverified).
- `scripts/check_connection.py`, `scripts/sync.py` for local-only data pulls.
- Reference metrics: daily load, rolling and EWMA acute:chronic ratio, monotony and strain.
- Seeded synthetic demo data and `scripts/plot_acwr.py` demo chart.
- Daily and session log templates for subjective inputs.
- GitHub Actions workflow running ruff and pytest.
