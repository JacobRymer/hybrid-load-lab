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

### Changed
- Terms aligned: "metabolic load" for HR/TRIMP-based watch load, "mechanical load proxy" for the planned second load built from power, elevation, station volume and legs RPE.
- intervals.icu is now the primary data source; synthetic data is for tests and the no-account demo only.
- `plot_acwr.py` uses real data by default and exits with a message if none exists, instead of silently falling back to demo data.
- `check_connection.py` lists all wellness keys and more activity key candidates (names and counts only).
