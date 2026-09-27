# pocket-guide

Personal quick-reference cheat sheets, numbered from basic to advanced.

## Foundations

| # | Guide | Covers |
|---|---|---|
| 01 | [Markdown](01_markdown.md) | Headings, formatting, lists, links, images, code, tables, anchors |
| 02 | [Terminal and PowerShell](02_terminal-powershell.md) | Navigation, files, search, pipes, env vars, processes, network, winget, CMD/Bash equivalents |
| 03 | [Linux](03_linux.md) | Navigation, files, grep/find, permissions, apt, processes, systemd, network, SSH, tar, cron |
| 04 | [Git and GitHub](04_git.md) | Commit, branch, merge/rebase, conflicts, undo, stash, .gitignore, gh CLI, PR workflow |
| 05 | [VS Code](05_vscode.md) | Shortcuts, multi-cursor, search, debugging, Python setup, Git, extensions, settings, remote |
| 06 | [Regex](06_regex.md) | Classes, anchors, quantifiers, groups, lookarounds, common patterns, Python re, pandas, grep, SQL |

## Python

| # | Guide | Covers |
|---|---|---|
| 07 | [Python Basics](07_python-basics.md) | Types, strings, f-strings, lists, dicts, loops, comprehensions, functions, errors, files, classes, logging |
| 08 | [Python Virtual Environment](08_python-virtual-environment.md) | venv create/activate, pip, requirements.txt, VS Code, troubleshooting |
| 09 | [uv](09_uv.md) | Projects, add/remove, run, lock/sync, Python versions, pip interface, uvx tools, Docker |
| 10 | [Jupyter](10_jupyter.md) | Kernels from venv, shortcuts, magics, display options, autoreload, export, notebooks in Git |

## Data and Machine Learning

| # | Guide | Covers |
|---|---|---|
| 11 | [NumPy](11_numpy.md) | Create arrays, indexing, filtering, reshape, math, broadcasting, axis, random, linear algebra |
| 12 | [Pandas](12_pandas.md) | Read/write, inspect, select, filter, clean, groupby, pivot, merge |
| 13 | [SQL](13_sql.md) | SELECT, WHERE, GROUP BY, JOINs, CTEs, window functions, DDL/DML, psql/sqlite3, SQL from pandas |
| 14 | [Matplotlib](14_matplotlib.md) | Line, scatter, bar, hist, box, pie, labels, legend, subplots, styles, save |
| 15 | [Seaborn](15_seaborn.md) | Distribution, categorical, relationship, regression, heatmap, pairplot, facets, palettes |
| 16 | [Scikit-learn](16_scikit-learn.md) | Split, preprocessing, pipelines, models, metrics, cross-validation, tuning, saving models |

## APIs and Deployment

| # | Guide | Covers |
|---|---|---|
| 17 | [FastAPI](17_fastapi.md) | Routes, Pydantic validation, dependencies, settings, routers, testing, ML model API, Docker |
| 18 | [Docker](18_docker.md) | Images, containers, run options, Dockerfile, volumes, networks, Compose, cleanup, registry |
| 19 | [Azure VM + Linux + Ollama](19_azure-vm-ollama.md) | Azure CLI, VM, NSG, SSH, Linux basics, Ollama, SSH tunnel |

## Conventions

- File names: `NN_topic.md` (two-digit number, lowercase, hyphens).
- Each guide opens with an **Introduction**: what the tool is, why we use it, key terms and where it fits with the other guides.
- Then a numbered **Contents** list; sections are numbered to match.
- Section **0. Flags and Parameters** breaks a sample command into its parts and explains every flag / parameter used in that guide.
- Each section opens with **What** (what it is), **How** (how it works) and **When to use** (a real scenario).
- Commands have a short comment on the right explaining what they do.
- Most guides end with a **Troubleshooting** table of common errors and fixes.
