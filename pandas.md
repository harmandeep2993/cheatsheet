PANDAS
---
  - [Data Aggregation](#data-aggregation)
      - [Groupby Aggregation](#1-groupby-aggregation)
      - [Pivot Tables](#2-pivot-tables)

### Data Aggregation
Data aggregation in Pandas is used to summarize data. The most common aggregation techniques are:
  - Groupby Aggregation
  - Pivot tables
  - Crosstab

#### 1. Groupby Aggregation
The `groupby` method is used to split data into groups based on one or more categories and then apply aggregation functions.

***Basic Syntax:***
```
df[subset].groupby(category).aggregation()
```
***Usage***
  ```
  df[['Department', 'Age']].groupby('Department').count()  # Use count() aggregation
  ```
***Common Aggregation Functions***

We can also use:
  - mean()
  - sum()
  - max()
  - min()
  - median()
  - std()

**Multiple Columns & Multiple Aggregations**
```
df [[list of columns]].groupby(by=[list of dimensions to aggregate by]).agg({list of functions}
```
***Usage***

```
df[["EducationField", "HourlyRate", "Department", "Age"]].groupby(by=["Department", "EducationField"]).agg({
"HourlyRate":"count",
"Age":"mean"})
```

```
df[["EducationField", "HourlyRate", "Department", "Age"]].groupby(by=["Department", "EducationField"]).agg({
"HourlyRate":["mean","max", "min"]    # Multiple aggregations
"Age":"mean"})
```

For more details, refer to the official Pandas [documentation](#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)

#### 2. Pivot Tables
The pivot_table() function in Pandas is used to summarize data in a spreadsheet-like format.

***Key Parameters***
- `df`: The DataFrame you want to pivot.
- `values`: The columns containing the values you want to aggregate.
- `index`: The columns that will become the new index of the pivot table.
- `columns`: The columns that will become the new columns of the pivot table.
- `aggfunc`: The aggregation function to be applied to the values (default is 'mean').

***Basic Syntax***
```
DataFrame.pivot_table(
    values=column_name,
    index=column_name,
    aggfunc="mean"
)
```
***Usage***
```
df.pivot_table(
    values="Age",
    index="Department",
    aggfunc="mean"
)
```
**Multi-Index, Multi-Value, and Multiple Aggregations**

```
DataFrame.pivot_table(
    values=[col1, col2],
    index=[group_col1, group_col2],
    columns=optional_column,      # optional
    aggfunc=[func1, func2]
)
```
***Usage***
```
df.pivot_table (
    values = ["MonthlyIncome", "Age"],
    index = ["Department", "EducationField"],
    aggfunc = ["sum", "max"]
)
```
**When to Use Pivot Tables?**
- Spreadsheet-style summaries
- Multi-dimensional aggregation
- Comparing multiple metrics across categories

For more details, refer to the official Pandas [documentation](#https://pandas.pydata.org/docs/reference/api/pandas.pivot_table.html)
