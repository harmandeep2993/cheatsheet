# 03 - Linux

<!-- nav:start -->
**Previous:** [02 - Terminal and PowerShell](02_terminal-powershell.md) | **Index:** [All guides](README.md) | **Next:** [04 - Git and GitHub](04_git.md)
<!-- nav:end -->

Quick reference for everyday Linux commands (Ubuntu / Debian focus, works on most distros, WSL and Mac for the basics).

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Linux?

Linux is a free, open-source operating system, like Windows or macOS. It comes in **distributions** (Ubuntu, Debian, Fedora, ...) that bundle the Linux kernel with tools and a package manager. Most servers, cloud VMs, Docker containers and supercomputers run Linux, usually without a desktop, so you control them through the **Bash** shell.

### Why learn it?

- **Servers run on it**: Azure / AWS VMs, web servers, databases and ML training machines are mostly Linux.
- **Docker runs on it**: almost every container image is a small Linux system.
- **Developer tooling**: many tools and tutorials assume Linux commands (`grep`, `chmod`, `apt`).
- **WSL**: Windows Subsystem for Linux gives you a real Linux on your Windows laptop.
- **Stable and free**: no licence costs, runs for months without reboot.

### Key terms

| Term | Meaning |
|---|---|
| Distribution (distro) | A packaged Linux version: Ubuntu, Debian, Fedora |
| Bash | The default shell on most Linux systems |
| root / sudo | The administrator account / run one command as administrator |
| Package manager | Installs software from trusted repositories (`apt` on Ubuntu) |
| systemd / service | Starts and supervises background programs (web server, Ollama) |
| Permissions | Who may read, write or execute each file |
| SSH | Secure remote login to another machine |

**Where it fits:** needed for [42 - Docker](42_docker.md) and [48 - Azure VM](48_azure-vm-ollama.md). Windows equivalents: [02 - Terminal and PowerShell](02_terminal-powershell.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Ubuntu Server documentation | https://documentation.ubuntu.com/server/ |
| Linux man pages online | https://man7.org/linux/man-pages/ |
| GNU Bash manual | https://www.gnu.org/software/bash/manual/ |
| WSL (Linux on Windows) | https://learn.microsoft.com/en-us/windows/wsl/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Basics and Shortcuts](#1-basics-and-shortcuts)
2. [Help](#2-help)
3. [Filesystem Layout](#3-filesystem-layout)
4. [Navigation](#4-navigation)
5. [Files and Folders](#5-files-and-folders)
6. [View Files](#6-view-files)
7. [Edit Files (nano, vim)](#7-edit-files-nano-vim)
8. [Find Files](#8-find-files)
9. [Search Text (grep)](#9-search-text-grep)
10. [Text Processing](#10-text-processing)
11. [Redirection and Pipes](#11-redirection-and-pipes)
12. [Permissions](#12-permissions)
13. [Users and sudo](#13-users-and-sudo)
14. [Packages (apt)](#14-packages-apt)
15. [Processes](#15-processes)
16. [Services (systemd) and Logs](#16-services-systemd-and-logs)
17. [Disk and Memory](#17-disk-and-memory)
18. [System Info](#18-system-info)
19. [Network](#19-network)
20. [SSH and File Transfer](#20-ssh-and-file-transfer)
21. [Archives (tar, zip)](#21-archives-tar-zip)
22. [Environment Variables and PATH](#22-environment-variables-and-path)
23. [Aliases and .bashrc](#23-aliases-and-bashrc)
24. [Shell Scripts](#24-shell-scripts)
25. [Scheduled Jobs (cron)](#25-scheduled-jobs-cron)
26. [Long-Running Jobs](#26-long-running-jobs)
27. [Troubleshooting](#27-troubleshooting)
28. [Try It](#28-try-it)

---

## 0. Flags and Parameters

> How Linux command options are written, and what every option used below means. A command is split into program, options and arguments; tables list options per command. Use this when you see a command like `ls -lah /var/log` or `tar -czvf` and want to know what each letter does.

### How a command is built

```text
ls  -lah  /var/log
|   |     |
|   |     +-- argument: which folder to list
|   +-------- options: -l long format, -a all (hidden too), -h human sizes
+------------ program

tar  -czvf  backup.tar.gz  folder/
      ||||  |              |
      ||||  |              +-- what to pack
      ||||  +----------------- archive name (value of -f)
      |||+-------------------- -f: file name follows
      ||+--------------------- -v: verbose, list files
      |+---------------------- -z: compress with gzip
      +----------------------- -c: create
```

- **Short options**: one dash + one letter; they can be combined: `-lah` = `-l -a -h`.
- **Long options**: two dashes + word: `--help`, `--all`. Often the same as a short one (`-a` = `--all`).
- An option can take a **value**: `-n 20`, `-u nginx`, `--since "1 hour ago"`.
- Everything is **case-sensitive**: `-r` and `-R` can mean different things.
- Look up any option: `man ls` then type `/-h` to search.

### Files, viewing and searching

| Command | Option | Meaning |
|---|---|---|
| `ls` | `-l` | Long format: permissions, owner, size, date |
| `ls` | `-a` | All files, including hidden (starting with `.`) |
| `ls` | `-h` | Human-readable sizes (with `-l`) |
| `ls` | `-t` | Sort by modification time, newest first |
| `tree` | `-L 2` | Only 2 levels deep |
| `mkdir` | `-p` | Create parent folders as needed, no error if it exists |
| `cp` / `rm` / `chmod` / `scp` | `-r` (or `-R`) | Recursive: include folder contents |
| `rm` | `-f` | Force: no questions, no error if missing |
| `rm` | `-i` | Interactive: ask before each delete |
| `ln` | `-s` | Symbolic link (shortcut) instead of hard link |
| `head` / `tail` | `-n 20` | Number of lines |
| `tail` | `-f` | Follow: keep printing new lines |
| `wc` | `-l` | Count lines only |
| `find` | `-name "*.csv"` / `-iname` | Match name / ignoring case |
| `find` | `-type f` / `-type d` | Only files / only folders |
| `find` | `-mtime -1` | Modified less than 1 day ago (`+7` = more than 7 days) |
| `find` | `-size +100M` | Larger than 100 MB |
| `find` | `-delete` | Delete what was found |
| `grep` | `-i` | Ignore case |
| `grep` | `-n` | Show line numbers |
| `grep` | `-v` | Invert: lines that do NOT match |
| `grep` | `-c` | Count matching lines |
| `grep` | `-r` | Recursive: search all files in folders |
| `grep` | `-l` | Only print file names |
| `grep` | `-E` | Extended regex (`a\|b`, `+`, `?`) |
| `grep` | `-A 3` / `-B 3` | Also show 3 lines After / Before each match |
| `sort` | `-n` / `-r` / `-h` | Numeric / reverse / human sizes (`2K`, `1G`) |
| `uniq` | `-c` | Prefix each line with its count |
| `cut` | `-d ","` / `-f 1,3` | Delimiter / which fields (columns) |
| `awk` | `-F ","` | Field separator; `$1` = first field |
| `sed` | `-i` | Edit the file in place |
| `sed` | `'s/old/new/g'` | `s` = substitute, `g` = every match on the line (not only first) |

### Permissions, users and packages

| Command | Option | Meaning |
|---|---|---|
| `chmod` | `+x` | Add execute permission |
| `chmod` | `755` | Owner rwx (7=4+2+1), group r-x (5=4+1), others r-x |
| `chown` | `user:group` | New owner and group |
| `sudo` | `-i` | Open a root shell |
| `su` | `- username` | Switch user with their full login environment |
| `usermod` | `-aG docker user` | `-a` append (keep other groups), `-G` supplementary group |
| `apt install` | `-y` | Answer yes to all prompts |

### Processes, services, disk and network

| Command | Option | Meaning |
|---|---|---|
| `ps` | `aux` | `a` all users, `u` user-friendly columns, `x` include background processes |
| `pgrep` | `-a` | Show the full command line with the PID |
| `kill` | `-9` | Force kill (SIGKILL); without it: polite stop (SIGTERM) |
| `systemctl list-units` | `--type=service --state=running` | Only running services |
| `journalctl` | `-u nginx` | Only this unit (service) |
| `journalctl` | `-f` | Follow new lines |
| `journalctl` | `--since "1 hour ago"` | Time filter |
| `journalctl` | `-p err` | Only priority error and worse |
| `journalctl` | `-b` | Only since the last boot |
| `df` / `du` / `free` | `-h` | Human-readable sizes |
| `du` | `-s` | Summary: one total per argument |
| `uname` | `-a` | All kernel information |
| `ping` | `-c 4` | Send 4 packets then stop |
| `curl` | `-I` | Only response headers |
| `curl` | `-O` | Save with the remote file name |
| `ss` | `-tulpn` | `t` TCP, `u` UDP, `l` listening, `p` process, `n` numbers not names |
| `lsof` | `-i :8000` | Open network connections on port 8000 |
| `ufw allow` | `22/tcp` | Port and protocol to open |

### SSH, transfer and archives

| Command | Option | Meaning |
|---|---|---|
| `ssh` / `scp` | `-i key.pem` | Private key file to log in with |
| `ssh` | `-p 2222` | Port (default 22); note `scp` uses `-P` |
| `ssh` | `-N` | No remote command; only keep the connection (tunnels) |
| `ssh` | `-L 8080:localhost:80` | Local port 8080 forwarded to port 80 on the server |
| `ssh-keygen` | `-t ed25519` | Key type |
| `rsync` | `-avz` | `a` archive (recursive, keep permissions / times), `v` verbose, `z` compress |
| `tar` | `-c` / `-x` / `-t` | Create / extract / list contents |
| `tar` | `-z` | gzip compression (`.tar.gz`) |
| `tar` | `-v` | Verbose: print each file |
| `tar` | `-f name` | Archive file name (must come right before the name) |
| `tar` | `-C /target/` | Extract into this folder |
| `zip` | `-r` | Include folder contents |
| `unzip` | `-d target/` | Extract into this folder |

### Symbols

| Symbol | Meaning |
|---|---|
| `\|` | Pipe output into the next command |
| `>` / `>>` | Write / append output to a file |
| `2>&1` | Send errors (2) to the same place as normal output (1) |
| `&` at the end | Run in the background |
| `&&` | Run the next command only if this one succeeded |
| `~` | Your home folder |
| `*` | Any characters in a file name (`*.csv`) |
| `$VAR` | Value of a variable |

## 1. Basics and Shortcuts

> Everyday shell tricks: history, repeat, clear, and key shortcuts. Bash keeps a history; `!!` repeats the last command, shortcuts edit the current line. Use this when you forgot `sudo` (`sudo !!`), or want to re-run a long command from earlier.

```bash
clear                           # clear screen (or Ctrl+L)
history                         # previous commands
!!                              # repeat last command
sudo !!                         # repeat last command with sudo
!42                             # run command number 42 from history
exit                            # close shell / SSH session
```

| Keys | Action |
|---|---|
| `Tab` | Autocomplete (twice to list options) |
| `Up` / `Down` | Previous / next command |
| `Ctrl+R` | Search history |
| `Ctrl+C` | Stop running command |
| `Ctrl+D` | Exit / end input |
| `Ctrl+Z` | Pause job (resume with `fg`) |
| `Ctrl+A` / `Ctrl+E` | Start / end of line |
| `Ctrl+U` / `Ctrl+K` | Delete to start / end of line |
| `Ctrl+W` | Delete previous word |

Linux is **case-sensitive**: `File.txt` and `file.txt` are different files.

## 2. Help

> Documentation built into Linux. `man` shows the full manual; `--help` shows a short summary. Use it for unsure about a flag, for example what `-h` means for `df`.

```bash
man ls                          # manual (q to quit, / to search)
ls --help                       # short help
whatis ls                       # one-line description
type ls                         # alias, builtin or file?
which python3                   # path of a command
```

## 3. Filesystem Layout

> Where Linux keeps configs, logs, programs and your files. One tree starting at `/`; everything (disks too) is a folder in it. Use it for finding a config file (`/etc`), a log (`/var/log`), or your Windows drive in WSL (`/mnt/c`).

| Path | Contains |
|---|---|
| `/` | Root of everything |
| `~` or `/home/<user>` | Your home folder |
| `/root` | Home of the root user |
| `/etc` | Configuration files |
| `/var/log` | Log files |
| `/usr/bin`, `/bin` | Programs |
| `/usr/local` | Manually installed software |
| `/opt` | Optional / third-party software |
| `/tmp` | Temporary files (cleared on reboot) |
| `/mnt`, `/media` | Mounted drives (WSL: `/mnt/c` = `C:\`) |

Paths: `/` = root, `~` = home, `.` = current folder, `..` = parent folder. Files starting with `.` are hidden.

## 4. Navigation

> Moving around folders and listing their contents. `cd` changes folder, `ls -la` lists with details and hidden files. Use it in every session, especially after SSH into a server.

```bash
pwd                             # current folder
ls                              # list
ls -l                           # details (permissions, size, date)
ls -la                          # include hidden files
ls -lh                          # human-readable sizes
ls -lt                          # newest first
tree -L 2                       # folder tree, 2 levels (apt install tree)
cd /var/log                     # absolute path
cd projects                     # relative path
cd ..                           # up one level
cd ~  or  cd                    # home
cd -                            # previous folder
```

## 5. Files and Folders

> Creating, copying, moving and deleting files and folders. `touch`, `mkdir -p`, `cp -r`, `mv`, `rm -r`. Use it for organising project files on a VM; there is no recycle bin, so double-check `rm`.

```bash
touch file.txt                  # create empty file / update timestamp
mkdir folder                    # create folder
mkdir -p a/b/c                  # create nested folders
cp a.txt b.txt                  # copy file
cp -r src/ dest/                # copy folder
mv a.txt folder/                # move
mv old.txt new.txt              # rename
rm file.txt                     # delete file (no recycle bin!)
rm -i file.txt                  # ask before deleting
rm -r folder                    # delete folder and contents
rm -rf folder                   # force, no questions (be careful)
rmdir folder                    # delete empty folder
ln -s /path/to/target link      # symbolic link (shortcut)
```

## 6. View Files

> Reading files from the terminal. `cat` for short files, `less` to scroll, `head` / `tail` for start / end, `tail -f` to follow. Use it for reading a config, checking the last errors in a log, watching a log while testing.

```bash
cat file.txt                    # whole file
less file.txt                   # scroll (Space next page, / search, q quit)
head file.txt                   # first 10 lines
head -n 20 file.txt             # first 20 lines
tail -n 20 file.txt             # last 20 lines
tail -f app.log                 # follow a growing file (Ctrl+C to stop)
wc -l file.txt                  # line count
file image.png                  # file type
diff a.txt b.txt                # differences
```

## 7. Edit Files (nano, vim)

> Editing text files directly on a server with no GUI. `nano` shows its shortcuts on screen; `vim` uses modes (insert and command). Use it for changing a config file over SSH; use nano unless you already know vim.

**nano** (easiest):

| Keys | Action |
|---|---|
| `nano file.txt` | Open |
| `Ctrl+O`, `Enter` | Save |
| `Ctrl+X` | Exit |
| `Ctrl+W` | Search |
| `Ctrl+K` / `Ctrl+U` | Cut / paste line |

**vim** (if you end up in it):

| Keys | Action |
|---|---|
| `i` | Start typing (insert mode) |
| `Esc` | Back to command mode |
| `:w` | Save |
| `:q` | Quit |
| `:wq` | Save and quit |
| `:q!` | Quit without saving |
| `/word` | Search |
| `dd` / `u` | Delete line / undo |

## 8. Find Files

> Searching for files by name, age or size. `find <folder> <conditions>` walks the folder tree; `locate` uses a fast index. Use it to answer questions like "Where did that .env / config / log end up?", "which files are over 100 MB?".

```bash
find . -name "*.csv"                    # by name, from current folder
find . -iname "readme*"                 # case-insensitive
find /var/log -type f -mtime -1         # files changed in last day
find . -type f -size +100M              # larger than 100 MB
find . -name "*.tmp" -delete            # find and delete
locate nginx.conf                       # fast search (apt install plocate)
```

## 9. Search Text (grep)

> Searching for text inside files. `grep pattern file`; `-r` for a whole folder, `-i` ignore case, `-n` line numbers. Use it for finding an error in logs, or every file that uses a function or setting.

```bash
grep "error" app.log                    # lines containing text
grep -i "error" app.log                 # case-insensitive
grep -n "error" app.log                 # show line numbers
grep -v "debug" app.log                 # lines NOT containing
grep -c "error" app.log                 # count matches
grep -rn "import pandas" .              # search all files in folder
grep -rl "TODO" .                       # only file names
grep -E "error|warning" app.log         # regex OR
grep -A 3 -B 3 "error" app.log          # 3 lines after / before
```

## 10. Text Processing

> Transforming text: sort, count, cut columns, replace. Small tools chained with pipes: `sort`, `uniq`, `cut`, `awk`, `sed`. Use it for quick analysis of logs or CSVs on a server ("top 10 IPs in the access log").

```bash
sort file.txt                           # sort lines
sort -n numbers.txt                     # numeric sort
sort -r file.txt                        # reverse
uniq                                    # remove adjacent duplicates (sort first)
sort file.txt | uniq -c | sort -rn      # count occurrences, most first
cut -d "," -f 1,3 data.csv              # columns 1 and 3 of CSV
awk '{print $1}' file.txt               # first whitespace column
awk -F "," '{print $2}' data.csv        # second CSV column
sed 's/old/new/g' file.txt              # replace (prints result)
sed -i 's/old/new/g' file.txt           # replace in file
tr 'a-z' 'A-Z' < file.txt               # uppercase
```

## 11. Redirection and Pipes

> Sending output to files or into other commands. `>` overwrite, `>>` append, `2>&1` include errors, `|` pipe, `tee` screen + file. Use it for saving command output, silencing noisy commands, building one-line pipelines.

| Syntax | Meaning |
|---|---|
| `cmd > file` | Output to file (overwrite) |
| `cmd >> file` | Append to file |
| `cmd 2> file` | Errors to file |
| `cmd > file 2>&1` | Output and errors to file |
| `cmd > /dev/null` | Discard output |
| `cmd < file` | Use file as input |
| `cmd1 \| cmd2` | Output of cmd1 into cmd2 |
| `cmd \| tee file` | Show on screen AND save to file |

```bash
ls -la | less
ps aux | grep python
echo "hello" > file.txt
cat a.txt b.txt > both.txt
```

## 12. Permissions

> Who may read, write or execute a file. Three groups (owner, group, others) x three rights (r=4, w=2, x=1); change with `chmod` / `chown`. Use it to answer questions like "Permission denied" on a script, protecting SSH keys (`chmod 400`), fixing files owned by root.

```text
-rwxr-xr--  1  user  group  1234  Jan 1 12:00  script.sh
 |  |  |
 |  |  +-- others: r-- (read)
 |  +----- group:  r-x (read, execute)
 +-------- owner:  rwx (read, write, execute)
```

| Number | Permission |
|---|---|
| 4 | read (r) |
| 2 | write (w) |
| 1 | execute (x) |

```bash
chmod +x script.sh                      # make executable
chmod 755 script.sh                     # rwx r-x r-x (scripts, folders)
chmod 644 file.txt                      # rw- r-- r-- (normal files)
chmod 600 secret.txt                    # rw- --- --- (private)
chmod 400 key.pem                       # r-- --- --- (SSH keys)
chmod -R 755 folder/                    # recursive
chown user:group file.txt               # change owner
sudo chown -R $USER:$USER folder/       # take ownership of folder
```

## 13. Users and sudo

> User accounts and running commands as administrator. `sudo` runs one command as root; groups grant extra rights (for example `docker`). Use it for installing software, editing system configs, giving a user access to Docker.

```bash
whoami                                  # current user
id                                      # user id and groups
sudo command                            # run as administrator (root)
sudo -i                                 # root shell (exit to leave)
su - username                           # switch user
passwd                                  # change own password
sudo adduser alice                      # create user
sudo usermod -aG sudo alice             # give sudo rights
sudo usermod -aG docker $USER           # add yourself to a group (log out and in)
groups                                  # your groups
```

## 14. Packages (apt)

> Installing and updating software on Ubuntu / Debian. `apt` downloads packages from Ubuntu's repositories; always `apt update` first. Use it for setting up a fresh VM, installing tools like git, htop, unzip.

```bash
sudo apt update                         # refresh package list (do first)
sudo apt upgrade -y                     # upgrade installed packages
sudo apt install -y git curl htop       # install
sudo apt remove htop                    # remove
sudo apt purge htop                     # remove with config
sudo apt autoremove                     # remove unused dependencies
apt search nginx                        # search
apt show nginx                          # details
apt list --installed                    # installed packages
sudo dpkg -i package.deb                # install a .deb file
```

Other distros: Fedora/RHEL `sudo dnf install <pkg>`, Arch `sudo pacman -S <pkg>`, Mac `brew install <pkg>`.

## 15. Processes

> Running programs and how to stop them. `ps` / `top` / `htop` to see them, `kill` / `pkill` to stop by PID or name. Use this when a script hangs, a server uses 100% CPU, or a port is still taken by an old process.

```bash
ps aux                                  # all processes
ps aux | grep python                    # find one
pgrep -a python                         # PIDs by name
top                                     # live view (q quit)
htop                                    # nicer live view (F9 kill, q quit)
kill 1234                               # stop process by PID
kill -9 1234                            # force kill
pkill python                            # kill by name
killall python                          # kill all by name
```

## 16. Services (systemd) and Logs

> Background services (web servers, databases, Ollama) and their logs. `systemctl` starts / stops / enables services; `journalctl` reads their logs. Use this when a service is down after reboot, you changed its config, or need to see why it crashed.

```bash
systemctl status nginx                  # status (q to quit)
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl enable nginx             # start on boot
sudo systemctl disable nginx
systemctl list-units --type=service --state=running

journalctl -u nginx                     # service logs
journalctl -u nginx -f                  # follow live
journalctl -u nginx --since "1 hour ago"
journalctl -p err -b                    # errors since boot
sudo tail -f /var/log/syslog            # system log
```

## 17. Disk and Memory

> Disk space and memory usage. `df` per disk, `du` per folder, `free` for RAM. Use it to answer questions like "No space left on device", or checking if a model fits in RAM.

```bash
df -h                                   # free space per disk
du -sh folder/                          # size of folder
du -sh * | sort -h                      # sizes in current folder, sorted
free -h                                 # RAM and swap
lsblk                                   # disks and partitions
```

## 18. System Info

> Details about the OS, CPU and hardware. Read-only info commands like `uname`, `lscpu`, `/etc/os-release`. Use it for checking the Ubuntu version before following a guide, or CPU / GPU of a VM.

```bash
uname -a                                # kernel info
cat /etc/os-release                     # distro and version
hostname                                # machine name
uptime                                  # running time and load
lscpu                                   # CPU details
nproc                                   # number of CPUs
date                                    # date and time
nvidia-smi                              # GPU (NVIDIA only)
```

## 19. Network

> IP addresses, connectivity, open ports and the firewall. `ip`, `ping`, `curl`, `ss` for listening ports, `ufw` for the firewall. Use it to answer questions like "Is my app listening?", "can the VM reach the internet?", opening a port.

```bash
ip a                                    # IP addresses
ip r                                    # routes / gateway
ping -c 4 google.com                    # connectivity (4 packets)
curl ifconfig.me                        # public IP
curl -I https://example.com             # HTTP headers only
curl -O https://example.com/file.zip    # download (keep name)
wget https://example.com/file.zip       # download
ss -tulpn                               # listening ports and processes
sudo lsof -i :8000                      # who uses port 8000
nslookup google.com                     # DNS lookup
sudo ufw status                         # firewall status
sudo ufw allow 22/tcp                   # open port
```

## 20. SSH and File Transfer

> Secure remote login and copying files between machines. SSH encrypts the connection; keys replace passwords; `scp` / `rsync` copy files over SSH. Use it for working on a cloud VM, deploying files, or tunnelling a remote port to your laptop.

```bash
ssh user@host                           # connect
ssh -i key.pem user@host                # with key file
ssh -p 2222 user@host                   # custom port
ssh-keygen -t ed25519                   # create key pair (~/.ssh/id_ed25519)
ssh-copy-id user@host                   # install your public key on server

scp file.txt user@host:~/               # copy to server
scp user@host:~/file.txt .              # copy from server
scp -r folder user@host:~/              # copy folder
rsync -avz folder/ user@host:~/folder/  # sync (only changed files)

ssh -N -L 8080:localhost:80 user@host   # tunnel: local 8080 -> server port 80
```

`~/.ssh/config` shortcut (then just `ssh myvm`):

```text
Host myvm
    HostName 20.1.2.3
    User azureuser
    IdentityFile ~/.ssh/my-vm_key.pem
```

## 21. Archives (tar, zip)

> Packing many files into one compressed file and unpacking it. `tar -czf` / `tar -xzf` for .tar.gz, `zip` / `unzip` for .zip. Use it for backups, moving a project folder to a server, downloading release archives.

```bash
tar -czvf archive.tar.gz folder/        # create .tar.gz
tar -xzvf archive.tar.gz                # extract
tar -xzvf archive.tar.gz -C /target/    # extract to folder
tar -tzvf archive.tar.gz                # list contents
zip -r archive.zip folder/              # create zip
unzip archive.zip                       # extract zip
unzip archive.zip -d target/            # extract to folder
```

Mnemonic: **c**reate / e**x**tract, **z** = gzip, **v** = verbose, **f** = file name follows.

## 22. Environment Variables and PATH

> Variables that programs read, including PATH (where commands are found). `export NAME=value` for the session; add to `~/.bashrc` to keep it. Use it to answer questions like "command not found" after installing to `~/.local/bin`, or configuring an app.

```bash
echo $HOME                              # show one
env                                     # show all
export MY_VAR="value"                   # set for this session
unset MY_VAR                            # remove
export PATH="$HOME/.local/bin:$PATH"    # add folder to PATH (session)
```

To keep it permanently, add the `export` line to `~/.bashrc`, then run `source ~/.bashrc`.

## 23. Aliases and .bashrc

> Short names for long commands, loaded at every login. `alias` defines one; `~/.bashrc` runs at each new shell so aliases persist. Use this when you type the same long command often (`ll`, `gs` for git status).

```bash
alias ll='ls -la'                       # create alias (session)
alias                                   # list aliases
unalias ll                              # remove
nano ~/.bashrc                          # add aliases/exports here to keep them
source ~/.bashrc                        # reload without logging out
```

## 24. Shell Scripts

> A file of commands that runs as a program. Start with `#!/bin/bash`, `chmod +x`, run with `./script.sh`. Use it for repeating the same multi-step task: backups, deploys, setup of a new server.

```bash
#!/bin/bash
# backup.sh - copy a folder into a dated archive

NAME="backup-$(date +%Y-%m-%d).tar.gz"
tar -czf "$NAME" ~/projects
echo "Created $NAME"

if [ -f "$NAME" ]; then
    echo "OK"
fi

for f in *.csv; do
    echo "Processing $f"
done
```

```bash
chmod +x backup.sh                      # make executable
./backup.sh                             # run
bash backup.sh                          # run without chmod
```

## 25. Scheduled Jobs (cron)

> Running commands automatically on a schedule. `crontab -e`; each line = minute hour day month weekday command. Use it nightly backups, hourly data pulls, cleaning old logs.

```bash
crontab -e                              # edit your jobs
crontab -l                              # list jobs
```

```text
# min hour day month weekday  command
0    2    *   *     *        /home/user/backup.sh       # every day at 02:00
*/15 *    *   *     *        /home/user/check.sh        # every 15 minutes
0    9    *   *     1        /home/user/report.sh       # Mondays at 09:00
```

## 26. Long-Running Jobs

> Keeping a command running after you close the terminal or SSH. `nohup` / `&` for simple cases, `tmux` for a session you can re-attach to. Use it for training a model or running a server on a VM while you disconnect.

```bash
command &                               # run in background
jobs                                    # list background jobs
fg                                      # bring to foreground
nohup python app.py > app.log 2>&1 &    # keep running after logout

tmux                                    # session that survives disconnect
tmux ls                                 # list sessions
tmux attach                             # reattach
# inside tmux: Ctrl+B then D to detach
```

## 27. Troubleshooting

| Problem | Fix |
|---|---|
| `Permission denied` | Use `sudo`, or fix with `chmod` / `chown` |
| `command not found` | Install it (`sudo apt install ...`) or add its folder to PATH |
| `./script.sh: Permission denied` | `chmod +x script.sh` |
| `bad interpreter: /bin/bash^M` | Windows line endings: `sed -i 's/\r$//' script.sh` |
| `No space left on device` | `df -h`, then `du -sh * \| sort -h` to find big folders |
| `Could not get lock /var/lib/dpkg/lock` | Another apt is running; wait, or check `ps aux \| grep apt` |
| `Address already in use` | `sudo lsof -i :PORT` then `kill <PID>` |
| `WARNING: UNPROTECTED PRIVATE KEY FILE` | `chmod 400 key.pem` |
| Stuck in vim | `Esc` then `:q!` |
| Terminal frozen after `Ctrl+S` | Press `Ctrl+Q` |

## 28. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution. Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Disk hogs

Show the 5 largest folders inside `/var`.

<details markdown="1">
<summary>Solution</summary>

```bash
sudo du -sh /var/* 2>/dev/null | sort -h | tail -5
```

</details>

### Exercise 2: Search a log

Count the lines containing `error` (any case) in `app.log`, then show the last 20 of them with line numbers.

<details markdown="1">
<summary>Solution</summary>

```bash
grep -ic "error" app.log
grep -in "error" app.log | tail -20
```

</details>

### Exercise 3: Scheduled backup

Make `backup.sh` executable and run it every day at 02:00 with cron.

<details markdown="1">
<summary>Solution</summary>

```bash
chmod +x ~/backup.sh
crontab -e
# add this line:
0 2 * * * /home/azureuser/backup.sh >> /home/azureuser/backup.log 2>&1
```

</details>

### Exercise 4: Archive without the venv

Create `projects.tar.gz` of `~/projects` but leave out every `.venv` folder.

<details markdown="1">
<summary>Solution</summary>

```bash
tar --exclude=".venv" -czvf projects.tar.gz ~/projects
tar -tzvf projects.tar.gz | head        # check the contents
```

</details>

---

<!-- nav:start -->
**Previous:** [02 - Terminal and PowerShell](02_terminal-powershell.md) | **Index:** [All guides](README.md) | **Next:** [04 - Git and GitHub](04_git.md)
<!-- nav:end -->
