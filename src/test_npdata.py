"""Self-checks for the statistical helpers. Run: python -m src.test_npdata"""
import numpy as np
import pandas as pd

from . import npdata as nd


def month_row(**counts):
    """One calendar as a (1 x 12) matrix, e.g. month_row(jul=100)."""
    names = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    row = {m: 0.0 for m in range(1, 13)}
    for name, value in counts.items():
        row[names.index(name) + 1] = float(value)
    # counts are per-day-normalised inside, so scale by month length to hit exact midpoints
    return pd.DataFrame([{m: row[m] * nd.DAYS_IN_MONTH[m - 1] for m in range(1, 13)}])


def test_peak_month_is_on_a_1_to_12_scale():
    for i, name in enumerate(["jan", "apr", "jul", "dec"]):
        got = nd.seasonality_indices(month_row(**{name: 100})).peak_month.iloc[0]
        assert abs(got - (i * 3 + 1 if name != "dec" else 12)) < 1e-9, (name, got)


def test_flat_calendar_is_aseasonal():
    flat = nd.seasonality_indices(month_row(**{m: 100 for m in
                                               ["jan", "feb", "mar", "apr", "may", "jun",
                                                "jul", "aug", "sep", "oct", "nov", "dec"]})).iloc[0]
    assert flat.concentration < 1e-9
    assert abs(flat.eff_months - 12) < 1e-6


def test_concentration_misses_bimodal_but_eff_months_does_not():
    """The documented weakness: offsetting peaks cancel to concentration 0."""
    bimodal = nd.seasonality_indices(month_row(jan=100, jul=100)).iloc[0]
    assert bimodal.concentration < 1e-9          # reads as "no dominant season"
    assert abs(bimodal.eff_months - 2) < 1e-6    # but only 2 effective months


def test_trend_recovers_a_known_slope():
    years = np.arange(1979, 2024)
    fit = nd.trend(pd.Series(0.5 - 0.002 * (years - 1979), index=years))
    assert abs(fit.slope - (-0.02)) < 1e-9       # -0.002/yr -> -0.02/decade
    assert fit.ci_low < fit.slope < fit.ci_high


def test_shift_share_components_sum_to_the_total():
    df = nd.load_by_month()
    d = nd.shift_share(df, (1979, 1983), (2017, 2023), ["TentCampers", "RVCampers"])
    assert abs(d.within_share + d.between_share + d.interaction_share - 1) < 1e-9
    assert abs(d.within_sym + d.between_sym - 1) < 1e-9


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
