import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.lines as mlines
from matplotlib.colors import LinearSegmentedColormap

df = pd.read_csv("../data/US-National-Parks_Use_1979-2023_By-Month.csv",
                  encoding="utf-8-sig")
df.columns = df.columns.str.strip()
for c in ["ParkName", "UnitCode", "ParkType", "Region", "State"]:
    df[c] = df[c].str.strip()

recent = df[df.Year.between(2019, 2023)]
pm = recent.groupby(["ParkName", "Month"])["RecreationVisits"].sum().unstack("Month")
pmn = pm.div(pm.sum(1), axis=0)
peak = pmn.idxmax(axis=1)
order = peak.sort_values(kind="stable").index
mat = pmn.loc[order]

BLUE = "#2a78d6"
DARK_BLUE = "#0d2f5c"
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"

cmap = LinearSegmentedColormap.from_list("blue_seq", [SURFACE, BLUE, DARK_BLUE])
mpl.rcParams["font.family"] = "DejaVu Sans"

fig = plt.figure(figsize=(9.8, 12.8), dpi=200)
fig.patch.set_facecolor(SURFACE)
# reserve a left margin for cluster labels, right margin for colorbar
ax = fig.add_axes([0.34, 0.045, 0.55, 0.87])
ax.set_facecolor(SURFACE)

n = len(mat.index)
im = ax.imshow(mat.values, aspect="auto", cmap=cmap, vmin=0, vmax=mat.values.max())

month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
ax.set_xticks(range(12))
ax.set_xticklabels(month_labels, fontsize=10, color=TEXT_SECONDARY)
ax.set_yticks(range(n))
ax.set_yticklabels(mat.index, fontsize=8.3, color=TEXT_PRIMARY)
ax.tick_params(length=0)
for spine in ax.spines.values():
    spine.set_visible(False)

ax.set_xticks(np.arange(-0.5, 12, 1), minor=True)
ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
ax.grid(which="minor", color=SURFACE, linewidth=1.5)
ax.tick_params(which="minor", length=0)

cbar = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.02)
cbar.set_label("Share of 2019–2023 visits", fontsize=9.5, color=TEXT_SECONDARY)
cbar.ax.tick_params(labelsize=8, labelcolor=TEXT_SECONDARY)
cbar.outline.set_visible(False)

desert_n = int((peak.loc[order] <= 4).sum())
alpine_n = int((peak.loc[order] >= 8).sum())

# convert data y-coords (row index, axes coords) to figure coords for clean external annotation
def row_to_fig_y(row):
    disp = ax.transData.transform((0, row))
    return fig.transFigure.inverted().transform(disp)[1]

top_y = row_to_fig_y(-0.5)
desert_bottom_y = row_to_fig_y(desert_n - 0.5)
alpine_top_y = row_to_fig_y(n - alpine_n - 0.5)
bottom_y = row_to_fig_y(n - 0.5)

bracket_x = 0.045
fig.add_artist(mlines.Line2D([bracket_x, bracket_x], [desert_bottom_y, top_y],
                              color=BLUE, lw=3, solid_capstyle="round", transform=fig.transFigure))
fig.text(bracket_x + 0.015, (top_y + desert_bottom_y) / 2,
          "Winter/spring peak\n(desert & southern\nparks)",
          fontsize=9.3, color=TEXT_SECONDARY, ha="left", va="center")

fig.add_artist(mlines.Line2D([bracket_x, bracket_x], [bottom_y, alpine_top_y],
                              color=DARK_BLUE, lw=3, solid_capstyle="round", transform=fig.transFigure))
fig.text(bracket_x + 0.015, (alpine_top_y + bottom_y) / 2,
          "Summer peak\n(alpine & high-\nlatitude parks)",
          fontsize=9.3, color=TEXT_SECONDARY, ha="left", va="center")

fig.suptitle("Every park has its own peak season", fontsize=17, fontweight="bold",
             color=TEXT_PRIMARY, x=0.02, ha="left", y=0.985)
fig.text(0.02, 0.955, "Monthly share of visits, 63 national parks, sorted by peak month (2019–2023 avg.)",
          fontsize=10.5, color=TEXT_SECONDARY, ha="left")

fig.text(0.02, 0.006,
         "Source: NPS Visitor Use Statistics, via responsible-datasets-in-context.com  |  "
         "SI 699 mini project EDA",
         fontsize=8, color=TEXT_SECONDARY)

out = "park_seasonality_heatmap.png"
plt.savefig(out, facecolor=SURFACE)
print("saved", out, "desert_n", desert_n, "alpine_n", alpine_n)
