# 02 - Terminal and PowerShell

<!-- nav:start -->
**Previous:** [01 - Markdown](01_markdown.md) | **Index:** [All guides](README.md) | **Next:** [03 - Linux](03_linux.md)
<!-- nav:end -->

Quick reference for everyday terminal work on Windows (PowerShell, CMD) with Bash equivalents (Linux, Mac, Git Bash).

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is a terminal and what is PowerShell?

A **terminal** is a text window where you type commands instead of clicking. The program that reads and runs those commands is the **shell**. Windows has two built-in shells: the old **CMD** (Command Prompt) and **PowerShell**, a modern shell from Microsoft. PowerShell commands are named `Verb-Noun` (`Get-Process`, `Remove-Item`) and pass **objects** (with properties like Name, CPU, Size) between commands instead of plain text, which makes filtering and sorting very powerful.

### Why use it?

- **Speed**: one command can do what takes many clicks (rename 100 files, find every CSV on a drive).
- **Required by dev tools**: git, python, pip, uv, docker, az and ssh all run in a terminal.
- **Automation**: save commands in a `.ps1` script and run them again anytime.
- **Remote work**: servers and cloud VMs usually have no desktop, only a shell.
- **Precision**: exact, repeatable steps you can copy into docs (like these guides).

### Key terms

| Term | Meaning |
|---|---|
| Shell | Program that interprets commands (PowerShell, CMD, Bash) |
| Cmdlet | A PowerShell command (`Get-ChildItem`) |
| Alias | Short name for a command (`ls` -> `Get-ChildItem`) |
| Pipeline | Passing output to the next command with `\|` |
| Path | Location of a file or folder (`D:\Projects\app`) |
| PATH (env var) | List of folders where the shell looks for programs |
| Working directory | The folder the terminal is currently "in" |

**Where it fits:** the foundation for every other guide. Linux servers use Bash instead: see [03 - Linux](03_linux.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| PowerShell documentation | https://learn.microsoft.com/en-us/powershell/ |
| Windows Terminal | https://learn.microsoft.com/en-us/windows/terminal/ |
| winget (Windows Package Manager) | https://learn.microsoft.com/en-us/windows/package-manager/winget/ |
| Windows commands (CMD) reference | https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Which Shell Am I In?](#1-which-shell-am-i-in)
2. [Keyboard Shortcuts](#2-keyboard-shortcuts)
3. [Help](#3-help)
4. [Navigation](#4-navigation)
5. [Files and Folders](#5-files-and-folders)
6. [View and Search File Content](#6-view-and-search-file-content)
7. [Find Files](#7-find-files)
8. [Redirection and Pipes](#8-redirection-and-pipes)
9. [PowerShell Pipeline: Filter, Sort, Select](#9-powershell-pipeline-filter-sort-select)
10. [Variables](#10-variables)
11. [Environment Variables](#11-environment-variables)
12. [System Info](#12-system-info)
13. [Processes](#13-processes)
14. [Network](#14-network)
15. [Install Software (winget)](#15-install-software-winget)
16. [Run Programs and Scripts](#16-run-programs-and-scripts)
17. [Chaining Commands](#17-chaining-commands)
18. [PowerShell Profile and Aliases](#18-powershell-profile-and-aliases)
19. [Command Equivalents Table](#19-command-equivalents-table)
20. [Troubleshooting](#20-troubleshooting)
21. [Try It](#21-try-it)

---

## 0. Flags and Parameters

> How PowerShell, CMD and Bash parameters are written, and what each one used below means. A command is split into command name, parameters and values; tables list every parameter.
>
> Use this when you see a command like `Get-ChildItem -Recurse -Filter *.csv` and want to know what each part does.

### How a command is built

```text
Get-ChildItem  -Path D:\data  -Filter *.csv  -Recurse
|              |              |              |
|              |              |              +-- switch parameter: on when present, no value
|              |              +----------------- parameter with value: only names matching *.csv
|              +-------------------------------- parameter with value: folder to look in
+----------------------------------------------- command: Verb-Noun (Get = read, ChildItem = folder contents)
```

- PowerShell parameters start with one dash and a word: `-Recurse`. They are **not** case-sensitive.
- You may shorten a parameter while it stays unique: `-Rec` = `-Recurse`. `Tab` completes names.
- Some values can be given **by position** without the name: `Get-ChildItem D:\data` = `Get-ChildItem -Path D:\data`.
- CMD commands use slashes: `/s`, `/q`. Bash uses dashes: `-r` (short) and `--recursive` (long).
- See all parameters: `Get-Help Get-ChildItem -Full`, or `Get-Help Get-ChildItem -Parameter Filter`.

### PowerShell parameters

| Command | Parameter | Meaning |
|---|---|---|
| `Get-ChildItem` | `-Force` | Include hidden and system items |
| `Get-ChildItem` | `-Recurse` | Include all subfolders |
| `Get-ChildItem` | `-Filter *.csv` | Only names matching the pattern (`*` = any characters) |
| `Get-Content` | `-TotalCount 10` | First 10 lines |
| `Get-Content` | `-Tail 10` | Last 10 lines |
| `Get-Content` | `-Wait` | Keep reading as the file grows (like `tail -f`) |
| `Get-Content` | `-Raw` | Read as one string instead of a list of lines |
| `Select-String` | `-CaseSensitive` | Match upper / lower case exactly (default ignores case) |
| `New-Item` | `-ItemType Directory` | Create a folder instead of a file |
| `New-Item` | `-Force` | Create parent folders / overwrite |
| `Remove-Item` | `-Recurse` | Delete folder contents too |
| `Remove-Item` / `Stop-Process` | `-Force` | Do not ask; include read-only / hidden items |
| `Copy-Item` | `-Recurse` | Copy a folder with all contents |
| `Sort-Object` | `-Descending` | Largest / newest first |
| `Select-Object` | `-First 5` | Only the first 5 objects |
| `Select-Object` | `Name, Id` | Only these properties (columns) |
| `Measure-Object` | `-Sum` | Add up the given property |
| `Format-Table` | `-AutoSize` | Fit column widths to content |
| `Out-File` / `Set-Content` | `-Encoding utf8` | Character encoding of the written file |
| `Export-Csv` | `-NoTypeInformation` | Do not write the `#TYPE` header line |
| `Get-Help` | `-Examples` | Only show usage examples |
| `Get-PSDrive` | `-PSProvider FileSystem` | Only disk drives (not registry etc.) |
| `Stop-Process` | `-Name` / `-Id` | Choose the process by name / by process ID |
| `Start-Process` | `-Verb RunAs` | Start as Administrator |
| `Get-NetTCPConnection` | `-LocalPort 8000` | Only connections on this local port |
| `Get-NetTCPConnection` | `-State Listen` | Only ports waiting for connections |
| `Test-NetConnection` | `-Port 443` | Test this TCP port, not just ping |
| `Invoke-WebRequest` | `-OutFile page.html` | Save the download to a file |
| `Set-ExecutionPolicy` | `-Scope CurrentUser` | Change only for your user (no admin needed) |
| `Set-ExecutionPolicy` | `RemoteSigned` | Local scripts run; downloaded scripts need a signature |

### PowerShell operators and symbols

| Symbol | Meaning | Example |
|---|---|---|
| `\|` | Pipe: pass the output objects to the next command | `Get-Process \| Sort-Object CPU` |
| `$_` | The current object inside `{ }` in a pipeline | `Where-Object { $_.CPU -gt 100 }` |
| `-eq -ne -gt -ge -lt -le` | Equal, not equal, greater, greater or equal, less, less or equal | `CPU -gt 100` |
| `-like` | Wildcard match (`*`, `?`) | `$_.Name -like "py*"` |
| `-match` | Regular expression match | `$_ -match "^err"` |
| `-split` | Split a string into parts | `$env:PATH -split ";"` |
| `$env:NAME` | Environment variable | `$env:PATH` |
| `.\` | Current folder (required to run a script there) | `.\script.ps1` |
| `&` | Call operator: run a program whose path is in quotes | `& "C:\Program Files\app.exe"` |
| `$?` | True if the last command succeeded | `if ($?) { ... }` |
| `` ` `` | Line continuation / escape character | |

### CMD and other Windows tools

| Command | Flag | Meaning |
|---|---|---|
| `rmdir` | `/s` / `/q` | Delete all subfolders and files / quiet, do not ask |
| `ipconfig` | `/flushdns` | Clear the DNS cache |
| `netstat` | `-ano` | `-a` all connections, `-n` numbers not names, `-o` show process ID |
| `findstr` | `:8000` | Keep only lines containing this text (like grep) |
| `taskkill` | `/PID 1234 /F` | Kill process 1234, `/F` = force |
| `winget install` | `-e --id X` | Exact match on package ID X |
| `winget upgrade` | `--all` | Upgrade every package that has an update |
| `ping` (Bash) | `-c 4` | Send 4 packets then stop (Windows ping stops after 4 by default) |
| `curl` | `-O` | Save with the remote file name |

## 1. Which Shell Am I In?

> Identifying which command-line program (shell) you are typing into. Look at the prompt, or run `$PSVersionTable` in PowerShell.
>
> Use this when a command from a tutorial fails; it may be written for Bash while you are in PowerShell (or the reverse).

| Prompt looks like | Shell |
|---|---|
| `PS C:\Users\me>` | PowerShell |
| `C:\Users\me>` | CMD (Command Prompt) |
| `me@pc MINGW64 ~` | Git Bash |
| `me@host:~$` | Bash (Linux / Mac / WSL) |

```powershell
$PSVersionTable.PSVersion       # PowerShell version
```

- **Windows PowerShell 5.1** (`powershell`) is built in. **PowerShell 7** (`pwsh`) is the newer version.
- Many Linux names (`ls`, `cd`, `cat`, `pwd`, `rm`, `cp`, `mv`) also work in PowerShell as aliases.

## 2. Keyboard Shortcuts

> Keys that save typing and help you recover from mistakes. Built into the terminal; work in every shell with small differences.
>
> Use it for all the time: `Tab` for paths, `Up` to repeat, `Ctrl+C` to stop something stuck.

| Keys | Action |
|---|---|
| `Tab` | Autocomplete path or command (press again to cycle) |
| `Up` / `Down` | Previous / next command |
| `Ctrl+R` | Search command history |
| `Ctrl+C` | Stop the running command |
| `Ctrl+L` or `cls` / `clear` | Clear screen |
| `Ctrl+A` / `Ctrl+E` | Start / end of line (Bash) |
| `Home` / `End` | Start / end of line (PowerShell) |
| `Ctrl+Backspace` | Delete previous word (PowerShell) |
| Right-click / `Ctrl+V` | Paste |

## 3. Help

> Built-in documentation for commands. `Get-Help` / `Get-Command` in PowerShell, `man` / `--help` in Bash.
>
> Use this when you remember roughly what a command is called but not its options.

```powershell
Get-Help Get-ChildItem          # help for a command
Get-Help Get-ChildItem -Examples
Get-Command *process*           # find commands by name
Get-Alias ls                    # what an alias points to
Get-Member                      # properties of an object: Get-Process | Get-Member
```

```bash
man ls                          # manual page (Bash)
ls --help                       # short help
```

## 4. Navigation

> Moving between folders and seeing what is in them. `cd` to change folder, `ls` / `Get-ChildItem` to list, `pwd` to see where you are.
>
> Use it as the first thing in any terminal session: go to your project folder before running anything.

```powershell
pwd                             # current folder (Get-Location)
cd D:\Projects                  # go to folder (Set-Location)
cd ..                           # up one level
cd ~                            # home folder
cd -                            # previous folder (PowerShell 7 / Bash)
D:                              # switch drive (CMD / PowerShell)
ls                              # list items (Get-ChildItem)
ls -Force                       # include hidden items
ls -Recurse                     # include subfolders
ii .                            # open current folder in Explorer (Invoke-Item)
code .                          # open folder in VS Code
```

Bash: `ls -la` (all + details), `open .` (Mac), `explorer .` (Git Bash on Windows).

Paths with spaces need quotes: `cd "C:\Program Files"`.

## 5. Files and Folders

> Creating, copying, moving, renaming and deleting files and folders. PowerShell `*-Item` cmdlets (with Linux-style aliases like `cp`, `mv`, `rm`).
>
> Use it for setting up a project structure, cleaning build output, scripting file tasks.

```powershell
mkdir new-folder                                    # create folder (New-Item -ItemType Directory)
New-Item file.txt                                   # create empty file
Set-Content file.txt "hello"                        # write (overwrite)
Add-Content file.txt "more"                         # append
Copy-Item a.txt b.txt                               # copy (cp)
Copy-Item src dest -Recurse                         # copy folder
Move-Item a.txt folder\                             # move (mv)
Rename-Item old.txt new.txt                         # rename
Remove-Item file.txt                                # delete file (rm)
Remove-Item folder -Recurse -Force                  # delete folder and contents
Test-Path file.txt                                  # exists? True / False
```

```bash
mkdir -p a/b/c                  # create nested folders
touch file.txt                  # create empty file
echo "hello" > file.txt         # write (overwrite)
echo "more" >> file.txt         # append
cp a.txt b.txt ; cp -r src dest # copy file, folder
mv a.txt folder/                # move / rename
rm file.txt ; rm -rf folder     # delete file, folder (no recycle bin!)
```

## 6. View and Search File Content

> Reading files and searching inside them without opening an editor. `Get-Content` to read (head, tail, follow), `Select-String` to search (like grep).
>
> Use it for checking a log file, following a running server's log, finding where an error message appears.

```powershell
cat file.txt                            # show file (Get-Content)
Get-Content file.txt -TotalCount 10     # first 10 lines (head)
Get-Content file.txt -Tail 10           # last 10 lines (tail)
Get-Content app.log -Wait -Tail 20      # follow a growing file (tail -f)
(Get-Content file.txt).Count            # line count
Select-String "error" file.txt          # search text in file (grep)
Select-String "error" *.log -CaseSensitive
notepad file.txt                        # open in Notepad
```

```bash
cat file.txt
head -n 10 file.txt ; tail -n 10 file.txt
tail -f app.log                         # follow
wc -l file.txt                          # line count
grep -n "error" file.txt                # search with line numbers
grep -rn "error" .                      # search all files in folder
less file.txt                           # scroll (q to quit)
```

## 7. Find Files

> Locating files by name, content or size. `Get-ChildItem -Recurse` with `-Filter`, piped into `Select-String` or `Sort-Object`.
>
> Use it to answer questions like "Where is that config file?", "which scripts import pandas?", "what is filling my disk?".

```powershell
Get-ChildItem -Recurse -Filter *.csv                # find by name
Get-ChildItem -Recurse -Filter *.py | Select-String "import pandas"   # files containing text
Get-ChildItem | Sort-Object Length -Descending | Select-Object -First 5   # largest files
```

```bash
find . -name "*.csv"
grep -rl "import pandas" .
du -sh *                                # folder sizes
```

## 8. Redirection and Pipes

> Sending command output to a file or into another command. `>` overwrite, `>>` append, `2>` errors, `|` pipe to the next command.
>
> Use it for saving output for later, building a report, combining small commands into one.

| Syntax | Meaning |
|---|---|
| `cmd > file.txt` | Write output to file (overwrite) |
| `cmd >> file.txt` | Append output to file |
| `cmd 2> errors.txt` | Write errors to file |
| `cmd > $null` (PS) / `> /dev/null` (Bash) | Discard output |
| `cmd1 \| cmd2` | Send output of cmd1 into cmd2 |

```powershell
Get-Process | Out-File procs.txt -Encoding utf8     # save with explicit encoding
Get-Process | Export-Csv procs.csv -NoTypeInformation
Get-Content data.csv | ConvertFrom-Csv              # CSV text to objects
Get-Content data.json -Raw | ConvertFrom-Json       # JSON text to objects
"text" | Set-Clipboard                              # copy to clipboard
```

## 9. PowerShell Pipeline: Filter, Sort, Select

> Filtering, sorting and selecting PowerShell output by property. PowerShell passes objects; `Where-Object`, `Sort-Object`, `Select-Object` work on their properties.
>
> Use it to answer questions like "Show the 5 processes using most CPU", "list files bigger than 100 MB".

PowerShell passes **objects**, not text, so you can filter on properties.

```powershell
Get-Process | Where-Object CPU -gt 100                  # filter
Get-Process | Where-Object { $_.Name -like "py*" }      # $_ = current item
Get-Process | Sort-Object CPU -Descending               # sort
Get-Process | Select-Object Name, Id, CPU -First 5      # pick columns / rows
Get-ChildItem | Measure-Object Length -Sum              # count / sum
Get-Process | Group-Object Name                         # group
Get-ChildItem | ForEach-Object { $_.Name.ToUpper() }    # loop
Get-Process | Format-Table -AutoSize                    # table view
Get-Process | Out-GridView                              # interactive grid window
```

Comparison operators: `-eq -ne -gt -ge -lt -le -like -notlike -match -contains -in`

## 10. Variables

> Storing values to reuse in later commands. `$name = value` in PowerShell, `name=value` in Bash.
>
> Use it for long values you type often (resource group, VM name, IP), like in the Azure guide.

```powershell
$name = "Harman"
$n = 5
"Hello $name"                   # double quotes expand variables
'Hello $name'                   # single quotes are literal
"Count: $($n * 2)"              # expression inside string
$list = @(1, 2, 3)              # array
$map = @{ a = 1; b = 2 }        # hashtable
$map.a                          # 1
```

```bash
name="Harman"                   # no spaces around =
echo "Hello $name"
```

## 11. Environment Variables

> System-wide or session-wide settings that programs read (PATH, API hosts, keys). `$env:NAME` in PowerShell; permanent via `SetEnvironmentVariable` or System Settings.
>
> Use this when a program cannot be found (PATH), or an app needs a setting like `OLLAMA_HOST`.

```powershell
$env:PATH                               # show
$env:PATH -split ";"                    # PATH one entry per line
$env:MY_VAR = "value"                   # set for this session only
Remove-Item Env:MY_VAR                  # unset
Get-ChildItem Env:                      # list all
[Environment]::SetEnvironmentVariable("MY_VAR", "value", "User")   # permanent (new terminal needed)
```

```bash
echo $PATH
export MY_VAR="value"                   # session only
env                                     # list all
```

```cmd
echo %PATH%
set MY_VAR=value
```

## 12. System Info

> Information about your machine: OS, user, memory, disks. Built-in cmdlets and tools such as `Get-ComputerInfo`, `systeminfo`, `Get-PSDrive`.
>
> Use it for checking free disk space, OS version for an install guide, or RAM before running a model.

```powershell
hostname                                # computer name
whoami                                  # current user
Get-ComputerInfo | Select-Object OsName, OsVersion, CsTotalPhysicalMemory
Get-PSDrive -PSProvider FileSystem      # disks and free space
Get-Date                                # date and time
systeminfo                              # full system summary
```

```bash
uname -a ; df -h ; free -h ; uptime ; date
```

## 13. Processes

> Running programs, their resource usage, and stopping them. `Get-Process` to list, `Stop-Process` to kill, `Get-NetTCPConnection` for ports.
>
> Use this when an app is frozen, or "port 8000 is already in use" and you need to find what uses it.

```powershell
Get-Process                             # all processes (ps)
Get-Process python                      # by name
Stop-Process -Name python               # kill by name
Stop-Process -Id 1234 -Force            # kill by id
Start-Process notepad                   # start program
Start-Process powershell -Verb RunAs    # open as Administrator
Get-Service                             # Windows services
Restart-Service -Name Spooler           # restart a service (admin)
```

Which process is using a port:

```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object LocalPort, OwningProcess
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess
```

```bash
ps aux | grep python ; kill 1234 ; kill -9 1234
lsof -i :8000                           # who uses port 8000 (Mac/Linux)
```

## 14. Network

> Checking connectivity, IPs, DNS and downloading files. `ipconfig`, `ping`, `Test-NetConnection`, `Invoke-WebRequest` / `curl.exe`.
>
> Use it to answer questions like "Can I reach the server?", "is port 443 open?", "what is my public IP?".

```powershell
ipconfig                                # IP addresses
ipconfig /flushdns                      # clear DNS cache
ping google.com
Test-NetConnection google.com -Port 443 # is a port reachable?
Resolve-DnsName google.com              # DNS lookup (nslookup)
Invoke-RestMethod https://api.ipify.org # public IP
Invoke-WebRequest https://example.com -OutFile page.html   # download
curl.exe https://example.com            # real curl (plain "curl" is an alias in PS 5.1)
netstat -ano | findstr :8000            # port usage (CMD style)
```

```bash
ip a ; ping -c 4 google.com ; curl -O https://example.com/file.zip
```

## 15. Install Software (winget)

> Installing and updating software from the command line on Windows. `winget` (Windows Package Manager) downloads and installs from a central catalog.
>
> Use it for setting up a new laptop quickly, or updating all apps with one command.

```powershell
winget search python                    # search
winget install -e --id Python.Python.3.12
winget install -e --id Git.Git
winget install -e --id Microsoft.VisualStudioCode
winget list                             # installed
winget upgrade                          # available updates
winget upgrade --all                    # update everything
winget uninstall <name>
```

Mac: `brew install <name>`. Ubuntu: `sudo apt install <name>`.

## 16. Run Programs and Scripts

> Running scripts and programs, and the security policy that controls scripts. Prefix scripts with `.\`; set the execution policy once to allow local scripts.
>
> Use it for running a `.ps1` setup script, or activating a venv fails with "scripts are disabled".

```powershell
.\script.ps1                            # run a PowerShell script (.\ is required)
python app.py                           # run Python
& "C:\Program Files\App\app.exe" --arg  # run exe with spaces in path
Get-ExecutionPolicy                     # current policy
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # allow local scripts
```

```bash
chmod +x script.sh                      # make executable
./script.sh
bash script.sh
```

## 17. Chaining Commands

> Running several commands in one line, optionally depending on success. `;` always runs the next; `&&` only on success (PowerShell 7 / Bash / CMD).
>
> Use it to answer questions like "Build then run", "pull then install" as one line; copying commands from Bash tutorials.

| Goal | PowerShell 5.1 | PowerShell 7 / Bash | CMD |
|---|---|---|---|
| Run B after A (always) | `A; B` | `A; B` | `A & B` |
| Run B only if A succeeds | `A; if ($?) { B }` | `A && B` | `A && B` |
| Run B only if A fails | `A; if (-not $?) { B }` | `A \|\| B` | `A \|\| B` |

Line continuation: backtick `` ` `` (PowerShell), backslash `\` (Bash), `^` (CMD).

## 18. PowerShell Profile and Aliases

> Personal startup script with your own shortcuts. `$PROFILE` runs every time PowerShell starts; put aliases and functions there.
>
> Use this when you type the same long command every day and want a short alias for it.

```powershell
$PROFILE                                # path of your profile script
notepad $PROFILE                        # edit (create it if missing: New-Item $PROFILE -Force)
Set-Alias g git                         # alias (add to profile to keep it)
function ll { Get-ChildItem -Force }    # small shortcut function
Get-History                             # command history this session
```

## 19. Command Equivalents Table

> The same task side by side in PowerShell, CMD and Bash. Look up the task in the left column, read across to your shell.
>
> Use it for following a tutorial written for another shell.

| Task | PowerShell | CMD | Bash |
|---|---|---|---|
| Current folder | `Get-Location` / `pwd` | `cd` | `pwd` |
| List | `Get-ChildItem` / `ls` | `dir` | `ls -la` |
| Change folder | `Set-Location` / `cd` | `cd` | `cd` |
| Make folder | `New-Item -ItemType Directory` / `mkdir` | `mkdir` | `mkdir -p` |
| Create file | `New-Item file` | `type nul > file` | `touch file` |
| Show file | `Get-Content` / `cat` | `type` | `cat` |
| Copy | `Copy-Item` / `cp` | `copy`, `xcopy` | `cp -r` |
| Move / rename | `Move-Item` / `mv` | `move`, `ren` | `mv` |
| Delete file | `Remove-Item` / `rm` | `del` | `rm` |
| Delete folder | `Remove-Item -Recurse -Force` | `rmdir /s /q` | `rm -rf` |
| Search text | `Select-String` | `findstr` | `grep` |
| Clear screen | `Clear-Host` / `cls` | `cls` | `clear` |
| Processes | `Get-Process` | `tasklist` | `ps aux` |
| Kill process | `Stop-Process` | `taskkill /PID 1234 /F` | `kill -9 1234` |
| Env variable | `$env:NAME` | `%NAME%` | `$NAME` |
| Locate command | `Get-Command python` / `where.exe` | `where` | `which` |
| Download | `Invoke-WebRequest -OutFile` | `curl -O` | `curl -O` / `wget` |

## 20. Troubleshooting

| Problem | Fix |
|---|---|
| `running scripts is disabled on this system` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `The term 'x' is not recognized` | Not installed or not on PATH; reopen terminal after installing |
| `Access is denied` | Run the terminal as Administrator, or close the program locking the file |
| `script.ps1` not found in current folder | Prefix with `.\` : `.\script.ps1` |
| `&&` gives a parser error | You are in PowerShell 5.1, use `A; if ($?) { B }` or install `pwsh` |
| `curl` behaves oddly in PowerShell | Use `curl.exe` (5.1 maps `curl` to `Invoke-WebRequest`) |
| Weird characters in saved files | Use `Out-File -Encoding utf8` / `Set-Content -Encoding utf8` |
| Command stuck | `Ctrl+C` |

## 21. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Biggest CSV files

List the 5 largest `.csv` files anywhere under `D:\Projects`, with name and size.

<details markdown="1">
<summary>Solution</summary>

```powershell
Get-ChildItem D:\Projects -Recurse -Filter *.csv |
  Sort-Object Length -Descending |
  Select-Object -First 5 Name, @{n="MB"; e={[math]::Round($_.Length / 1MB, 1)}}
```

</details>

### Exercise 2: Port already in use

Find which process is using port 8000 and stop it.

<details markdown="1">
<summary>Solution</summary>

```powershell
$conn = Get-NetTCPConnection -LocalPort 8000 -State Listen
Get-Process -Id $conn.OwningProcess
Stop-Process -Id $conn.OwningProcess
```

</details>

### Exercise 3: Environment variables

Set `LLM_MODEL` for this session only, print it, and show `PATH` one entry per line.

<details markdown="1">
<summary>Solution</summary>

```powershell
$env:LLM_MODEL = "claude-opus-5"
$env:LLM_MODEL
$env:PATH -split ";"
```

</details>

---

<!-- nav:start -->
**Previous:** [01 - Markdown](01_markdown.md) | **Index:** [All guides](README.md) | **Next:** [03 - Linux](03_linux.md)
<!-- nav:end -->
