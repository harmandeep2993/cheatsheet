# 08 - NumPy

Quick reference for numerical arrays with NumPy (the base library under pandas, matplotlib and scikit-learn).

## Contents

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

---

## 1. Install and Import

```powershell
pip install numpy
```

```python
import numpy as np
np.__version__
```

## 2. Create Arrays

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

```python
a = np.array([[1, 2, 3], [4, 5, 6]])

a.shape                 # (2, 3)  rows, cols
a.ndim                  # 2       number of dimensions
a.size                  # 6       total elements
a.dtype                 # int64   element type
len(a)                  # 2       length of first dimension
```

## 4. Data Types

```python
np.array([1, 2], dtype=float)           # set type on creation
a.astype(int)                           # convert (returns new array)
a.astype("float32")
```

Common types: `int64`, `float64`, `bool`, `str_`, `object`. An array holds ONE type for all elements.

## 5. Indexing and Slicing

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

Arrays of different shapes are stretched automatically when sizes match or one of them is 1.

```python
m = np.array([[1, 2, 3], [4, 5, 6]])    # shape (2, 3)
m + np.array([10, 20, 30])              # adds to every row -> (2, 3)
m + np.array([[100], [200]])            # adds to every column -> (2, 3)
m - m.mean(axis=0)                      # center each column
```

## 10. Aggregations and Statistics

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

```python
b = a[0:3]              # slice = VIEW: changing b changes a
b = a[0:3].copy()       # independent copy
b = a[a > 2]            # boolean / fancy indexing = copy
```

## 17. Save and Load

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
