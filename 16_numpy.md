# 16 - NumPy

Quick reference for numerical arrays with NumPy (the base library under pandas, matplotlib and scikit-learn).

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is NumPy?

NumPy (Numerical Python) is the core library for numbers in Python. Its main object is the **ndarray**: a grid of values (1D vector, 2D matrix, or more dimensions) that all have the same type. Operations on arrays run in fast compiled C code and apply to all elements at once, so you rarely need Python loops. pandas, matplotlib, scikit-learn and most scientific libraries are built on top of NumPy.

### Why use it?

- **Speed**: array maths is often 10 to 100 times faster than Python lists and loops.
- **Less code**: `a * 2` doubles a million numbers; no loop needed (vectorisation).
- **Maths toolbox**: statistics, linear algebra, random numbers, rounding, trigonometry.
- **Memory efficient**: compact storage of large numeric data.
- **Foundation**: understanding arrays, shapes and `axis` makes pandas and ML much easier.

### Key terms

| Term | Meaning |
|---|---|
| ndarray | NumPy's N-dimensional array |
| Shape | Size of each dimension, e.g. `(3, 4)` = 3 rows, 4 columns |
| dtype | The single data type of all elements (`int64`, `float64`) |
| Axis | A dimension: `axis=0` rows direction, `axis=1` columns direction |
| Vectorisation | Applying an operation to a whole array at once |
| Broadcasting | Automatic stretching of arrays with different shapes |

**Where it fits:** the base under [17 - Pandas](17_pandas.md), [20 - Matplotlib](20_matplotlib.md) and [22 - Scikit-learn](22_scikit-learn.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| NumPy documentation | https://numpy.org/doc/stable/ |
| NumPy: the absolute basics for beginners | https://numpy.org/doc/stable/user/absolute_beginners.html |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install and Import](#1-install-and-import)
2. [Create Arrays](#2-create-arrays)
3. [Array Attributes](#3-array-attributes)
4. [Data Types](#4-data-types)
5. [Indexing and Slicing](#5-indexing-and-slicing)
6. [Boolean Filtering](#6-boolean-filtering)
7. [Reshape and Combine](#7-reshape-and-combine)
8. [Math Operations](#8-math-operations)
9. [Broadcasting](#9-broadcasting)
10. [Aggregations and Statistics](#10-aggregations-and-statistics)
11. [The axis Parameter](#11-the-axis-parameter)
12. [Sorting and Searching](#12-sorting-and-searching)
13. [Missing Values (NaN)](#13-missing-values-nan)
14. [Random Numbers](#14-random-numbers)
15. [Linear Algebra](#15-linear-algebra)
16. [Copies vs Views](#16-copies-vs-views)
17. [Save and Load](#17-save-and-load)
18. [Troubleshooting](#18-troubleshooting)
19. [Try It](#19-try-it)

---

## 0. Flags and Parameters

> - **What:** The meaning of the arguments and parameters used in the NumPy calls below.
> - **How:** Explains how a call is built, then lists each parameter with its meaning and example.
> - **When to use:** You see `a.sum(axis=0)` or `rng.normal(loc=0, scale=1, size=100)` and want to know what each argument does.

### How a function call is built

```text
np.arange(0, 10, 2)
          |  |   |
          |  |   +-- step
          |  +------ stop (excluded)
          +--------- start
positional arguments: meaning comes from the order

rng.normal(loc=0, scale=1, size=100)
           |      |        |
           |      |        +-- size: how many values
           |      +----------- scale: standard deviation
           +------------------ loc: mean
keyword arguments: name=value, any order
```

- **Positional** arguments come first, in a fixed order. **Keyword** arguments use `name=value` and can be in any order.
- Arguments you leave out use their **default** value (for example `step=1` in `np.arange`).
- See all parameters and defaults: `help(np.arange)`, or `Shift+Tab` inside the brackets in Jupyter.

| Parameter | Used in | Meaning | Example |
|---|---|---|---|
| `start, stop, step` | `arange`, slices `a[start:stop:step]` | Begin, end (excluded), step size | `np.arange(0, 10, 2)` |
| `num` (3rd argument) | `linspace` | How many evenly spaced values (end included) | `np.linspace(0, 1, 5)` |
| shape `(rows, cols)` | `zeros`, `ones`, `full`, `reshape` | Size of each dimension as a tuple | `np.zeros((2, 3))` |
| `-1` | `reshape` | "Work this dimension out for me" | `a.reshape(-1, 1)` |
| `dtype` | `array`, `zeros`, `astype` | Element type | `dtype=float` |
| `axis` | `sum`, `mean`, `concatenate`, `apply` | `0` = down the rows (per column), `1` = across columns (per row), none = everything | `m.sum(axis=0)` |
| `size` | random methods | Number (or shape) of values to generate | `size=10` |
| `loc`, `scale` | `rng.normal` | Mean and standard deviation | `loc=0, scale=1` |
| `low, high` | `rng.integers`, `rng.uniform` | Range; `high` is excluded | `rng.integers(1, 7)` |
| `replace` | `rng.choice` | `False` = never pick the same element twice | `replace=False` |
| seed | `default_rng(42)` | Fixed start value so random results repeat | `42` |
| `return_counts` | `np.unique` | Also return how often each value occurs | `return_counts=True` |
| `nan` | `nan_to_num` | Value that replaces NaN | `nan=0` |
| `delimiter` | `savetxt`, `loadtxt`, `genfromtxt` | Column separator in text files | `delimiter=","` |
| `skip_header` | `genfromtxt` | Number of top lines to skip | `skip_header=1` |
| list of positions | `a[[...]]` | Pick several elements by position (fancy indexing) | `a[[0, 2, 4]]` |

## 1. Install and Import

> - **What:** Installing and importing NumPy.
> - **How:** `pip install numpy`, then `import numpy as np` by convention.
> - **When to use:** Any numeric work; pandas, matplotlib and scikit-learn already depend on it.

```powershell
pip install numpy
```

```python
import numpy as np
np.__version__
```

## 2. Create Arrays

> - **What:** Ways to create arrays.
> - **How:** From lists with `np.array`, or generated with `zeros`, `ones`, `arange`, `linspace`.
> - **When to use:** Test data, placeholders to fill later, evenly spaced x-values for plots.

```python
np.array([1, 2, 3])                     # 1D from list
np.array([[1, 2], [3, 4]])              # 2D (matrix)
np.zeros(5)                             # [0. 0. 0. 0. 0.]
np.zeros((2, 3))                        # 2 rows x 3 cols of 0
np.ones((2, 3))                         # all 1
np.full((2, 3), 7)                      # all 7
np.eye(3)                               # 3x3 identity matrix
np.arange(0, 10, 2)                     # [0 2 4 6 8]  (end excluded)
np.linspace(0, 1, 5)                    # 5 evenly spaced: [0. .25 .5 .75 1.]
np.empty((2, 2))                        # uninitialized (fast, random content)
np.zeros_like(a)                        # same shape as a, filled with 0
```

## 3. Array Attributes

> - **What:** Checking an array's shape, dimensions, size and type.
> - **How:** Attributes on every array: `.shape`, `.ndim`, `.size`, `.dtype`.
> - **When to use:** Debugging shape errors, or checking data before feeding a model.

```python
a = np.array([[1, 2, 3], [4, 5, 6]])

a.shape                 # (2, 3)  rows, cols
a.ndim                  # 2       number of dimensions
a.size                  # 6       total elements
a.dtype                 # int64   element type
len(a)                  # 2       length of first dimension
```

## 4. Data Types

> - **What:** The single type all elements in an array share.
> - **How:** Set with `dtype=` or convert with `.astype()`.
> - **When to use:** Saving memory (float32), or fixing numbers loaded as strings.

```python
np.array([1, 2], dtype=float)           # set type on creation
a.astype(int)                           # convert (returns new array)
a.astype("float32")
```

Common types: `int64`, `float64`, `bool`, `str_`, `object`. An array holds ONE type for all elements.

## 5. Indexing and Slicing

> - **What:** Getting single values, ranges, rows and columns.
> - **How:** `[row, col]` with numbers, slices `start:stop:step`, or lists of positions.
> - **When to use:** Picking a feature column, the first N rows, or a sub-matrix.

```python
a = np.array([10, 20, 30, 40, 50])
a[0]                    # 10     first
a[-1]                   # 50     last
a[1:4]                  # [20 30 40]  (end excluded)
a[::2]                  # [10 30 50]  every 2nd
a[::-1]                 # reversed
a[[0, 2, 4]]            # [10 30 50]  fancy indexing (list of positions)

m = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
m[0, 1]                 # 2      row 0, col 1
m[1]                    # [4 5 6]    row 1
m[:, 1]                 # [2 5 8]    column 1
m[0:2, 1:]              # [[2 3] [5 6]]  sub-matrix
```

## 6. Boolean Filtering

> - **What:** Selecting elements that match a condition.
> - **How:** A comparison gives a True / False mask; `a[mask]` keeps the True ones.
> - **When to use:** Removing outliers, replacing negative values, counting matches.

```python
a = np.array([5, 12, 3, 20, 8])
a > 6                               # [False True False True True]
a[a > 6]                            # [12 20 8]
a[(a > 4) & (a < 15)]               # AND (brackets required)
a[(a < 4) | (a > 15)]               # OR
a[~(a > 6)]                         # NOT
np.where(a > 6, "big", "small")     # if / else per element
np.where(a > 6)                     # positions where True
a[a > 6] = 0                        # replace matching values
```

## 7. Reshape and Combine

> - **What:** Changing an array's shape or joining arrays.
> - **How:** `reshape` keeps the data in a new layout; `concatenate` / `stack` join arrays.
> - **When to use:** Preparing input for a model (`reshape(-1, 1)`), combining features.

```python
a = np.arange(12)
a.reshape(3, 4)                     # 3 rows x 4 cols
a.reshape(3, -1)                    # -1 = calculate automatically
a.reshape(-1, 1)                    # column vector (often needed for sklearn)
m.flatten()                         # to 1D (copy)
m.ravel()                           # to 1D (view if possible)
m.T                                 # transpose
np.expand_dims(a, axis=0)           # add a dimension

np.concatenate([a, b])              # join 1D
np.vstack([a, b])                   # stack as rows
np.hstack([a, b])                   # stack side by side
np.column_stack([a, b])             # 1D arrays as columns
np.split(a, 3)                      # split into 3 equal parts
```

## 8. Math Operations

> - **What:** Element-wise arithmetic and math functions.
> - **How:** Operators and `np.` functions apply to every element at once (no loops).
> - **When to use:** Scaling, normalising, transforming data fast.

Operations apply **element by element** (no loops needed).

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

a + b                   # [5 7 9]
a - b ; a * b ; a / b
a ** 2                  # [1 4 9]
a // 2 ; a % 2          # floor division, remainder
a * 10                  # [10 20 30]

np.sqrt(a) ; np.exp(a) ; np.log(a) ; np.abs(a)
np.round(x, 2) ; np.floor(x) ; np.ceil(x)
np.clip(a, 0, 2)        # limit values to range [0, 2]
```

## 9. Broadcasting

> - **What:** Operations between arrays of different shapes.
> - **How:** NumPy stretches dimensions of size 1 to match the other array.
> - **When to use:** Subtracting the column means from every row, adding a bias to every sample.

Arrays of different shapes are stretched automatically when sizes match or one of them is 1.

```python
m = np.array([[1, 2, 3], [4, 5, 6]])    # shape (2, 3)
m + np.array([10, 20, 30])              # adds to every row -> (2, 3)
m + np.array([[100], [200]])            # adds to every column -> (2, 3)
m - m.mean(axis=0)                      # center each column
```

## 10. Aggregations and Statistics

> - **What:** Summaries: sum, mean, min, max, std, percentiles.
> - **How:** Methods on arrays; with `axis=` they work per row or column.
> - **When to use:** Descriptive statistics, finding the position of the maximum.

```python
a.sum() ; a.mean() ; np.median(a)
a.min() ; a.max()
a.argmin() ; a.argmax()                 # position of min / max
a.std() ; a.var()                       # standard deviation, variance
a.cumsum()                              # running total
np.percentile(a, 90)                    # 90th percentile
np.unique(a)                            # unique sorted values
np.unique(a, return_counts=True)        # values and counts
np.corrcoef(x, y)                       # correlation matrix
np.round(a.mean(), 2)
```

## 11. The axis Parameter

> - **What:** Choosing whether an operation works down rows or across columns.
> - **How:** `axis=0` collapses rows (result per column); `axis=1` collapses columns (per row).
> - **When to use:** Any aggregation on a 2D array; same idea in pandas.

```text
m = [[1, 2, 3],
     [4, 5, 6]]

axis=0  -> down the rows    -> one result per COLUMN
axis=1  -> across columns   -> one result per ROW
```

```python
m.sum()                 # 21        everything
m.sum(axis=0)           # [5 7 9]   per column
m.sum(axis=1)           # [6 15]    per row
```

## 12. Sorting and Searching

> - **What:** Sorting values and testing membership / conditions.
> - **How:** `np.sort`, `argsort` for sort order, `isin`, `any`, `all`.
> - **When to use:** Ranking, top-N, checking whether any value breaks a rule.

```python
np.sort(a)                      # sorted copy
np.sort(a)[::-1]                # descending
a.sort()                        # sort in place
np.argsort(a)                   # indices that would sort a
np.isin(a, [1, 3])              # membership test per element
np.any(a > 5) ; np.all(a > 0)   # at least one / all True
np.count_nonzero(a > 5)         # how many True
```

## 13. Missing Values (NaN)

> - **What:** Dealing with missing numbers (NaN).
> - **How:** NaN spreads through normal math; `nan*` functions skip it, `isnan` finds it.
> - **When to use:** Real-world data with gaps, when `mean()` suddenly returns `nan`.

```python
a = np.array([1, np.nan, 3])
np.isnan(a)                     # [False True False]
a.mean()                        # nan (NaN spreads)
np.nanmean(a)                   # 2.0 (ignores NaN)
np.nansum(a) ; np.nanmax(a)
a[~np.isnan(a)]                 # drop NaN
np.nan_to_num(a, nan=0)         # replace NaN with 0
```

## 14. Random Numbers

> - **What:** Generating random numbers reproducibly.
> - **How:** Create a `default_rng(seed)` generator and call its methods.
> - **When to use:** Simulations, sampling, shuffling, reproducible train / test splits.

```python
rng = np.random.default_rng(42)         # seeded generator (reproducible)

rng.random(5)                           # 5 floats in [0, 1)
rng.integers(1, 7, size=10)             # 10 dice rolls (7 excluded)
rng.normal(loc=0, scale=1, size=100)    # normal distribution
rng.uniform(0, 10, size=5)              # uniform in [0, 10)
rng.choice(["a", "b", "c"], size=3)     # random pick
rng.choice(a, size=3, replace=False)    # sample without replacement
rng.shuffle(a)                          # shuffle in place
```

Older style (still common in tutorials): `np.random.seed(42)`, `np.random.rand(3)`, `np.random.randint(0, 10, 5)`.

## 15. Linear Algebra

> - **What:** Matrix operations.
> - **How:** `@` for matrix multiply, `np.linalg` for inverse, determinant, solving equations.
> - **When to use:** Linear regression by hand, geometry, understanding ML maths.

```python
A @ B                           # matrix multiplication
np.dot(a, b)                    # dot product
A.T                             # transpose
np.linalg.inv(A)                # inverse
np.linalg.det(A)                # determinant
np.linalg.solve(A, b)           # solve Ax = b
np.linalg.norm(v)               # vector length
np.linalg.eig(A)                # eigenvalues, eigenvectors
```

`A * B` is element-wise, `A @ B` is matrix multiplication.

## 16. Copies vs Views

> - **What:** Whether a new variable shares data with the original.
> - **How:** Slices are views (shared data); `.copy()` makes an independent array.
> - **When to use:** The original array changed unexpectedly after editing a slice.

```python
b = a[0:3]              # slice = VIEW: changing b changes a
b = a[0:3].copy()       # independent copy
b = a[a > 2]            # boolean / fancy indexing = copy
```

## 17. Save and Load

> - **What:** Saving arrays to disk and loading them back.
> - **How:** `.npy` / `.npz` binary formats keep type and shape; `savetxt` for CSV.
> - **When to use:** Caching expensive results, sharing arrays between scripts.

```python
np.save("data.npy", a)                  # binary, one array
a = np.load("data.npy")
np.savez("data.npz", x=a, y=b)          # several arrays
data = np.load("data.npz"); data["x"]
np.savetxt("data.csv", a, delimiter=",")
a = np.loadtxt("data.csv", delimiter=",")
a = np.genfromtxt("data.csv", delimiter=",", skip_header=1)   # handles missing
```

## 18. Troubleshooting

| Error | Fix |
|---|---|
| `operands could not be broadcast together with shapes` | Shapes do not match; check `.shape`, use `reshape` |
| `cannot reshape array of size X into shape Y` | Product of new shape must equal `size` |
| `The truth value of an array ... is ambiguous` | Use `&`, `\|`, `~` (not `and`, `or`, `not`) or `.any()` / `.all()` |
| `IndexError: index out of bounds` | Index starts at 0, last is `len - 1` |
| Result is `nan` | NaN in the data; use `np.nanmean` etc. |
| Original array changed unexpectedly | Slice was a view; use `.copy()` |
| `Expected 2D array, got 1D array` (sklearn) | `a.reshape(-1, 1)` |

## 19. Try It

> - **What:** Short exercises to practise this guide.
> - **How:** Try each task yourself first, then open the solution.
> - **When to use:** Right after reading the guide, or later as a quick self-test.

### Exercise 1: Random matrix stats

With seed 42, create a 3x4 array of random integers 0 to 9; print column means and row sums.

<details markdown="1">
<summary>Solution</summary>

```python
rng = np.random.default_rng(42)
m = rng.integers(0, 10, size=(3, 4))
m.mean(axis=0), m.sum(axis=1)
```

</details>

### Exercise 2: Clip negatives

Replace negative values in an array with 0 using a boolean mask.

<details markdown="1">
<summary>Solution</summary>

```python
a[a < 0] = 0            # or: np.clip(a, 0, None)
```

</details>

### Exercise 3: Standardise columns

Scale each column to mean 0 and standard deviation 1 with broadcasting.

<details markdown="1">
<summary>Solution</summary>

```python
z = (m - m.mean(axis=0)) / m.std(axis=0)
```

</details>
