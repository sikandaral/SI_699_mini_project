"""Data loading, cleaning, and statistical helpers for the national-parks EDA."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "US-National-Parks_Use_1979-2023_By-Month.csv"
SUMMER = (6, 7, 8)
COUNT_COLS = ["RecreationVisits", "NonRecreationVisits", "TentCampers", "RVCampers", "Backcountry"]
TEXT_COLS = ["ParkName", "UnitCode", "ParkType", "Region", "State"]


def load_by_month(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the by-month file and apply light, documented cleaning.

    - strips the UTF-8 BOM and trailing whitespace in text columns (e.g. ``"Northeast "``)
    - adds a month-start ``Date`` column
    - flags months with zero recreation visits (``ZeroMonth``) and park-years containing
      any such month (``ZeroYear``) so non-reporting can be excluded in sensitivity checks
    """
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    for col in TEXT_COLS:
        df[col] = df[col].str.strip()
    df["Date"] = pd.to_datetime(dict(year=df.Year, month=df.Month, day=1))
    df["ZeroMonth"] = df["RecreationVisits"].eq(0)
    zero_years = df.groupby(["UnitCode", "Year"])["ZeroMonth"].transform("any")
    df["ZeroYear"] = zero_years
    return df.sort_values(["ParkName", "Date"]).reset_index(drop=True)


def data_dictionary() -> pd.DataFrame:
    rows = [
        ("ParkName", "Park name as published by NPS (63 parks designated 'National Park')"),
        ("UnitCode", "Four-letter NPS unit code (stable key)"),
        ("ParkType", "Constant: 'National Park'"),
        ("Region", "NPS administrative region (6 values)"),
        ("State", "Primary state (30 values); multi-state parks list one"),
        ("Year / Month", "Calendar year (1979-2023) and month (1-12)"),
        ("RecreationVisits", "Counted recreation visits (the headline visitation metric)"),
        ("NonRecreationVisits", "Commuter, through-traffic, staff, research visits"),
        ("TentCampers / RVCampers", "Overnight stays in front-country campgrounds, by shelter type"),
        ("Backcountry", "Overnight stays in the backcountry (permit-based)"),
    ]
    return pd.DataFrame(rows, columns=["Field", "Meaning"]).set_index("Field")


# --- Seasonality metrics ----------------------------------------------------

def monthly_matrix(df: pd.DataFrame, by: list[str] | None = None,
                   value: str = "RecreationVisits") -> pd.DataFrame:
    """Pivot to a (group x Month) matrix of summed values."""
    keys = (by or []) + ["Month"]
    return df.groupby(keys)[value].sum().unstack("Month")


def summer_share(matrix: pd.DataFrame) -> pd.Series:
    """Share of the row total that falls in June-August."""
    return matrix[list(SUMMER)].sum(axis=1) / matrix.sum(axis=1)


def peak3_share(matrix: pd.DataFrame) -> pd.Series:
    """Share in the best three *consecutive* months of each row (wraps Dec->Jan).

    Park-agnostic alternative to summer share: a desert park peaking in Feb-Apr is measured
    on its own peak, not on a calendar summer it does not have.
    """
    vals = matrix[list(range(1, 13))].to_numpy(dtype=float)
    wrapped = np.concatenate([vals, vals[:, :2]], axis=1)
    windows = np.stack([wrapped[:, i:i + 3].sum(axis=1) for i in range(12)], axis=1)
    return pd.Series(windows.max(axis=1) / vals.sum(axis=1), index=matrix.index)


# --- Trend estimation ---------------------------------------------------------

def trend(series: pd.Series, per: float = 10.0, log: bool = False, maxlags: int = 2) -> pd.Series:
    """OLS of ``series`` on year with HAC (Newey-West) standard errors.

    Returns slope per ``per`` years (default: per decade), its 95% CI, p-value and n.
    With ``log=True`` the slope is converted to a percent change per ``per`` years.
    """
    s = series.dropna()
    x = s.index.get_level_values(-1).to_numpy(dtype=float) if isinstance(s.index, pd.MultiIndex) \
        else s.index.to_numpy(dtype=float)
    y = np.log(s.to_numpy(dtype=float)) if log else s.to_numpy(dtype=float)
    model = sm.OLS(y, sm.add_constant(x)).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    b, (lo, hi) = model.params[1] * per, model.conf_int()[1] * per
    if log:
        b, lo, hi = [(np.exp(v) - 1) * 100 for v in (b, lo, hi)]
    return pd.Series({"slope": b, "ci_low": lo, "ci_high": hi, "p_value": model.pvalues[1], "n": len(s)})


def park_trends(share_by_park_year: pd.Series, min_years: int = 20, **kwargs) -> pd.DataFrame:
    """Apply :func:`trend` to each park's annual series (index: ParkName, Year)."""
    out = {}
    for park, s in share_by_park_year.groupby(level=0):
        s = s.droplevel(0).dropna()
        if len(s) >= min_years:
            out[park] = trend(s, **kwargs)
    res = pd.DataFrame(out).T.sort_values("slope")
    res["significant"] = res["p_value"] < 0.05
    return res


def shift_share(df: pd.DataFrame, early: tuple[int, int], late: tuple[int, int],
                numerator: list[str], denominator: str = "RecreationVisits") -> pd.Series:
    """Decompose the change in an aggregate rate into within-park, between-park (mix) and interaction terms.

    rate = sum_p w_p * r_p, with w = visit share, r = numerator / denominator.
    """
    def period(y0, y1):
        g = df[df.Year.between(y0, y1)].groupby("ParkName")[[denominator] + numerator].sum()
        g["num"] = g[numerator].sum(axis=1)
        return g
    a, b = period(*early), period(*late)
    common = a.index.intersection(b.index)
    a, b = a.loc[common], b.loc[common]
    wa, wb = a[denominator] / a[denominator].sum(), b[denominator] / b[denominator].sum()
    ra, rb = a["num"] / a[denominator], b["num"] / b[denominator]
    total = (wb * rb).sum() - (wa * ra).sum()
    within = (wa * (rb - ra)).sum()
    between = ((wb - wa) * ra).sum()
    interaction = ((wb - wa) * (rb - ra)).sum()
    return pd.Series({"rate_early": (wa * ra).sum(), "rate_late": (wb * rb).sum(), "total_change": total,
                      "within_share": within / total, "between_share": between / total,
                      "interaction_share": interaction / total,
                      # symmetric (average-weight) split: the interaction term is divided evenly,
                      # which avoids reporting a large residual that is hard to interpret
                      "within_sym": (within + interaction / 2) / total,
                      "between_sym": (between + interaction / 2) / total})
