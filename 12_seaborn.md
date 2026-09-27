# 12 - Seaborn

Quick reference for statistical plots with Seaborn (built on matplotlib, works directly with pandas DataFrames).

## Contents

1. [Install and Import](#1-install-and-import)
2. [Built-in Datasets](#2-built-in-datasets)
3. [How Seaborn Works](#3-how-seaborn-works)
4. [Theme and Style](#4-theme-and-style)
5. [Distribution Plots](#5-distribution-plots)
6. [Categorical Plots](#6-categorical-plots)
7. [Relationship Plots](#7-relationship-plots)
8. [Regression Plots](#8-regression-plots)
9. [Heatmap and Correlation](#9-heatmap-and-correlation)
10. [Pair Plot and Joint Plot](#10-pair-plot-and-joint-plot)
11. [Figure-level vs Axes-level](#11-figure-level-vs-axes-level)
12. [Facets (Grid of Plots)](#12-facets-grid-of-plots)
13. [Colors and Palettes](#13-colors-and-palettes)
14. [Customize with Matplotlib](#14-customize-with-matplotlib)
15. [Save a Figure](#15-save-a-figure)
16. [Which Plot to Use](#16-which-plot-to-use)
17. [Troubleshooting](#17-troubleshooting)

---

## 1. Install and Import

```powershell
pip install seaborn
```

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
```

## 2. Built-in Datasets

```python
sns.get_dataset_names()             # list available datasets (needs internet)
tips = sns.load_dataset("tips")     # restaurant bills and tips
iris = sns.load_dataset("iris")     # flower measurements
titanic = sns.load_dataset("titanic")
```

Examples below use `tips` (columns: `total_bill`, `tip`, `sex`, `smoker`, `day`, `time`, `size`).

## 3. How Seaborn Works

Pass a DataFrame to `data=` and column **names** to `x=`, `y=`, `hue=`:

```python
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="time")
plt.show()
```

| Parameter | Meaning |
|---|---|
| `data` | DataFrame |
| `x`, `y` | column names |
| `hue` | color by this column |
| `size` | marker size by this column |
| `style` | marker / line style by this column |
| `col`, `row` | split into subplots (figure-level functions only) |
| `palette` | color set |
| `order`, `hue_order` | category order |
| `ax` | draw into an existing matplotlib Axes |

## 4. Theme and Style

```python
sns.set_theme()                                     # default seaborn look
sns.set_theme(style="whitegrid", palette="deep", font_scale=1.2)
sns.set_style("ticks")                              # darkgrid, whitegrid, dark, white, ticks
sns.set_context("talk")                             # paper, notebook, talk, poster (size)
sns.despine()                                       # remove top and right borders
```

## 5. Distribution Plots

One variable: how are values spread?

```python
sns.histplot(data=tips, x="total_bill")                     # histogram
sns.histplot(data=tips, x="total_bill", bins=20, kde=True)  # + density curve
sns.histplot(data=tips, x="total_bill", hue="time", multiple="stack")   # layer, stack, dodge, fill
sns.kdeplot(data=tips, x="total_bill", hue="time", fill=True)          # smooth density
sns.ecdfplot(data=tips, x="total_bill")                     # cumulative
sns.rugplot(data=tips, x="total_bill")                      # ticks per value
sns.displot(data=tips, x="total_bill", col="time", kde=True)            # figure-level, facets
```

## 6. Categorical Plots

One category axis and one numeric axis.

```python
# Counts
sns.countplot(data=tips, x="day")                           # rows per category
sns.countplot(data=tips, x="day", hue="sex")

# Estimate (mean + confidence interval)
sns.barplot(data=tips, x="day", y="total_bill")             # mean with error bar
sns.barplot(data=tips, x="day", y="total_bill", estimator="sum", errorbar=None)
sns.pointplot(data=tips, x="day", y="total_bill", hue="sex")

# Distribution per category
sns.boxplot(data=tips, x="day", y="total_bill")             # median, quartiles, outliers
sns.violinplot(data=tips, x="day", y="total_bill", hue="sex", split=True)
sns.boxenplot(data=tips, x="day", y="total_bill")           # for large data

# Every point
sns.stripplot(data=tips, x="day", y="total_bill", jitter=True)
sns.swarmplot(data=tips, x="day", y="total_bill")           # no overlap

# Combine: box + points
sns.boxplot(data=tips, x="day", y="total_bill", color="lightgray")
sns.stripplot(data=tips, x="day", y="total_bill", size=3)

# Figure-level version of all of the above
sns.catplot(data=tips, x="day", y="total_bill", kind="box", col="time")
```

Horizontal: swap `x` and `y` (category on `y`).

## 7. Relationship Plots

Two numeric variables.

```python
sns.scatterplot(data=tips, x="total_bill", y="tip")
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="day", size="size", style="time")
sns.lineplot(data=df, x="month", y="sales")                 # mean + confidence band
sns.lineplot(data=df, x="month", y="sales", hue="region", errorbar=None, marker="o")
sns.relplot(data=tips, x="total_bill", y="tip", col="time", hue="smoker")   # figure-level
sns.relplot(data=df, x="month", y="sales", kind="line")
```

## 8. Regression Plots

```python
sns.regplot(data=tips, x="total_bill", y="tip")             # scatter + fit line
sns.regplot(data=tips, x="total_bill", y="tip", ci=None, scatter_kws={"alpha": 0.5})
sns.regplot(data=tips, x="total_bill", y="tip", order=2)    # polynomial fit
sns.lmplot(data=tips, x="total_bill", y="tip", hue="smoker", col="time")   # figure-level
sns.residplot(data=tips, x="total_bill", y="tip")           # residuals
```

## 9. Heatmap and Correlation

```python
corr = tips.corr(numeric_only=True)
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, center=0)

# Pivot then heatmap
table = tips.pivot_table(values="tip", index="day", columns="time", aggfunc="mean")
sns.heatmap(table, annot=True, cmap="Blues", linewidths=0.5)

sns.clustermap(corr, cmap="coolwarm")                       # clustered heatmap
```

## 10. Pair Plot and Joint Plot

```python
sns.pairplot(iris, hue="species")                           # every numeric pair
sns.pairplot(iris, hue="species", corner=True, diag_kind="kde")
sns.pairplot(tips, vars=["total_bill", "tip", "size"])

sns.jointplot(data=tips, x="total_bill", y="tip")           # scatter + both histograms
sns.jointplot(data=tips, x="total_bill", y="tip", kind="reg")   # scatter, kde, hist, hex, reg, resid
```

## 11. Figure-level vs Axes-level

| Figure-level (own figure, supports `col` / `row`) | Axes-level (draws into one `ax`) |
|---|---|
| `displot` | `histplot`, `kdeplot`, `ecdfplot`, `rugplot` |
| `catplot` | `countplot`, `barplot`, `boxplot`, `violinplot`, `stripplot`, `swarmplot`, `pointplot` |
| `relplot` | `scatterplot`, `lineplot` |
| `lmplot` | `regplot` |
| `pairplot`, `jointplot` | - |

```python
# Axes-level: put into matplotlib subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.histplot(data=tips, x="tip", ax=axes[0])
sns.boxplot(data=tips, x="day", y="tip", ax=axes[1])

# Figure-level: set size with height / aspect (not figsize)
g = sns.catplot(data=tips, x="day", y="tip", kind="box", height=4, aspect=1.5)
g.set_axis_labels("Day", "Tip")
g.set_titles("{col_name}")
g.figure.suptitle("Tips by Day", y=1.03)
```

## 12. Facets (Grid of Plots)

```python
sns.relplot(data=tips, x="total_bill", y="tip", col="time", row="smoker")
sns.catplot(data=tips, x="day", y="tip", kind="bar", col="sex", col_wrap=2)

g = sns.FacetGrid(tips, col="time", row="sex")
g.map_dataframe(sns.histplot, x="tip")
g.add_legend()
```

## 13. Colors and Palettes

```python
sns.color_palette()                                 # current palette
sns.set_palette("Set2")                             # default for all plots
sns.boxplot(data=tips, x="day", y="tip", palette="pastel", hue="day", legend=False)
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="size", palette="viridis")
sns.barplot(data=tips, x="day", y="tip", color="steelblue")    # one color
```

| Type | Use for | Examples |
|---|---|---|
| Qualitative | categories | `deep`, `muted`, `pastel`, `Set2`, `tab10`, `colorblind` |
| Sequential | low to high | `Blues`, `viridis`, `rocket`, `mako` |
| Diverging | negative / zero / positive | `coolwarm`, `vlag`, `RdBu`, `icefire` |

## 14. Customize with Matplotlib

Axes-level functions return a matplotlib `ax`:

```python
ax = sns.barplot(data=tips, x="day", y="tip")
ax.set_title("Average Tip by Day")
ax.set_xlabel("") ; ax.set_ylabel("Tip (USD)")
ax.tick_params(axis="x", rotation=45)
ax.bar_label(ax.containers[0], fmt="%.2f")         # value on bars
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))   # legend outside
plt.tight_layout()
plt.show()
```

See [11 - Matplotlib](11_matplotlib.md) for more options.

## 15. Save a Figure

```python
# Axes-level
ax = sns.histplot(data=tips, x="tip")
ax.figure.savefig("tips.png", dpi=300, bbox_inches="tight")

# Figure-level
g = sns.pairplot(iris, hue="species")
g.savefig("pairplot.png", dpi=300)
```

## 16. Which Plot to Use

| Question | Plot |
|---|---|
| How is one numeric column distributed? | `histplot`, `kdeplot`, `boxplot` |
| How many rows per category? | `countplot` |
| Compare an average across categories | `barplot`, `pointplot` |
| Compare distributions across categories | `boxplot`, `violinplot`, `stripplot` |
| Relationship between two numeric columns | `scatterplot`, `regplot`, `jointplot` |
| Trend over time | `lineplot` |
| Correlation between many columns | `heatmap` of `df.corr()`, `pairplot` |
| Same plot split by a category | `col=` / `row=` in `relplot`, `catplot`, `displot` |

## 17. Troubleshooting

| Problem | Fix |
|---|---|
| Nothing appears (script) | Add `plt.show()` |
| `figsize` has no effect | Figure-level function: use `height=` and `aspect=` |
| `ax=` not accepted | Figure-level functions (`catplot`, `relplot`...) create their own figure; use the axes-level version |
| `FutureWarning: Passing palette without hue` | Add `hue=` (same column as x) and `legend=False` |
| `ValueError: could not convert string to float` in heatmap | Use `df.corr(numeric_only=True)` or select numeric columns |
| Plots stack on top of each other | Call `plt.figure()` or `plt.subplots()` before each new plot |
| `load_dataset` fails | Needs internet; use your own DataFrame |
| Categories in wrong order | `order=["Thur", "Fri", "Sat", "Sun"]` |
