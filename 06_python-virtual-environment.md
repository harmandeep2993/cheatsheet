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

A virtual environment is an isolated folder with its own Python interpreter and its own installed packages.

- Each project gets its own package versions, so projects do not conflict.
- The system Python stays clean.
- The project is reproducible on another machine via `requirements.txt`.

Common folder names: `.venv` (recommended), `venv`, `env`.

## 2. Check Python Installation

```powershell
python --version        # Windows
py --version            # Windows launcher
py -0                   # list all installed Python versions (Windows)
python3 --version       # Mac / Linux
```

## 3. Create

```powershell
python -m venv .venv            # Windows
python3 -m venv .venv           # Mac / Linux
py -3.12 -m venv .venv          # specific Python version (Windows)
```

## 4. Activate

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

```powershell
deactivate
```

## 6. Install and Manage Packages

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

```powershell
pip freeze > requirements.txt       # save current packages
pip install -r requirements.txt     # install from file
```

## 8. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

## 9. Delete

Deactivate first, then delete the folder:

```powershell
Remove-Item -Recurse -Force .venv   # Windows PowerShell
rmdir /s /q .venv                   # Windows CMD
rm -rf .venv                        # Mac / Linux
```

## 10. Use in VS Code

1. `Ctrl+Shift+P` -> **Python: Select Interpreter**
2. Choose the one inside `.venv`
3. New terminals will activate it automatically

## 11. Git: Ignore the Environment

Add to `.gitignore` (commit `requirements.txt`, never the environment folder):

```text
.venv/
venv/
env/
```

## 12. Typical Workflow

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
