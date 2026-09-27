# 19 - SQL

Quick reference for SQL queries (standard SQL, notes for PostgreSQL / SQLite / MySQL where they differ) plus using SQL from Python and pandas.

## Introduction

### What is SQL?

SQL (Structured Query Language) is the standard language for working with **relational databases**: systems that store data in tables linked by keys. With SQL you describe **what** data you want ("average salary per department, highest first") and the database works out **how** to get it efficiently. The same core language works in PostgreSQL, MySQL, SQLite, SQL Server, Snowflake, BigQuery and more, with small differences.

### Why use it?

- **Where business data lives**: customers, orders, transactions are almost always in a SQL database.
- **Handles huge data**: databases filter and aggregate millions of rows before sending you the result.
- **Declarative and readable**: a query says what you want, not how to loop.
- **Reliable**: transactions, constraints and permissions keep data correct and safe.
- **Must-have skill** for data analysts, data scientists and backend developers.

### Key terms

| Term | Meaning |
|---|---|
| Database | A collection of tables managed by a database system |
| Table / row / column | Data as a grid: records and fields |
| Primary key | Unique ID of each row |
| Foreign key | Column that links to another table's primary key |
| Query | A `SELECT` statement that reads data |
| JOIN | Combine rows from tables by a key |
| Index | Structure that makes lookups on a column faster |
| DDL / DML | Statements that define structure (CREATE) / change data (INSERT) |

**Where it fits:** load query results into [17 - Pandas](17_pandas.md); run databases with [41 - Docker](41_docker.md). Vector search in Postgres: [29 - pgvector](29_embeddings-vector-db.md); SQL on files: [18 - DuckDB](18_polars-duckdb.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| PostgreSQL documentation | https://www.postgresql.org/docs/ |
| SQLite documentation | https://www.sqlite.org/docs.html |
| MySQL documentation | https://dev.mysql.com/doc/ |
| SQLAlchemy | https://docs.sqlalchemy.org/ |

---

## Contents

1. [Concepts](#1-concepts)
2. [Query Order](#2-query-order)
3. [SELECT Basics](#3-select-basics)
4. [WHERE Filters](#4-where-filters)
5. [Sorting and Limiting](#5-sorting-and-limiting)
6. [Aggregate Functions](#6-aggregate-functions)
7. [GROUP BY and HAVING](#7-group-by-and-having)
8. [JOINs](#8-joins)
9. [CASE (If / Else)](#9-case-if--else)
10. [NULL Handling](#10-null-handling)
11. [String Functions](#11-string-functions)
12. [Date Functions](#12-date-functions)
13. [Subqueries](#13-subqueries)
14. [CTEs (WITH)](#14-ctes-with)
15. [Window Functions](#15-window-functions)
16. [UNION, INTERSECT, EXCEPT](#16-union-intersect-except)
17. [Create Tables](#17-create-tables)
18. [Insert, Update, Delete](#18-insert-update-delete)
19. [Alter and Drop](#19-alter-and-drop)
20. [Indexes and Views](#20-indexes-and-views)
21. [Transactions](#21-transactions)
22. [SQLite and PostgreSQL CLI](#22-sqlite-and-postgresql-cli)
23. [SQL from Python and Pandas](#23-sql-from-python-and-pandas)
24. [SQL vs Pandas](#24-sql-vs-pandas)
25. [Troubleshooting](#25-troubleshooting)

---

## 1. Concepts

> - **What:** The building blocks of relational databases.
> - **How:** Data lives in tables; keys link tables together.
> - **When to use:** Read once; the rest of the guide uses these terms and example tables.

| Term | Meaning |
|---|---|
| **Table** | Rows and columns (like a DataFrame) |
| **Primary key** | Column that uniquely identifies a row (`id`) |
| **Foreign key** | Column that points to a primary key in another table |
| **Query** | A `SELECT` statement that reads data |
| **Schema** | Structure: tables, columns, types |

Example tables used below:

```text
employees(id, name, department_id, salary, hire_date, manager_id)
departments(id, name, city)
```

Keywords are not case-sensitive (`SELECT` = `select`); writing them in UPPERCASE is a convention. End statements with `;`.

## 2. Query Order

> - **What:** The order clauses are written vs the order the database runs them.
> - **How:** Written SELECT first, but executed FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY.
> - **When to use:** Understanding why an alias fails in WHERE, or where a filter belongs.

Written order:

```sql
SELECT    columns
FROM      table
JOIN      other_table ON ...
WHERE     row filter
GROUP BY  columns
HAVING    group filter
ORDER BY  columns
LIMIT     n;
```

Execution order: `FROM / JOIN -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT`.
That is why you cannot use a `SELECT` alias inside `WHERE`.

## 3. SELECT Basics

> - **What:** Reading columns from a table.
> - **How:** `SELECT columns FROM table`, with aliases, calculations and DISTINCT.
> - **When to use:** Every query starts here.

```sql
SELECT * FROM employees;                            -- all columns
SELECT name, salary FROM employees;                 -- some columns
SELECT name AS employee_name FROM employees;        -- column alias
SELECT DISTINCT department_id FROM employees;       -- unique values
SELECT name, salary * 12 AS yearly FROM employees;  -- calculated column
SELECT COUNT(*) FROM employees;                     -- number of rows
```

Comments: `-- one line` and `/* block */`.

## 4. WHERE Filters

> - **What:** Keeping only rows that match conditions.
> - **How:** `WHERE` with comparisons, AND / OR, IN, BETWEEN, LIKE, IS NULL.
> - **When to use:** Any question about a subset: "orders from 2024", "customers in Berlin".

```sql
SELECT * FROM employees WHERE salary > 50000;
SELECT * FROM employees WHERE department_id = 2 AND salary >= 40000;
SELECT * FROM employees WHERE department_id = 1 OR department_id = 3;
SELECT * FROM employees WHERE NOT department_id = 2;
SELECT * FROM employees WHERE department_id IN (1, 2, 3);
SELECT * FROM employees WHERE salary BETWEEN 40000 AND 60000;   -- inclusive
SELECT * FROM employees WHERE name LIKE 'A%';       -- starts with A
SELECT * FROM employees WHERE name LIKE '%son';     -- ends with son
SELECT * FROM employees WHERE name LIKE '_a%';      -- 2nd letter is a
SELECT * FROM employees WHERE name ILIKE 'a%';      -- case-insensitive (PostgreSQL)
SELECT * FROM employees WHERE manager_id IS NULL;   -- never use = NULL
```

Operators: `=  <> (or !=)  >  <  >=  <=`. Text values use single quotes: `'Berlin'`.

## 5. Sorting and Limiting

> - **What:** Ordering results and returning only some rows.
> - **How:** `ORDER BY col [DESC]`, then `LIMIT n OFFSET m`.
> - **When to use:** Top N lists, latest records, paging results in an app.

```sql
SELECT * FROM employees ORDER BY salary;                    -- ascending
SELECT * FROM employees ORDER BY salary DESC;               -- descending
SELECT * FROM employees ORDER BY department_id, salary DESC;
SELECT * FROM employees ORDER BY salary DESC LIMIT 5;       -- top 5
SELECT * FROM employees ORDER BY id LIMIT 10 OFFSET 20;     -- page 3 (rows 21 to 30)
```

SQL Server: `SELECT TOP 5 ...`. Oracle / standard: `FETCH FIRST 5 ROWS ONLY`.

## 6. Aggregate Functions

> - **What:** Calculating one value from many rows.
> - **How:** `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` over the selected rows.
> - **When to use:** Totals and averages for a whole table or filtered subset.

```sql
SELECT
    COUNT(*)              AS rows_total,
    COUNT(manager_id)     AS with_manager,      -- ignores NULL
    COUNT(DISTINCT department_id) AS departments,
    SUM(salary)           AS total,
    AVG(salary)           AS average,
    MIN(salary)           AS lowest,
    MAX(salary)           AS highest,
    ROUND(AVG(salary), 2) AS avg_rounded
FROM employees;
```

## 7. GROUP BY and HAVING

> - **What:** Aggregating per group and filtering groups.
> - **How:** `GROUP BY` makes one row per group; `HAVING` filters on the aggregated values.
> - **When to use:** "Sales per region", "departments with more than 10 employees".

```sql
-- One row per department
SELECT department_id, COUNT(*) AS headcount, AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id;

-- Filter groups (HAVING) vs filter rows (WHERE)
SELECT department_id, AVG(salary) AS avg_salary
FROM employees
WHERE hire_date >= '2020-01-01'         -- rows first
GROUP BY department_id
HAVING AVG(salary) > 50000              -- then groups
ORDER BY avg_salary DESC;
```

Every column in `SELECT` must be in `GROUP BY` or inside an aggregate function.

## 8. JOINs

> - **What:** Combining rows from two or more tables by a key.
> - **How:** `JOIN ... ON a.key = b.key`; the join type decides what happens to non-matching rows.
> - **When to use:** Data spread across tables: employees + departments, orders + customers.

```sql
SELECT e.name, d.name AS department
FROM employees AS e
INNER JOIN departments AS d ON e.department_id = d.id;
```

| Join | Returns |
|---|---|
| `INNER JOIN` | Only rows with a match in both tables |
| `LEFT JOIN` | All rows from left, matched rows from right (NULL if none) |
| `RIGHT JOIN` | All rows from right, matched rows from left |
| `FULL OUTER JOIN` | All rows from both (not in MySQL) |
| `CROSS JOIN` | Every combination |

```sql
-- Employees without a department (anti-join)
SELECT e.name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
WHERE d.id IS NULL;

-- Self join: employee and their manager
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Several joins
SELECT e.name, d.name, p.title
FROM employees e
JOIN departments d ON e.department_id = d.id
JOIN projects p ON p.owner_id = e.id;
```

## 9. CASE (If / Else)

> - **What:** If / else logic inside a query.
> - **How:** `CASE WHEN condition THEN value ... ELSE value END`.
> - **When to use:** Categorising values (salary bands), conditional counts / sums.

```sql
SELECT name, salary,
    CASE
        WHEN salary >= 80000 THEN 'high'
        WHEN salary >= 50000 THEN 'medium'
        ELSE 'low'
    END AS salary_band
FROM employees;

-- Conditional count
SELECT
    COUNT(CASE WHEN salary > 50000 THEN 1 END) AS above_50k,
    SUM(CASE WHEN department_id = 1 THEN salary ELSE 0 END) AS dept1_total
FROM employees;
```

## 10. NULL Handling

> - **What:** Working with missing values.
> - **How:** `IS NULL` to test, `COALESCE` for defaults, `NULLIF` to avoid division by zero.
> - **When to use:** Optional fields, left joins that produce NULLs, safe ratios.

```sql
WHERE manager_id IS NULL
WHERE manager_id IS NOT NULL
SELECT COALESCE(manager_id, 0) FROM employees;      -- first non-NULL value
SELECT NULLIF(bonus, 0) FROM employees;             -- NULL if bonus = 0 (avoid divide by zero)
SELECT salary / NULLIF(hours, 0) FROM employees;
```

Any comparison with NULL (`= NULL`, `<> NULL`) is unknown, not true. Aggregates (except `COUNT(*)`) ignore NULL.

## 11. String Functions

> - **What:** Changing and extracting text.
> - **How:** Functions like `UPPER`, `TRIM`, `SUBSTRING`, `CONCAT` (names vary slightly per database).
> - **When to use:** Cleaning names, building labels, matching inconsistent text.

```sql
UPPER(name) ; LOWER(name)
LENGTH(name)                            -- LEN() in SQL Server
TRIM(name)
SUBSTRING(name, 1, 3)                   -- first 3 chars (SUBSTR in SQLite)
REPLACE(name, 'a', 'b')
CONCAT(first_name, ' ', last_name)      -- or first_name || ' ' || last_name
POSITION('a' IN name)                   -- INSTR(name, 'a') in SQLite / MySQL
LEFT(name, 3) ; RIGHT(name, 3)
```

## 12. Date Functions

> - **What:** Extracting parts of dates and date arithmetic.
> - **How:** Database-specific functions (`EXTRACT`, `DATE_TRUNC`, `STRFTIME`, `DATE_ADD`).
> - **When to use:** Monthly reports, filtering the last 30 days, grouping by year.

```sql
-- PostgreSQL
CURRENT_DATE ; NOW()
EXTRACT(YEAR FROM hire_date)
DATE_TRUNC('month', hire_date)                  -- first day of month
hire_date + INTERVAL '30 days'
AGE(CURRENT_DATE, hire_date)
TO_CHAR(hire_date, 'YYYY-MM')

-- SQLite
DATE('now') ; DATETIME('now')
STRFTIME('%Y', hire_date)                       -- year
DATE(hire_date, '+30 days')

-- MySQL
CURDATE() ; NOW() ; YEAR(hire_date)
DATE_ADD(hire_date, INTERVAL 30 DAY)
DATE_FORMAT(hire_date, '%Y-%m')
```

## 13. Subqueries

> - **What:** A query inside another query.
> - **How:** Put `(SELECT ...)` in WHERE, FROM or SELECT.
> - **When to use:** Comparing to an aggregate ("above average"), or filtering by another table.

```sql
-- In WHERE: above average salary
SELECT name, salary FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- With IN
SELECT name FROM employees
WHERE department_id IN (SELECT id FROM departments WHERE city = 'Berlin');

-- EXISTS
SELECT d.name FROM departments d
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id);

-- In FROM (derived table)
SELECT AVG(headcount) FROM (
    SELECT department_id, COUNT(*) AS headcount
    FROM employees GROUP BY department_id
) AS t;
```

## 14. CTEs (WITH)

> - **What:** Named temporary result sets defined before the main query.
> - **How:** `WITH name AS (SELECT ...)` then use `name` like a table.
> - **When to use:** Complex queries in readable steps; replaces deeply nested subqueries.

Named temporary result; easier to read than nested subqueries.

```sql
WITH dept_stats AS (
    SELECT department_id, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department_id
)
SELECT e.name, e.salary, s.avg_salary
FROM employees e
JOIN dept_stats s ON e.department_id = s.department_id
WHERE e.salary > s.avg_salary;
```

Several CTEs: `WITH a AS (...), b AS (...) SELECT ...`

## 15. Window Functions

> - **What:** Calculations across related rows while keeping every row.
> - **How:** `function() OVER (PARTITION BY ... ORDER BY ...)`.
> - **When to use:** Rankings, top N per group, running totals, comparing with the previous row.

Calculate across related rows **without** collapsing them (unlike GROUP BY).

```sql
SELECT name, department_id, salary,
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn,
    RANK()       OVER (PARTITION BY department_id ORDER BY salary DESC) AS rnk,
    DENSE_RANK() OVER (ORDER BY salary DESC)                            AS dense_rnk,
    AVG(salary)  OVER (PARTITION BY department_id)                      AS dept_avg,
    SUM(salary)  OVER (ORDER BY hire_date)                              AS running_total,
    LAG(salary)  OVER (ORDER BY hire_date)                              AS prev_salary,
    LEAD(salary) OVER (ORDER BY hire_date)                              AS next_salary,
    NTILE(4)     OVER (ORDER BY salary)                                 AS quartile
FROM employees;
```

Top N per group:

```sql
WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
    FROM employees
)
SELECT * FROM ranked WHERE rn <= 3;
```

| Function | Ties |
|---|---|
| `ROW_NUMBER()` | 1, 2, 3, 4 (always unique) |
| `RANK()` | 1, 2, 2, 4 (gap after tie) |
| `DENSE_RANK()` | 1, 2, 2, 3 (no gap) |

Moving average: `AVG(sales) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`

## 16. UNION, INTERSECT, EXCEPT

> - **What:** Combining results of two queries vertically.
> - **How:** `UNION` (unique rows), `UNION ALL` (all rows), `INTERSECT`, `EXCEPT`.
> - **When to use:** Merging similar tables (customers + suppliers), finding rows in one list but not another.

```sql
SELECT city FROM customers
UNION                       -- combine, remove duplicates
SELECT city FROM suppliers;

UNION ALL                   -- combine, keep duplicates (faster)
INTERSECT                   -- in both
EXCEPT                      -- in first but not second (MINUS in Oracle)
```

Both queries need the same number of columns with compatible types.

## 17. Create Tables

> - **What:** Defining a new table and its columns.
> - **How:** `CREATE TABLE` with column types and constraints (PRIMARY KEY, NOT NULL, REFERENCES).
> - **When to use:** Setting up a new database or storing processed results.

```sql
CREATE TABLE departments (
    id    SERIAL PRIMARY KEY,               -- INTEGER PRIMARY KEY AUTOINCREMENT in SQLite
    name  VARCHAR(100) NOT NULL UNIQUE,
    city  VARCHAR(100)
);

CREATE TABLE employees (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    salary        NUMERIC(10, 2) CHECK (salary >= 0),
    hire_date     DATE DEFAULT CURRENT_DATE,
    manager_id    INTEGER REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS logs (id SERIAL PRIMARY KEY, msg TEXT);
CREATE TABLE top_earners AS SELECT * FROM employees WHERE salary > 80000;
```

Common types: `INTEGER`, `BIGINT`, `NUMERIC(p, s)`, `REAL` / `FLOAT`, `VARCHAR(n)`, `TEXT`, `BOOLEAN`, `DATE`, `TIMESTAMP`, `JSON` / `JSONB` (PostgreSQL).

## 18. Insert, Update, Delete

> - **What:** Adding, changing and removing rows.
> - **How:** `INSERT INTO`, `UPDATE ... SET ... WHERE`, `DELETE FROM ... WHERE`.
> - **When to use:** Loading data, correcting records, removing test data.

```sql
INSERT INTO departments (name, city) VALUES ('Data', 'Berlin');
INSERT INTO departments (name, city) VALUES ('HR', 'Munich'), ('IT', 'Hamburg');
INSERT INTO archive SELECT * FROM employees WHERE hire_date < '2015-01-01';

UPDATE employees SET salary = salary * 1.05 WHERE department_id = 2;
UPDATE employees SET salary = 60000, department_id = 3 WHERE id = 7;

DELETE FROM employees WHERE id = 7;
TRUNCATE TABLE logs;                    -- delete all rows fast

-- Upsert (PostgreSQL / SQLite)
INSERT INTO departments (id, name) VALUES (1, 'Data')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
```

`UPDATE` or `DELETE` without `WHERE` changes EVERY row. Run the same `WHERE` with `SELECT` first.

## 19. Alter and Drop

> - **What:** Changing or removing a table's structure.
> - **How:** `ALTER TABLE` adds / drops / renames columns; `DROP TABLE` removes the table.
> - **When to use:** The schema needs a new column, or an old table is no longer used.

```sql
ALTER TABLE employees ADD COLUMN email VARCHAR(200);
ALTER TABLE employees DROP COLUMN email;
ALTER TABLE employees RENAME COLUMN name TO full_name;
ALTER TABLE employees RENAME TO staff;
ALTER TABLE employees ALTER COLUMN salary TYPE NUMERIC(12, 2);   -- PostgreSQL

DROP TABLE logs;
DROP TABLE IF EXISTS logs;
```

## 20. Indexes and Views

> - **What:** Speed-ups for queries and saved queries.
> - **How:** An index is a lookup structure on columns; a view is a stored SELECT.
> - **When to use:** Slow filters / joins on large tables (index); reusable reports (view).

```sql
CREATE INDEX idx_emp_dept ON employees(department_id);      -- faster filters / joins
CREATE UNIQUE INDEX idx_emp_email ON employees(email);
DROP INDEX idx_emp_dept;

CREATE VIEW dept_summary AS
SELECT department_id, COUNT(*) AS headcount, AVG(salary) AS avg_salary
FROM employees GROUP BY department_id;

SELECT * FROM dept_summary;             -- use like a table

EXPLAIN SELECT * FROM employees WHERE department_id = 2;          -- query plan
EXPLAIN ANALYZE SELECT * FROM employees WHERE department_id = 2;  -- plan + real timing (PostgreSQL)
```

## 21. Transactions

> - **What:** Several changes that succeed or fail together.
> - **How:** `BEGIN`, run statements, then `COMMIT` or `ROLLBACK`.
> - **When to use:** Money transfers, multi-table updates where partial changes would corrupt data.

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;             -- save both
-- ROLLBACK;        -- or undo both
```

## 22. SQLite and PostgreSQL CLI

> - **What:** Command-line clients for SQLite and PostgreSQL.
> - **How:** `sqlite3 file.db` or `psql -h host -U user -d db`; dot / backslash commands inspect the database.
> - **When to use:** Quick checks on a server or container without a GUI tool.

**SQLite** (file-based, no server):

```text
sqlite3 mydb.db                 open / create database
.tables                         list tables
.schema employees               show CREATE statement
.headers on                     show column names
.mode column                    aligned output (also: csv, table, markdown)
.import data.csv employees      import CSV (use .mode csv first)
.output result.csv              send output to file
.quit                           exit
```

**PostgreSQL** (`psql`):

```text
psql -h localhost -U postgres -d mydb     connect
\l                              list databases
\c mydb                         switch database
\dt                             list tables
\d employees                    describe table
\dn                             list schemas
\du                             list users
\x                              toggle expanded output
\i script.sql                   run SQL file
\copy employees TO 'emp.csv' CSV HEADER    export CSV
\q                              quit
```

Postgres in Docker: see [41 - Docker](41_docker.md), section "Useful Ready-Made Containers".

## 23. SQL from Python and Pandas

> - **What:** Running SQL from Python and moving data between SQL and pandas.
> - **How:** `sqlite3` / SQLAlchemy connections; `pd.read_sql` and `df.to_sql`.
> - **When to use:** Pulling data from a database into an analysis, or saving results back.

```python
import sqlite3

import pandas as pd
from sqlalchemy import create_engine

# sqlite3 (standard library)
conn = sqlite3.connect("mydb.db")
cur = conn.cursor()
cur.execute("SELECT name FROM employees WHERE salary > ?", (50000,))   # ? = parameter
rows = cur.fetchall()
conn.commit()
conn.close()

# pandas + SQLAlchemy (pip install sqlalchemy psycopg2-binary)
engine = create_engine("sqlite:///mydb.db")
# engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/mydb")

df = pd.read_sql("SELECT * FROM employees", engine)
df = pd.read_sql("SELECT * FROM employees WHERE salary > :min", engine, params={"min": 50000})
df.to_sql("employees_clean", engine, if_exists="replace", index=False)   # or "append"
```

Always pass values as **parameters** (`?`, `:name`, `%s`), never with f-strings; string formatting allows SQL injection.

Keep connection strings (with passwords) in environment variables, not in code.

## 24. SQL vs Pandas

> - **What:** The pandas equivalent of each SQL operation.
> - **How:** Find the SQL clause on the left, use the pandas code on the right.
> - **When to use:** You know how to do it in SQL but not in pandas (or the reverse).

| SQL | Pandas |
|---|---|
| `SELECT a, b FROM t` | `df[["a", "b"]]` |
| `WHERE a > 5` | `df[df["a"] > 5]` |
| `WHERE a IN (1, 2)` | `df[df["a"].isin([1, 2])]` |
| `WHERE a IS NULL` | `df[df["a"].isna()]` |
| `ORDER BY a DESC` | `df.sort_values("a", ascending=False)` |
| `LIMIT 5` | `df.head(5)` |
| `SELECT DISTINCT a` | `df["a"].unique()` / `df.drop_duplicates("a")` |
| `COUNT(*)` | `len(df)` |
| `GROUP BY a` + `AVG(b)` | `df.groupby("a")["b"].mean()` |
| `HAVING AVG(b) > 10` | `g = df.groupby("a")["b"].mean(); g[g > 10]` |
| `INNER JOIN ... ON` | `pd.merge(df1, df2, on="key")` |
| `LEFT JOIN` | `pd.merge(df1, df2, on="key", how="left")` |
| `UNION ALL` | `pd.concat([df1, df2])` |
| `CASE WHEN` | `np.where(...)` / `np.select(...)` |
| `ROW_NUMBER() OVER (PARTITION BY a ORDER BY b)` | `df.groupby("a")["b"].rank(method="first")` |
| `SUM(b) OVER (ORDER BY d)` | `df.sort_values("d")["b"].cumsum()` |

See [17 - Pandas](17_pandas.md).

## 25. Troubleshooting

| Error | Fix |
|---|---|
| `column must appear in the GROUP BY clause` | Add the column to `GROUP BY` or wrap it in an aggregate |
| `column "x" does not exist` (with alias) | Aliases cannot be used in `WHERE`; repeat the expression or use a CTE |
| `column reference "id" is ambiguous` | Prefix with the table alias: `e.id` |
| `aggregate functions are not allowed in WHERE` | Use `HAVING` |
| `WHERE x = NULL` returns nothing | Use `IS NULL` |
| Join returns too many rows | Join key is not unique; duplicated matches multiply rows |
| `division by zero` | `x / NULLIF(y, 0)` |
| Integer division gives 0 | Cast: `x * 1.0 / y` or `CAST(x AS NUMERIC) / y` |
| Text with `'` breaks the query | Double it: `'O''Brien'` (better: use parameters) |
| `relation "table" does not exist` | Wrong database / schema, or name case: PostgreSQL lowercases unquoted names |
| Query is slow | `EXPLAIN`, add an index on filter / join columns, avoid `SELECT *` |
