"""Regenerate every number and figure used in the write-up.

Run: python -m src.report   (prints the stats block, writes figures/report_*.png)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import npdata as nd
from . import npviz as viz

CAMP = ["TentCampers", "RVCampers", "Backcountry"]
MONTHS = "J F M A M J J A S O N D".split()


def summer_share_by_year(df: pd.DataFrame, equal_weight: bool = False) -> pd.Series:
    """National June-Aug share of recreation visits, per year.

    equal_weight=True averages each park's own share instead of pooling visits,
    so the answer is not dominated by the handful of largest parks.
    """
    if equal_weight:
        m = nd.monthly_matrix(df, by=["ParkName", "Year"])
        return nd.summer_share(m).groupby(level="Year").mean()
    return nd.summer_share(nd.monthly_matrix(df, by=["Year"]))


def camping_rate_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Overnight stays per 1,000 recreation visits, nationally, per year."""
    g = df.groupby("Year")[["RecreationVisits"] + CAMP].sum()
    return g[CAMP].div(g["RecreationVisits"], axis=0) * 1000


def stats(df: pd.DataFrame) -> dict:
    out = {}
    pooled = summer_share_by_year(df)
    out["summer_pooled"] = nd.trend(pooled)
    out["summer_equal"] = nd.trend(summer_share_by_year(df, equal_weight=True))
    out["summer_ex_covid"] = nd.trend(pooled.drop([2020, 2021]))
    out["summer_peak3"] = nd.trend(nd.peak3_share(nd.monthly_matrix(df, by=["Year"])))
    out["summer_1979"], out["summer_2023"] = pooled.loc[1979], pooled.loc[2023]
    out["summer_recent"] = pooled.loc[2019:2023].mean()

    # Per-park trends: is the national move broad-based or a few big parks?
    park_year = nd.summer_share(nd.monthly_matrix(df, by=["ParkName", "Year"]))
    pt = nd.park_trends(park_year)
    out["park_trends"] = pt
    out["n_parks"] = len(pt)
    out["n_down"] = int((pt.slope < 0).sum())
    out["n_down_sig"] = int(((pt.slope < 0) & pt.significant).sum())
    out["n_up_sig"] = int(((pt.slope > 0) & pt.significant).sum())

    rates = camping_rate_by_year(df)
    for col in CAMP:
        out[f"trend_{col}"] = nd.trend(rates[col], log=True)
    out["rate_first"] = rates.loc[1979]
    out["rate_last"] = rates.loc[2023]
    out["shift_share"] = nd.shift_share(df, (1979, 1983), (2017, 2023), CAMP)

    # Same decline inside single long-running parks -> not a composition artefact.
    big = ["Yellowstone NP", "Yosemite NP", "Grand Canyon NP", "Zion NP"]
    rows = {}
    for park in big:
        sub = df[df.ParkName == park]
        g = sub.groupby("Year")[["RecreationVisits"] + CAMP].sum()
        rate = g[CAMP].sum(axis=1) / g["RecreationVisits"] * 1000
        rows[park] = nd.trend(rate, log=True)
    out["big_parks"] = pd.DataFrame(rows).T

    # Is de-seasonalisation summer shrinking, or the shoulders growing? Compare
    # absolute levels, not shares, between the first and last five reporting years.
    early, late = df[df.Year.between(1979, 1983)], df[df.Year.between(2019, 2023)]
    per_year = lambda d, months: d[d.Month.isin(months)].RecreationVisits.sum() / 5
    out["levels"] = pd.Series({
        "summer_early": per_year(early, nd.SUMMER), "summer_late": per_year(late, nd.SUMMER),
        "other_early": per_year(early, set(range(1, 13)) - set(nd.SUMMER)),
        "other_late": per_year(late, set(range(1, 13)) - set(nd.SUMMER)),
    })
    out["month_share"] = pd.DataFrame({
        "early": early.groupby("Month").RecreationVisits.sum() / early.RecreationVisits.sum(),
        "late": late.groupby("Month").RecreationVisits.sum() / late.RecreationVisits.sum()})

    # Camping: a falling *rate* could be pure denominator growth. Check the numerator.
    out["overnight_abs"] = pd.Series({
        "early": early[CAMP].sum().sum() / 5, "late": late[CAMP].sum().sum() / 5})
    return out


# --- Figures ----------------------------------------------------------------

def fig_summer(df: pd.DataFrame, s: dict) -> None:
    # peak-3-consecutive-months is omitted here: nationally Jun-Aug *is* the peak window,
    # so the two lines coincide. It is reported in the robustness table instead.
    pooled, equal = summer_share_by_year(df), summer_share_by_year(df, equal_weight=True)
    fig, ax = viz.new_figure(8, 3.9)
    for series, color, label, lw in [(equal, viz.ORANGE, "Every park weighted equally", 1.6),
                                     (pooled, viz.BLUE, "Weighted by visits", 2.2)]:
        ax.plot(series.index, series.values, color=color, label=label, linewidth=lw)
    fit = np.poly1d(np.polyfit(pooled.index, pooled.values, 1))
    ax.plot(pooled.index, fit(pooled.index), color=viz.DARK_BLUE, linestyle=(0, (4, 3)), linewidth=1.2)
    for series, color in [(equal, viz.ORANGE), (pooled, viz.BLUE)]:
        viz.end_label(ax, series.index[-1], series.iloc[-1], f"{series.iloc[-1]:.0%}", color=color)
    ax.annotate("2020", xy=(2020, pooled.loc[2020]), xytext=(2011, pooled.loc[2020] - 0.035),
                fontsize=8.5, color=viz.TEXT_MUTED,
                arrowprops=dict(arrowstyle="-", color=viz.TEXT_MUTED, linewidth=0.8))
    viz.pct_axis(ax)
    ax.set_xlim(1978, 2029)
    ax.set_xlabel("Year")
    ax.set_ylabel("Share of annual recreation visits")
    viz.title(ax, "Peak-season concentration has fallen for four decades",
              f"Jun–Aug share: {s['summer_pooled'].slope*100:+.2f} pp/decade "
              f"(95% CI {s['summer_pooled'].ci_low*100:.2f} to {s['summer_pooled'].ci_high*100:.2f}, p<0.001)")
    ax.legend(loc="lower left", ncol=3)
    viz.source_note(fig)
    viz.save(fig, "report_summer_share")


def fig_park_trends(s: dict) -> None:
    pt = s["park_trends"].copy()
    pt["pp"] = pt.slope * 100  # percentage points per decade
    fig, ax = viz.new_figure(8, 3.4)
    colors = np.where(pt.pp < 0, viz.BLUE, viz.ORANGE)
    colors = np.where(pt.significant, colors, viz.EMPHASIS_GRAY)
    ax.scatter(pt.pp, np.arange(len(pt)), s=26, color=colors, zorder=3)
    ax.hlines(np.arange(len(pt)), 0, pt.pp, color=viz.GRID, linewidth=0.8, zorder=1)
    ax.axvline(0, color=viz.TEXT_MUTED, linewidth=0.9)
    # labels sit to the left of these points: they are the right-most in the chart
    for name in ["Katmai NP & PRES", "Wrangell-St. Elias NP & PRES", "Lake Clark NP & PRES"]:
        if name in pt.index:
            i = pt.index.get_loc(name)
            ax.text(pt.pp.iloc[i] - 0.3, i, name.split(" NP")[0], fontsize=8, ha="right",
                    color=viz.TEXT_SECONDARY, va="center")
    ax.set_xlim(None, pt.pp.max() + 1.2)
    ax.set_yticks([])
    ax.set_xlabel("Change in Jun–Aug share, percentage points per decade")
    ax.set_ylabel(f"Each of {len(pt)} parks")
    viz.title(ax, "The shift is broad-based, not a few big parks",
              f"{s['n_down']} of {len(pt)} parks trend toward less summer concentration; "
              f"{s['n_down_sig']} significantly (p<0.05). Grey = not significant.")
    viz.source_note(fig)
    viz.save(fig, "report_park_trends")


def fig_camping(df: pd.DataFrame, s: dict) -> None:
    rates = camping_rate_by_year(df)
    fig, ax = viz.new_figure(8, 3.9)
    labels = {"TentCampers": "Tent", "RVCampers": "RV", "Backcountry": "Backcountry"}
    for col, color in zip(CAMP, [viz.BLUE, viz.ORANGE, viz.AQUA]):
        ax.plot(rates.index, rates[col], color=color)
        t = s[f"trend_{col}"]
        sig = "n.s." if t.p_value >= 0.05 else f"{t.slope:+.0f}%/decade"
        viz.end_label(ax, rates.index[-1], rates[col].iloc[-1], f"{labels[col]}  {sig}", color=color)
    ax.set_xlim(1978, 2036)
    ax.set_ylim(0, None)
    ax.set_xlabel("Year")
    ax.set_ylabel("Overnight stays per 1,000 recreation visits")
    viz.title(ax, "Visits grew; overnight stays per visit did not",
              "Front-country camping per 1,000 visits has roughly halved since 1979; "
              "backcountry use is flat.")
    viz.source_note(fig)
    viz.save(fig, "report_camping")


def main() -> None:
    viz.apply_style()
    df = nd.load_by_month()
    s = stats(df)
    fig_summer(df, s)
    fig_park_trends(s)
    fig_camping(df, s)

    p = s["summer_pooled"]
    print(f"parks={df.ParkName.nunique()} years={df.Year.min()}-{df.Year.max()} rows={len(df)}")
    print(f"\nSUMMER SHARE {s['summer_1979']:.3f} (1979) -> {s['summer_recent']:.3f} (2019-23 mean), "
          f"{s['summer_2023']:.3f} (2023)")
    for k in ["summer_pooled", "summer_equal", "summer_ex_covid", "summer_peak3"]:
        t = s[k]
        print(f"  {k:<16} {t.slope*100:+.2f} pp/decade  CI [{t.ci_low*100:+.2f},{t.ci_high*100:+.2f}]  "
              f"p={t.p_value:.2g}  n={t.n:.0f}")
    print(f"  parks n={s['n_parks']} down={s['n_down']} down_sig={s['n_down_sig']} up_sig={s['n_up_sig']}")
    print(f"  most positive:\n{(s['park_trends'].slope * 100).tail(4).to_string()}")

    print("\nCAMPING per 1,000 visits")
    for col in CAMP:
        t = s[f"trend_{col}"]
        print(f"  {col:<14} {s['rate_first'][col]:6.1f} -> {s['rate_last'][col]:5.1f}   "
              f"{t.slope:+.1f}%/decade CI [{t.ci_low:+.1f},{t.ci_high:+.1f}] p={t.p_value:.2g}")
    ss = s["shift_share"]
    print(f"  shift-share 1979-83 -> 2017-23: {ss.rate_early*1000:.1f} -> {ss.rate_late*1000:.1f} per 1,000; "
          f"raw within={ss.within_share:.1%} between={ss.between_share:.1%} inter={ss.interaction_share:.1%} | "
          f"symmetric within={ss.within_sym:.1%} between={ss.between_sym:.1%}")
    print("  big parks, total overnight rate:")
    for park, row in s["big_parks"].iterrows():
        print(f"    {park:<18} {row.slope:+.1f}%/decade  p={row.p_value:.2g}")

    lv, ab = s["levels"], s["overnight_abs"]
    print(f"\nLEVELS per year, 1979-83 -> 2019-23 (millions of visits)")
    print(f"  Jun-Aug   {lv.summer_early/1e6:6.1f} -> {lv.summer_late/1e6:6.1f}  "
          f"({lv.summer_late/lv.summer_early-1:+.1%})")
    print(f"  other 9m  {lv.other_early/1e6:6.1f} -> {lv.other_late/1e6:6.1f}  "
          f"({lv.other_late/lv.other_early-1:+.1%})")
    print(f"  overnight stays {ab.early/1e6:.1f}M -> {ab.late/1e6:.1f}M ({ab.late/ab.early-1:+.1%})")
    ms = s["month_share"]
    gain = ((ms.late - ms.early) * 100).round(2)
    print(f"  month-share change (pp):\n{gain.to_string()}")


if __name__ == "__main__":
    main()
