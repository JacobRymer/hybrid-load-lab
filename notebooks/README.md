# Notebooks

This is where the analysis is written first (session analysis, A:C ratio, monotony and strain). Once a piece of analysis is stable, it moves into `src/hll`.

## Rules

- **Data source.** Notebooks read from `data/processed/` (written by `scripts/sync.py`). While the `FIELDS` mapping in `src/hll/config.py` is unverified, they may read the raw JSON in `data/raw/<date>/` instead. Both folders are git-ignored.
- **Write the analysis here.** Do not import the analysis functions from `hll.metrics`. Those are reference implementations used by the tests and the demo; the notebook versions are written from scratch. Importing helpers such as `hll.config` or `hll.ingest` is fine.
- **Outputs are stripped on commit.** nbstripout (set up in `.gitattributes`) removes cell outputs, so real numbers and charts in a notebook are not published. Run `nbstripout --install` once after cloning to enable the filter locally.
- **Never save real charts into `docs/img/`.** That folder is for synthetic demo charts only. Save real charts to `outputs/`, which is git-ignored.
- Use the `hll` Jupyter kernel.
