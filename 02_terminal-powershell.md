# 02 - Terminal and PowerShell

Quick reference for everyday terminal work on Windows (PowerShell, CMD) with Bash equivalents (Linux, Mac, Git Bash).

## Contents

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

---

## 1. Which Shell Am I In?

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

| Goal | PowerShell 5.1 | PowerShell 7 / Bash | CMD |
|---|---|---|---|
| Run B after A (always) | `A; B` | `A; B` | `A & B` |
| Run B only if A succeeds | `A; if ($?) { B }` | `A && B` | `A && B` |
| Run B only if A fails | `A; if (-not $?) { B }` | `A \|\| B` | `A \|\| B` |

Line continuation: backtick `` ` `` (PowerShell), backslash `\` (Bash), `^` (CMD).

## 18. PowerShell Profile and Aliases

```powershell
$PROFILE                                # path of your profile script
notepad $PROFILE                        # edit (create it if missing: New-Item $PROFILE -Force)
Set-Alias g git                         # alias (add to profile to keep it)
function ll { Get-ChildItem -Force }    # small shortcut function
Get-History                             # command history this session
```

## 19. Command Equivalents Table

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
