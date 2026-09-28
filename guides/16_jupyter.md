# 16 - Jupyter

<!-- nav:start -->
**Previous:** [15 - pytest](15_pytest.md) | **Index:** [All guides](../README.md) | **Next:** [17 - NumPy](17_numpy.md)
<!-- nav:end -->

Quick reference for Jupyter notebooks (JupyterLab, classic Notebook and notebooks in VS Code).

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### Before you start

**You should know:** basic Python ([10](10_python-basics.md)) and how to create a project environment ([12 - uv](12_uv.md)), because a notebook runs inside one.

**The problem it solves:** data work is exploration: load data, look at it, try something, look again. With a normal script you rerun everything from the start for every small change, and results (tables, charts) appear in separate windows or not at all. You also want to explain your findings next to the code that produced them.

**Before Jupyter:** people used the Python prompt (results vanish when you close it), scripts (rerun everything each time), or tools like MATLAB and Mathematica notebooks. IPython Notebook (2011) brought that notebook style to Python; it became Jupyter when it grew to support other languages (Julia, Python, R: "Ju-Pyt-R").

**Think of it like:** a lab notebook. Each experiment (cell) is written down with its result right below it, you can redo one experiment without redoing the whole day, and a reader can follow your reasoning. The catch is the same as with a real lab notebook: cells run in the order you choose, so a notebook can end up in a state nobody can reproduce unless you rerun it top to bottom.

### What is Jupyter?

Jupyter is an interactive environment where you write and run code in small blocks called **cells** inside a **notebook** (`.ipynb` file). The output of each cell (tables, charts, text) appears right below it, and you can mix code with Markdown explanations. **JupyterLab** is the browser-based app; VS Code can open notebooks too. Behind every notebook runs a **kernel**: the Python process that executes your cells and keeps variables in memory between them.

### Why use it?

- **Explore step by step**: run one cell, look at the result, adjust, run again, without re-running everything.
- **See results immediately**: DataFrames and plots show inline.
- **Tell a story**: combine code, results and explanations in one document.
- **Great for data analysis, teaching and prototyping** ML models.
- **Share and export**: HTML / PDF reports, or share the notebook itself.

Notebooks are less suited for production code: move stable code into `.py` modules and scripts.

### Key terms

| Term | Meaning |
|---|---|
| Notebook | The `.ipynb` document with cells |
| Cell | One block of code or Markdown |
| Kernel | The Python process that runs the cells |
| Magic command | Jupyter helper starting with `%` or `%%` (`%timeit`) |
| Execution count | The number `[5]` showing the order cells ran |

**Where it fits:** the usual place to work with [17 - NumPy](17_numpy.md), [18 - Pandas](18_pandas.md), [21 - Matplotlib](21_matplotlib.md) and [23 - Scikit-learn](23_scikit-learn.md). Also great for prototyping LLM calls ([27 - LLM APIs](27_llm-apis.md)) and RAG ([31](31_rag.md)).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Project Jupyter documentation | https://docs.jupyter.org/ |
| JupyterLab documentation | https://jupyterlab.readthedocs.io/ |
| IPython magic commands | https://ipython.readthedocs.io/en/stable/interactive/magics.html |
| Jupyter notebooks in VS Code | https://code.visualstudio.com/docs/datascience/jupyter-notebooks |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install and Start](#1-install-and-start)
2. [Use a Virtual Environment as Kernel](#2-use-a-virtual-environment-as-kernel)
3. [Notebooks in VS Code](#3-notebooks-in-vs-code)
4. [Cells and Modes](#4-cells-and-modes)
5. [Keyboard Shortcuts](#5-keyboard-shortcuts)
6. [Shell Commands (!)](#6-shell-commands-)
7. [Line Magics (%)](#7-line-magics-)
8. [Cell Magics (%%)](#8-cell-magics-)
9. [Display Output](#9-display-output)
10. [Pandas Display Options](#10-pandas-display-options)
11. [Plots in Notebooks](#11-plots-in-notebooks)
12. [Auto-reload Your Own Modules](#12-auto-reload-your-own-modules)
13. [Kernel Management](#13-kernel-management)
14. [Export and Convert](#14-export-and-convert)
15. [Notebooks and Git](#15-notebooks-and-git)
16. [Good Practices](#16-good-practices)
17. [Troubleshooting](#17-troubleshooting)
18. [Try It](#18-try-it)

---

## 0. Flags and Parameters

> The meaning of every flag in the Jupyter commands and magics below. Tables list each command-line flag and magic option.
>
> Use this when you see `python -m ipykernel install --user --name myproject` and want to know what each part does.

### How a command is built

```text
python -m ipykernel  install  --user  --name myproject  --display-name "Python (myproject)"
          |          |        |       |                 |
          |          |        |       |                 +-- label shown in the kernel menu
          |          |        |       +-------------------- internal kernel name (no spaces)
          |          |        +---------------------------- install for your user only (no admin)
          |          +------------------------------------- action
          +------------------------------------------------ module that registers kernels
```

### Command-line flags

| Command | Flag | Meaning |
|---|---|---|
| `jupyter lab` | `--no-browser` | Start the server without opening a browser |
| `jupyter lab` | `--port 8889` | Use another port (default 8888) |
| `ipykernel install` | `--user` | Install for the current user only |
| `ipykernel install` | `--name` | Internal kernel name |
| `ipykernel install` | `--display-name` | Name shown in the kernel list |
| `nbconvert` | `--to html` | Output format: `html`, `script`, `markdown`, `pdf`, `webpdf`, `notebook` |
| `nbconvert` | `--no-input` | Hide code cells, keep outputs |
| `nbconvert` | `--execute` | Run all cells before converting |
| `nbconvert` | `--clear-output` | Remove all outputs |
| `nbconvert` | `--inplace` | Overwrite the input file instead of creating a new one |
| `nbstripout` | `--install` | Add a Git filter that strips outputs on every commit |
| `jupytext` | `--set-formats ipynb,py:percent` | Keep the notebook paired with a `.py` file using `# %%` cells |

### Magic options

| Magic | Option | Meaning |
|---|---|---|
| `%reset` | `-f` | Force: do not ask for confirmation |
| `%history` | `-n 1-10` | Show inputs 1 to 10 with their numbers |
| `%autoreload` | `2` | Reload all modules before each cell (`1` = only `%aimport` ones, `0` = off) |
| `%matplotlib` | `inline` / `widget` | Static images / interactive plots |
| `%%capture` | `output` | Variable name that stores the hidden output |
| `%%writefile` | `helpers.py` | File to write the cell into (`-a` to append) |
| `?` / `??` | after a name | Show docstring / show source code |

## 1. Install and Start

> Installing and starting Jupyter in the browser. `pip install jupyterlab`, then `jupyter lab` starts a local server on port 8888.
>
> Use it for exploratory data analysis, teaching, or step-by-step experiments with visible output.

```powershell
pip install jupyterlab              # JupyterLab (recommended)
pip install notebook                # classic Notebook

jupyter lab                         # start, opens http://localhost:8888
jupyter notebook                    # start classic
jupyter lab --no-browser --port 8889
jupyter server list                 # running servers and their tokens
```

Stop the server: `Ctrl+C` twice in the terminal.

## 2. Use a Virtual Environment as Kernel

> Letting notebooks use your project's venv. Install `ipykernel` in the venv and register it as a named kernel.
>
> Use it for notebook imports fail even though the package is installed in your venv.

A **kernel** is the Python process that runs your code. Register each venv once:

```powershell
.venv\Scripts\Activate.ps1
pip install ipykernel
python -m ipykernel install --user --name myproject --display-name "Python (myproject)"

jupyter kernelspec list                 # installed kernels
jupyter kernelspec uninstall myproject  # remove one
```

Then pick **Python (myproject)** in Kernel -> Change Kernel.

## 3. Notebooks in VS Code

> Running notebooks inside VS Code instead of the browser. The Jupyter extension opens `.ipynb` files; choose the venv as kernel.
>
> Use this when you want notebooks plus VS Code features (Git, debugging, variable viewer).

1. Install the **Jupyter** and **Python** extensions.
2. Create `analysis.ipynb` (or `Ctrl+Shift+P` -> **Create: New Jupyter Notebook**).
3. Top right: **Select Kernel** -> choose the `.venv` interpreter (needs `ipykernel` installed in it).
4. `Shift+Enter` runs a cell. The **Variables** button shows all variables.

Interactive window alternative: put `# %%` in a normal `.py` file to create runnable cells.

## 4. Cells and Modes

> Cell types and the two keyboard modes. Code cells run Python, Markdown cells show text; `Esc` / `Enter` switch mode.
>
> Use it for mixing code with explanations to make a readable analysis.

| Cell type | Content |
|---|---|
| **Code** | Python, output shown below |
| **Markdown** | Text, headings, tables (see [02 - Markdown](02_markdown.md)) |
| **Raw** | Unformatted text |

| Mode | How to enter | Border |
|---|---|---|
| **Command** mode (act on cells) | `Esc` | blue |
| **Edit** mode (type in a cell) | `Enter` | green |

## 5. Keyboard Shortcuts

> Shortcuts for running and editing cells quickly. Command mode for cell actions, edit mode for typing.
>
> Use it for all the time; `Shift+Enter`, `A`, `B`, `D D` save a lot of clicking.

### Both modes

| Keys | Action |
|---|---|
| `Shift+Enter` | Run cell, move to next |
| `Ctrl+Enter` | Run cell, stay |
| `Alt+Enter` | Run cell, insert new below |

### Command mode (press `Esc` first)

| Keys | Action |
|---|---|
| `A` / `B` | Insert cell above / below |
| `D`, `D` | Delete cell |
| `Z` | Undo delete |
| `M` / `Y` | Change to Markdown / Code |
| `X` / `C` / `V` | Cut / copy / paste cell |
| `Shift+M` | Merge selected cells |
| `Up` / `Down` or `K` / `J` | Move between cells |
| `Shift+Up` / `Shift+Down` | Select several cells |
| `L` | Toggle line numbers |
| `O` | Toggle output |
| `I`, `I` | Interrupt kernel |
| `0`, `0` | Restart kernel |
| `H` | Show all shortcuts |

### Edit mode

| Keys | Action |
|---|---|
| `Tab` | Autocomplete |
| `Shift+Tab` | Show function signature / docstring |
| `Ctrl+/` | Comment / uncomment |
| `Ctrl+Shift+-` | Split cell at cursor |

## 6. Shell Commands (!)

> Running terminal commands from a cell. `!` sends the line to the shell; `%pip` installs into the current kernel.
>
> Use it for installing a missing package or listing files without leaving the notebook.

```python
!pip install pandas                 # runs in a shell (may use the wrong Python)
%pip install pandas                 # installs into the CURRENT kernel (preferred)
!ls                                 # list files (Linux / Mac)
!dir                                # list files (Windows)
files = !ls *.csv                   # capture output into a variable
!echo {variable}                    # pass Python variables with { }
```

## 7. Line Magics (%)

> Jupyter helper commands for one line. Lines starting with `%` are handled by Jupyter (IPython), not Python.
>
> Use it for timing code (`%timeit`), listing variables, changing folder, loading scripts.

Apply to one line.

```python
%pwd                                # current folder
%cd data                            # change folder
%ls                                 # list files
%who                                # list variables
%whos                               # variables with type and info
%time result = slow_function()      # time one run
%timeit sum(range(1000))            # average over many runs
%run script.py                      # run a Python file
%load script.py                     # load file content into cell
%history -n 1-10                    # past inputs
%env MY_VAR=value                   # set environment variable
%env                                # show environment variables
%reset -f                           # delete all variables
%debug                              # debugger after an error
%lsmagic                            # list all magics
%matplotlib inline                  # static plots
%config InlineBackend.figure_format = "retina"   # sharper plots
```

`?` and `??` for help: `pd.read_csv?` (docstring), `my_func??` (source code).

## 8. Cell Magics (%%)

> Jupyter helper commands for a whole cell. `%%` on the first line applies to the entire cell.
>
> Use it for timing a whole cell, writing a cell to a `.py` file, running bash.

Must be the **first line** of the cell; apply to the whole cell.

```python
%%time                              # time the whole cell
%%timeit                            # average run time of the cell
%%writefile helpers.py              # save cell content to a file
%%capture output                    # hide output (read later with output.show())
%%bash                              # run cell as bash (Linux / Mac / Git Bash)
%%html                              # render HTML
%%markdown                          # render Markdown
```

## 9. Display Output

> Controlling what a cell shows. The last expression is shown automatically; `display()` shows several; `;` hides.
>
> Use it for showing two DataFrames in one cell, or hiding noisy return values.

```python
df                                  # last expression in a cell is displayed
display(df.head())                  # display several things in one cell
display(df1, df2)
print(df)                           # plain text (no table formatting)
x = 5;                              # ; at the end hides output

from IPython.display import Markdown, HTML, Image
display(Markdown("**Bold** text"))
display(Image("chart.png"))
```

## 10. Pandas Display Options

> Showing more or nicer pandas output. `pd.set_option` changes limits and formats; `df.style` adds colours.
>
> Use this when columns are hidden as `...`, or you want a readable table for a report.

```python
import pandas as pd

pd.set_option("display.max_columns", None)      # show all columns
pd.set_option("display.max_rows", 200)
pd.set_option("display.width", 200)
pd.set_option("display.float_format", "{:.2f}".format)
pd.set_option("display.max_colwidth", 100)      # longer text in cells
pd.reset_option("all")                          # back to defaults

df.style.highlight_max(axis=0)                  # highlight max per column
df.style.background_gradient(cmap="Blues")      # heatmap-style table
df.style.format({"price": "{:.2f} EUR"})
```

## 11. Plots in Notebooks

> How plots appear in notebooks. `%matplotlib inline` embeds static images; `widget` makes them interactive.
>
> Use this when plots are not showing, or you want to zoom / pan.

```python
import matplotlib.pyplot as plt
%matplotlib inline                  # static (default)
%matplotlib widget                  # interactive (pip install ipympl)

plt.plot([1, 2, 3]);                # ; hides the "[<Line2D ...>]" text
```

See [21 - Matplotlib](21_matplotlib.md) and [22 - Seaborn](22_seaborn.md).

## 12. Auto-reload Your Own Modules

> Picking up changes in your own `.py` files automatically. The autoreload extension re-imports modules before each cell.
>
> Use this when you keep helper functions in a module and edit them while using the notebook.

Without this, edits to your `.py` files are ignored until you restart the kernel.

```python
%load_ext autoreload
%autoreload 2                       # reload all modules before each cell

from utils.cleaning import clean_data
```

## 13. Kernel Management

> Stopping, restarting and switching the Python process behind the notebook. Interrupt stops a cell; restart clears all variables.
>
> Use this when a cell hangs, memory is full, or state is confusing after running cells out of order.

| Action | JupyterLab menu | Shortcut |
|---|---|---|
| Interrupt (stop running cell) | Kernel -> Interrupt | `I`, `I` |
| Restart (clear all variables) | Kernel -> Restart | `0`, `0` |
| Restart and run all | Kernel -> Restart Kernel and Run All Cells | - |
| Change kernel | Kernel -> Change Kernel | - |
| Clear all outputs | Edit -> Clear All Outputs | - |

Check which Python the kernel uses:

```python
import sys
sys.executable                      # should point inside your .venv
```

## 14. Export and Convert

> Turning a notebook into HTML, PDF, a script or Markdown. `jupyter nbconvert --to <format>`.
>
> Use it for sharing results with people who do not use Jupyter, or moving code into a `.py` file.

```powershell
jupyter nbconvert --to html analysis.ipynb           # HTML report
jupyter nbconvert --to html --no-input analysis.ipynb   # hide code
jupyter nbconvert --to script analysis.ipynb         # .py file
jupyter nbconvert --to markdown analysis.ipynb
jupyter nbconvert --to pdf analysis.ipynb            # needs LaTeX (or use --to webpdf)
jupyter nbconvert --to notebook --execute analysis.ipynb   # run all, save outputs
```

## 15. Notebooks and Git

> Keeping notebooks clean in version control. Strip outputs before committing (`nbstripout`) or pair with a `.py` file (`jupytext`).
>
> Use it for notebooks in a Git repo where diffs are unreadable or outputs contain data.

Outputs make diffs noisy and can leak data. Options:

```powershell
jupyter nbconvert --clear-output --inplace analysis.ipynb   # strip outputs manually

pip install nbstripout
nbstripout --install                # strip outputs automatically on every commit

pip install jupytext
jupytext --set-formats ipynb,py:percent analysis.ipynb     # keep a paired .py copy for diffs
```

Add `.ipynb_checkpoints/` to `.gitignore`.

## 16. Good Practices

> Habits that keep notebooks reliable. Imports first, restart-and-run-all before sharing, reusable code in modules.
>
> Use it in any notebook someone else (or future you) will run.

- Put all imports in the first cell.
- Run **Restart and Run All** before sharing: it proves the notebook runs top to bottom.
- Do not rely on cell execution order; the number `[5]` shows the order cells ran.
- Move reusable code into `.py` files and import it (with autoreload).
- Use Markdown cells as headings to structure the analysis.
- Keep secrets out of notebooks; load them from environment variables.

## 17. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` but package is installed | Kernel uses another Python; check `sys.executable`, use `%pip install`, or select the right kernel |
| Venv not shown as kernel | `pip install ipykernel` in the venv, then `python -m ipykernel install --user --name ...` |
| Cell shows `[*]` forever | Still running or stuck; Interrupt (`I`, `I`) or Restart (`0`, `0`) |
| Variables from deleted cells still exist | Restart the kernel |
| Edits to `.py` files not picked up | `%load_ext autoreload` + `%autoreload 2`, or restart |
| `jupyter` not recognized | Activate the venv or `pip install jupyterlab` |
| Asks for a token / password | `jupyter server list` shows the URL with token |
| Notebook is huge / slow | Clear outputs (large images or DataFrames stored in the file) |
| Plot not showing | Add `%matplotlib inline` or `plt.show()` |

## 18. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Venv as kernel

Make your project's `.venv` selectable as a Jupyter kernel.

<details markdown="1">
<summary>Solution</summary>

```powershell
.venv\Scripts\Activate.ps1
pip install ipykernel
python -m ipykernel install --user --name myproject --display-name "Python (myproject)"
```

</details>

### Exercise 2: Timing

Measure a one-line expression and a whole cell.

<details markdown="1">
<summary>Solution</summary>

```python
%timeit sum(range(10_000))
```

```python
%%time
df = pd.read_csv("big.csv")
summary = df.groupby("region")["amount"].sum()
```

</details>

### Exercise 3: Edit modules live

Make the notebook pick up changes you save in `utils.py` without restarting.

<details markdown="1">
<summary>Solution</summary>

```python
%load_ext autoreload
%autoreload 2
from utils import clean_data
```

</details>

---

<!-- nav:start -->
**Previous:** [15 - pytest](15_pytest.md) | **Index:** [All guides](../README.md) | **Next:** [17 - NumPy](17_numpy.md)
<!-- nav:end -->
