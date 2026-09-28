# 06 - VS Code

<!-- nav:start -->
**Previous:** [05 - Git and GitHub](05_git.md) | **Index:** [All guides](../README.md) | **Next:** [07 - Regex](07_regex.md)
<!-- nav:end -->

Quick reference for Visual Studio Code on Windows (on Mac use `Cmd` instead of `Ctrl`, `Option` instead of `Alt`).

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is VS Code?

Visual Studio Code is a free code editor from Microsoft. It is lightweight like a text editor but becomes a full development environment through **extensions**: Python support, debugging, Jupyter notebooks, Git, Docker, remote servers and more. It runs on Windows, macOS and Linux and is the most used editor among developers and data scientists.

### Why use it?

- **One tool for everything**: code, terminal, Git, notebooks, debugger and Markdown preview in one window.
- **Smart editing**: autocomplete, error highlighting, go to definition and rename across files (IntelliSense / Pylance).
- **Debugger**: pause code, inspect variables, step line by line.
- **Extensions**: add support for almost any language or tool.
- **Remote development**: edit code on a VM, in WSL or inside a Docker container as if it were local.
- **Free and fast**, with a huge community.

### Key terms

| Term | Meaning |
|---|---|
| Workspace | The folder (project) you have open |
| Command Palette | `Ctrl+Shift+P`: search box for every command |
| Extension | Add-on that adds features |
| Interpreter | The Python executable VS Code uses to run your code (pick your `.venv`) |
| IntelliSense | Autocomplete and code understanding |
| Breakpoint | A line where the debugger pauses |

**Where it fits:** the editor for all other guides; pairs with [11 - venv](11_python-virtual-environment.md) / [12 - uv](12_uv.md) and [05 - Git](05_git.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| VS Code documentation | https://code.visualstudio.com/docs |
| Python in VS Code | https://code.visualstudio.com/docs/python/python-tutorial |
| Remote development (SSH, WSL, containers) | https://code.visualstudio.com/docs/remote/remote-overview |
| Ruff (linter / formatter) | https://docs.astral.sh/ruff/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install and Open](#1-install-and-open)
2. [Interface Overview](#2-interface-overview)
3. [Command Palette and Quick Open](#3-command-palette-and-quick-open)
4. [Essential Shortcuts](#4-essential-shortcuts)
5. [Editing Shortcuts](#5-editing-shortcuts)
6. [Multi-Cursor and Selection](#6-multi-cursor-and-selection)
7. [Search and Replace](#7-search-and-replace)
8. [Code Navigation](#8-code-navigation)
9. [Integrated Terminal](#9-integrated-terminal)
10. [Python Setup](#10-python-setup)
11. [Run and Debug](#11-run-and-debug)
12. [launch.json (Debug Configurations)](#12-launchjson-debug-configurations)
13. [Git in VS Code](#13-git-in-vs-code)
14. [Recommended Extensions](#14-recommended-extensions)
15. [Settings](#15-settings)
16. [Formatting and Linting (Ruff)](#16-formatting-and-linting-ruff)
17. [Workspace Files and Tasks](#17-workspace-files-and-tasks)
18. [Remote Development (SSH, WSL, Containers)](#18-remote-development-ssh-wsl-containers)
19. [Troubleshooting](#19-troubleshooting)
20. [Try It](#20-try-it)

---

## 0. Flags and Parameters

> The options of the `code` command you type in a terminal. `code [options] [path]`; the path is a file or folder to open.
>
> Use it for opening projects, comparing files or installing extensions from the terminal.

```text
code  -g  app.py:42:5
|     |   |      |  |
|     |   |      |  +-- column
|     |   |      +----- line
|     |   +------------ file to open
|     +---------------- -g (--goto): jump to file:line:column
+---------------------- VS Code command-line launcher
```

| Flag | Long form | Meaning | Example |
|---|---|---|---|
| `.` | | Open the current folder | `code .` |
| `-n` | `--new-window` | Open in a new window | `code -n .` |
| `-r` | `--reuse-window` | Open in the window that is already open | `code -r notes.md` |
| `-g` | `--goto` | Open file at `line:column` | `code -g app.py:42` |
| `-d` | `--diff` | Compare two files side by side | `code -d old.py new.py` |
| `-w` | `--wait` | Wait until the file is closed (used as Git editor) | `code --wait` |
| | `--install-extension` | Install an extension by ID | `code --install-extension ms-python.python` |
| | `--list-extensions` | List installed extensions | `code --list-extensions` |
| | `--disable-extensions` | Start with all extensions off (troubleshooting) | `code --disable-extensions .` |

---

## 1. Install and Open

> Installing VS Code and opening a project folder. Install with winget or from code.visualstudio.com; open a whole folder, not single files.
>
> Use it for new machine, or the start of every work session.

```powershell
winget install -e --id Microsoft.VisualStudioCode
code .                          # open current folder
code D:\Projects\pocket-guide   # open a folder
```

During install on Windows, tick **Add to PATH** and **Open with Code** (right-click menu).

## 2. Interface Overview

> The main areas of the window. Activity bar on the left switches the side panel; editor in the middle; panel (terminal) at the bottom.
>
> Use this when getting oriented; knowing where things are when a guide says "open the Explorer".

| Area | Shortcut | Purpose |
|---|---|---|
| Explorer | `Ctrl+Shift+E` | Files and folders |
| Search | `Ctrl+Shift+F` | Search across all files |
| Source Control | `Ctrl+Shift+G` | Git changes, commit, push |
| Run and Debug | `Ctrl+Shift+D` | Start the debugger |
| Extensions | `Ctrl+Shift+X` | Install add-ons |
| Toggle side bar | `Ctrl+B` | Hide / show the left panel |
| Toggle panel | `Ctrl+J` | Hide / show terminal, problems, output |
| Problems | `Ctrl+Shift+M` | Errors and warnings list |
| Zen mode | `Ctrl+K Z` | Distraction-free editor (`Esc Esc` to leave) |

`Ctrl+K Z` means: press `Ctrl+K`, release, then press `Z`.

## 3. Command Palette and Quick Open

> Search boxes for every command and every file. Type part of a name; results filter as you type.
>
> Use this when you do not remember a shortcut or where a file is. This is the most useful shortcut in VS Code.

| Shortcut | Opens | Tip |
|---|---|---|
| `Ctrl+Shift+P` or `F1` | Command Palette (all commands) | Type "Python: Select Interpreter", "Format Document", ... |
| `Ctrl+P` | Quick Open (files by name) | Type `>` to switch to commands, `@` for symbols, `:` for a line |
| `Ctrl+G` | Go to line | `Ctrl+G` then `120` |
| `Ctrl+Shift+O` | Go to symbol in file | Jump to a function / class |
| `Ctrl+T` | Go to symbol in workspace | Find a function in any file |
| `Ctrl+R` | Recent folders / workspaces | Switch project |

## 4. Essential Shortcuts

> The shortcuts worth learning first. Built in; see or change all in `Ctrl+K Ctrl+S`.
>
> Use it every day; they remove most mouse work.

| Shortcut | Action |
|---|---|
| `Ctrl+S` | Save |
| `Ctrl+K S` | Save all |
| `Ctrl+W` | Close editor tab |
| `Ctrl+Shift+T` | Reopen closed tab |
| `Ctrl+Tab` | Switch between open tabs |
| `Ctrl+\` | Split editor |
| `Ctrl+1` / `Ctrl+2` | Focus left / right editor group |
| `Ctrl+N` | New file |
| `Ctrl+,` | Settings |
| `Ctrl+K Ctrl+S` | Keyboard shortcuts list |
| `Ctrl+=` / `Ctrl+-` | Zoom in / out |
| `Ctrl+Shift+N` | New window |

## 5. Editing Shortcuts

> Shortcuts for moving, copying and changing lines of code. Work on the current line when nothing is selected.
>
> Use it for reorganising code without cut-and-paste.

| Shortcut | Action |
|---|---|
| `Alt+Up` / `Alt+Down` | Move line up / down |
| `Shift+Alt+Up` / `Shift+Alt+Down` | Copy line up / down |
| `Ctrl+Shift+K` | Delete line |
| `Ctrl+X` (no selection) | Cut whole line |
| `Ctrl+Enter` / `Ctrl+Shift+Enter` | New line below / above |
| `Ctrl+/` | Toggle line comment |
| `Shift+Alt+A` | Toggle block comment |
| `Tab` / `Shift+Tab` | Indent / outdent selection |
| `Shift+Alt+F` | Format document |
| `Ctrl+Space` | Trigger suggestions |
| `Ctrl+Shift+Space` | Parameter hints |
| `Ctrl+.` | Quick fix (auto import, fix problem) |
| `F2` | Rename symbol everywhere |
| `Ctrl+Z` / `Ctrl+Y` | Undo / redo |
| `Ctrl+K Ctrl+0` / `Ctrl+K Ctrl+J` | Fold all / unfold all |

## 6. Multi-Cursor and Selection

> Editing many places at once. Add extra cursors; everything you type happens at each cursor.
>
> Use it for renaming a word in a few places, editing a column of values, adding quotes to many lines.

| Shortcut | Action |
|---|---|
| `Alt+Click` | Add a cursor where you click |
| `Ctrl+Alt+Up` / `Ctrl+Alt+Down` | Add cursor above / below |
| `Ctrl+D` | Select next occurrence of the current word |
| `Ctrl+K Ctrl+D` | Skip this occurrence, go to next |
| `Ctrl+Shift+L` | Select ALL occurrences |
| `Shift+Alt+I` | Cursor at the end of every selected line |
| `Shift+Alt+Drag` | Column (box) selection |
| `Ctrl+L` | Select current line |
| `Shift+Alt+Right` / `Left` | Expand / shrink selection |
| `Esc` | Back to one cursor |

## 7. Search and Replace

> Finding and replacing text in one file or the whole project. `Ctrl+F` / `Ctrl+H` in a file, `Ctrl+Shift+F` / `Ctrl+Shift+H` across files; toggles for case, word and regex.
>
> Use it for renaming a setting in many files, finding every use of a function, bulk edits with regex.

| Shortcut | Action |
|---|---|
| `Ctrl+F` | Find in file |
| `Ctrl+H` | Replace in file |
| `Ctrl+Shift+F` | Search in all files |
| `Ctrl+Shift+H` | Replace in all files |
| `F3` / `Shift+F3` | Next / previous match |
| `Alt+Enter` | Select all matches (in find box) |
| `Alt+C` / `Alt+W` / `Alt+R` | Toggle Match Case / Whole Word / Regex |

- In the search panel use **files to include / exclude**: `*.py`, `src/**`, `!tests/**`.
- With regex on, use `$1`, `$2` in the replacement for captured groups. See [07 - Regex](07_regex.md).

```text
Find:     print\((.*)\)
Replace:  logger.info($1)
```

## 8. Code Navigation

> Jumping between definitions, usages and past positions. Uses the language extension (Pylance for Python) to understand the code.
>
> Use it for reading unfamiliar code, finding where a function is defined or used.

| Shortcut | Action |
|---|---|
| `F12` or `Ctrl+Click` | Go to definition |
| `Alt+F12` | Peek definition (inline) |
| `Shift+F12` | Find all references |
| `Ctrl+Shift+\` | Jump to matching bracket |
| `Alt+Left` / `Alt+Right` | Go back / forward |
| `F8` / `Shift+F8` | Next / previous problem |
| `Ctrl+K Ctrl+I` | Show hover info (type, docstring) |
| `Ctrl+Shift+.` | Breadcrumbs: pick a symbol |

## 9. Integrated Terminal

> A terminal inside VS Code, opened in the project folder. `` Ctrl+` `` toggles it; choose the shell (PowerShell, Git Bash, WSL) from the dropdown.
>
> Use it for running scripts, git, pip and docker without leaving the editor.

| Shortcut | Action |
|---|---|
| `` Ctrl+` `` | Show / hide terminal |
| `` Ctrl+Shift+` `` | New terminal |
| `Ctrl+Shift+5` | Split terminal |
| `Ctrl+PageUp` / `PageDown` | Switch terminal |
| `Ctrl+Up` / `Ctrl+Down` | Scroll by command |
| Select text + `Ctrl+C` | Copy (without selection `Ctrl+C` stops the command) |

Change the default shell: `Ctrl+Shift+P` -> **Terminal: Select Default Profile**.

## 10. Python Setup

> Making VS Code use the right Python and venv. Install the Python extension, then select the interpreter inside `.venv`.
>
> Use it in every new project; red squiggles on imports usually mean the wrong interpreter.

1. Install the **Python** extension (includes Pylance and the debugger).
2. Create the venv: see [11 - Python Virtual Environment](11_python-virtual-environment.md) or [12 - uv](12_uv.md).
3. `Ctrl+Shift+P` -> **Python: Select Interpreter** -> pick `.venv`.
4. New terminals activate the venv automatically; the status bar shows the version.

Run the current file: `Ctrl+F5` (without debugger) or the play button top right.
Send selected lines to Python: `Shift+Enter`.

## 11. Run and Debug

> Running code step by step and inspecting variables. Set breakpoints, start with `F5`, then step through; values show in the Variables panel.
>
> Use this when a result is wrong and print statements are not enough.

| Shortcut | Action |
|---|---|
| `F9` | Toggle breakpoint on current line |
| `F5` | Start / continue debugging |
| `Ctrl+F5` | Run without debugging |
| `F10` | Step over (next line) |
| `F11` | Step into function |
| `Shift+F11` | Step out of function |
| `Shift+F5` | Stop |
| `Ctrl+Shift+F5` | Restart |

- Right-click a breakpoint -> **Edit Breakpoint** for a condition (`i == 50`) or a log message.
- **Debug Console**: type expressions while paused (`df.shape`).
- **Watch**: add expressions to follow while stepping.

## 12. launch.json (Debug Configurations)

> Saved debug setups (file, arguments, env vars) in `.vscode/launch.json`. Run and Debug -> **create a launch.json file**; pick one from the dropdown, then `F5`.
>
> Use it for debugging a script with arguments, a FastAPI app, or with a `.env` file.

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: current file",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "args": ["data.csv", "--limit", "5"]
    },
    {
      "name": "FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "envFile": "${workspaceFolder}/.env",
      "jinja": true
    }
  ]
}
```

## 13. Git in VS Code

> Git through the Source Control panel instead of commands. Changed files appear in `Ctrl+Shift+G`; stage with `+`, type a message, commit, then sync.
>
> Use it for reviewing diffs visually, staging parts of files, resolving merge conflicts. Commands: see [05 - Git](05_git.md).

| Action | How |
|---|---|
| See changes | Click a file in Source Control (side-by-side diff) |
| Stage file | `+` next to the file |
| Stage some lines | Select lines in the diff -> right-click -> **Stage Selected Ranges** |
| Commit | Type message, `Ctrl+Enter` |
| Push / pull | **Sync Changes** button, or `...` menu |
| Switch / create branch | Click the branch name in the status bar (bottom left) |
| Discard changes | Curved arrow next to the file |
| Resolve conflict | **Accept Current / Incoming / Both** above each conflict, or the merge editor |
| Line history | Install **GitLens** for blame and history per line |

## 14. Recommended Extensions

> Add-ons that add language support and tools. `Ctrl+Shift+X`, search, Install; or `code --install-extension <id>`.
>
> Use it for setting up a new machine; install only what you use (extensions slow startup).

| Extension | ID | For |
|---|---|---|
| Python | `ms-python.python` | Python run, debug, interpreter selection |
| Pylance | `ms-python.vscode-pylance` | Autocomplete, type checking |
| Jupyter | `ms-toolsai.jupyter` | Notebooks in VS Code |
| Ruff | `charliermarsh.ruff` | Fast linting and formatting |
| GitLens | `eamodio.gitlens` | Git blame and history |
| Docker / Container Tools | `ms-azuretools.vscode-docker` | Dockerfiles, containers |
| Remote - SSH | `ms-vscode-remote.remote-ssh` | Work on a VM over SSH |
| WSL | `ms-vscode-remote.remote-wsl` | Work inside WSL Linux |
| Dev Containers | `ms-vscode-remote.remote-containers` | Develop inside a container |
| Rainbow CSV | `mechatroner.rainbow-csv` | Readable CSV files |
| markdownlint | `davidanson.vscode-markdownlint` | Clean Markdown (like these guides) |
| Error Lens | `usernamehw.errorlens` | Show errors inline |

## 15. Settings

> Preferences for the editor, per user or per project. `Ctrl+,` for the UI; `Ctrl+Shift+P` -> **Preferences: Open User Settings (JSON)** for the file.
>
> Use it for changing font size, auto save, formatting on save, or project-specific settings.

| Level | File | Applies to |
|---|---|---|
| User | `%APPDATA%\Code\User\settings.json` | All projects on this machine |
| Workspace | `.vscode/settings.json` in the project | Only this project (can be committed to Git) |

```json
{
  "editor.fontSize": 14,
  "editor.rulers": [100],
  "editor.wordWrap": "on",
  "editor.minimap.enabled": false,
  "files.autoSave": "afterDelay",
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.exclude": { "**/__pycache__": true, "**/.ipynb_checkpoints": true },
  "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

## 16. Formatting and Linting (Ruff)

> Automatic code style (formatting) and error / smell detection (linting). The Ruff extension formats and fixes on save using rules from `pyproject.toml`.
>
> Use it in every Python project; keeps code consistent without thinking about it.

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  }
}
```

```toml
# pyproject.toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]   # errors, pyflakes, imports, bugbear, pyupgrade
```

## 17. Workspace Files and Tasks

> Project-level config in the `.vscode/` folder. `settings.json`, `launch.json`, `tasks.json`, `extensions.json` are read when the folder opens.
>
> Use it for sharing the same setup with teammates, or one-key commands like "run tests".

```json
// .vscode/extensions.json - VS Code suggests these when someone opens the project
{ "recommendations": ["ms-python.python", "charliermarsh.ruff"] }
```

```json
// .vscode/tasks.json - run with Ctrl+Shift+P -> Tasks: Run Task
{
  "version": "2.0.0",
  "tasks": [
    { "label": "tests", "type": "shell", "command": "pytest -q", "group": "test" },
    { "label": "api", "type": "shell", "command": "uvicorn app.main:app --reload" }
  ]
}
```

## 18. Remote Development (SSH, WSL, Containers)

> Using VS Code on your laptop while the code runs on another machine. Remote extensions install a small server on the target; you edit and run there with local UI.
>
> Use it for coding on an Azure VM (SSH), in Linux on Windows (WSL), or inside a Docker container.

| Target | Steps |
|---|---|
| SSH (VM) | Install **Remote - SSH**; `F1` -> **Remote-SSH: Connect to Host** -> `azureuser@<ip>`; uses `~/.ssh/config` |
| WSL | Install **WSL**; in a WSL terminal run `code .` |
| Container | Install **Dev Containers**; `F1` -> **Dev Containers: Reopen in Container** (uses `.devcontainer/devcontainer.json`) |

The green / blue button at the bottom left shows the current remote and opens the remote menu.

## 19. Troubleshooting

| Problem | Fix |
|---|---|
| `code` not recognized in terminal | Reinstall with **Add to PATH**, or `F1` -> **Shell Command: Install 'code' command in PATH** (Mac) |
| Imports underlined red, but code runs | Wrong interpreter; **Python: Select Interpreter** -> `.venv` |
| Venv not activated in terminal | Close and open a new terminal after selecting the interpreter |
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Format on save does nothing | Set `editor.defaultFormatter` for `[python]` and install the formatter extension |
| Debugger ignores breakpoints | Running with `Ctrl+F5` (no debug) or wrong file; use `F5` |
| VS Code slow / high CPU | `F1` -> **Developer: Show Running Extensions**; disable heavy ones, exclude big folders in `files.watcherExclude` |
| Shortcut does nothing | Another extension or app uses it; check `Ctrl+K Ctrl+S` |
| Settings seem ignored | Workspace settings override user settings; check `.vscode/settings.json` |

## 20. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Rename safely

What is the difference between renaming a variable with `Ctrl+D` multi-cursor and with `F2`?

<details markdown="1">
<summary>Solution</summary>

`Ctrl+D` selects the next text match in the current file only, so it can also change unrelated words (a comment, another variable with the same name). `F2` (Rename Symbol) uses the language server: it renames exactly that symbol everywhere it is used, across files. Prefer `F2` for code.

</details>

### Exercise 2: Regex replace across files

Replace every `print(...)` in `.py` files with `logger.info(...)` keeping the arguments.

<details markdown="1">
<summary>Solution</summary>

`Ctrl+Shift+H`, turn on regex (`Alt+R`), files to include: `*.py`

```text
Find:     print\((.*)\)
Replace:  logger.info($1)
```

Review the preview before clicking Replace All.

</details>

### Exercise 3: Pick the interpreter

Your imports are underlined red although `pip list` shows the package. Fix it.

<details markdown="1">
<summary>Solution</summary>

`Ctrl+Shift+P` -> **Python: Select Interpreter** -> choose the one inside the project's `.venv`, then open a new terminal. The editor was using a different Python than the one you installed into.

</details>

---

<!-- nav:start -->
**Previous:** [05 - Git and GitHub](05_git.md) | **Index:** [All guides](../README.md) | **Next:** [07 - Regex](07_regex.md)
<!-- nav:end -->
