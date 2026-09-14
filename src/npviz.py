"""Plot styling helpers for the SI 699 national-parks EDA.

Design rules (see docs in notebook "Figure conventions"):
- Categorical colours use a fixed, validated colour-blind-safe order and are never cycled.
- Sequential colour is a single hue, light -> dark.
- Marks are thin; grids are hairline, solid, recessive; text never wears a data colour.
- Every multi-series chart has a legend AND selective direct labels.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# --- Tokens -----------------------------------------------------------------
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
TEXT_MUTED = "#8a8985"
GRID = "#e6e5e0"

# Validated categorical order (worst adjacent CVD dE 9.1, normal-vision dE 19.6).
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
               "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = CATEGORICAL
DARK_BLUE = "#0d2f5c"
EMPHASIS_GRAY = "#c9c8c2"  # de-emphasised series when one series is highlighted

# Single-hue sequential ramp for magnitude (heatmaps).
SEQUENTIAL = LinearSegmentedColormap.from_list("np_blue", [SURFACE, BLUE, DARK_BLUE])

FIG_DIR = Path(__file__).resolve().parents[1] / "figures"


def apply_style() -> None:
    """Set global matplotlib defaults for the notebook."""
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlecolor": TEXT_PRIMARY,
        "axes.labelsize": 9.5,
        "axes.labelcolor": TEXT_SECONDARY,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "grid.linestyle": "-",
        "xtick.color": TEXT_SECONDARY,
        "ytick.color": TEXT_SECONDARY,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "lines.linewidth": 2,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "legend.frameon": False,
        "legend.fontsize": 9,
        "legend.labelcolor": TEXT_SECONDARY,
        "axes.prop_cycle": mpl.cycler(color=CATEGORICAL),
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "axes.axisbelow": True,
    })


def new_figure(width: float = 8, height: float = 4.2, **kwargs):
    """Create a figure/axes pair with the house style."""
    return plt.subplots(figsize=(width, height), **kwargs)


def title(ax, main: str, sub: str | None = None) -> None:
    """Left-aligned bold title with an optional secondary subtitle line."""
    ax.set_title(main, pad=22 if sub else 10)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9.5,
                color=TEXT_SECONDARY, ha="left", va="bottom")


def source_note(fig, text: str = "Source: NPS Visitor Use Statistics (by-month), via "
                                  "responsible-datasets-in-context.com") -> None:
    fig.text(0.01, -0.02, text, fontsize=7.5, color=TEXT_MUTED, ha="left", va="top")


def end_label(ax, x, y, text: str, color: str = TEXT_SECONDARY, dx: float = 0.4,
              fontsize: float = 9) -> None:
    """Direct label at the right-hand end of a line. Text uses a text token, never the series colour;
    identity comes from the end marker drawn in the series colour."""
    ax.scatter([x], [y], s=36, color=color, zorder=5, edgecolor=SURFACE, linewidth=1.5)
    ax.text(x + dx, y, text, fontsize=fontsize, color=TEXT_SECONDARY, va="center", ha="left")


def save(fig, name: str, formats: tuple[str, ...] = ("png", "svg")) -> None:
    """Save the figure under figures/ in each format (PNG for docs, SVG for print/zoom)."""
    FIG_DIR.mkdir(exist_ok=True)
    for ext in formats:
        fig.savefig(FIG_DIR / f"{name}.{ext}")


def pct_axis(ax, axis: str = "y", decimals: int = 0) -> None:
    fmt = mpl.ticker.PercentFormatter(xmax=1.0, decimals=decimals)
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def thousands_axis(ax, axis: str = "y") -> None:
    fmt = mpl.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def millions_axis(ax, axis: str = "y") -> None:
    fmt = mpl.ticker.FuncFormatter(lambda v, _: f"{v/1e6:,.0f}M")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)
