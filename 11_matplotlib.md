# 11 - Matplotlib

Quick reference for plotting with Matplotlib (the base plotting library; seaborn and pandas `.plot()` build on it).

## Contents

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

---

## 1. Install and Import

> - **What:** Installing and importing matplotlib.
> - **How:** `pip install matplotlib`, then `import matplotlib.pyplot as plt`.
> - **When to use:** Any chart in Python; seaborn and pandas plotting use it underneath.

```powershell
pip install matplotlib
```

```python
import matplotlib.pyplot as plt
import numpy as np
```

## 2. Two Ways to Plot

> - **What:** The two coding styles: quick `plt.` calls vs explicit `fig, ax` objects.
> - **How:** pyplot draws on the current chart; object-oriented draws on a named `ax`.
> - **When to use:** pyplot for a fast single chart; `fig, ax` for anything you will customise or combine.

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

> - **What:** The parts of a chart and their names.
> - **How:** A Figure holds one or more Axes; each Axes has title, axes, data and legend.
> - **When to use:** Knowing what to call (`fig.` or `ax.`) when changing something.

```text
Figure  (the whole window / image)
 +-- Axes  (one chart; a figure can hold several)
      +-- Title
      +-- X axis / Y axis  (label, ticks, limits)
      +-- Lines, bars, points  (the data)
      +-- Legend
```

## 4. Line Plot

> - **What:** Lines connecting points in order.
> - **How:** `ax.plot(x, y)`; call it several times for several lines.
> - **When to use:** Trends over time or any ordered x-values.

```python
x = np.linspace(0, 10, 100)
fig, ax = plt.subplots()
ax.plot(x, np.sin(x), label="sin")
ax.plot(x, np.cos(x), label="cos", linestyle="--", color="red")
ax.legend()
plt.show()
```

## 5. Scatter Plot

> - **What:** Individual points for two numeric variables.
> - **How:** `ax.scatter(x, y)`; size / colour can show extra variables.
> - **When to use:** Relationship between two measures (price vs size), spotting clusters and outliers.

```python
ax.scatter(x, y)
ax.scatter(x, y, s=50, c="green", alpha=0.6)           # size, color, transparency
sc = ax.scatter(x, y, c=values, cmap="viridis")         # color by value
fig.colorbar(sc, ax=ax, label="value")
```

## 6. Bar Chart

> - **What:** Bars comparing values across categories.
> - **How:** `ax.bar` / `ax.barh`; shift x-positions for grouped bars, `bottom=` for stacked.
> - **When to use:** Comparing totals per category (sales per product, count per department).

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

> - **What:** Distribution of one numeric variable in bins.
> - **How:** `ax.hist(data, bins=n)` counts values per interval.
> - **When to use:** Seeing how values are spread: skew, outliers, typical range.

```python
ax.hist(data, bins=20)
ax.hist(data, bins=20, color="gray", edgecolor="black", alpha=0.7)
ax.hist([d1, d2], bins=20, label=["group 1", "group 2"])   # compare
ax.hist(data, bins=20, density=True)                       # proportions
```

## 8. Box Plot

> - **What:** Median, quartiles and outliers in one compact shape.
> - **How:** `ax.boxplot(data)`; pass a list to compare several groups.
> - **When to use:** Comparing distributions across groups, detecting outliers.

```python
ax.boxplot(data)
ax.boxplot([d1, d2, d3], labels=["A", "B", "C"])   # matplotlib 3.9+: tick_labels=
ax.boxplot(data, vert=False)                        # horizontal
```

## 9. Pie Chart

> - **What:** Parts of a whole as slices.
> - **How:** `ax.pie(values, labels=..., autopct=...)`.
> - **When to use:** Only for a few categories (2 to 5) summing to 100%; otherwise prefer a bar chart.

```python
ax.pie(vals, labels=cats, autopct="%1.1f%%", startangle=90)
ax.axis("equal")                                    # keep it round
```

A bar chart is usually easier to read than a pie chart.

## 10. Other Plot Types

> - **What:** Less common chart types: areas, error bars, steps, violins, heatmaps.
> - **How:** Dedicated `ax.` methods for each.
> - **When to use:** Confidence ranges (fill_between / errorbar), matrices (imshow).

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

> - **What:** Text that explains the chart.
> - **How:** `set_title`, `set_xlabel`, `set_ylabel`, `legend` (uses `label=` from plot calls).
> - **When to use:** Every chart someone else will read.

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

> - **What:** Controlling axis range, tick marks, scale and grid.
> - **How:** `set_xlim` / `set_ylim`, `set_xticks`, `set_yscale("log")`, `grid`.
> - **When to use:** Zooming in, custom tick labels, data spanning many orders of magnitude (log).

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

> - **What:** Look of lines and points.
> - **How:** Keyword arguments `color`, `marker`, `linestyle`, `alpha`, `cmap`.
> - **When to use:** Distinguishing series, matching brand colours, printing in black and white.

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

> - **What:** Several charts in one figure.
> - **How:** `plt.subplots(rows, cols)` returns a grid of Axes; draw on each one.
> - **When to use:** Comparing related charts side by side, dashboards, before / after views.

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

> - **What:** Reference lines, shaded areas and text notes on a chart.
> - **How:** `axhline` / `axvline`, `axvspan`, `text`, `annotate` with arrows.
> - **When to use:** Marking a target, a threshold, an event date, or labelling a peak.

```python
ax.axhline(y=50, color="gray", linestyle="--")      # horizontal line
ax.axvline(x=3, color="red")                        # vertical line
ax.axvspan(2, 4, alpha=0.2)                         # shaded region
ax.text(5, 80, "Note", fontsize=12)                 # text at data position
ax.annotate("Peak", xy=(5, 95), xytext=(7, 110),
            arrowprops=dict(arrowstyle="->"))
```

## 16. Figure Size and Styles

> - **What:** Overall figure size and visual theme.
> - **How:** `figsize=(w, h)` in inches; `plt.style.use()` for predefined looks.
> - **When to use:** Charts for slides (bigger), reports (consistent style), dark backgrounds.

```python
fig, ax = plt.subplots(figsize=(10, 5))     # width, height in inches
plt.rcParams["figure.figsize"] = (10, 5)    # default for all figures
plt.rcParams["font.size"] = 12

plt.style.available                         # list styles
plt.style.use("ggplot")                     # also: seaborn-v0_8, fivethirtyeight, bmh, dark_background
plt.style.use("default")                    # reset
```

## 17. Plot Directly from Pandas

> - **What:** Plotting a DataFrame without writing matplotlib code.
> - **How:** `df.plot(kind=...)` calls matplotlib and returns an `ax` you can customise.
> - **When to use:** Fast exploration while analysing data in pandas.

```python
df.plot(x="month", y="sales")                   # line
df.plot(kind="bar", x="city", y="sales")        # bar, barh, hist, box, scatter, pie, area
df["age"].plot(kind="hist", bins=20)
df.groupby("dept")["salary"].mean().plot(kind="bar")

ax = df.plot(x="month", y="sales", figsize=(10, 4))   # returns ax: customize further
ax.set_title("Sales")
```

## 18. Save a Figure

> - **What:** Writing the chart to an image or PDF file.
> - **How:** `fig.savefig(path, dpi=..., bbox_inches="tight")` before `plt.show()`.
> - **When to use:** Charts for reports, slides, README images.

```python
fig.savefig("chart.png", dpi=300, bbox_inches="tight")   # call BEFORE plt.show()
fig.savefig("chart.pdf")                                  # vector
fig.savefig("chart.svg")
fig.savefig("chart.png", transparent=True)
plt.close(fig)                                            # free memory in loops
```

## 19. Jupyter Notes

> - **What:** Matplotlib settings specific to Jupyter.
> - **How:** `%matplotlib inline` or `widget`; `;` hides text output.
> - **When to use:** Plots not showing in a notebook, or you want interactive zoom.

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
