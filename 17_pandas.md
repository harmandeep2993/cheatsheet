# 17 - Pandas

<!-- nav:start -->
**Previous:** [16 - NumPy](16_numpy.md) | **Index:** [All guides](README.md) | **Next:** [18 - Polars and DuckDB](18_polars-duckdb.md)
<!-- nav:end -->

Quick reference for data analysis with pandas.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is pandas?

pandas is the most popular Python library for working with **tabular data** (rows and columns, like Excel or a SQL table). Its main object is the **DataFrame**: a table with named columns, where each column can have its own type (numbers, text, dates). pandas can read and write CSV, Excel, JSON and SQL, and gives you tools to clean, filter, transform, group, merge and summarise data with a few lines of code.

### Why use it?

- **Read almost any data source** into one consistent structure.
- **Clean messy data**: missing values, duplicates, wrong types, inconsistent text.
- **Analyse quickly**: filter rows, group and aggregate, pivot tables, statistics.
- **Combine datasets** like SQL joins.
- **Handles more data than Excel** and every step is repeatable as code.
- **Works with everything**: plots (matplotlib / seaborn), ML (scikit-learn), APIs, databases.

### Key terms

| Term | Meaning |
|---|---|
| DataFrame | A table: rows and named columns |
| Series | One column (or row) with an index |
| Index | Row labels (default 0, 1, 2, ...) |
| dtype | Data type of a column (`int64`, `float64`, `object`, `datetime64`) |
| NaN | Missing value |
| Vectorised operation | Works on a whole column at once, no loop |
| groupby | Split rows into groups, then aggregate each |

**Where it fits:** built on [16 - NumPy](16_numpy.md); plots with [20 - Matplotlib](20_matplotlib.md) / [21 - Seaborn](21_seaborn.md); feeds [22 - Scikit-learn](22_scikit-learn.md). SQL equivalents: [19 - SQL](19_sql.md). Faster alternatives for big data: [18 - Polars and DuckDB](18_polars-duckdb.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| pandas documentation | https://pandas.pydata.org/docs/ |
| 10 minutes to pandas | https://pandas.pydata.org/docs/user_guide/10min.html |
| pandas user guide | https://pandas.pydata.org/docs/user_guide/index.html |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
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
22. [Try It](#22-try-it)

---

## 0. Flags and Parameters

> The meaning of the arguments and parameters used in the pandas calls below. Explains how a call is built, then lists each parameter with its meaning and example.
>
> Use this when you see `df.drop_duplicates(subset=["A"], keep="first")` and want to know what each argument does.

### How a function call is built

```text
df.sort_values("salary", ascending=False)
|  |           |         |
|  |           |         +-- keyword argument: name=value, any order, optional
|  |           +------------ positional argument: meaning comes from its position
|  +------------------------ method name
+--------------------------- the object it works on (DataFrame)
```

- **Positional** arguments come first, in a fixed order. **Keyword** arguments use `name=value` and can be in any order.
- Arguments you leave out use their **default** value (for example `ascending=True`).
- See all parameters and defaults: `help(pd.DataFrame.sort_values)`, or `Shift+Tab` inside the brackets in Jupyter.

| Parameter | Used in | Meaning | Example |
|---|---|---|---|
| `sep` | `read_csv` | Column separator in the file | `sep=";"` |
| `encoding` | `read_csv`, `to_csv` | Text encoding of the file | `encoding="utf-8"` |
| `sheet_name` | `read_excel` | Which Excel sheet to read | `sheet_name="Sheet1"` |
| `index` | `to_csv`, `to_excel`, `to_sql` | `False` = do not write the row index as a column | `index=False` |
| `if_exists` | `to_sql` | Table already exists: `"fail"`, `"replace"` or `"append"` | `if_exists="replace"` |
| `n` (1st argument) | `head`, `tail`, `sample`, `nlargest` | Number of rows | `df.head(10)` |
| `include` | `describe` | `"all"` = also summarise text columns | `include="all"` |
| `normalize` | `value_counts`, `crosstab` | Shares instead of counts (`"index"` = per row in crosstab) | `normalize=True` |
| `axis` | `drop`, `apply`, `concat` | `0` = rows, `1` = columns | `axis=1` |
| `columns` / `index` | `drop`, `rename` | Which columns / rows to act on | `columns=["C"]` |
| `inplace` | many methods | `True` = change `df` itself instead of returning a new one (prefer `df = ...`) | `inplace=True` |
| `subset` | `dropna`, `drop_duplicates` | Only look at these columns | `subset=["A"]` |
| `keep` | `drop_duplicates` | Which duplicate to keep: `"first"`, `"last"`, `False` (drop all) | `keep="first"` |
| `errors` | `to_numeric`, `to_datetime` | `"coerce"` = turn invalid values into NaN instead of failing | `errors="coerce"` |
| `case` | `str.contains` | `False` = ignore upper / lower case | `case=False` |
| `ascending` | `sort_values` | `False` = largest first; list for several columns | `ascending=[True, False]` |
| `numeric_only` | `corr`, `mean` | Ignore text columns | `numeric_only=True` |
| `on` | `merge` | Key column present in both tables | `on="key"` |
| `left_on`, `right_on` | `merge` | Key columns with different names | `left_on="id", right_on="user_id"` |
| `how` | `merge`, `join` | Join type: `"inner"`, `"left"`, `"right"`, `"outer"` | `how="left"` |
| `ignore_index` | `concat` | Renumber the index 0, 1, 2 ... | `ignore_index=True` |
| `values` | `pivot_table` | Column(s) to aggregate | `values="Age"` |
| `index` | `pivot_table` | Column(s) that become the rows | `index="Department"` |
| `columns` | `pivot_table` | Column(s) that become the columns | `columns="Gender"` |
| `aggfunc` | `pivot_table`, `agg` | Aggregation: `"mean"`, `"sum"`, `"count"`, list for several | `aggfunc=["sum", "max"]` |
| `fill_value` | `pivot_table` | Value for empty cells | `fill_value=0` |
| `margins` | `crosstab`, `pivot_table` | Add row and column totals | `margins=True` |
| `drop` | `reset_index` | `True` = throw the old index away instead of making it a column | `drop=True` |
| `method` | `rank` | How ties are ranked (`"first"` = by order of appearance) | `method="first"` |

## 1. Install and Import

> Installing and importing pandas. `pip install pandas`, then `import pandas as pd` by convention.
>
> Use it in any work with tabular data: CSV, Excel, SQL results.

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

> A single labelled column of data. `pd.Series(list or dict)`; one column of a DataFrame is a Series.
>
> Use it for working with one column, or results of a groupby on one column.

A Series is a single column with an index.

```python
s = pd.Series([1, 2, 3, 4, 5])
s = pd.Series({"Madrid": 12, "Paris": 10})
s = pd.Series([10, 20], index=["a", "b"])

s.index                 # index labels
s.values                # values as array
```

## 3. Create DataFrames

> A table of rows and columns. From a dict of columns, a list of rows, or a NumPy array.
>
> Use it for test data, or building a table from results you collected in Python.

A DataFrame is a table of rows and columns.

```python
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})                     # from dict
df = pd.DataFrame([[1, 4], [2, 5]], columns=["A", "B"])                 # from list
df = pd.DataFrame(np.random.rand(5, 3), columns=["A", "B", "C"])        # random
```

## 4. Read and Write Files

> Loading data from files / databases and saving it back. `pd.read_*` functions create a DataFrame; `df.to_*` methods write it.
>
> Use it for the start and end of almost every analysis.

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

> First look at a dataset. `head`, `info`, `describe`, `value_counts` summarise structure and content.
>
> Use it right after loading data: check columns, types, missing values, odd values.

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

> Picking columns, rows and single cells. `df["col"]` for columns; `loc` by label, `iloc` by position.
>
> Use it for focusing on the columns you need, or reading a specific value.

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

> Keeping only rows that match conditions. Boolean masks inside `df[...]`, combined with `&`, `|`, `~`; or `df.query()`.
>
> Use it to answer questions like "Customers from Berlin with orders > 100", removing invalid rows.

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

> Creating new columns, renaming, dropping, replacing values. Assign to `df["new"]`, `np.where` for conditional values, `rename` / `drop` / `replace`.
>
> Use it for feature engineering, cleaning column names, removing unused columns.

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

> Finding and handling empty values. `isna` to detect, `dropna` to remove, `fillna` / `ffill` to fill.
>
> Use it in almost every real dataset; must be handled before statistics or models.

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

> Finding and removing repeated rows. `duplicated` flags repeats; `drop_duplicates` removes them.
>
> Use it for data merged from several sources, or exports that repeat records.

```python
df.duplicated().sum()                       # number of duplicate rows
df = df.drop_duplicates()                   # remove duplicates
df = df.drop_duplicates(subset=["A"], keep="first")
```

## 11. Data Types

> Converting columns to the right type. `astype` for direct conversion; `pd.to_numeric(errors="coerce")` for dirty data.
>
> Use it for numbers read as text, IDs read as numbers, saving memory with `category`.

```python
df["A"] = df["A"].astype(int)
df["A"] = df["A"].astype("category")
df["A"] = pd.to_numeric(df["A"], errors="coerce")   # invalid -> NaN
```

## 12. String Operations

> Text operations on a whole column. The `.str` accessor applies string methods to every value.
>
> Use it for cleaning names (strip, lower), searching text, splitting full names.

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

> Working with date columns. `pd.to_datetime` parses text; the `.dt` accessor gives year, month, weekday.
>
> Use it for time analysis: sales per month, filtering a date range, weekday patterns.

```python
df["Date"] = pd.to_datetime(df["Date"])
df["Date"].dt.year
df["Date"].dt.month
df["Date"].dt.day_name()
df[df["Date"] >= "2024-01-01"]
```

## 14. Apply Functions

> Running your own function on values, rows or columns. `apply` with a function or lambda; `map` with a dict for lookups.
>
> Use it for custom logic not covered by built-in methods (use vectorised methods first, they are faster).

```python
df["A"].apply(lambda x: x * 2)              # function on each value
df["A"].map({1: "one", 2: "two"})           # map values with dict
df.apply(np.sum, axis=0)                    # per column
df.apply(np.sum, axis=1)                    # per row
```

## 15. Sort

> Ordering rows. `sort_values` by one or more columns; `nlargest` / `nsmallest` for top N.
>
> Use it for rankings, top 10 products, making output readable.

```python
df.sort_values("A")                         # ascending
df.sort_values("A", ascending=False)        # descending
df.sort_values(["A", "B"], ascending=[True, False])
df.sort_index()                             # by index
df.nlargest(5, "A")                         # top 5
df.nsmallest(5, "A")                        # bottom 5
```

## 16. Statistics

> Summary statistics for columns. Methods like `mean`, `median`, `std`, `corr`, `quantile` on DataFrames or Series.
>
> Use it for quick numeric summaries and checking relationships between columns.

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

> Summarising data per group (split - apply - combine). `groupby(column)` splits rows into groups, then an aggregation summarises each.
>
> Use it to answer questions like "Average salary per department", "total sales per region and month".

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

> Spreadsheet-style summary tables. `pivot_table` puts one category on rows, another on columns, aggregated values in cells.
>
> Use it for reports comparing a metric across two dimensions (department x gender).

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

> Frequency tables of two categories. `pd.crosstab(a, b)` counts combinations; `normalize` gives shares.
>
> Use it to answer questions like "How many of each gender in each department?", survey analysis.

Count how often combinations of two categories occur.

```python
pd.crosstab(df["Department"], df["Gender"])
pd.crosstab(df["Department"], df["Gender"], normalize="index")   # row shares
pd.crosstab(df["Department"], df["Gender"], margins=True)        # add totals
```

## 20. Merge, Join and Concat

> Combining tables side by side (by key) or stacked. `merge` joins on key columns like SQL; `concat` stacks rows or columns.
>
> Use it for adding customer info to orders (merge), combining monthly files (concat).

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

> Moving columns in and out of the row index. `set_index` makes a column the index; `reset_index` turns it back into a column.
>
> Use it after `groupby` (to get a normal table back), or for fast lookups by ID.

```python
df = df.set_index("id")                 # column -> index
df = df.reset_index()                   # index -> column
df = df.reset_index(drop=True)          # discard old index
```

## 22. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Missing values

Load `sales.csv`, show missing values per column, and fill missing numbers in `amount` with the median.

<details markdown="1">
<summary>Solution</summary>

```python
df = pd.read_csv("sales.csv")
df.isna().sum()
df["amount"] = df["amount"].fillna(df["amount"].median())
```

</details>

### Exercise 2: Group and sort

Total and average `amount` per `region`, largest total first.

<details markdown="1">
<summary>Solution</summary>

```python
(df.groupby("region")["amount"]
   .agg(total="sum", average="mean")
   .sort_values("total", ascending=False))
```

</details>

### Exercise 3: Orphan orders

Keep all orders when merging with customers, then find orders whose customer does not exist.

<details markdown="1">
<summary>Solution</summary>

```python
merged = orders.merge(customers, left_on="customer_id", right_on="id", how="left", indicator=True)
orphans = merged[merged["_merge"] == "left_only"]
```

</details>

### Exercise 4: Pivot

Regions as rows, months as columns, summed amount, empty cells as 0.

<details markdown="1">
<summary>Solution</summary>

```python
df.pivot_table(values="amount", index="region", columns="month", aggfunc="sum", fill_value=0)
```

</details>

---

<!-- nav:start -->
**Previous:** [16 - NumPy](16_numpy.md) | **Index:** [All guides](README.md) | **Next:** [18 - Polars and DuckDB](18_polars-duckdb.md)
<!-- nav:end -->
