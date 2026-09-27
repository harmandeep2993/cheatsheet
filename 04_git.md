# 04 - Git and GitHub

Quick reference for version control with Git and working with GitHub (including the `gh` CLI).

## Contents

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

## 1. Concepts

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

```bash
git init                                    # new repo in current folder
git clone https://github.com/user/repo.git  # download existing repo
git clone https://github.com/user/repo.git my-folder   # into specific folder
git clone git@github.com:user/repo.git      # via SSH
```

## 4. Daily Workflow

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

```bash
git tag                                     # list
git tag v1.0.0                              # lightweight tag
git tag -a v1.0.0 -m "First release"        # annotated tag
git push origin v1.0.0                      # push one tag
git push --tags                             # push all tags
git tag -d v1.0.0                           # delete local tag
```

## 14. .gitignore

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

```bash
git mv old.py new.py                        # rename (keeps history)
git mv file.py src/                         # move
git rm file.py                              # delete and stage
git log --follow new.py                     # history across renames
```

## 16. Commit Message Convention

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

```bash
ssh-keygen -t ed25519 -C "you@example.com"  # create key (Enter for defaults)
cat ~/.ssh/id_ed25519.pub                   # copy this public key
# GitHub -> Settings -> SSH and GPG keys -> New SSH key -> paste
ssh -T git@github.com                       # test: "Hi <user>! You've successfully authenticated"
```

## 20. Useful Extras

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
