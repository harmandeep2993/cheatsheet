# pocket-guide

Personal quick-reference cheat sheets, numbered from basic to advanced.

## Foundations

| # | Guide | Covers |
|---|---|---|
| 01 | [Markdown](01_markdown.md) | Headings, formatting, lists, links, images, code, tables, anchors |
| 02 | [Terminal and PowerShell](02_terminal-powershell.md) | Navigation, files, search, pipes, env vars, processes, network, winget, CMD/Bash equivalents |
| 03 | [Linux](03_linux.md) | Navigation, files, grep/find, permissions, apt, processes, systemd, network, SSH, tar, cron |
| 04 | [Git and GitHub](04_git.md) | Commit, branch, merge/rebase, conflicts, undo, stash, .gitignore, gh CLI, PR workflow |

## Python

| # | Guide | Covers |
|---|---|---|
| 05 | [Python Basics](05_python-basics.md) | Types, strings, f-strings, lists, dicts, loops, comprehensions, functions, errors, files, classes, logging |
| 06 | [Python Virtual Environment](06_python-virtual-environment.md) | venv create/activate, pip, requirements.txt, VS Code, troubleshooting |
| 07 | [Jupyter](07_jupyter.md) | Kernels from venv, shortcuts, magics, display options, autoreload, export, notebooks in Git |

## Data

| # | Guide | Covers |
|---|---|---|
| 08 | [NumPy](08_numpy.md) | Create arrays, indexing, filtering, reshape, math, broadcasting, axis, random, linear algebra |
| 09 | [Pandas](09_pandas.md) | Read/write, inspect, select, filter, clean, groupby, pivot, merge |
| 10 | [SQL](10_sql.md) | SELECT, WHERE, GROUP BY, JOINs, CTEs, window functions, DDL/DML, psql/sqlite3, SQL from pandas |
| 11 | [Matplotlib](11_matplotlib.md) | Line, scatter, bar, hist, box, pie, labels, legend, subplots, styles, save |
| 12 | [Seaborn](12_seaborn.md) | Distribution, categorical, relationship, regression, heatmap, pairplot, facets, palettes |

## Deployment

| # | Guide | Covers |
|---|---|---|
| 13 | [Docker](13_docker.md) | Images, containers, run options, Dockerfile, volumes, networks, Compose, cleanup, registry |
| 14 | [Azure VM + Linux + Ollama](14_azure-vm-ollama.md) | Azure CLI, VM, NSG, SSH, Linux basics, Ollama, SSH tunnel |

## Conventions

- File names: `NN_topic.md` (two-digit number, lowercase, hyphens).
- Each guide starts with a numbered **Contents** list; sections are numbered to match.
- Commands have a short comment on the right explaining what they do.
- Most guides end with a **Troubleshooting** table of common errors and fixes.
