"""Plot daily load and the rolling acute:chronic (A:C) ratio.

    python scripts/plot_acwr.py --demo   # synthetic data -> docs/img/ (committed)
    python scripts/plot_acwr.py --real   # your data      -> outputs/  (git-ignored)

With no flag, real data is used if data/processed/activities.csv exists,
otherwise the synthetic demo.
"""

import argparse
import sys
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from hll.config import DOCS_IMG_DIR, OUTPUTS_DIR, PROCESSED_DIR, PROJECT_ROOT
from hll.demo import make_demo_activities
from hll.ingest import load_activities_csv
from hll.metrics import acwr_rolling, daily_load

ACTIVITIES_CSV = PROCESSED_DIR / "activities.csv"

# Colours: categorical slots 1-2 plus neutral ink (validated reference palette).
BAR_COLOUR = "#2a78d6"
ACUTE_COLOUR = "#eb6834"
CHRONIC_COLOUR = "#0b0b0b"
GRID_COLOUR = "#e6e5e0"
TEXT_MUTED = "#52514e"

NORM_LOW, NORM_HIGH = 0.8, 1.3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot daily load and the A:C ratio.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--demo", action="store_true", help="use synthetic demo data")
    mode.add_argument("--real", action="store_true", help="use data/processed/activities.csv")
    return parser.parse_args()


def build_figure(daily, ratios, title: str) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.4],
        vertical_spacing=0.06,
        subplot_titles=("Daily load (mechanical load proxy)", "Acute:chronic ratio (7 / 28 days)"),
    )

    fig.add_trace(
        go.Bar(x=daily.index, y=daily, name="Daily load", marker_color=BAR_COLOUR, opacity=0.45),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=ratios.index,
            y=ratios["acute"],
            name="7-day average",
            line=dict(color=ACUTE_COLOUR, width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=ratios.index,
            y=ratios["chronic"],
            name="28-day average",
            line=dict(color=CHRONIC_COLOUR, width=2, dash="dot"),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=ratios.index,
            y=ratios["acwr"],
            name="A:C ratio",
            line=dict(color=CHRONIC_COLOUR, width=2),
        ),
        row=2,
        col=1,
    )

    # Bands go after the ratio trace: plotly skips shapes on empty subplots.
    # Descriptive bands only: how this week compares with the recent norm.
    ratio_top = max(2.0, float(ratios["acwr"].max(skipna=True) or 0) + 0.2)
    fig.add_hrect(
        y0=NORM_LOW, y1=NORM_HIGH, fillcolor="#1baf7a", opacity=0.12, line_width=0,
        annotation_text="in line with recent norm", annotation_position="top left",
        annotation_font_color=TEXT_MUTED, row=2, col=1,
    )  # fmt: skip
    fig.add_hrect(
        y0=NORM_HIGH, y1=ratio_top, fillcolor="#eda100", opacity=0.12, line_width=0,
        annotation_text="above recent norm", annotation_position="top left",
        annotation_font_color=TEXT_MUTED, row=2, col=1,
    )  # fmt: skip

    fig.update_layout(
        title=dict(text=title, x=0.01),
        template="plotly_white",
        height=650,
        width=1000,
        hovermode="x unified",
        bargap=0.15,
        legend=dict(orientation="h", y=1.1, x=1, xanchor="right", yanchor="bottom"),
        margin=dict(l=60, r=30, t=130, b=50),
    )
    fig.update_xaxes(gridcolor=GRID_COLOUR)
    fig.update_yaxes(gridcolor=GRID_COLOUR)
    fig.update_yaxes(title_text="Load", row=1, col=1)
    fig.update_yaxes(title_text="Ratio", range=[0, ratio_top], row=2, col=1)
    return fig


def save(fig: go.Figure, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / f"{stem}.html"
    fig.write_html(html_path, include_plotlyjs="cdn")
    print(f"Saved {html_path.relative_to(PROJECT_ROOT)}")

    png_path = out_dir / f"{stem}.png"
    try:
        fig.write_image(png_path, scale=2)
        print(f"Saved {png_path.relative_to(PROJECT_ROOT)}")
    except Exception as exc:  # kaleido problems vary by platform
        print(f"PNG export failed ({type(exc).__name__}: {exc}). The HTML chart was saved.")


def main() -> int:
    args = parse_args()
    use_demo = args.demo or (not args.real and not ACTIVITIES_CSV.exists())

    if use_demo:
        activities = make_demo_activities()
        title = "Synthetic demo data: daily load and A:C ratio"
        out_dir, stem = DOCS_IMG_DIR, "acwr_demo"
    else:
        if not ACTIVITIES_CSV.exists():
            print("No processed data found. Run scripts/sync.py first, or use --demo.")
            return 1
        activities = load_activities_csv(ACTIVITIES_CSV)
        title = "Daily load and A:C ratio"
        out_dir, stem = OUTPUTS_DIR, "acwr"

    daily = daily_load(activities)
    ratios = acwr_rolling(daily)
    save(build_figure(daily, ratios, title), out_dir, stem)
    return 0


if __name__ == "__main__":
    sys.exit(main())
