# 06 - Python Virtual Environment

Quick reference for creating and managing Python virtual environments with `venv` and `pip`.

## Contents

1. [What and Why](#1-what-and-why)
2. [Check Python Installation](#2-check-python-installation)
3. [Create](#3-create)
4. [Activate](#4-activate)
5. [Deactivate](#5-deactivate)
6. [Install and Manage Packages](#6-install-and-manage-packages)
7. [requirements.txt](#7-requirementstxt)
8. [Upgrade pip](#8-upgrade-pip)
9. [Delete](#9-delete)
10. [Use in VS Code](#10-use-in-vs-code)
11. [Git: Ignore the Environment](#11-git-ignore-the-environment)
12. [Typical Workflow](#12-typical-workflow)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. What and Why

> - **What:** An isolated Python setup per project.
> - **How:** A folder (`.venv`) holding its own Python and packages, separate from the system.
> - **When to use:** Every Python project, so package versions never clash between projects.

A virtual environment is an isolated folder with its own Python interpreter and its own installed packages.

- Each project gets its own package versions, so projects do not conflict.
- The system Python stays clean.
- The project is reproducible on another machine via `requirements.txt`.

Common folder names: `.venv` (recommended), `venv`, `env`.

## 2. Check Python Installation

> - **What:** Checking Python is installed and which version.
> - **How:** `python --version`; on Windows `py -0` lists all installed versions.
> - **When to use:** Before creating a venv, or when a project needs a specific Python version.

```powershell
python --version        # Windows
py --version            # Windows launcher
py -0                   # list all installed Python versions (Windows)
python3 --version       # Mac / Linux
```

## 3. Create

> - **What:** Creating the environment folder.
> - **How:** `python -m venv .venv` copies / links a Python interpreter into `.venv`.
> - **When to use:** Once per project, right after creating or cloning it.

```powershell
python -m venv .venv            # Windows
python3 -m venv .venv           # Mac / Linux
py -3.12 -m venv .venv          # specific Python version (Windows)
```

## 4. Activate

> - **What:** Switching the terminal to use the venv's Python and pip.
> - **How:** Run the activate script for your shell; the prompt then shows `(.venv)`.
> - **When to use:** Every new terminal before running or installing anything for the project.

| Shell | Command |
|---|---|
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows CMD | `.venv\Scripts\activate.bat` |
| Git Bash (Windows) | `source .venv/Scripts/activate` |
| Mac / Linux | `source .venv/bin/activate` |

After activation the prompt shows the environment name:

```text
(.venv) PS D:\Projects\my-project>
```

Check which Python is active:

```powershell
where.exe python        # Windows (first path should be inside .venv)
which python            # Mac / Linux
python -c "import sys; print(sys.prefix)"
```

## 5. Deactivate

> - **What:** Switching back to the system Python.
> - **How:** `deactivate` undoes the activation in the current terminal.
> - **When to use:** Moving to another project in the same terminal.

```powershell
deactivate
```

## 6. Install and Manage Packages

> - **What:** Adding, upgrading, removing and inspecting packages.
> - **How:** `pip` installs from PyPI into the active environment.
> - **When to use:** Whenever the project needs a new library or a different version.

```powershell
pip install pandas                  # install latest
pip install pandas==2.2.2           # install exact version
pip install "pandas>=2.0"           # minimum version
pip install --upgrade pandas        # upgrade
pip uninstall pandas                # remove
pip list                            # installed packages
pip list --outdated                 # packages with newer versions
pip show pandas                     # details of one package
```

## 7. requirements.txt

> - **What:** A file listing the exact packages the project needs.
> - **How:** `pip freeze` writes installed versions; `pip install -r` reinstalls them.
> - **When to use:** Sharing a project, deploying it, or rebuilding the venv on another machine.

```powershell
pip freeze > requirements.txt       # save current packages
pip install -r requirements.txt     # install from file
```

## 8. Upgrade pip

> - **What:** Updating pip itself.
> - **How:** `python -m pip install --upgrade pip` inside the venv.
> - **When to use:** Right after creating a venv, or when pip warns it is outdated.

```powershell
python -m pip install --upgrade pip
```

## 9. Delete

> - **What:** Removing an environment completely.
> - **How:** Delete the `.venv` folder; nothing else is installed system-wide.
> - **When to use:** The venv is broken, the project moved, or you want a clean reinstall.

Deactivate first, then delete the folder:

```powershell
Remove-Item -Recurse -Force .venv   # Windows PowerShell
rmdir /s /q .venv                   # Windows CMD
rm -rf .venv                        # Mac / Linux
```

## 10. Use in VS Code

> - **What:** Making VS Code use the project venv.
> - **How:** Select the interpreter inside `.venv`; VS Code then activates it in new terminals.
> - **When to use:** Imports show red squiggles, or Run uses the wrong Python.

1. `Ctrl+Shift+P` -> **Python: Select Interpreter**
2. Choose the one inside `.venv`
3. New terminals will activate it automatically

## 11. Git: Ignore the Environment

> - **What:** Keeping the venv out of Git.
> - **How:** Add the venv folder to `.gitignore`; commit only `requirements.txt`.
> - **When to use:** Every project; venvs are large and machine-specific.

Add to `.gitignore` (commit `requirements.txt`, never the environment folder):

```text
.venv/
venv/
env/
```

## 12. Typical Workflow

> - **What:** The full step-by-step flow for new and cloned projects.
> - **How:** Create, activate, upgrade pip, install, freeze.
> - **When to use:** Starting any project; copy the block as a checklist.

```powershell
# New project
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pandas
pip freeze > requirements.txt

# Cloned project
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 13. Troubleshooting

| Problem | Fix |
|---|---|
| `running scripts is disabled on this system` (PowerShell) | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `python` opens Microsoft Store | Install Python from python.org, or disable the alias in Settings -> Apps -> App execution aliases |
| `pip` installs into the wrong Python | Use `python -m pip install ...` |
| `ModuleNotFoundError` after install | Environment not activated, or wrong interpreter selected in VS Code |
| Moved or renamed the project folder | Delete `.venv` and recreate it (paths inside are absolute) |
