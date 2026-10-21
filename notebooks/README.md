# Notebooks

This is where the analysis is written first. Once a piece of analysis is stable, it moves into `src/hll`.

## Notebooks

| Notebook | What it shows |
|---|---|
| [`01_weekly_summary.ipynb`](01_weekly_summary.ipynb) | Last 7 days of training: totals, time in heart-rate zones, split by sport group, activity list. |
| [`02_daily_readiness.ipynb`](02_daily_readiness.ipynb) | Daily readiness for a chosen day: HRV baseline vs normal range, HRV variability, resting HR, sleep, acute vs chronic load, yesterday's training class, and rule-based guidance for today. |

Next: session analysis, monotony and strain, and the RPE vs heart-rate load comparison.

## Running a notebook

1. Activate the environment and sync your data (see the main README):
```bash
   conda activate hll
   python scripts/sync.py --days 120
```
2. Open folder, pick a notebook, and choose the **`hll`** kernel.
3. **Restart and Run All.** Every notebook is written to run top to bottom.
4. To look at a past day in `02_daily_readiness.ipynb`, set `SELECTED_DATE` in the first code cell (for example `"2026-10-18"`), then run all again.

## Rules

- **Data source.** Notebooks read from `data/processed/` (written by `scripts/sync.py` using the `FIELDS` mapping in `src/hll/config.py`). For a field not in `FIELDS`, read the raw JSON in `data/raw/<date>/`. Both folders are git-ignored.
- **Write the analysis here.** Do not import the analysis functions from `hll.metrics`. Those are reference implementations used by the tests and the demo; the notebook versions are written from scratch. Importing helpers such as `hll.config` or `hll.ingest` is fine.
- **Outputs are stripped on commit.** nbstripout (set up in `.gitattributes`) removes cell outputs, so real numbers and charts in a notebook are not published. Run `nbstripout --install` once after cloning to enable the filter locally.
- **Save charts to `outputs/`, not `docs/img/`.** `outputs/` is git-ignored. Copy a chart into `docs/img/` by hand only once you have decided to publish it (see the checklist below).
- Use the `hll` Jupyter kernel.

## Conventions

- **Structure.** Each code cell has a markdown heading and a sentence or two above it saying what it does and why. Setup comes first, then settings, then analysis, with the display code last.
- **One settings cell.** Window lengths and thresholds live together in a single cell near the top, with a comment that they are heuristics, not validated cut-offs. Change a rule there, not inside the analysis.
- **Load metric.** The dashboards use `icu_load` (intervals.icu's HR-based load) as the daily load.
- **Status is never colour alone.** Dashboard ratings (OK / Watch / Flag, green / amber / red) always carry an icon and a word as well as a colour.
- **Limitations cell.** Every notebook ends with a short limitations and next-steps section.
- **Before committing:** Restart and Run All, confirm there are no errors, and add the notebook by name rather than `git add .`.
