# SI 699 Mini Project: visits to American National Parks

Exploratory analysis of NPS by-month visitation data (1979–2023, 63 parks)
to identify a defensible claim about how people visit national parks.

## Structure

- `data/US-National-Parks_Use_1979-2023_By-Month.csv`, the raw by-month NPS
  visitor-use data, from [Responsible Datasets in Context](https://www.responsible-datasets-in-context.com/posts/np-data/).
- `src/npdata.py`, data loading, cleaning, and statistical helpers
  (trend regression with HAC standard errors, within-park panel regression,
  seasonality indices, shift-share decomposition).
- `src/npviz.py`, the shared, accessibility-checked plotting style (colour
  palette, fonts, labeling conventions) used by every figure.
- `notebooks/sikandar_eda.ipynb`, the analysis notebook: methodology,
  two statistically-backed findings (de-seasonalization of visits;
  declining overnight camping relative to visits), supporting context,
  limitations, and a recommended claim for the write-up.
- `figures/`, every chart the notebook produces, saved as PNG and SVG.

## Reproducing

```
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace notebooks/sikandar_eda.ipynb
```

## Source

NPS Visitor Use Statistics (by-month extract), distributed via
[Responsible Datasets in Context](https://www.responsible-datasets-in-context.com/posts/np-data/)
(Walsh et al.); see the accompanying
[data essay](https://www.responsible-datasets-in-context.com/posts/np-data/?tab=data-essay)
for collection methodology and caveats, cited throughout the notebook.
