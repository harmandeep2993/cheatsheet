PANDAS
---
  - [Data Aggregation](#data-aggregation)
      - [Groupby Aggregation](#1.-groupby-aggregation)

### Data Aggregation
Data aggregation in Pandas is used to summarize data. The most common aggregation techniques are:
  - Groupby Aggregation
  - Pivot tables
  - Crosstab

#### 1. Groupby Aggregation
The `groupby` method is used to split data into groups based on one or more categories and then apply aggregation functions.

**Basic Syntax:**
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

For more details, refer to the official Pandas documentation:
https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html
