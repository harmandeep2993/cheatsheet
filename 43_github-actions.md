# 43 - GitHub Actions (CI/CD)

<!-- nav:start -->
**Previous:** [42 - Docker](42_docker.md) | **Index:** [All guides](README.md) | **Next:** [44 - Nginx, Reverse Proxy and HTTPS](44_nginx-https.md)
<!-- nav:end -->

Quick reference for automating tests, linting, evals, Docker builds and deployments with GitHub Actions.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is CI/CD and GitHub Actions?

- **CI (Continuous Integration)**: every push / pull request automatically runs checks (lint, tests, evals) so broken code is caught before it is merged.
- **CD (Continuous Delivery / Deployment)**: after checks pass, the app is automatically built (e.g. a Docker image) and deployed.
- **GitHub Actions** is GitHub's built-in automation: you describe **workflows** in YAML files under `.github/workflows/`, and GitHub runs them on its servers (**runners**) when **events** happen (push, pull request, schedule, manual click).

### Mental model

```text
EVENT                  WORKFLOW (.github/workflows/ci.yml)
push / pull_request -> +-----------------------------------------------------------+
schedule (cron)        | JOB "test"  (runs-on: ubuntu-latest = fresh virtual machine) |
manual (dispatch)      |   step 1: checkout code          (uses: actions/checkout)  |
                       |   step 2: set up Python / uv     (uses: an action)         |
                       |   step 3: install dependencies   (run: shell command)      |
                       |   step 4: ruff check             (run)                     |
                       |   step 5: pytest                 (run)                     |
                       +------------------------ needs ------------------------------+
                       | JOB "deploy" (only on main, only if "test" passed)         |
                       |   build Docker image -> push to registry -> deploy to Azure |
                       +-----------------------------------------------------------+
RESULT: green check / red X on the commit and pull request
```

Each job gets a **clean machine**: nothing is installed unless your steps install it, and nothing persists afterwards unless you cache or upload it.

### Why use it?

- **Catch bugs early**: tests run on every pull request automatically.
- **Consistency**: same checks for everyone; no "works on my machine".
- **Automation**: releases, Docker images, deployments, nightly evals, scheduled data jobs.
- **Free** for public repos and included minutes for private ones.

### Key terms

| Term | Meaning |
|---|---|
| Workflow | A YAML file describing automation |
| Event / trigger (`on`) | What starts the workflow |
| Job | A set of steps that runs on one runner; jobs run in parallel unless linked with `needs` |
| Step | One command (`run`) or one reusable action (`uses`) |
| Action | Reusable building block from the Marketplace (`actions/checkout@v4`) |
| Runner | The machine executing a job (GitHub-hosted or self-hosted) |
| Secret | Encrypted value (API key) available to workflows |
| Matrix | Run the same job for several versions / OSes |
| Artifact | Files saved from a run (reports, builds) |
| Environment | Deployment target with its own secrets and protection rules |
| OIDC | Keyless login from GitHub to a cloud (no stored cloud passwords) |

**Where it fits:** runs [14 - pytest](14_pytest.md) and [34 - Evals](34_evals-observability.md); builds images from [42 - Docker](42_docker.md); deploys to [47 - Azure](47_azure.md) / [45 - Kubernetes](45_kubernetes.md); lives in your [04 - Git](04_git.md) repo; YAML syntax in [07](07_yaml-json.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| GitHub Actions documentation | https://docs.github.com/en/actions |
| GitHub Marketplace (actions) | https://github.com/marketplace?type=actions |
| setup-uv action | https://github.com/astral-sh/setup-uv |
| Azure login action | https://github.com/Azure/login |

---

## Contents

1. [Workflow File Structure](#1-workflow-file-structure)
2. [Triggers (on)](#2-triggers-on)
3. [Python CI with uv](#3-python-ci-with-uv)
4. [Python CI with pip](#4-python-ci-with-pip)
5. [Matrix Builds](#5-matrix-builds)
6. [Secrets and Variables](#6-secrets-and-variables)
7. [Caching Dependencies](#7-caching-dependencies)
8. [Artifacts](#8-artifacts)
9. [Running LLM Evals in CI](#9-running-llm-evals-in-ci)
10. [Build and Push a Docker Image](#10-build-and-push-a-docker-image)
11. [Deploy to Azure (OIDC)](#11-deploy-to-azure-oidc)
12. [Conditions, Needs and Environments](#12-conditions-needs-and-environments)
13. [Scheduled Jobs](#13-scheduled-jobs)
14. [Reusable Workflows and Composite Actions](#14-reusable-workflows-and-composite-actions)
15. [Branch Protection and Required Checks](#15-branch-protection-and-required-checks)
16. [gh CLI for Actions](#16-gh-cli-for-actions)
17. [Security Best Practices](#17-security-best-practices)
18. [Troubleshooting](#18-troubleshooting)
19. [Try It](#19-try-it)

---

## 1. Workflow File Structure

> The anatomy of a workflow YAML file. `name`, `on` (triggers), `jobs` -> each job has `runs-on` and `steps`.
>
> Use it in every workflow; files live in `.github/workflows/*.yml`.

```yaml
name: CI                                  # shown in the Actions tab

on:                                       # WHEN to run
  push:
    branches: [main]
  pull_request:

jobs:                                     # WHAT to run
  test:                                   # job id
    runs-on: ubuntu-latest                # WHERE to run (fresh VM)
    steps:
      - uses: actions/checkout@v4         # reusable action: get the repo code
      - name: Say hello                   # shell command step
        run: echo "Hello from ${{ github.repository }} on ${{ github.ref_name }}"
```

`${{ ... }}` is an expression: access contexts like `github`, `secrets`, `env`, `matrix`, `steps`.

## 2. Triggers (on)

> Events that start a workflow. List one or more events with optional filters.
>
> Use it for deciding when checks and deployments should run.

```yaml
on:
  push:
    branches: [main]
    paths: ["src/**", "tests/**", "pyproject.toml"]     # only when these change
  pull_request:
    branches: [main]
  workflow_dispatch:                                     # "Run workflow" button in the UI
    inputs:
      environment:
        type: choice
        options: [dev, prod]
  schedule:
    - cron: "0 3 * * *"                                  # every day 03:00 UTC
  release:
    types: [published]
```

## 3. Python CI with uv

> Lint and test a uv project on every push / pull request. Install uv, sync dependencies from the lock file, run Ruff and pytest.
>
> Use it for projects managed with uv ([11](11_uv.md)).

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true

      - name: Install dependencies
        run: uv sync --locked --all-groups

      - name: Lint
        run: uv run ruff check .

      - name: Format check
        run: uv run ruff format --check .

      - name: Tests
        run: uv run pytest -q -m "not integration" --cov=src --cov-report=term-missing
```

## 4. Python CI with pip

> The same checks for a requirements.txt project. `actions/setup-python` with pip caching, then install and test.
>
> Use it for projects using venv + pip ([10](10_python-virtual-environment.md)).

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: ruff check .
      - run: pytest -q
```

## 5. Matrix Builds

> Running a job for several combinations (Python versions, OSes). `strategy.matrix` defines the values; the job runs once per combination.
>
> Use it for libraries supporting several versions; checking Windows compatibility.

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.11", "3.12", "3.13"]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: ${{ matrix.python-version }}
      - run: uv sync --locked
      - run: uv run pytest -q
```

## 6. Secrets and Variables

> Giving workflows API keys and config without putting them in the repo. Repo -> Settings -> Secrets and variables -> Actions; reference with `${{ secrets.NAME }}` / `${{ vars.NAME }}`; pass them as environment variables to steps.
>
> Use it for LLM API keys for eval jobs, registry passwords, deployment settings.

```yaml
      - name: Run integration tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          LLM_MODEL: ${{ vars.LLM_MODEL }}
        run: uv run pytest -q -m integration
```

```bash
gh secret set ANTHROPIC_API_KEY            # set from the terminal (prompts for the value)
gh variable set LLM_MODEL --body "claude-opus-5"
```

- Secrets are masked in logs, but never `echo` them.
- Secrets are **not** available to workflows triggered by pull requests from forks (by design).

## 7. Caching Dependencies

> Reusing downloaded packages between runs to save time. Built-in caching in setup actions (`enable-cache`, `cache: pip`) or `actions/cache` with a key based on the lock file hash.
>
> Use it in every CI workflow; can cut minutes from each run.

```yaml
      - uses: actions/cache@v4
        with:
          path: ~/.cache/huggingface
          key: hf-${{ runner.os }}-${{ hashFiles('models.txt') }}     # cache downloaded models
```

## 8. Artifacts

> Files saved from a workflow run (test reports, eval results, build outputs). `actions/upload-artifact` in one job; `actions/download-artifact` in another; downloadable from the run page.
>
> Use it for keeping eval results, coverage reports, built packages.

```yaml
      - uses: actions/upload-artifact@v4
        if: always()                         # upload even if tests failed
        with:
          name: eval-results
          path: results/
          retention-days: 14
```

## 9. Running LLM Evals in CI

> Automatically checking AI quality on pull requests and nightly. A small smoke eval on pull requests (fast, cheap) with a score threshold; the full eval on a schedule; results as artifacts.
>
> Use it for repos with prompts, RAG or agents ([34](34_evals-observability.md)).

```yaml
name: Evals

on:
  pull_request:
    paths: ["prompts/**", "src/**", "evals/**"]
  schedule:
    - cron: "0 2 * * *"

jobs:
  evals:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv sync --locked
      - name: Smoke evals (pull requests) or full evals (nightly)
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          EVAL_SET: ${{ github.event_name == 'schedule' && 'evals/full.jsonl' || 'evals/smoke.jsonl' }}
        run: uv run python -m evals.run --cases "$EVAL_SET" --min-score 0.9 --out results/
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: eval-results
          path: results/
```

Keep the PR set small to control cost and time; fail the job when the score drops below the threshold.

## 10. Build and Push a Docker Image

> Building your app image in CI and pushing it to a registry. Log in to the registry, then `docker/build-push-action` with tags (commit SHA + `latest`) and layer caching.
>
> Use it in every deployable app ([42 - Docker](42_docker.md)).

```yaml
name: Build image

on:
  push:
    branches: [main]

permissions:
  contents: read
  packages: write                          # push to GitHub Container Registry

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}          # built-in token, no setup needed
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.sha }}
            ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

For Azure Container Registry, log in with `azure/login` (section 11) and `az acr login`, or `docker/login-action` with the ACR name.

## 11. Deploy to Azure (OIDC)

> Deploying without storing Azure passwords in GitHub. Create an Entra ID app / managed identity with a **federated credential** trusting your repo; the workflow gets a short-lived token via OIDC.
>
> Use it in any deployment from GitHub to Azure ([47](47_azure.md)).

```yaml
name: Deploy

on:
  push:
    branches: [main]

permissions:
  id-token: write                          # required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production                # protection rules + environment secrets
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Build in ACR and update the container app
        run: |
          az acr build -r ${{ vars.ACR_NAME }} -t sales-api:${{ github.sha }} .
          az containerapp update -n sales-api -g ${{ vars.RESOURCE_GROUP }} \
            --image ${{ vars.ACR_NAME }}.azurecr.io/sales-api:${{ github.sha }}
```

Setup (once): create an app registration / user-assigned identity, add a federated credential for `repo:<owner>/<repo>:environment:production`, assign it a role (e.g. Contributor on the resource group, AcrPush on the registry). See Microsoft's "Use GitHub Actions with OpenID Connect" guide.

## 12. Conditions, Needs and Environments

> Controlling order and when jobs / steps run. `needs` for dependencies, `if` for conditions, `environment` for protected deployments with approvals.
>
> Use it for test -> build -> deploy pipelines.

```yaml
jobs:
  test: { ... }
  build:
    needs: test                                            # only after test succeeds
    if: github.ref == 'refs/heads/main'                   # only on main
    ...
  deploy:
    needs: build
    environment: production                               # can require manual approval
    ...
```

| Expression | Meaning |
|---|---|
| `if: success()` / `failure()` / `always()` | Step runs on success / failure / always |
| `if: github.event_name == 'pull_request'` | Only for PRs |
| `if: contains(github.event.head_commit.message, '[skip evals]') == false` | Skip by commit message |
| `timeout-minutes: 20` | Kill job after 20 minutes |
| `concurrency: deploy-${{ github.ref }}` | Only one deploy per branch at a time |

## 13. Scheduled Jobs

> Running workflows on a timer. `on.schedule.cron` in UTC.
>
> Use it nightly evals, re-indexing RAG documents, data refreshes, dependency checks.

```yaml
on:
  schedule:
    - cron: "30 5 * * 1-5"          # 05:30 UTC, Monday to Friday
  workflow_dispatch:                # also allow manual runs
```

Scheduled workflows run on the default branch and may be delayed at busy times; in inactive public repos they are disabled after 60 days.

## 14. Reusable Workflows and Composite Actions

> Sharing CI logic between workflows and repos. A reusable workflow (`on: workflow_call`) is called with `uses:` at job level; a composite action bundles steps in `action.yml`.
>
> Use it for many repos with the same Python CI, standard deploy steps.

```yaml
# caller
jobs:
  ci:
    uses: my-org/ci-templates/.github/workflows/python-ci.yml@v1
    with:
      python-version: "3.12"
    secrets: inherit
```

## 15. Branch Protection and Required Checks

> Preventing merges into `main` unless CI passes. Repo -> Settings -> Branches / Rulesets -> require pull requests and required status checks.
>
> Use it in any shared repository.

- Require status checks (e.g. `test`) to pass before merging.
- Require pull request reviews.
- Block force pushes to `main`.

## 16. gh CLI for Actions

> Managing workflow runs from the terminal. `gh run` and `gh workflow` commands ([04 - Git](04_git.md)).
>
> Use it for watching CI without opening the browser.

```bash
gh workflow list
gh workflow run deploy.yml -f environment=dev      # trigger workflow_dispatch
gh run list --limit 5
gh run watch                                       # follow the latest run live
gh run view --log-failed                           # logs of failed steps
gh run rerun <run-id> --failed
```

## 17. Security Best Practices

> Keeping CI from becoming an attack path. Minimal permissions, pinned actions, OIDC instead of long-lived secrets, careful with pull requests from forks.
>
> Use it in every repository.

- Set `permissions:` explicitly (least privilege; default read-only).
- Pin third-party actions to a version tag you trust or a commit SHA.
- Prefer OIDC to cloud providers over stored keys.
- Never print secrets; avoid `pull_request_target` with untrusted code checkout.
- Enable Dependabot for actions and Python dependencies.
- Protect deployment environments with required reviewers.

## 18. Troubleshooting

| Problem | Fix |
|---|---|
| Workflow does not start | File must be in `.github/workflows/` on the right branch; check `on:` filters (branches / paths) |
| YAML error in the Actions tab | Indentation / quoting; validate YAML ([07](07_yaml-json.md)) |
| `ModuleNotFoundError` in CI but not locally | Dependency missing from `pyproject.toml` / requirements; use the lock file (`uv sync --locked`) |
| Tests pass locally, fail in CI | Missing env vars / secrets, OS differences, reliance on local files, timezone |
| Secret is empty | Wrong name, not set for this repo / environment, or fork PR (secrets withheld) |
| `Resource not accessible by integration` | Add the needed `permissions:` (e.g. `packages: write`, `id-token: write`) |
| Azure login fails with OIDC | Federated credential subject must match repo / branch / environment exactly |
| Slow runs | Enable caching, run only affected paths, split jobs, parallel matrix |
| Eval job too expensive | Smaller smoke set on PRs; full set nightly; cache LLM results for unchanged inputs |

## 19. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: CI for a uv project

Run Ruff and pytest on every push and pull request.

<details markdown="1">
<summary>Solution</summary>

```yaml
name: CI
on: {push: {branches: [main]}, pull_request: {}}
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv sync --locked
      - run: uv run ruff check .
      - run: uv run pytest -q
```

</details>

### Exercise 2: Use a secret

Pass `ANTHROPIC_API_KEY` to an integration-test step.

<details markdown="1">
<summary>Solution</summary>

```bash
gh secret set ANTHROPIC_API_KEY
```

```yaml
      - run: uv run pytest -m integration
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

</details>

### Exercise 3: Read this repo's CI

Open `.github/workflows/` in this repo: which workflow catches a library API change, and when does it run?

<details markdown="1">
<summary>Solution</summary>

`examples.yml`, job `latest-deps`: it upgrades all dependencies (ignoring the lock file) and runs the tests every Monday, so breaking changes like MCP SDK v2 show up as a failing check.

</details>

---

<!-- nav:start -->
**Previous:** [42 - Docker](42_docker.md) | **Index:** [All guides](README.md) | **Next:** [44 - Nginx, Reverse Proxy and HTTPS](44_nginx-https.md)
<!-- nav:end -->
