# 21 - Seaborn

<!-- nav:start -->
**Previous:** [20 - Matplotlib](20_matplotlib.md) | **Index:** [All guides](README.md) | **Next:** [22 - Scikit-learn](22_scikit-learn.md)
<!-- nav:end -->

Quick reference for statistical plots with Seaborn (built on matplotlib, works directly with pandas DataFrames).

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Seaborn?

Seaborn is a statistical visualisation library built on Matplotlib. You pass a pandas DataFrame and column names, and it creates attractive, informative charts in one line: distributions, comparisons between categories, relationships, regression lines and correlation heatmaps. It automatically handles grouping (`hue`), colours, legends and confidence intervals.

### Why use it?

- **Less code**: one call replaces many lines of Matplotlib.
- **Built for DataFrames**: refer to columns by name.
- **Statistics included**: averages with error bars, density curves, fitted regression lines.
- **Good defaults**: nice themes and colour palettes out of the box.
- **Fast exploration**: `pairplot` or `heatmap` of correlations gives a quick overview of a dataset.

### Key terms

| Term | Meaning |
|---|---|
| hue | Column used to colour groups |
| Axes-level function | Draws one plot into a Matplotlib Axes (`boxplot`) |
| Figure-level function | Creates a whole figure, can split into facets (`catplot`) |
| Facet | One small plot per category value (`col=`, `row=`) |
| Palette | Set of colours |
| KDE | Smooth estimate of a distribution |

**Where it fits:** needs [17 - Pandas](17_pandas.md) data; customise with [20 - Matplotlib](20_matplotlib.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| seaborn documentation | https://seaborn.pydata.org/ |
| seaborn API reference | https://seaborn.pydata.org/api.html |
| seaborn example gallery | https://seaborn.pydata.org/examples/index.html |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
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
18. [Try It](#18-try-it)

---

## 0. Flags and Parameters

> The meaning of the arguments and parameters used in the seaborn calls below. Explains how a call is built, then lists each parameter with its meaning and example.
>
> Use this when you see `sns.catplot(data=tips, x="day", y="tip", kind="box", col="time")` and want to know what each argument does.

### How a function call is built

```text
sns.boxplot(data=tips, x="day", y="tip", hue="sex")
|   |       |          |        |        |
|   |       |          |        |        +-- colour by this column
|   |       |          |        +----------- column for the y axis
|   |       |          +-------------------- column for the x axis
|   |       +------------------------------- the DataFrame to use
|   +--------------------------------------- plot type
+------------------------------------------- seaborn module
```

- **Positional** arguments come first, in a fixed order. **Keyword** arguments use `name=value` and can be in any order.
- Arguments you leave out use their **default** value (for example no `hue` = one colour).
- See all parameters and defaults: `help(sns.boxplot)`, or `Shift+Tab` inside the brackets in Jupyter.

| Parameter | Used in | Meaning | Example |
|---|---|---|---|
| `data` | all | The DataFrame | `data=tips` |
| `x`, `y` | all | Column names for the axes | `x="day", y="tip"` |
| `hue` | most | Colour by this column | `hue="sex"` |
| `size` | `scatterplot`, `relplot` | Marker size by this column | `size="size"` |
| `style` | `scatterplot`, `lineplot` | Marker / line style by this column | `style="time"` |
| `col`, `row` | figure-level (`relplot`, `catplot`, `displot`, `lmplot`) | One subplot per value of this column | `col="time"` |
| `col_wrap` | figure-level | Max subplots per row | `col_wrap=2` |
| `kind` | `catplot`, `relplot`, `displot`, `jointplot` | Which plot to draw | `kind="box"` |
| `ax` | axes-level | Draw into this matplotlib Axes | `ax=axes[0]` |
| `height`, `aspect` | figure-level | Height of each subplot (inches), width = height x aspect | `height=4, aspect=1.5` |
| `palette` | most | Colour set for `hue` | `palette="Set2"` |
| `color` | most | One colour for everything | `color="steelblue"` |
| `order`, `hue_order` | categorical | Order of categories | `order=["Thur", "Fri"]` |
| `legend` | most | `False` = hide the legend | `legend=False` |
| `bins` | `histplot` | Number of bars | `bins=20` |
| `kde` | `histplot`, `displot` | Add a smooth density curve | `kde=True` |
| `multiple` | `histplot` | Several hue groups: `"layer"`, `"stack"`, `"dodge"`, `"fill"` | `multiple="stack"` |
| `fill` | `kdeplot` | Fill the area under the curve | `fill=True` |
| `estimator` | `barplot`, `pointplot` | What the bar height shows: `"mean"` (default), `"sum"`, `"median"` | `estimator="sum"` |
| `errorbar` | `barplot`, `lineplot` | Error bar type: `("ci", 95)` default, `"sd"`, `None` | `errorbar=None` |
| `split` | `violinplot` | Two hue groups as halves of one violin | `split=True` |
| `jitter` | `stripplot` | Spread points sideways so they overlap less | `jitter=True` |
| `ci` | `regplot`, `lmplot` | Confidence band around the line; `None` = hide | `ci=None` |
| `order` | `regplot` | Polynomial degree of the fitted line (not category order here) | `order=2` |
| `scatter_kws` | `regplot` | Extra options for the points, as a dict | `scatter_kws={"alpha": 0.5}` |
| `annot` | `heatmap` | Write the value in each cell | `annot=True` |
| `fmt` | `heatmap` | Number format of `annot` | `fmt=".2f"` |
| `cmap` | `heatmap` | Colour map | `cmap="coolwarm"` |
| `vmin`, `vmax`, `center` | `heatmap` | Colour scale limits and middle value | `vmin=-1, vmax=1, center=0` |
| `linewidths` | `heatmap` | Gap between cells | `linewidths=0.5` |
| `corner` | `pairplot` | Only lower triangle (no duplicates) | `corner=True` |
| `diag_kind` | `pairplot` | Plot on the diagonal: `"hist"` or `"kde"` | `diag_kind="kde"` |
| `vars` | `pairplot` | Only these columns | `vars=["tip", "size"]` |
| `style`, `context`, `font_scale` | `set_theme` | Background style, overall size, font size factor | `style="whitegrid"` |

## 1. Install and Import

> Installing and importing seaborn. `pip install seaborn`, then `import seaborn as sns` (plus matplotlib to show / save).
>
> Use it for statistical charts from DataFrames with less code than matplotlib.

```powershell
pip install seaborn
```

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
```

## 2. Built-in Datasets

> Sample datasets that ship with seaborn. `sns.load_dataset(name)` downloads a small DataFrame.
>
> Use it for practising, testing a plot type, or reproducing documentation examples.

```python
sns.get_dataset_names()             # list available datasets (needs internet)
tips = sns.load_dataset("tips")     # restaurant bills and tips
iris = sns.load_dataset("iris")     # flower measurements
titanic = sns.load_dataset("titanic")
```

Examples below use `tips` (columns: `total_bill`, `tip`, `sex`, `smoker`, `day`, `time`, `size`).

## 3. How Seaborn Works

> The common pattern of every seaborn function. Pass the DataFrame as `data=` and column names to `x`, `y`, `hue`. Read once; every function in this guide works this way.

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

> Global look: background, grid, font size, colours. `sns.set_theme(style=..., context=..., palette=...)` affects all following plots.
>
> Use it at the start of a notebook to make all charts consistent and presentation-ready.

```python
sns.set_theme()                                     # default seaborn look
sns.set_theme(style="whitegrid", palette="deep", font_scale=1.2)
sns.set_style("ticks")                              # darkgrid, whitegrid, dark, white, ticks
sns.set_context("talk")                             # paper, notebook, talk, poster (size)
sns.despine()                                       # remove top and right borders
```

## 5. Distribution Plots

> How values of one variable are spread. `histplot`, `kdeplot`, `ecdfplot`; `hue` compares groups.
>
> Use it for checking skew, outliers and differences between groups before modelling.

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

> Comparing a numeric value across categories. Counts (`countplot`), estimates (`barplot`), distributions (`boxplot`, `violinplot`), points (`stripplot`).
>
> Use it to answer questions like "Which day has the highest bills?", "how do salaries differ by department?".

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

> Relationship between two numeric variables. `scatterplot` for points, `lineplot` for trends (with confidence band).
>
> Use it for correlation checks, time series by group.

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

> Scatter plot with a fitted trend line. `regplot` / `lmplot` fit a linear (or polynomial) model and draw it.
>
> Use it for quick visual check of a linear relationship before building a model.

```python
sns.regplot(data=tips, x="total_bill", y="tip")             # scatter + fit line
sns.regplot(data=tips, x="total_bill", y="tip", ci=None, scatter_kws={"alpha": 0.5})
sns.regplot(data=tips, x="total_bill", y="tip", order=2)    # polynomial fit
sns.lmplot(data=tips, x="total_bill", y="tip", hue="smoker", col="time")   # figure-level
sns.residplot(data=tips, x="total_bill", y="tip")           # residuals
```

## 9. Heatmap and Correlation

> Colour-coded matrix of values. `sns.heatmap(matrix, annot=True)`; often on `df.corr()` or a pivot table.
>
> Use it for correlation overview of many columns, or a two-category summary table.

```python
corr = tips.corr(numeric_only=True)
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, center=0)

# Pivot then heatmap
table = tips.pivot_table(values="tip", index="day", columns="time", aggfunc="mean")
sns.heatmap(table, annot=True, cmap="Blues", linewidths=0.5)

sns.clustermap(corr, cmap="coolwarm")                       # clustered heatmap
```

## 10. Pair Plot and Joint Plot

> Many relationships in one view. `pairplot` draws every pair of numeric columns; `jointplot` one pair with margins.
>
> Use it for a first exploration of a new dataset with several numeric columns.

```python
sns.pairplot(iris, hue="species")                           # every numeric pair
sns.pairplot(iris, hue="species", corner=True, diag_kind="kde")
sns.pairplot(tips, vars=["total_bill", "tip", "size"])

sns.jointplot(data=tips, x="total_bill", y="tip")           # scatter + both histograms
sns.jointplot(data=tips, x="total_bill", y="tip", kind="reg")   # scatter, kde, hist, hex, reg, resid
```

## 11. Figure-level vs Axes-level

> The two kinds of seaborn functions and how they differ. Axes-level draw into one `ax`; figure-level create their own figure and support facets.
>
> Use it for deciding between `ax=` (combine with subplots) and `col=` / `row=` (facets).

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

> A grid of the same plot split by categories. `col=` / `row=` in figure-level functions, or `FacetGrid` for full control.
>
> Use it for comparing a pattern across groups (lunch vs dinner, smokers vs non-smokers).

```python
sns.relplot(data=tips, x="total_bill", y="tip", col="time", row="smoker")
sns.catplot(data=tips, x="day", y="tip", kind="bar", col="sex", col_wrap=2)

g = sns.FacetGrid(tips, col="time", row="sex")
g.map_dataframe(sns.histplot, x="tip")
g.add_legend()
```

## 13. Colors and Palettes

> Choosing colours. Named palettes via `palette=` or `set_palette`; match the palette type to the data.
>
> Use it for categories (qualitative), low-to-high (sequential), around zero (diverging).

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

> Fine-tuning seaborn charts with matplotlib. Axes-level functions return `ax`; use `ax.set_title`, `ax.bar_label` and so on.
>
> Use it for titles, rotated labels, value labels, moving the legend.

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

See [20 - Matplotlib](20_matplotlib.md) for more options.

## 15. Save a Figure

> Writing seaborn charts to files. `ax.figure.savefig` (axes-level) or `g.savefig` (figure-level).
>
> Use it for charts for reports, slides and READMEs.

```python
# Axes-level
ax = sns.histplot(data=tips, x="tip")
ax.figure.savefig("tips.png", dpi=300, bbox_inches="tight")

# Figure-level
g = sns.pairplot(iris, hue="species")
g.savefig("pairplot.png", dpi=300)
```

## 16. Which Plot to Use

> A lookup table from question to plot type. Find your question on the left, use the plot on the right.
>
> Use this when you know what you want to show but not which chart fits.

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

## 18. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Distribution by group

Histogram of `total_bill` from the tips dataset, coloured by `time`, with a density curve.

<details markdown="1">
<summary>Solution</summary>

```python
tips = sns.load_dataset("tips")
sns.histplot(data=tips, x="total_bill", hue="time", kde=True)
```

</details>

### Exercise 2: Ordered boxplot

Box plot of `tip` per `day` in the order Thur, Fri, Sat, Sun.

<details markdown="1">
<summary>Solution</summary>

```python
sns.boxplot(data=tips, x="day", y="tip", order=["Thur", "Fri", "Sat", "Sun"])
```

</details>

### Exercise 3: Correlation heatmap

Annotated heatmap of the correlations of the numeric tips columns.

<details markdown="1">
<summary>Solution</summary>

```python
sns.heatmap(tips.corr(numeric_only=True), annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)
```

</details>

---

<!-- nav:start -->
**Previous:** [20 - Matplotlib](20_matplotlib.md) | **Index:** [All guides](README.md) | **Next:** [22 - Scikit-learn](22_scikit-learn.md)
<!-- nav:end -->
