# 21 - Matplotlib

<!-- nav:start -->
**Previous:** [20 - SQL](20_sql.md) | **Index:** [All guides](../README.md) | **Next:** [22 - Seaborn](22_seaborn.md)
<!-- nav:end -->

Quick reference for plotting with Matplotlib (the base plotting library; seaborn and pandas `.plot()` build on it).

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Matplotlib?

Matplotlib is Python's original and most widely used plotting library. It can draw almost any 2D chart: lines, bars, scatter plots, histograms, heatmaps and more, and you control every detail (colours, labels, sizes, layout). A chart is a **Figure** (the whole image) containing one or more **Axes** (individual plots). Seaborn and pandas' `.plot()` are built on top of Matplotlib.

### Why use it?

- **Visualise data** to spot trends, outliers and patterns numbers hide.
- **Full control** over every element for publication-quality charts.
- **Many output formats**: PNG, SVG, PDF for reports, slides and papers.
- **Works everywhere**: scripts, Jupyter, web apps.
- **Foundation**: knowing Matplotlib lets you customise Seaborn and pandas plots too.

### Key terms

| Term | Meaning |
|---|---|
| Figure | The whole image / window |
| Axes | One plot area inside a figure (with its x and y axis) |
| pyplot (`plt`) | The quick, state-based interface |
| Artist | Anything drawn: lines, text, patches |
| Colormap (`cmap`) | Mapping from values to colours |
| DPI | Resolution of saved images |

**Where it fits:** plots data from [17 - NumPy](17_numpy.md) and [18 - Pandas](18_pandas.md); higher-level statistical plots in [22 - Seaborn](22_seaborn.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Matplotlib documentation | https://matplotlib.org/stable/ |
| Matplotlib example gallery | https://matplotlib.org/stable/gallery/index.html |
| Matplotlib cheatsheets | https://matplotlib.org/cheatsheets/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install and Import](#1-install-and-import)
2. [Two Ways to Plot](#2-two-ways-to-plot)
3. [Figure Anatomy](#3-figure-anatomy)
4. [Line Plot](#4-line-plot)
5. [Scatter Plot](#5-scatter-plot)
6. [Bar Chart](#6-bar-chart)
7. [Histogram](#7-histogram)
8. [Box Plot](#8-box-plot)
9. [Pie Chart](#9-pie-chart)
10. [Other Plot Types](#10-other-plot-types)
11. [Titles, Labels and Legend](#11-titles-labels-and-legend)
12. [Axes: Limits, Ticks, Scale, Grid](#12-axes-limits-ticks-scale-grid)
13. [Colors, Markers, Line Styles](#13-colors-markers-line-styles)
14. [Subplots (Several Charts)](#14-subplots-several-charts)
15. [Annotations and Reference Lines](#15-annotations-and-reference-lines)
16. [Figure Size and Styles](#16-figure-size-and-styles)
17. [Plot Directly from Pandas](#17-plot-directly-from-pandas)
18. [Save a Figure](#18-save-a-figure)
19. [Jupyter Notes](#19-jupyter-notes)
20. [Troubleshooting](#20-troubleshooting)
21. [Try It](#21-try-it)

---

## 0. Flags and Parameters

> The meaning of the arguments and parameters used in the matplotlib calls below. Explains how a call is built, then lists each parameter with its meaning and example.
>
> Use this when you see `ax.hist(data, bins=20, alpha=0.7, edgecolor="black")` and want to know what each argument does.

### How a function call is built

```text
ax.plot(x, y, color="red", linestyle="--", label="sales")
|  |    |  |  |
|  |    |  |  +-- keyword arguments: style options, any order
|  |    |  +----- positional: y values
|  |    +-------- positional: x values
|  +------------- method: what to draw
+---------------- the Axes (chart) to draw on
```

- **Positional** arguments come first, in a fixed order. **Keyword** arguments use `name=value` and can be in any order.
- Arguments you leave out use their **default** value (for example a solid line).
- See all parameters and defaults: `help(plt.Axes.plot)`, or `Shift+Tab` inside the brackets in Jupyter.

| Parameter | Used in | Meaning | Example |
|---|---|---|---|
| `nrows, ncols` | `plt.subplots(2, 2)` | Grid of charts: rows, columns | `plt.subplots(2, 2)` |
| `figsize` | `subplots`, `figure` | Width, height in inches | `figsize=(10, 5)` |
| `sharex`, `sharey` | `subplots` | Charts use the same axis range | `sharex=True` |
| `label` | all plot methods | Name shown in the legend | `label="sales"` |
| `color` | all plot methods | One colour: name, hex or `"C0"` | `color="tab:blue"` |
| `c` | `scatter` | Colour per point (list or column of values) | `c=values` |
| `s` | `scatter` | Marker size | `s=50` |
| `cmap` | `scatter`, `imshow` | Colour map for values | `cmap="viridis"` |
| `alpha` | all | Transparency, 0 (invisible) to 1 (solid) | `alpha=0.6` |
| `marker` | `plot`, `scatter` | Point symbol | `marker="o"` |
| `linestyle` | `plot` | Line style: `"-"`, `"--"`, `":"`, `"-."` | `linestyle="--"` |
| `linewidth`, `markersize` | `plot` | Line thickness, point size | `linewidth=2` |
| `"ro--"` | `plot` | Shorthand: colour `r`, marker `o`, style `--` | `ax.plot(x, y, "ro--")` |
| `bins` | `hist` | Number of bars (or list of edges) | `bins=20` |
| `density` | `hist` | Show proportions instead of counts | `density=True` |
| `edgecolor` | `bar`, `hist` | Border colour of bars | `edgecolor="black"` |
| `bottom` | `bar` | Start bars on top of these values (stacked) | `bottom=a` |
| width (3rd argument) | `bar` | Bar width | `ax.bar(x, vals, 0.4)` |
| `yerr` / `fmt` | `errorbar` | Error sizes / marker format | `yerr=err, fmt="o"` |
| `vert` | `boxplot` | `False` = horizontal | `vert=False` |
| `autopct` | `pie` | Label format for percentages | `autopct="%1.1f%%"` |
| `startangle` | `pie` | Rotation of the first slice in degrees | `startangle=90` |
| `loc` | `legend` | Legend position: `"best"`, `"upper left"`, ... | `loc="upper left"` |
| `bbox_to_anchor` | `legend` | Exact legend position; `(1.05, 1)` = just outside right | `bbox_to_anchor=(1.05, 1)` |
| `frameon` | `legend` | `False` = no box around the legend | `frameon=False` |
| `fontsize`, `fontweight` | titles, text | Text size and weight | `fontsize=14, fontweight="bold"` |
| `axis`, `rotation` | `tick_params` | Which axis, rotate tick labels (degrees) | `axis="x", rotation=45` |
| `kind` | `df.plot` | Chart type: `"line"`, `"bar"`, `"hist"`, `"box"`, `"scatter"` ... | `kind="bar"` |
| `dpi` | `savefig` | Resolution (dots per inch); 300 for print | `dpi=300` |
| `bbox_inches` | `savefig` | `"tight"` = trim empty borders, keep labels | `bbox_inches="tight"` |
| `transparent` | `savefig` | Transparent background | `transparent=True` |

## 1. Install and Import

> Installing and importing matplotlib. `pip install matplotlib`, then `import matplotlib.pyplot as plt`.
>
> Use it in any chart in Python; seaborn and pandas plotting use it underneath.

```powershell
pip install matplotlib
```

```python
import matplotlib.pyplot as plt
import numpy as np
```

## 2. Two Ways to Plot

> The two coding styles: quick `plt.` calls vs explicit `fig, ax` objects. pyplot draws on the current chart; object-oriented draws on a named `ax`.
>
> Use it for pyplot for a fast single chart; `fig, ax` for anything you will customise or combine.

**pyplot style** (quick, one chart):

```python
plt.plot([1, 2, 3], [4, 1, 6])
plt.title("Quick plot")
plt.show()
```

**Object-oriented style** (recommended, needed for subplots):

```python
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 1, 6])
ax.set_title("OO plot")
plt.show()
```

| pyplot | Object-oriented |
|---|---|
| `plt.title()` | `ax.set_title()` |
| `plt.xlabel()` / `plt.ylabel()` | `ax.set_xlabel()` / `ax.set_ylabel()` |
| `plt.xlim()` / `plt.ylim()` | `ax.set_xlim()` / `ax.set_ylim()` |
| `plt.xticks()` | `ax.set_xticks()` |
| `plt.legend()` | `ax.legend()` |
| `plt.grid()` | `ax.grid()` |

## 3. Figure Anatomy

> The parts of a chart and their names. A Figure holds one or more Axes; each Axes has title, axes, data and legend.
>
> Use it for knowing what to call (`fig.` or `ax.`) when changing something.

```text
Figure  (the whole window / image)
 +-- Axes  (one chart; a figure can hold several)
      +-- Title
      +-- X axis / Y axis  (label, ticks, limits)
      +-- Lines, bars, points  (the data)
      +-- Legend
```

## 4. Line Plot

> Lines connecting points in order. `ax.plot(x, y)`; call it several times for several lines.
>
> Use it for trends over time or any ordered x-values.

```python
x = np.linspace(0, 10, 100)
fig, ax = plt.subplots()
ax.plot(x, np.sin(x), label="sin")
ax.plot(x, np.cos(x), label="cos", linestyle="--", color="red")
ax.legend()
plt.show()
```

## 5. Scatter Plot

> Individual points for two numeric variables. `ax.scatter(x, y)`; size / colour can show extra variables.
>
> Use it for relationship between two measures (price vs size), spotting clusters and outliers.

```python
ax.scatter(x, y)
ax.scatter(x, y, s=50, c="green", alpha=0.6)           # size, color, transparency
sc = ax.scatter(x, y, c=values, cmap="viridis")         # color by value
fig.colorbar(sc, ax=ax, label="value")
```

## 6. Bar Chart

> Bars comparing values across categories. `ax.bar` / `ax.barh`; shift x-positions for grouped bars, `bottom=` for stacked.
>
> Use it for comparing totals per category (sales per product, count per department).

```python
cats = ["A", "B", "C"]
vals = [10, 25, 15]

ax.bar(cats, vals)                              # vertical
ax.barh(cats, vals)                             # horizontal
ax.bar(cats, vals, color="skyblue", edgecolor="black")
ax.bar_label(ax.containers[0])                  # value on each bar
```

Grouped bars:

```python
x = np.arange(len(cats))
w = 0.4
ax.bar(x - w/2, vals_2023, w, label="2023")
ax.bar(x + w/2, vals_2024, w, label="2024")
ax.set_xticks(x, cats)
ax.legend()
```

Stacked bars: `ax.bar(cats, a); ax.bar(cats, b, bottom=a)`

## 7. Histogram

> Distribution of one numeric variable in bins. `ax.hist(data, bins=n)` counts values per interval.
>
> Use this when seeing how values are spread: skew, outliers, typical range.

```python
ax.hist(data, bins=20)
ax.hist(data, bins=20, color="gray", edgecolor="black", alpha=0.7)
ax.hist([d1, d2], bins=20, label=["group 1", "group 2"])   # compare
ax.hist(data, bins=20, density=True)                       # proportions
```

## 8. Box Plot

> Median, quartiles and outliers in one compact shape. `ax.boxplot(data)`; pass a list to compare several groups.
>
> Use it for comparing distributions across groups, detecting outliers.

```python
ax.boxplot(data)
ax.boxplot([d1, d2, d3], labels=["A", "B", "C"])   # matplotlib 3.9+: tick_labels=
ax.boxplot(data, vert=False)                        # horizontal
```

## 9. Pie Chart

> Parts of a whole as slices. `ax.pie(values, labels=..., autopct=...)`.
>
> Use it only for a few categories (2 to 5) summing to 100%; otherwise prefer a bar chart.

```python
ax.pie(vals, labels=cats, autopct="%1.1f%%", startangle=90)
ax.axis("equal")                                    # keep it round
```

A bar chart is usually easier to read than a pie chart.

## 10. Other Plot Types

> Less common chart types: areas, error bars, steps, violins, heatmaps. Dedicated `ax.` methods for each.
>
> Use it for confidence ranges (fill_between / errorbar), matrices (imshow).

```python
ax.fill_between(x, y1, y2, alpha=0.3)       # shaded area
ax.stackplot(x, y1, y2, labels=["a", "b"])  # stacked area
ax.errorbar(x, y, yerr=err, fmt="o")        # error bars
ax.step(x, y)                               # step line
ax.violinplot(data)                         # violin
im = ax.imshow(matrix, cmap="coolwarm")     # heatmap / image
fig.colorbar(im, ax=ax)
```

## 11. Titles, Labels and Legend

> Text that explains the chart. `set_title`, `set_xlabel`, `set_ylabel`, `legend` (uses `label=` from plot calls).
>
> Use it in every chart someone else will read.

```python
ax.set_title("Sales per Month", fontsize=14, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Sales (EUR)")
fig.suptitle("Overall title for all subplots")

ax.legend()                                 # uses label= from plot calls
ax.legend(loc="upper left")                 # best, upper right, lower left, center ...
ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")   # outside the plot
ax.legend(title="Year", frameon=False)
```

## 12. Axes: Limits, Ticks, Scale, Grid

> Controlling axis range, tick marks, scale and grid. `set_xlim` / `set_ylim`, `set_xticks`, `set_yscale("log")`, `grid`.
>
> Use it for zooming in, custom tick labels, data spanning many orders of magnitude (log).

```python
ax.set_xlim(0, 10) ; ax.set_ylim(0, 100)
ax.set_xticks([0, 5, 10])
ax.set_xticks([0, 1, 2], ["Jan", "Feb", "Mar"])       # custom tick labels
ax.tick_params(axis="x", rotation=45)                 # rotate tick labels
ax.set_yscale("log")                                  # log scale
ax.grid(True, linestyle=":", alpha=0.5)
ax.invert_yaxis()
ax.spines[["top", "right"]].set_visible(False)       # remove top/right border
ax2 = ax.twinx()                                      # second y-axis
```

## 13. Colors, Markers, Line Styles

> Look of lines and points. Keyword arguments `color`, `marker`, `linestyle`, `alpha`, `cmap`.
>
> Use it for distinguishing series, matching brand colours, printing in black and white.

```python
ax.plot(x, y, color="tab:blue", marker="o", linestyle="--", linewidth=2, markersize=6)
ax.plot(x, y, "ro--")                   # shorthand: red, circle, dashed
```

| Option | Values |
|---|---|
| `color` | `"red"`, `"tab:blue"`, `"#1f77b4"`, `"C0"` to `"C9"` (default cycle) |
| `marker` | `"o"` circle, `"s"` square, `"^"` triangle, `"x"`, `"+"`, `"."`, `"*"`, `"D"` |
| `linestyle` | `"-"` solid, `"--"` dashed, `":"` dotted, `"-."` dash-dot, `""` none |
| `alpha` | 0 (transparent) to 1 (solid) |
| `cmap` | `"viridis"`, `"coolwarm"`, `"Blues"`, `"RdYlGn"`, `"magma"` |

## 14. Subplots (Several Charts)

> Several charts in one figure. `plt.subplots(rows, cols)` returns a grid of Axes; draw on each one.
>
> Use it for comparing related charts side by side, dashboards, before / after views.

```python
fig, axes = plt.subplots(2, 2, figsize=(10, 8))    # 2 rows x 2 cols
axes[0, 0].plot(x, y)
axes[0, 1].scatter(x, y)
axes[1, 0].bar(cats, vals)
axes[1, 1].hist(data)
fig.tight_layout()                                  # fix overlapping labels
plt.show()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))   # 1 row x 2 cols
fig, axes = plt.subplots(2, 1, sharex=True)             # share x axis

for ax in axes.flat:                                    # loop over all
    ax.grid(True)
```

## 15. Annotations and Reference Lines

> Reference lines, shaded areas and text notes on a chart. `axhline` / `axvline`, `axvspan`, `text`, `annotate` with arrows.
>
> Use it for marking a target, a threshold, an event date, or labelling a peak.

```python
ax.axhline(y=50, color="gray", linestyle="--")      # horizontal line
ax.axvline(x=3, color="red")                        # vertical line
ax.axvspan(2, 4, alpha=0.2)                         # shaded region
ax.text(5, 80, "Note", fontsize=12)                 # text at data position
ax.annotate("Peak", xy=(5, 95), xytext=(7, 110),
            arrowprops=dict(arrowstyle="->"))
```

## 16. Figure Size and Styles

> Overall figure size and visual theme. `figsize=(w, h)` in inches; `plt.style.use()` for predefined looks.
>
> Use it for charts for slides (bigger), reports (consistent style), dark backgrounds.

```python
fig, ax = plt.subplots(figsize=(10, 5))     # width, height in inches
plt.rcParams["figure.figsize"] = (10, 5)    # default for all figures
plt.rcParams["font.size"] = 12

plt.style.available                         # list styles
plt.style.use("ggplot")                     # also: seaborn-v0_8, fivethirtyeight, bmh, dark_background
plt.style.use("default")                    # reset
```

## 17. Plot Directly from Pandas

> Plotting a DataFrame without writing matplotlib code. `df.plot(kind=...)` calls matplotlib and returns an `ax` you can customise.
>
> Use it for fast exploration while analysing data in pandas.

```python
df.plot(x="month", y="sales")                   # line
df.plot(kind="bar", x="city", y="sales")        # bar, barh, hist, box, scatter, pie, area
df["age"].plot(kind="hist", bins=20)
df.groupby("dept")["salary"].mean().plot(kind="bar")

ax = df.plot(x="month", y="sales", figsize=(10, 4))   # returns ax: customize further
ax.set_title("Sales")
```

## 18. Save a Figure

> Writing the chart to an image or PDF file. `fig.savefig(path, dpi=..., bbox_inches="tight")` before `plt.show()`.
>
> Use it for charts for reports, slides, README images.

```python
fig.savefig("chart.png", dpi=300, bbox_inches="tight")   # call BEFORE plt.show()
fig.savefig("chart.pdf")                                  # vector
fig.savefig("chart.svg")
fig.savefig("chart.png", transparent=True)
plt.close(fig)                                            # free memory in loops
```

## 19. Jupyter Notes

> Matplotlib settings specific to Jupyter. `%matplotlib inline` or `widget`; `;` hides text output.
>
> Use it for plots not showing in a notebook, or you want interactive zoom.

```python
%matplotlib inline          # static images (default in Jupyter)
%matplotlib widget          # interactive (pip install ipympl)
```

End a cell with `plt.show()` or `;` to hide the `[<matplotlib...>]` text output.

## 20. Troubleshooting

| Problem | Fix |
|---|---|
| Nothing appears (script) | Add `plt.show()` at the end |
| Saved image is blank | `savefig` must come before `plt.show()` |
| Labels overlap or are cut off | `fig.tight_layout()` or `bbox_inches="tight"` |
| Long x labels overlap | `ax.tick_params(axis="x", rotation=45)` |
| `AttributeError: 'Axes' object has no attribute 'title'` | OO style uses `set_`: `ax.set_title()` |
| `'numpy.ndarray' object has no attribute 'plot'` | `axes` is a grid; use `axes[0, 0]` or `axes.flat` |
| Legend is empty | Add `label=` to each plot call |
| Too many open figures warning | `plt.close(fig)` after saving in loops |

## 21. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Two lines

Plot two series on one chart with title, axis labels and legend, saved at 300 dpi.

<details markdown="1">
<summary>Solution</summary>

```python
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(months, sales_2025, label="2025")
ax.plot(months, sales_2026, label="2026", linestyle="--")
ax.set_title("Monthly sales") ; ax.set_xlabel("Month") ; ax.set_ylabel("EUR")
ax.legend()
fig.savefig("sales.png", dpi=300, bbox_inches="tight")
```

</details>

### Exercise 2: Dashboard grid

Make a 2x2 figure with a histogram, a bar chart, a scatter plot and a box plot.

<details markdown="1">
<summary>Solution</summary>

```python
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes[0, 0].hist(df["amount"], bins=20)
axes[0, 1].bar(totals.index, totals.values)
axes[1, 0].scatter(df["size"], df["price"], alpha=0.5)
axes[1, 1].boxplot(df["amount"])
fig.tight_layout()
```

</details>

### Exercise 3: Clean look

Rotate x tick labels by 45 degrees and remove the top and right borders.

<details markdown="1">
<summary>Solution</summary>

```python
ax.tick_params(axis="x", rotation=45)
ax.spines[["top", "right"]].set_visible(False)
```

</details>

---

<!-- nav:start -->
**Previous:** [20 - SQL](20_sql.md) | **Index:** [All guides](../README.md) | **Next:** [22 - Seaborn](22_seaborn.md)
<!-- nav:end -->
