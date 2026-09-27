# 07 - Jupyter

Quick reference for Jupyter notebooks (JupyterLab, classic Notebook and notebooks in VS Code).

## Contents

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

---

## 1. Install and Start

> - **What:** Installing and starting Jupyter in the browser.
> - **How:** `pip install jupyterlab`, then `jupyter lab` starts a local server on port 8888.
> - **When to use:** Exploratory data analysis, teaching, or step-by-step experiments with visible output.

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

> - **What:** Letting notebooks use your project's venv.
> - **How:** Install `ipykernel` in the venv and register it as a named kernel.
> - **When to use:** Notebook imports fail even though the package is installed in your venv.

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

> - **What:** Running notebooks inside VS Code instead of the browser.
> - **How:** The Jupyter extension opens `.ipynb` files; choose the venv as kernel.
> - **When to use:** You want notebooks plus VS Code features (Git, debugging, variable viewer).

1. Install the **Jupyter** and **Python** extensions.
2. Create `analysis.ipynb` (or `Ctrl+Shift+P` -> **Create: New Jupyter Notebook**).
3. Top right: **Select Kernel** -> choose the `.venv` interpreter (needs `ipykernel` installed in it).
4. `Shift+Enter` runs a cell. The **Variables** button shows all variables.

Interactive window alternative: put `# %%` in a normal `.py` file to create runnable cells.

## 4. Cells and Modes

> - **What:** Cell types and the two keyboard modes.
> - **How:** Code cells run Python, Markdown cells show text; `Esc` / `Enter` switch mode.
> - **When to use:** Mixing code with explanations to make a readable analysis.

| Cell type | Content |
|---|---|
| **Code** | Python, output shown below |
| **Markdown** | Text, headings, tables (see [01 - Markdown](01_markdown.md)) |
| **Raw** | Unformatted text |

| Mode | How to enter | Border |
|---|---|---|
| **Command** mode (act on cells) | `Esc` | blue |
| **Edit** mode (type in a cell) | `Enter` | green |

## 5. Keyboard Shortcuts

> - **What:** Shortcuts for running and editing cells quickly.
> - **How:** Command mode for cell actions, edit mode for typing.
> - **When to use:** All the time; `Shift+Enter`, `A`, `B`, `D D` save a lot of clicking.

**Both modes**

| Keys | Action |
|---|---|
| `Shift+Enter` | Run cell, move to next |
| `Ctrl+Enter` | Run cell, stay |
| `Alt+Enter` | Run cell, insert new below |

**Command mode** (press `Esc` first)

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

**Edit mode**

| Keys | Action |
|---|---|
| `Tab` | Autocomplete |
| `Shift+Tab` | Show function signature / docstring |
| `Ctrl+/` | Comment / uncomment |
| `Ctrl+Shift+-` | Split cell at cursor |

## 6. Shell Commands (!)

> - **What:** Running terminal commands from a cell.
> - **How:** `!` sends the line to the shell; `%pip` installs into the current kernel.
> - **When to use:** Installing a missing package or listing files without leaving the notebook.

```python
!pip install pandas                 # runs in a shell (may use the wrong Python)
%pip install pandas                 # installs into the CURRENT kernel (preferred)
!ls                                 # list files (Linux / Mac)
!dir                                # list files (Windows)
files = !ls *.csv                   # capture output into a variable
!echo {variable}                    # pass Python variables with { }
```

## 7. Line Magics (%)

> - **What:** Jupyter helper commands for one line.
> - **How:** Lines starting with `%` are handled by Jupyter (IPython), not Python.
> - **When to use:** Timing code (`%timeit`), listing variables, changing folder, loading scripts.

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

> - **What:** Jupyter helper commands for a whole cell.
> - **How:** `%%` on the first line applies to the entire cell.
> - **When to use:** Timing a whole cell, writing a cell to a `.py` file, running bash.

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

> - **What:** Controlling what a cell shows.
> - **How:** The last expression is shown automatically; `display()` shows several; `;` hides.
> - **When to use:** Showing two DataFrames in one cell, or hiding noisy return values.

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

> - **What:** Showing more or nicer pandas output.
> - **How:** `pd.set_option` changes limits and formats; `df.style` adds colours.
> - **When to use:** Columns are hidden as `...`, or you want a readable table for a report.

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

> - **What:** How plots appear in notebooks.
> - **How:** `%matplotlib inline` embeds static images; `widget` makes them interactive.
> - **When to use:** Plots are not showing, or you want to zoom / pan.

```python
import matplotlib.pyplot as plt
%matplotlib inline                  # static (default)
%matplotlib widget                  # interactive (pip install ipympl)

plt.plot([1, 2, 3]);                # ; hides the "[<Line2D ...>]" text
```

See [11 - Matplotlib](11_matplotlib.md) and [12 - Seaborn](12_seaborn.md).

## 12. Auto-reload Your Own Modules

> - **What:** Picking up changes in your own `.py` files automatically.
> - **How:** The autoreload extension re-imports modules before each cell.
> - **When to use:** You keep helper functions in a module and edit them while using the notebook.

Without this, edits to your `.py` files are ignored until you restart the kernel.

```python
%load_ext autoreload
%autoreload 2                       # reload all modules before each cell

from utils.cleaning import clean_data
```

## 13. Kernel Management

> - **What:** Stopping, restarting and switching the Python process behind the notebook.
> - **How:** Interrupt stops a cell; restart clears all variables.
> - **When to use:** A cell hangs, memory is full, or state is confusing after running cells out of order.

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

> - **What:** Turning a notebook into HTML, PDF, a script or Markdown.
> - **How:** `jupyter nbconvert --to <format>`.
> - **When to use:** Sharing results with people who do not use Jupyter, or moving code into a `.py` file.

```powershell
jupyter nbconvert --to html analysis.ipynb           # HTML report
jupyter nbconvert --to html --no-input analysis.ipynb   # hide code
jupyter nbconvert --to script analysis.ipynb         # .py file
jupyter nbconvert --to markdown analysis.ipynb
jupyter nbconvert --to pdf analysis.ipynb            # needs LaTeX (or use --to webpdf)
jupyter nbconvert --to notebook --execute analysis.ipynb   # run all, save outputs
```

## 15. Notebooks and Git

> - **What:** Keeping notebooks clean in version control.
> - **How:** Strip outputs before committing (`nbstripout`) or pair with a `.py` file (`jupytext`).
> - **When to use:** Notebooks in a Git repo where diffs are unreadable or outputs contain data.

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

> - **What:** Habits that keep notebooks reliable.
> - **How:** Imports first, restart-and-run-all before sharing, reusable code in modules.
> - **When to use:** Any notebook someone else (or future you) will run.

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
