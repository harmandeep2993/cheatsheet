# 04 - Git and GitHub

Quick reference for version control with Git and working with GitHub (including the `gh` CLI).

## Introduction

### What is Git?

Git is a **version control system**: it records the history of your project as a series of snapshots called **commits**. Every commit stores what changed, who changed it, when and why (the message). You can go back to any earlier version, compare versions, and see who wrote each line. Git lets developers work on separate **branches** at the same time without disturbing each other and then **merge** their work together. Git runs locally on your machine; **GitHub** is a website that hosts Git repositories online so you can back them up, share them, review code with **pull requests** and run automation.

### Why use it?

- **Full history**: every version of every file is saved; nothing is lost.
- **Undo safely**: restore a file, revert a bad change, or go back to last week's version.
- **Experiment freely**: try ideas on a branch; delete it if it fails, merge it if it works.
- **Teamwork**: many people change the same project; Git merges their changes and flags conflicts.
- **Code review**: pull requests show exactly what changed before it reaches `main`.
- **Backup and sync**: push to GitHub and work from any computer.
- **Industry standard**: required in nearly every software and data job.

### Key terms

| Term | Meaning |
|---|---|
| Repository (repo) | A project folder tracked by Git (history lives in `.git/`) |
| Commit | A saved snapshot with a message |
| Branch | An independent line of development |
| Merge | Combine the changes of two branches |
| Remote / origin | The copy of the repo on a server (GitHub) |
| Push / pull | Upload / download commits |
| Pull request (PR) | A GitHub request to merge a branch, with review |
| Conflict | Two branches changed the same lines; you decide the result |

**Where it fits:** use it for every project, including this one. VS Code has Git built in: [05 - VS Code](05_vscode.md).

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Concepts](#1-concepts)
2. [Install and Configure](#2-install-and-configure)
3. [Start a Repository](#3-start-a-repository)
4. [Daily Workflow](#4-daily-workflow)
5. [Status and Differences](#5-status-and-differences)
6. [Commit History](#6-commit-history)
7. [Branches](#7-branches)
8. [Merge and Rebase](#8-merge-and-rebase)
9. [Merge Conflicts](#9-merge-conflicts)
10. [Remotes: Push, Pull, Fetch](#10-remotes-push-pull-fetch)
11. [Undo Things](#11-undo-things)
12. [Stash (Save Work for Later)](#12-stash-save-work-for-later)
13. [Tags and Releases](#13-tags-and-releases)
14. [.gitignore](#14-gitignore)
15. [Rename, Move, Delete Files](#15-rename-move-delete-files)
16. [Commit Message Convention](#16-commit-message-convention)
17. [GitHub CLI (gh)](#17-github-cli-gh)
18. [Pull Request Workflow](#18-pull-request-workflow)
19. [SSH Key for GitHub](#19-ssh-key-for-github)
20. [Useful Extras](#20-useful-extras)
21. [Troubleshooting](#21-troubleshooting)

---

## 0. Flags and Parameters

> - **What:** The meaning of every flag, value and special name used in the Git commands below.
> - **How:** A command is split into program, sub-command, flags and arguments; tables list every flag.
> - **When to use:** You see a command like `git push -u origin main` and want to know what each part does.

### How a command is built

```text
git  push  -u  origin  main
|    |     |   |       |
|    |     |   |       +-- branch to push
|    |     |   +---------- remote to push to (the name of the GitHub URL)
|    |     +-------------- -u (--set-upstream): remember this pairing, so later just "git push"
|    +-------------------- sub-command
+------------------------- program

git  commit  -m "feat: add login"
             |  |
             |  +-- value: the commit message
             +----- -m (--message): message given on the command line (no editor opens)
```

Help for any sub-command: `git commit --help` or `git commit -h` (short).

### Special names

| Name | Meaning |
|---|---|
| `.` | Current folder and everything below it (`git add .`) |
| `HEAD` | The commit you are on now |
| `HEAD~1` | One commit before HEAD (`HEAD~2` = two before) |
| `origin` | Default name of the remote you cloned from |
| `origin/main` | Your local copy of the `main` branch on the remote |
| `main..feature` | Commits in `feature` that are not in `main` |
| `a1b2c3d` | Short commit hash (first 7 characters are enough) |
| `stash@{1}` | Second newest stash entry (0 = newest) |

### Common flags

| Command | Flag | Meaning |
|---|---|---|
| `config` | `--global` | Setting for all repos of your user (without it: this repo only) |
| `config` | `--list` | Show all settings |
| `add` | `-p` (`--patch`) | Choose changes piece by piece |
| `commit` | `-m` | Commit message |
| `commit` | `-a` (`--all`) | Stage all modified / deleted tracked files first (not new files) |
| `commit` | `--amend` | Replace the last commit (message and / or content) |
| `commit` | `--no-edit` | Keep the existing message when amending |
| `status` | `-s` (`--short`) | Short two-column output |
| `diff` | `--staged` | Show staged changes instead of unstaged |
| `diff` | `--stat` | Only files and number of changed lines |
| `log` | `--oneline` | One line per commit: short hash + message |
| `log` | `--graph` | Draw branch lines |
| `log` | `--all` | Include all branches, not only the current one |
| `log` | `-5` | Only the last 5 commits |
| `log` | `-p` | Show the changes of each commit |
| `log` | `--author`, `--since`, `--grep` | Filter by author, date or message text |
| `log` | `--follow` | Keep following a file across renames |
| `switch` | `-c` (`--create`) | Create the branch and switch to it |
| `checkout` | `-b` | Same as `switch -c` (older command) |
| `branch` | `-a` | List local and remote branches |
| `branch` | `-d` / `-D` | Delete (only if merged) / force delete |
| `branch` | `-m` | Rename |
| `branch` | `-vv` | Show which remote branch each local branch tracks |
| `remote` | `-v` | Show remote URLs |
| `push` | `-u` | Set upstream (first push of a branch) |
| `push` | `--delete` | Delete a branch on the remote |
| `push` | `--tags` | Push all tags |
| `pull` | `--rebase` | Rebase your commits on top instead of creating a merge commit |
| `pull` | `--allow-unrelated-histories` | Allow merging two repos that started separately |
| `merge` | `--squash` | Combine all branch changes into one staged change |
| `merge` / `rebase` | `--abort` | Cancel and go back to the state before |
| `rebase` | `--continue` | Continue after fixing a conflict |
| `checkout` | `--ours` / `--theirs` | In a conflict, take your version / the incoming version |
| `restore` | `--staged` | Unstage (keep the file changes) |
| `restore` | `--source <hash>` | Take the file from that commit |
| `reset` | `--soft` | Move branch back; keep changes staged |
| `reset` | (no flag) / `--mixed` | Move branch back; keep changes unstaged |
| `reset` | `--hard` | Move branch back; DELETE the changes |
| `clean` | `-n` | Dry run: only show what would be deleted |
| `clean` | `-f` / `-d` | Force (required to delete) / include folders |
| `rm` | `--cached` | Stop tracking but keep the file on disk |
| `rm` | `-r` | Recursive (folders) |
| `stash` | `-u` | Include untracked files |
| `stash push` | `-m` | Name for the stash |
| `tag` | `-a` / `-m` | Annotated tag / its message |
| `tag` | `-d` | Delete a local tag |
| `shortlog` | `-sn` | `-s` counts only, `-n` sorted by number |

### GitHub CLI and SSH

| Command | Flag | Meaning |
|---|---|---|
| `gh repo create` | `--private` / `--public` | Visibility of the new repo |
| `gh repo create` | `--source .` | Use the current folder as the repo |
| `gh repo create` | `--push` | Push existing commits right away |
| `gh pr create` | `--fill` | Use commit messages as PR title and body |
| `gh pr create` | `--title`, `--body` | Set title and description yourself |
| `gh ... view` | `--web` | Open in the browser |
| `gh pr merge` | `--squash` | Squash all PR commits into one |
| `gh pr merge` | `--delete-branch` | Delete the branch after merging |
| `ssh-keygen` | `-t ed25519` | Key type (ed25519 = modern and short) |
| `ssh-keygen` | `-C "email"` | Comment stored in the key (to recognise it) |
| `ssh` | `-T` | No terminal; used to test the GitHub login |

## 1. Concepts

> - **What:** The basic ideas: working folder, staging area, commits, branches, remote.
> - **How:** Git stores snapshots (commits); you pick changes (stage), save them (commit), share them (push).
> - **When to use:** Read once before starting; it explains why each command exists.

```text
Working folder --(git add)--> Staging area --(git commit)--> Local repo --(git push)--> Remote (GitHub)
      ^                                                           |
      +------------------------(git pull / git checkout)----------+
```

| Term | Meaning |
|---|---|
| **Repository (repo)** | Project folder tracked by Git (history lives in `.git/`) |
| **Commit** | Saved snapshot with a message and a unique hash (`a1b2c3d`) |
| **Staging area** | Changes selected for the next commit |
| **Branch** | Independent line of work (`main`, `feature/login`) |
| **HEAD** | The commit / branch you currently have checked out |
| **Remote** | Copy of the repo on a server, usually named `origin` |
| **Clone** | Download a remote repo |
| **Pull request (PR)** | Request to merge a branch on GitHub, with review |

## 2. Install and Configure

> - **What:** One-time setup of Git on a machine.
> - **How:** `git config --global` stores your name, email and preferences for all repos.
> - **When to use:** New laptop or new VM, before your first commit.

```bash
winget install -e --id Git.Git              # Windows
sudo apt install git                        # Ubuntu
git --version

git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global core.editor "code --wait"   # VS Code as editor
git config --global pull.rebase false           # pull = merge (default behavior)
git config --global core.autocrlf true          # Windows: handle line endings
git config --list                               # show all settings
```

## 3. Start a Repository

> - **What:** Starting version control for a project.
> - **How:** `git init` in an existing folder, or `git clone` to download an existing repo.
> - **When to use:** New project (init) or working on something already on GitHub (clone).

```bash
git init                                    # new repo in current folder
git clone https://github.com/user/repo.git  # download existing repo
git clone https://github.com/user/repo.git my-folder   # into specific folder
git clone git@github.com:user/repo.git      # via SSH
```

## 4. Daily Workflow

> - **What:** The loop you repeat all day: change, stage, commit, push.
> - **How:** `git add` selects changes, `git commit` saves them locally, `git push` uploads them.
> - **When to use:** Every time you finish a small, meaningful piece of work.

```bash
git status                                  # what changed?
git add file.py                             # stage one file
git add .                                   # stage everything in folder
git add -p                                  # choose parts of files interactively
git commit -m "feat: add login page"        # commit staged changes
git commit -am "fix: typo"                  # stage tracked files + commit
git push                                    # upload to remote
git pull                                    # download + merge remote changes
```

## 5. Status and Differences

> - **What:** Seeing what changed before you commit.
> - **How:** `git status` lists changed files; `git diff` shows the exact lines.
> - **When to use:** Before every commit, to avoid committing debug code or secrets.

```bash
git status                                  # overview
git status -s                               # short format
git diff                                    # unstaged changes
git diff --staged                           # staged changes (what will be committed)
git diff main..feature                      # between branches
git diff HEAD~1                             # vs previous commit
git diff --stat                             # summary: files and line counts
```

Short status codes: `M` modified, `A` added, `D` deleted, `R` renamed, `??` untracked.

## 6. Commit History

> - **What:** Looking at past commits.
> - **How:** `git log` lists commits; `git show` / `git blame` show details for a commit or line.
> - **When to use:** "When did this break?", "who changed this line and why?", finding a commit hash.

```bash
git log                                     # full history (q to quit)
git log --oneline                           # one line per commit
git log --oneline --graph --all             # branch graph
git log -5                                  # last 5 commits
git log -p file.py                          # changes to one file
git log --author="Harman"                   # by author
git log --since="2 weeks ago"
git log --grep="login"                      # search messages
git show a1b2c3d                            # details of one commit
git blame file.py                           # who changed each line
```

## 7. Branches

> - **What:** Separate lines of work that do not affect main until merged.
> - **How:** `git switch -c name` creates a branch; commits go to the current branch.
> - **When to use:** Any new feature or fix, so main stays working while you experiment.

```bash
git branch                                  # list local branches
git branch -a                               # include remote branches
git switch -c feature/login                 # create and switch
git switch main                             # switch to existing
git checkout -b feature/login               # older syntax: create and switch
git branch -m old-name new-name             # rename
git branch -d feature/login                 # delete (merged)
git branch -D feature/login                 # force delete (unmerged)
git push origin --delete feature/login      # delete remote branch
```

## 8. Merge and Rebase

> - **What:** Bringing changes from one branch into another.
> - **How:** Merge adds a merge commit; rebase replays your commits on top for a straight history.
> - **When to use:** Merge a finished feature into main; rebase your branch to catch up with main.

```bash
# Merge feature into main
git switch main
git pull
git merge feature/login                     # creates merge commit if needed
git merge --squash feature/login            # combine into one change, then commit

# Rebase feature on latest main (linear history)
git switch feature/login
git rebase main
git rebase --continue                       # after fixing conflicts
git rebase --abort                          # cancel
```

Rule: never rebase commits that others have already pulled.

## 9. Merge Conflicts

> - **What:** What happens when two branches changed the same lines.
> - **How:** Git marks both versions in the file; you edit, `git add`, then commit.
> - **When to use:** A merge, rebase or pull stops with "CONFLICT".

A conflict looks like this in the file:

```text
<<<<<<< HEAD
your version
=======
their version
>>>>>>> feature/login
```

```bash
git status                                  # shows conflicted files
# edit the file: keep what you want, delete the markers
git add file.py                             # mark as resolved
git commit                                  # finish merge (or git rebase --continue)
git merge --abort                           # give up, go back
git checkout --ours file.py                 # keep your version
git checkout --theirs file.py               # keep their version
```

VS Code shows buttons: **Accept Current / Accept Incoming / Accept Both**.

## 10. Remotes: Push, Pull, Fetch

> - **What:** Syncing your local repo with GitHub.
> - **How:** `push` uploads commits, `fetch` downloads, `pull` downloads and merges.
> - **When to use:** Sharing work, getting teammates' changes, working from two computers.

```bash
git remote -v                               # list remotes
git remote add origin https://github.com/user/repo.git
git remote set-url origin git@github.com:user/repo.git   # change URL
git push -u origin main                     # first push, set upstream
git push                                    # later pushes
git push origin feature/login               # push a branch
git fetch                                   # download, do not merge
git pull                                    # fetch + merge
git pull --rebase                           # fetch + rebase
git branch -vv                              # local vs remote tracking
```

## 11. Undo Things

> - **What:** Fixing mistakes: unstaging, discarding, amending, reverting.
> - **How:** `restore` for files, `reset` to move the branch back, `revert` to undo safely with a new commit.
> - **When to use:** Wrong file committed, bad commit message, or a pushed commit broke something.

| Situation | Command |
|---|---|
| Discard changes in a file (not staged) | `git restore file.py` |
| Unstage a file (keep changes) | `git restore --staged file.py` |
| Fix last commit message (not pushed) | `git commit --amend -m "new message"` |
| Add forgotten file to last commit (not pushed) | `git add file.py` then `git commit --amend --no-edit` |
| Undo last commit, keep changes staged | `git reset --soft HEAD~1` |
| Undo last commit, keep changes unstaged | `git reset HEAD~1` |
| Undo last commit, DELETE changes | `git reset --hard HEAD~1` |
| Undo a pushed commit (safe, new commit) | `git revert a1b2c3d` |
| Reset branch to match remote | `git fetch` then `git reset --hard origin/main` |
| Remove untracked files | `git clean -n` (preview), `git clean -fd` |
| Restore a file from an older commit | `git restore --source a1b2c3d file.py` |
| Find a "lost" commit | `git reflog` then `git reset --hard <hash>` |
| Stop tracking a file (keep on disk) | `git rm --cached file.py` |

`--hard` and `git clean` delete work permanently. Pushed history: use `revert`, not `reset`.

## 12. Stash (Save Work for Later)

> - **What:** Temporarily shelving uncommitted changes.
> - **How:** `git stash` saves and cleans the working folder; `git stash pop` brings changes back.
> - **When to use:** You must switch branch or pull now, but your current work is not ready to commit.

```bash
git stash                                   # put changes aside
git stash -u                                # include untracked files
git stash push -m "wip login"               # with a name
git stash list                              # show stashes
git stash pop                               # re-apply latest and remove it
git stash apply stash@{1}                   # re-apply specific, keep it
git stash drop stash@{0}                    # delete one
git stash clear                             # delete all
```

## 13. Tags and Releases

> - **What:** Named markers on specific commits, usually versions.
> - **How:** `git tag -a v1.0.0`, then push the tag.
> - **When to use:** Marking a release so you can always return to exactly that version.

```bash
git tag                                     # list
git tag v1.0.0                              # lightweight tag
git tag -a v1.0.0 -m "First release"        # annotated tag
git push origin v1.0.0                      # push one tag
git push --tags                             # push all tags
git tag -d v1.0.0                           # delete local tag
```

## 14. .gitignore

> - **What:** A list of files Git should never track.
> - **How:** Patterns in `.gitignore`; matching untracked files are ignored.
> - **When to use:** Every project: keep out `.venv`, `.env`, data files, caches and logs.

```text
# Python
__pycache__/
*.pyc
.venv/
.ipynb_checkpoints/

# Secrets and local config
.env
*.pem

# Data and output
data/
*.log
*.csv

# OS / editor
.DS_Store
Thumbs.db
.vscode/
```

```bash
git check-ignore -v file.txt                # why is this file ignored?
git rm -r --cached .                        # re-apply .gitignore to tracked files
git add .
git commit -m "chore: apply gitignore"
```

Templates: https://github.com/github/gitignore

## 15. Rename, Move, Delete Files

> - **What:** Renaming, moving or deleting tracked files the Git way.
> - **How:** `git mv` / `git rm` change the file and stage the change in one step.
> - **When to use:** Reorganising a project (like renumbering these guides) while keeping file history.

```bash
git mv old.py new.py                        # rename (keeps history)
git mv file.py src/                         # move
git rm file.py                              # delete and stage
git log --follow new.py                     # history across renames
```

## 16. Commit Message Convention

> - **What:** A standard format for commit messages.
> - **How:** `type(scope): description`, where the type says what kind of change it is.
> - **When to use:** Every commit; makes history readable and enables automatic changelogs.

Conventional Commits: `type(scope): description`

| Type | Use for |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change without new feature or fix |
| `perf` | Performance |
| `test` | Tests |
| `build` / `ci` | Build system, CI pipelines |
| `chore` | Maintenance |
| `revert` | Revert a commit |

```bash
git commit -m "feat(auth): add login endpoint"
git commit -m "fix(pandas): correct read_csv example"
```

## 17. GitHub CLI (gh)

> - **What:** GitHub from the terminal: repos, PRs, issues, Actions.
> - **How:** `gh` talks to the GitHub API after `gh auth login`.
> - **When to use:** Creating a repo or PR without leaving the terminal, checking CI status.

```bash
winget install -e --id GitHub.cli
gh auth login                               # log in once
gh repo create my-repo --private --source . --push   # create repo from current folder
gh repo clone user/repo
gh repo view --web                          # open repo in browser

gh pr create --fill                         # PR from current branch
gh pr list
gh pr view 12 --web
gh pr checkout 12                           # check out someone's PR locally
gh pr merge 12 --squash --delete-branch

gh issue create --title "Bug" --body "Details"
gh issue list
gh run list                                 # GitHub Actions runs
gh run watch                                # follow current run
```

## 18. Pull Request Workflow

> - **What:** The standard team flow: branch, commit, push, pull request, review, merge.
> - **How:** Work on a branch, open a PR on GitHub, merge after review / checks.
> - **When to use:** Any shared repo, or solo when you want CI checks and a record of changes.

```bash
git switch main && git pull                 # 1. start from latest main
git switch -c feat/add-docker-guide         # 2. new branch
# ... edit files ...
git add .                                   # 3. commit
git commit -m "docs: add docker guide"
git push -u origin feat/add-docker-guide    # 4. push branch
gh pr create --fill                         # 5. open PR
# 6. review, then merge on GitHub or: gh pr merge --squash --delete-branch
git switch main && git pull                 # 7. update local main
git branch -d feat/add-docker-guide         # 8. clean up
```

Fork workflow: fork on GitHub, clone your fork, `git remote add upstream <original-url>`, then `git fetch upstream` and `git merge upstream/main` to stay updated.

## 19. SSH Key for GitHub

> - **What:** Password-less, secure authentication with GitHub.
> - **How:** Generate a key pair; add the public key to GitHub; Git uses the private key.
> - **When to use:** Tired of entering credentials, or HTTPS auth is blocked.

```bash
ssh-keygen -t ed25519 -C "you@example.com"  # create key (Enter for defaults)
cat ~/.ssh/id_ed25519.pub                   # copy this public key
# GitHub -> Settings -> SSH and GPG keys -> New SSH key -> paste
ssh -T git@github.com                       # test: "Hi <user>! You've successfully authenticated"
```

## 20. Useful Extras

> - **What:** Less common but powerful commands.
> - **How:** Aliases, cherry-pick, bisect, worktree and more.
> - **When to use:** Copy one fix to another branch (cherry-pick), find the commit that broke something (bisect).

```bash
git config --global alias.lg "log --oneline --graph --all"   # then: git lg
git config --global alias.st "status -s"
git shortlog -sn                            # commits per author
git cherry-pick a1b2c3d                     # copy one commit to current branch
git bisect start / good / bad               # find the commit that broke something
git worktree add ../repo-hotfix hotfix      # second folder for another branch
git archive -o release.zip HEAD             # export without .git
```

## 21. Troubleshooting

| Problem | Fix |
|---|---|
| `Author identity unknown` | Set `user.name` and `user.email` (section 2) |
| `rejected ... (fetch first)` / `non-fast-forward` | `git pull` (or `git pull --rebase`), then push again |
| `refusing to merge unrelated histories` | `git pull origin main --allow-unrelated-histories` |
| `fatal: not a git repository` | Wrong folder, or run `git init` |
| `Permission denied (publickey)` | SSH key not added to GitHub (section 19) or use HTTPS URL |
| `Your branch is ahead of 'origin/main' by N commits` | `git push` |
| `detached HEAD` | `git switch main`, or keep work with `git switch -c new-branch` |
| Committed a secret | Rotate the secret FIRST, then remove it from history (git filter-repo); deleting in a new commit is not enough |
| File still tracked after adding to .gitignore | `git rm --cached file` then commit |
| `LF will be replaced by CRLF` warning | Harmless on Windows; set `core.autocrlf true` |
| Accidentally committed to main instead of a branch | `git switch -c new-branch`, then `git switch main` and `git reset --hard origin/main` |
| Large file rejected by GitHub (>100 MB) | Remove it, add to `.gitignore`, or use Git LFS |
