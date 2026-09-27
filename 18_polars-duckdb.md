# 18 - Polars and DuckDB

<!-- nav:start -->
**Previous:** [17 - Pandas](17_pandas.md) | **Index:** [All guides](README.md) | **Next:** [19 - SQL](19_sql.md)
<!-- nav:end -->

Quick reference for two fast modern tools for data too big or too slow for pandas: Polars (DataFrames) and DuckDB (SQL on files and DataFrames).

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What are Polars and DuckDB?

- **Polars** is a DataFrame library like pandas, written in Rust. It uses all CPU cores, has a clean expression-based API, and a **lazy mode** that plans the whole query before running it. Typically many times faster than pandas and uses less memory.
- **DuckDB** is an **embedded analytical database**: a SQL engine that runs inside your Python process (no server). It can query CSV, Parquet and JSON files, and even pandas / Polars DataFrames, directly with SQL.

Both read and write **Parquet**, a compressed, column-based file format that is much faster and smaller than CSV.

### Mental model

```text
                 Same question: "total sales per region, 2025 only"

pandas (eager)   read ALL -> filter -> group -> sum        each step runs immediately, one core
Polars (lazy)    scan -> [optimiser: read only 3 columns, filter while reading] -> group -> sum   all cores
DuckDB (SQL)     SELECT region, SUM(amount) FROM 'sales/*.parquet' WHERE year = 2025 GROUP BY region
```

**Eager** = do each step now. **Lazy** = write the recipe first, let the engine optimise it, then cook once. **Columnar** = data stored column by column, so reading 3 of 50 columns reads only those 3.

| Tool | Think of it as | Best at |
|---|---|---|
| pandas | The standard Swiss army knife | Small / medium data, ecosystem, plotting, ML input |
| Polars | pandas rebuilt for speed | Large data transformations in Python code |
| DuckDB | SQLite for analytics | SQL over files, joins, ad-hoc analysis, very large files |

### Why use them?

- **Speed**: minutes in pandas can become seconds.
- **Bigger than RAM**: lazy / streaming execution and DuckDB spill to disk.
- **SQL on files**: query a folder of Parquet files without loading or a database server.
- **Interoperable**: convert between pandas, Polars, DuckDB and Arrow cheaply.

### Key terms

| Term | Meaning |
|---|---|
| Parquet | Compressed columnar file format (the standard for analytics) |
| Arrow | In-memory columnar format shared by Polars, DuckDB, pandas |
| Expression | Polars building block: `pl.col("a") * 2` |
| Lazy frame | A query plan that runs only on `.collect()` |
| Predicate pushdown | Filtering while reading, so less data is loaded |
| Projection pushdown | Reading only the needed columns |
| OLAP | Analytical queries over many rows (DuckDB) vs OLTP transactions (Postgres) |

**Where it fits:** alternatives to [17 - Pandas](17_pandas.md); SQL skills from [19 - SQL](19_sql.md); outputs feed [22 - Scikit-learn](22_scikit-learn.md) and [20 - Matplotlib](20_matplotlib.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Polars user guide | https://docs.pola.rs/ |
| DuckDB documentation | https://duckdb.org/docs/ |
| Apache Parquet | https://parquet.apache.org/docs/ |

---

## Contents

1. [Install](#1-install)
2. [Parquet Files](#2-parquet-files)
3. [Polars: Create and Read](#3-polars-create-and-read)
4. [Polars: Inspect](#4-polars-inspect)
5. [Polars: Expressions](#5-polars-expressions)
6. [Polars: Select, Filter, with_columns](#6-polars-select-filter-with_columns)
7. [Polars: Group By and Aggregate](#7-polars-group-by-and-aggregate)
8. [Polars: Joins and Concat](#8-polars-joins-and-concat)
9. [Polars: Strings, Dates, Nulls](#9-polars-strings-dates-nulls)
10. [Polars: Lazy Mode](#10-polars-lazy-mode)
11. [pandas to Polars Cheat Sheet](#11-pandas-to-polars-cheat-sheet)
12. [DuckDB: Query Files with SQL](#12-duckdb-query-files-with-sql)
13. [DuckDB: Query DataFrames](#13-duckdb-query-dataframes)
14. [DuckDB: Persistent Database and CLI](#14-duckdb-persistent-database-and-cli)
15. [Converting Between Tools](#15-converting-between-tools)
16. [Which Tool When](#16-which-tool-when)
17. [Troubleshooting](#17-troubleshooting)
18. [Try It](#18-try-it)

---

## 1. Install

> Installing Polars, DuckDB and Parquet support. Plain pip / uv packages; `pyarrow` adds Parquet / Arrow support to pandas. Use it once per project.

```powershell
pip install polars duckdb pyarrow
uv add polars duckdb pyarrow
```

```python
import duckdb
import polars as pl
```

## 2. Parquet Files

> The standard file format for analytical data. Stores data by column with compression and types; readers can skip columns and row groups. Use it instead of CSV for anything you will read more than once or that is large.

```python
df_pd.to_parquet("sales.parquet")                    # pandas (needs pyarrow)
pd.read_parquet("sales.parquet", columns=["region", "amount"])

df_pl.write_parquet("sales.parquet")                 # Polars
pl.read_parquet("sales.parquet")
```

| | CSV | Parquet |
|---|---|---|
| Size | Large | 5 to 10x smaller |
| Types (dates, ints) | Lost, re-guessed on read | Stored |
| Read only some columns | No | Yes |
| Human readable | Yes | No |

## 3. Polars: Create and Read

> Getting data into a Polars DataFrame. From dicts, files (eager `read_*`) or as a lazy scan (`scan_*`). Use it at the start of a Polars pipeline.

```python
df = pl.DataFrame({"region": ["N", "S", "N"], "amount": [10, 20, 30]})
df = pl.read_csv("sales.csv", try_parse_dates=True)
df = pl.read_parquet("sales.parquet")
df = pl.read_json("data.json")
lf = pl.scan_parquet("sales/*.parquet")       # lazy: nothing loaded yet
df.write_csv("out.csv")
```

## 4. Polars: Inspect

> Looking at the data. Methods similar to pandas. Use it right after loading.

```python
df.head(5) ; df.tail(5) ; df.sample(5)
df.shape ; df.columns ; df.schema            # schema = column -> type
df.describe()
df.glimpse()                                  # compact overview of every column
df["region"].value_counts()
df.null_count()
```

## 5. Polars: Expressions

> The core idea of Polars: describe a computation on columns with `pl.col(...)`. Expressions are combined and evaluated inside contexts (`select`, `filter`, `with_columns`, `group_by().agg`). Use it in every transformation.

```python
pl.col("amount")                       # a column
pl.col("amount") * 1.19                # arithmetic
pl.col("amount").sum()                 # aggregation
pl.col("name").str.to_uppercase()      # string namespace
pl.col("date").dt.year()               # date namespace
pl.col("amount").alias("gross")        # rename result
pl.when(pl.col("amount") > 20).then(pl.lit("big")).otherwise(pl.lit("small"))   # if / else
pl.all() ; pl.col(pl.Float64)          # all columns / all float columns
```

## 6. Polars: Select, Filter, with_columns

> Choosing columns, filtering rows and adding columns. Each method takes expressions and returns a new DataFrame (no in-place changes). Use it in most of your data preparation.

```python
df.select("region", "amount")
df.select(pl.col("amount").mean().alias("avg"))

df.filter(pl.col("amount") > 15)
df.filter((pl.col("region") == "N") & (pl.col("amount") > 5))
df.filter(pl.col("region").is_in(["N", "S"]))

df = df.with_columns(
    (pl.col("amount") * 1.19).alias("gross"),
    pl.col("region").str.to_lowercase(),
)
df.rename({"amount": "net"})
df.drop("gross")
df.sort("amount", descending=True)
df.unique(subset=["region"])
```

## 7. Polars: Group By and Aggregate

> Summaries per group. `group_by(cols).agg(expressions)`; any number of aggregations in one pass. Use it for reports, feature engineering.

```python
df.group_by("region").agg(
    pl.col("amount").sum().alias("total"),
    pl.col("amount").mean().alias("avg"),
    pl.len().alias("n"),
).sort("total", descending=True)

df.with_columns(pl.col("amount").sum().over("region").alias("region_total"))   # window function
df.pivot(on="month", index="region", values="amount", aggregate_function="sum")
```

## 8. Polars: Joins and Concat

> Combining tables. `join(other, on=..., how=...)` like SQL; `pl.concat` stacks frames. Use it for enriching data with lookups, merging files.

```python
orders.join(customers, on="customer_id", how="left")      # inner, left, right, full, semi, anti, cross
orders.join(customers, left_on="cust", right_on="id")
pl.concat([df_jan, df_feb])                               # vertical
pl.concat([a, b], how="horizontal")
```

## 9. Polars: Strings, Dates, Nulls

> Common cleaning operations. Namespaces `.str`, `.dt`, and null methods on expressions. Use it for cleaning raw data.

```python
df.with_columns(
    pl.col("name").str.strip_chars().str.to_titlecase(),
    pl.col("email").str.contains("@gmail").alias("is_gmail"),
    pl.col("date").str.to_date("%Y-%m-%d"),
    pl.col("date").dt.month().alias("month"),
    pl.col("amount").fill_null(0),
    pl.col("amount").cast(pl.Float64),
)
df.drop_nulls(subset=["email"])
```

## 10. Polars: Lazy Mode

> Building a query plan that Polars optimises and runs at the end. Start with `scan_*` or `.lazy()`, chain operations, finish with `.collect()`; `.explain()` shows the plan. Use it for large files, multi-step pipelines, data bigger than memory (`streaming`).

```python
result = (
    pl.scan_parquet("sales/*.parquet")
    .filter(pl.col("year") == 2025)
    .group_by("region")
    .agg(pl.col("amount").sum().alias("total"))
    .sort("total", descending=True)
    .collect()                     # runs here, only reading needed columns / rows
)

lf.explain()                       # optimised plan
lf.collect(engine="streaming")     # process in chunks for bigger-than-memory data
lf.sink_parquet("out.parquet")     # stream the result straight to a file
```

## 11. pandas to Polars Cheat Sheet

> Translating familiar pandas code. Most operations map one-to-one to an expression. Use it for porting existing notebooks.

| pandas | Polars |
|---|---|
| `df["a"]` | `df["a"]` or `df.select("a")` |
| `df[df["a"] > 1]` | `df.filter(pl.col("a") > 1)` |
| `df["c"] = df["a"] + df["b"]` | `df = df.with_columns((pl.col("a") + pl.col("b")).alias("c"))` |
| `df.groupby("g")["a"].sum()` | `df.group_by("g").agg(pl.col("a").sum())` |
| `df.sort_values("a", ascending=False)` | `df.sort("a", descending=True)` |
| `df.merge(o, on="k", how="left")` | `df.join(o, on="k", how="left")` |
| `df.fillna(0)` | `df.fill_null(0)` |
| `df.astype({"a": float})` | `df.with_columns(pl.col("a").cast(pl.Float64))` |
| `df.apply(f, axis=1)` | Prefer expressions; last resort `map_elements` |
| Index | No index in Polars (use columns) |

## 12. DuckDB: Query Files with SQL

> Running SQL directly on CSV / Parquet / JSON files. Use the file path (or a glob) as a table name in `FROM`. Use it for quick analysis of big files, joining files, exploring data without loading it all.

```python
import duckdb

duckdb.sql("SELECT * FROM 'sales.parquet' LIMIT 5").show()

totals = duckdb.sql("""
    SELECT region, SUM(amount) AS total, COUNT(*) AS n
    FROM 'sales/*.parquet'
    WHERE year = 2025
    GROUP BY region
    ORDER BY total DESC
""").df()                                        # -> pandas; .pl() -> Polars; .fetchall() -> tuples

duckdb.sql("SELECT * FROM read_csv('data.csv', header=true)")
duckdb.sql("DESCRIBE SELECT * FROM 'sales.parquet'")
duckdb.sql("COPY (SELECT * FROM 'data.csv') TO 'data.parquet' (FORMAT parquet)")   # CSV -> Parquet
```

## 13. DuckDB: Query DataFrames

> Using SQL on pandas / Polars DataFrames in memory. Refer to the Python variable name as a table. Use this when when SQL is easier than DataFrame code (complex joins, window functions).

```python
orders = pd.read_csv("orders.csv")
customers = pl.read_parquet("customers.parquet")

duckdb.sql("""
    SELECT c.country, AVG(o.amount) AS avg_order
    FROM orders o JOIN customers c ON o.customer_id = c.id
    GROUP BY c.country
""").df()
```

## 14. DuckDB: Persistent Database and CLI

> Saving tables in a DuckDB file and using the command-line shell. `duckdb.connect("file.duckdb")` creates / opens a database file. Use it for local analytics database, caching cleaned data between sessions.

```python
con = duckdb.connect("analytics.duckdb")
con.sql("CREATE TABLE sales AS SELECT * FROM 'sales/*.parquet'")
con.sql("SELECT COUNT(*) FROM sales").fetchone()
con.execute("SELECT * FROM sales WHERE region = ?", ["N"]).df()    # parameters
con.close()
```

```bash
duckdb analytics.duckdb          # CLI shell (winget install DuckDB.cli)
.tables                          # list tables
.quit
```

## 15. Converting Between Tools

> Moving data between pandas, Polars, DuckDB and NumPy. All share Apache Arrow, so conversion is fast. Use the fastest tool for each step, then hand off (e.g. to scikit-learn or seaborn).

```python
pl_df = pl.from_pandas(pd_df)
pd_df = pl_df.to_pandas()
arr = pl_df.to_numpy()
pd_df = duckdb.sql("SELECT ...").df()
pl_df = duckdb.sql("SELECT ...").pl()
```

## 16. Which Tool When

> Choosing between pandas, Polars and DuckDB. Match data size and whether you think in code or SQL. Use it for starting an analysis or pipeline.

| Situation | Use |
|---|---|
| < 1 GB, exploring, plotting, ML input | pandas |
| Large data, repeated pipelines, want speed in Python | Polars (lazy) |
| You think in SQL, querying many files, joins | DuckDB |
| Data bigger than RAM | Polars streaming or DuckDB |
| Shared multi-user transactional database | PostgreSQL ([19 - SQL](19_sql.md)) |

## 17. Troubleshooting

| Problem | Fix |
|---|---|
| `ImportError: Unable to find a usable engine` (pandas parquet) | `pip install pyarrow` |
| Polars `ColumnNotFoundError` | Check `df.columns`; names are case-sensitive |
| `SchemaError` / type mismatch on concat or join | `cast` columns to the same type first |
| Polars date parsing fails | `str.to_date("%d.%m.%Y")` with the right format, or `try_parse_dates=True` |
| Lazy query "does nothing" | Call `.collect()` |
| Out of memory | Use `scan_*` + lazy, `engine="streaming"`, or DuckDB |
| DuckDB `Catalog Error: Table ... does not exist` | Variable not in scope, or quote file paths: `FROM 'file.parquet'` |
| pandas code with `apply` is slow in Polars too | Rewrite as expressions; avoid `map_elements` |

## 18. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution. Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: CSV to Parquet

Convert `big.csv` to `big.parquet` with one DuckDB statement.

<details markdown="1">
<summary>Solution</summary>

```python
import duckdb
duckdb.sql("COPY (SELECT * FROM 'big.csv') TO 'big.parquet' (FORMAT parquet)")
```

</details>

### Exercise 2: Lazy Polars

From all Parquet files in `sales/`, sum `amount` per `region` for 2025, reading as little as possible.

<details markdown="1">
<summary>Solution</summary>

```python
(pl.scan_parquet("sales/*.parquet")
   .filter(pl.col("year") == 2025)
   .group_by("region")
   .agg(pl.col("amount").sum())
   .collect())
```

</details>

### Exercise 3: SQL on DataFrames

Join two pandas DataFrames `orders` and `customers` with DuckDB SQL and get the result as pandas.

<details markdown="1">
<summary>Solution</summary>

```python
duckdb.sql('''
    SELECT c.country, SUM(o.amount) AS revenue
    FROM orders o JOIN customers c ON o.customer_id = c.id
    GROUP BY c.country ORDER BY revenue DESC
''').df()
```

</details>

---

<!-- nav:start -->
**Previous:** [17 - Pandas](17_pandas.md) | **Index:** [All guides](README.md) | **Next:** [19 - SQL](19_sql.md)
<!-- nav:end -->
