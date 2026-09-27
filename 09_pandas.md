# 09 - Pandas

Quick reference for data analysis with pandas.

## Contents

1. [Install and Import](#1-install-and-import)
2. [Create Series](#2-create-series)
3. [Create DataFrames](#3-create-dataframes)
4. [Read and Write Files](#4-read-and-write-files)
5. [Inspect Data](#5-inspect-data)
6. [Select Data](#6-select-data)
7. [Filter Rows](#7-filter-rows)
8. [Add, Change and Remove](#8-add-change-and-remove)
9. [Missing Values](#9-missing-values)
10. [Duplicates](#10-duplicates)
11. [Data Types](#11-data-types)
12. [String Operations](#12-string-operations)
13. [Dates](#13-dates)
14. [Apply Functions](#14-apply-functions)
15. [Sort](#15-sort)
16. [Statistics](#16-statistics)
17. [Groupby Aggregation](#17-groupby-aggregation)
18. [Pivot Tables](#18-pivot-tables)
19. [Crosstab](#19-crosstab)
20. [Merge, Join and Concat](#20-merge-join-and-concat)
21. [Index Operations](#21-index-operations)

---

## 1. Install and Import

> - **What:** Installing and importing pandas.
> - **How:** `pip install pandas`, then `import pandas as pd` by convention.
> - **When to use:** Any work with tabular data: CSV, Excel, SQL results.

```powershell
pip install pandas numpy openpyxl       # terminal (openpyxl for Excel)
```

```python
!pip install pandas                     # Jupyter notebook (! runs a shell command)
```

```python
import pandas as pd
import numpy as np
```

## 2. Create Series

> - **What:** A single labelled column of data.
> - **How:** `pd.Series(list or dict)`; one column of a DataFrame is a Series.
> - **When to use:** Working with one column, or results of a groupby on one column.

A Series is a single column with an index.

```python
s = pd.Series([1, 2, 3, 4, 5])
s = pd.Series({"Madrid": 12, "Paris": 10})
s = pd.Series([10, 20], index=["a", "b"])

s.index                 # index labels
s.values                # values as array
```

## 3. Create DataFrames

> - **What:** A table of rows and columns.
> - **How:** From a dict of columns, a list of rows, or a NumPy array.
> - **When to use:** Test data, or building a table from results you collected in Python.

A DataFrame is a table of rows and columns.

```python
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})                     # from dict
df = pd.DataFrame([[1, 4], [2, 5]], columns=["A", "B"])                 # from list
df = pd.DataFrame(np.random.rand(5, 3), columns=["A", "B", "C"])        # random
```

## 4. Read and Write Files

> - **What:** Loading data from files / databases and saving it back.
> - **How:** `pd.read_*` functions create a DataFrame; `df.to_*` methods write it.
> - **When to use:** The start and end of almost every analysis.

```python
# Read
df = pd.read_csv("file.csv")
df = pd.read_csv("file.csv", sep=";", encoding="utf-8")
df = pd.read_excel("file.xlsx", sheet_name="Sheet1")
df = pd.read_json("file.json")
df = pd.read_sql("SELECT * FROM table", connection)

# Write
df.to_csv("file.csv", index=False)
df.to_excel("file.xlsx", index=False)
df.to_json("file.json")
df.to_sql("table", connection, if_exists="replace", index=False)
```

## 5. Inspect Data

> - **What:** First look at a dataset.
> - **How:** `head`, `info`, `describe`, `value_counts` summarise structure and content.
> - **When to use:** Right after loading data: check columns, types, missing values, odd values.

```python
df.head()               # first 5 rows
df.head(10)             # first 10 rows
df.tail()               # last 5 rows
df.sample(5)            # 5 random rows
df.shape                # (rows, columns)
df.columns              # column names
df.dtypes               # data type of each column
df.info()               # types, non-null counts, memory
df.describe()           # summary statistics (numeric)
df.describe(include="all")

df["A"].unique()        # unique values
df["A"].nunique()       # number of unique values
df["A"].value_counts()  # count of each value
df["A"].value_counts(normalize=True)   # share of each value
```

## 6. Select Data

> - **What:** Picking columns, rows and single cells.
> - **How:** `df["col"]` for columns; `loc` by label, `iloc` by position.
> - **When to use:** Focusing on the columns you need, or reading a specific value.

```python
df["A"]                 # one column (Series)
df[["A", "B"]]          # several columns (DataFrame)

df.loc[0]               # row by label
df.loc[0, "A"]          # cell by label
df.loc[0:2, ["A", "B"]] # rows 0 to 2 INCLUDED, by label

df.iloc[0]              # row by position
df.iloc[0, 0]           # cell by position
df.iloc[0:2, 0:2]       # rows 0 to 1 (end EXCLUDED), by position
```

`loc` = labels, `iloc` = integer positions.

## 7. Filter Rows

> - **What:** Keeping only rows that match conditions.
> - **How:** Boolean masks inside `df[...]`, combined with `&`, `|`, `~`; or `df.query()`.
> - **When to use:** "Customers from Berlin with orders > 100", removing invalid rows.

```python
df[df["A"] > 2]                             # one condition
df[(df["A"] > 1) & (df["B"] < 6)]           # AND (use & with brackets)
df[(df["A"] > 1) | (df["B"] < 6)]           # OR
df[~(df["A"] > 1)]                          # NOT
df[df["City"].isin(["Madrid", "Paris"])]    # value in list
df[df["A"].between(1, 3)]                   # range (inclusive)
df.query("A > 1 and B < 6")                 # query string
df.loc[df["A"] > 2, ["A", "B"]]             # filter and select columns
```

## 8. Add, Change and Remove

> - **What:** Creating new columns, renaming, dropping, replacing values.
> - **How:** Assign to `df["new"]`, `np.where` for conditional values, `rename` / `drop` / `replace`.
> - **When to use:** Feature engineering, cleaning column names, removing unused columns.

```python
df["C"] = df["A"] + df["B"]                 # new column
df["D"] = np.where(df["A"] > 2, "high", "low")   # conditional column
df = df.assign(E=df["A"] * 2)               # new column (chainable)

df = df.rename(columns={"A": "X"})          # rename column
df = df.drop(columns=["C"])                 # drop column
df = df.drop(index=[0])                     # drop row
df["A"] = df["A"].replace({1: 100})         # replace values
```

Most methods return a new DataFrame. Assign the result back (`df = df.drop(...)`) instead of relying on `inplace=True`.

## 9. Missing Values

> - **What:** Finding and handling empty values.
> - **How:** `isna` to detect, `dropna` to remove, `fillna` / `ffill` to fill.
> - **When to use:** Almost every real dataset; must be handled before statistics or models.

```python
df.isna()               # True where missing
df.isna().sum()         # missing count per column
df.dropna()             # drop rows with any missing value
df.dropna(subset=["A"]) # drop rows where A is missing
df.fillna(0)            # fill all missing with 0
df["A"] = df["A"].fillna(df["A"].mean())   # fill with mean
df.ffill()              # fill with previous value
```

## 10. Duplicates

> - **What:** Finding and removing repeated rows.
> - **How:** `duplicated` flags repeats; `drop_duplicates` removes them.
> - **When to use:** Data merged from several sources, or exports that repeat records.

```python
df.duplicated().sum()                       # number of duplicate rows
df = df.drop_duplicates()                   # remove duplicates
df = df.drop_duplicates(subset=["A"], keep="first")
```

## 11. Data Types

> - **What:** Converting columns to the right type.
> - **How:** `astype` for direct conversion; `pd.to_numeric(errors="coerce")` for dirty data.
> - **When to use:** Numbers read as text, IDs read as numbers, saving memory with `category`.

```python
df["A"] = df["A"].astype(int)
df["A"] = df["A"].astype("category")
df["A"] = pd.to_numeric(df["A"], errors="coerce")   # invalid -> NaN
```

## 12. String Operations

> - **What:** Text operations on a whole column.
> - **How:** The `.str` accessor applies string methods to every value.
> - **When to use:** Cleaning names (strip, lower), searching text, splitting full names.

```python
df["Name"].str.lower()
df["Name"].str.upper()
df["Name"].str.strip()
df["Name"].str.contains("abc", case=False)
df["Name"].str.replace("old", "new")
df["Name"].str.split(" ").str[0]            # first word
df["Name"].str.len()
```

## 13. Dates

> - **What:** Working with date columns.
> - **How:** `pd.to_datetime` parses text; the `.dt` accessor gives year, month, weekday.
> - **When to use:** Time analysis: sales per month, filtering a date range, weekday patterns.

```python
df["Date"] = pd.to_datetime(df["Date"])
df["Date"].dt.year
df["Date"].dt.month
df["Date"].dt.day_name()
df[df["Date"] >= "2024-01-01"]
```

## 14. Apply Functions

> - **What:** Running your own function on values, rows or columns.
> - **How:** `apply` with a function or lambda; `map` with a dict for lookups.
> - **When to use:** Custom logic not covered by built-in methods (use vectorised methods first, they are faster).

```python
df["A"].apply(lambda x: x * 2)              # function on each value
df["A"].map({1: "one", 2: "two"})           # map values with dict
df.apply(np.sum, axis=0)                    # per column
df.apply(np.sum, axis=1)                    # per row
```

## 15. Sort

> - **What:** Ordering rows.
> - **How:** `sort_values` by one or more columns; `nlargest` / `nsmallest` for top N.
> - **When to use:** Rankings, top 10 products, making output readable.

```python
df.sort_values("A")                         # ascending
df.sort_values("A", ascending=False)        # descending
df.sort_values(["A", "B"], ascending=[True, False])
df.sort_index()                             # by index
df.nlargest(5, "A")                         # top 5
df.nsmallest(5, "A")                        # bottom 5
```

## 16. Statistics

> - **What:** Summary statistics for columns.
> - **How:** Methods like `mean`, `median`, `std`, `corr`, `quantile` on DataFrames or Series.
> - **When to use:** Quick numeric summaries and checking relationships between columns.

```python
df.sum()                # sum
df.mean()               # mean
df.median()             # median
df.min(); df.max()      # min, max
df.std()                # standard deviation
df.count()              # non-null count
df.corr(numeric_only=True)                  # correlation matrix
df["A"].quantile(0.9)   # 90th percentile
```

## 17. Groupby Aggregation

> - **What:** Summarising data per group (split - apply - combine).
> - **How:** `groupby(column)` splits rows into groups, then an aggregation summarises each.
> - **When to use:** "Average salary per department", "total sales per region and month".

Split rows into groups, then summarize each group.

```python
# Basic: df[subset].groupby(category).aggregation()
df[["Department", "Age"]].groupby("Department").count()
df.groupby("Department")["Age"].mean()
df.groupby("Department").size()             # rows per group
```

Common aggregations: `count()`, `sum()`, `mean()`, `median()`, `min()`, `max()`, `std()`.

Multiple columns and multiple aggregations:

```python
df.groupby(["Department", "EducationField"]).agg({
    "HourlyRate": ["mean", "max", "min"],
    "Age": "mean",
})
```

Named aggregations (clean column names):

```python
df.groupby("Department").agg(
    avg_age=("Age", "mean"),
    headcount=("Age", "count"),
).reset_index()
```

Docs: [DataFrame.groupby](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)

## 18. Pivot Tables

> - **What:** Spreadsheet-style summary tables.
> - **How:** `pivot_table` puts one category on rows, another on columns, aggregated values in cells.
> - **When to use:** Reports comparing a metric across two dimensions (department x gender).

Spreadsheet-style summary.

| Parameter | Meaning |
|---|---|
| `values` | column(s) to aggregate |
| `index` | column(s) that become rows |
| `columns` | column(s) that become columns (optional) |
| `aggfunc` | aggregation function (default `"mean"`) |
| `fill_value` | value used for empty cells |

```python
df.pivot_table(values="Age", index="Department", aggfunc="mean")

df.pivot_table(
    values=["MonthlyIncome", "Age"],
    index=["Department", "EducationField"],
    columns="Gender",
    aggfunc=["sum", "max"],
    fill_value=0,
)
```

Use for multi-dimensional summaries and comparing several metrics across categories.

Docs: [pandas.pivot_table](https://pandas.pydata.org/docs/reference/api/pandas.pivot_table.html)

## 19. Crosstab

> - **What:** Frequency tables of two categories.
> - **How:** `pd.crosstab(a, b)` counts combinations; `normalize` gives shares.
> - **When to use:** "How many of each gender in each department?", survey analysis.

Count how often combinations of two categories occur.

```python
pd.crosstab(df["Department"], df["Gender"])
pd.crosstab(df["Department"], df["Gender"], normalize="index")   # row shares
pd.crosstab(df["Department"], df["Gender"], margins=True)        # add totals
```

## 20. Merge, Join and Concat

> - **What:** Combining tables side by side (by key) or stacked.
> - **How:** `merge` joins on key columns like SQL; `concat` stacks rows or columns.
> - **When to use:** Adding customer info to orders (merge), combining monthly files (concat).

```python
pd.merge(df1, df2, on="key")                    # inner join (default)
pd.merge(df1, df2, on="key", how="left")        # left join
pd.merge(df1, df2, on="key", how="outer")       # full outer join
pd.merge(df1, df2, left_on="id", right_on="user_id")

df1.join(df2)                                   # join on index

pd.concat([df1, df2])                           # stack rows
pd.concat([df1, df2], axis=1)                   # side by side
pd.concat([df1, df2], ignore_index=True)        # renumber index
```

| `how` | Keeps |
|---|---|
| `inner` | only matching keys |
| `left` | all rows from left |
| `right` | all rows from right |
| `outer` | all rows from both |

## 21. Index Operations

> - **What:** Moving columns in and out of the row index.
> - **How:** `set_index` makes a column the index; `reset_index` turns it back into a column.
> - **When to use:** After `groupby` (to get a normal table back), or for fast lookups by ID.

```python
df = df.set_index("id")                 # column -> index
df = df.reset_index()                   # index -> column
df = df.reset_index(drop=True)          # discard old index
```
