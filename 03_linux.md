# 03 - Linux

Quick reference for everyday Linux commands (Ubuntu / Debian focus, works on most distros, WSL and Mac for the basics).

## Contents

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

---

## 1. Basics and Shortcuts

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

```bash
man ls                          # manual (q to quit, / to search)
ls --help                       # short help
whatis ls                       # one-line description
type ls                         # alias, builtin or file?
which python3                   # path of a command
```

## 3. Filesystem Layout

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

```bash
find . -name "*.csv"                    # by name, from current folder
find . -iname "readme*"                 # case-insensitive
find /var/log -type f -mtime -1         # files changed in last day
find . -type f -size +100M              # larger than 100 MB
find . -name "*.tmp" -delete            # find and delete
locate nginx.conf                       # fast search (apt install plocate)
```

## 9. Search Text (grep)

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

```bash
df -h                                   # free space per disk
du -sh folder/                          # size of folder
du -sh * | sort -h                      # sizes in current folder, sorted
free -h                                 # RAM and swap
lsblk                                   # disks and partitions
```

## 18. System Info

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

```bash
echo $HOME                              # show one
env                                     # show all
export MY_VAR="value"                   # set for this session
unset MY_VAR                            # remove
export PATH="$HOME/.local/bin:$PATH"    # add folder to PATH (session)
```

To keep it permanently, add the `export` line to `~/.bashrc`, then run `source ~/.bashrc`.

## 23. Aliases and .bashrc

```bash
alias ll='ls -la'                       # create alias (session)
alias                                   # list aliases
unalias ll                              # remove
nano ~/.bashrc                          # add aliases/exports here to keep them
source ~/.bashrc                        # reload without logging out
```

## 24. Shell Scripts

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
