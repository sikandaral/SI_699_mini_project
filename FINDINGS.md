# Findings — Visits to American National Parks

Summary of results from `notebooks/sikandar_eda.ipynb`. Full methodology,
code, figures, and robustness checks live in the notebook; this file is a
standalone reference to the findings themselves.

**Data:** NPS Visitor Use Statistics, by-month extract, 1979–2023, 63
parks, via [Responsible Datasets in Context](https://www.responsible-datasets-in-context.com/posts/np-data/).

## Finding 1 — Visitation is de-seasonalizing

The share of national recreation visits occurring in June–August has fallen
by about **1.6 percentage points per decade** (95% CI 1.2–2.0, *p* < 0.001),
from roughly 50% in 1979 to roughly 44% in 2019–2023.

- Robust to weighting parks by visit volume vs. treating every park
  equally, to excluding the COVID-affected 2020–2021 years, and to using
  each park's own best three consecutive months instead of a fixed
  calendar summer.
- Driven by growth in the other nine months, not by summer shrinking:
  Jun–Aug visits rose 28.3M → 36.6M/yr (+29%) between 1979–83 and 2019–23,
  while the other nine months rose 27.6M → 49.9M/yr (+81%). The largest
  single month-share gain went to **March** (+1.8 pp), not to a shoulder month.
- Broad-based: 43 of 62 parks with sufficient history trend toward less
  summer concentration (34 significantly, vs. 9 significantly rising).
  A small cluster of Alaska parks (Katmai, Wrangell–St. Elias, Lake Clark)
  trends the other way, becoming more summer-concentrated as tourism to
  short-season parks grows.

## Finding 2 — Overnight camping is declining relative to visits

Overnight camping per 1,000 recreation visits has fallen significantly
since 1979: tent camping by roughly **14% per decade** and RV camping by
roughly **24% per decade** (both *p* < 0.001). Backcountry camping shows no
significant trend.

- A shift-share decomposition (1979–1983 vs. 2017–2023, rate 118.4 → 59.5
  per 1,000) attributes the change to a **within-park** shift: 105.9% under
  a symmetric split, with the between-park visit mix contributing −5.9%,
  i.e. slightly *offsetting* the decline. (Raw split: within 83.5%, between
  −28.3%, interaction 44.7% — the large interaction is why we report the
  symmetric version.)
- Overnight stays also fell in **absolute** terms, 6.6M → 4.9M per year
  (−27%) while total visits rose 55%, so this is not a denominator effect.
- The decline shows up inside individual long-running, high-traffic parks
  tracked on their own — Yellowstone −43%/decade, Zion −23%, Yosemite −19%
  (all *p* < 0.001) — with one exception: **Grand Canyon shows no
  significant trend** (+6.0%/decade, *p* = 0.14).

## Supporting context

- **Seasonal typology.** Sorting all 63 parks by peak month reveals two
  distinct seasonal profiles: winter/spring-peak desert and southern parks
  (e.g. Big Bend, Saguaro, Joshua Tree) and summer-peak alpine/high-latitude
  parks (e.g. Alaska parks, North Cascades), with most other parks peaking
  in July. This explains why Finding 1 isn't universal — the parks trending
  toward *more* summer concentration are disproportionately the extreme
  summer-peak Alaska parks.
- **2020 shock and recovery.** Every NPS region dropped sharply in 2020,
  but recovered at different speeds by 2022–2023 — treated as a single
  case study and a data-quality note (Carlsbad Caverns' broken counter
  since 2019, Kobuk Valley's 2014–2015 non-reporting gap, and the
  reportedly suppressed 2024 figures), not a generalizable trend.

## Recommended claim for the write-up

*National park visitation has been shifting away from its traditional
summer/overnight pattern for four decades — the June–August visit share
has fallen ~1.6 points/decade and overnight camping per 1,000 visits has
fallen 14–24%/decade, with both trends broad-based across individual parks
rather than driven by a handful of outliers or by 2020's disruption.*

This is preferred over the other candidates (a single-park "most visited"
fact, the seasonal-typology split alone, or the COVID-recovery comparison
alone) because it is quantified with confidence intervals and significance
tests, survives three plausible objections (mix-shift, COVID, definition of
"summer"/"camping rate"), and directly answers *how* visits are changing.

## Limitations

- Recreation-visit counts are estimated, not censused, and counting
  formulas have evolved over 45 years — some of the de-seasonalization
  signal could reflect measurement drift rather than pure behavior change.
- "Recreation visits" exclude commuters, researchers, staff, and Indigenous
  residents of park lands, so findings describe *counted* visitation, not
  visitation in the broadest sense.
- Camping rates are bounded by fixed campsite capacity in popular parks, so
  a flat or declining rate may partly reflect a supply ceiling rather than
  pure declining demand.
- The 2020 regional-recovery pattern is a single event, not a repeated,
  generalizable pattern.
- Findings apply to the 63 units designated "National Park" only; national
  monuments, seashores, and historic sites are not in this dataset and may
  behave differently.

## Potential topics for further exploration

1. Weekday/weekend and holiday timing (needs day-level data).
2. Climate (temperature/precipitation anomalies) as a driver of seasonal
   shifts, especially in the Alaska parks trending toward more summer
   concentration.
3. Campground capacity/reservation data, to separate demand-side change
   from a supply-side ceiling in Finding 2.
4. Timed-entry reservation systems (e.g. Zion, Glacier) as a possible
   policy driver of de-seasonalization.
5. `NonRecreationVisits` as a cross-check on counting-methodology drift.
6. Extending the analysis past 2023, once a by-month 2024–2025 extract is
   available.
