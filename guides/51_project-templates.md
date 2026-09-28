# 51 - Project Templates

<!-- nav:start -->
**Previous:** [50 - Project Structure: Python Microservices + Frontend](50_project-structure.md) | **Index:** [All guides](../README.md) | **Next:** [97 - Capstone Project: Document Chatbot](97_capstone-project.md)
<!-- nav:end -->

When and how to turn a project layout into a reusable template: GitHub template repositories, Copier (questions, placeholders, updates), Cookiecutter, what a good template contains and how to test it in CI. Comes with a working Copier template in `templates/service-template/` that adds a new service to the starter from [50](50_project-structure.md).

> **Last verified:** 2026-09-28. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is a project template?

A **project template** is a ready-made starting point that you copy to begin a new project (or a new part of a project) instead of building the same folders, config files and boilerplate by hand every time. The simplest template is a repository you copy. A smarter one asks a few questions ("service name?", "which database?") and fills the answers into file names and file contents.

**Copier** and **Cookiecutter** are the two common Python tools for question-based templates. Both use **Jinja** placeholders like `{{ service_name }}`. Copier can also **update** projects made from a template when the template improves later, which is why this guide uses it for the main example.

### Mental model

Think of a cookie cutter and dough. The template is the cutter (made once, carefully); each generated project is a cookie. With Copier, the cookie remembers which cutter and which version made it, so when you improve the cutter you can re-apply the changes to old cookies.

```text
Template (made once)                          Generated project (made many times)
--------------------                          -----------------------------------
copier.yml         questions + defaults
pyproject.toml.jinja   name = "{{ service_name }}-service"   -->  name = "feedback-service"
src/{{package_name}}/main.py.jinja                            -->  src/feedback_service/main.py
{{_copier_conf.answers_file}}.jinja                           -->  .copier-answers.yml
                                                                   (template URL, version, answers)

copier copy   = first generation
copier update = re-apply newer template versions, keeping your own changes
```

### Why use templates?

- **Speed**: a new project or service is ready in seconds, with tests, Docker and CI already working.
- **Consistency**: every service has the same layout, logging, health checks and settings style, so anyone can find their way in any of them.
- **Best practice by default**: security headers, non-root containers, linting and CI are included instead of remembered.
- **Fewer copy-paste mistakes**: no leftover old names in imports, Dockerfiles or config.
- **Improvements spread**: with Copier, a fix in the template can be applied to every project made from it.

### Key terms

| Term | Meaning |
|---|---|
| Project template | A reusable starting point for new projects or parts of projects |
| Scaffolding | Generating the initial files and folders of a project from a template |
| GitHub template repository | A repository marked as a template so "Use this template" creates a copy with fresh history |
| Copier | Python tool that renders templates from questions and can update generated projects later |
| Cookiecutter | Older, widely used Python templating tool; generates once, no built-in update |
| Jinja | The templating language behind `{{ variable }}`, `{% if %}` and filters like `upper` |
| Placeholder | A `{{ ... }}` expression replaced by an answer when the template is rendered |
| `copier.yml` | Copier's configuration: questions, defaults, validators and settings |
| Answers file | `.copier-answers.yml` in the generated project: template source, version and answers |
| `.jinja` suffix | Marks files Copier must render; the suffix is removed in the output |
| Template version | A Git tag on the template repository (for example `v1.2.0`) that `copier update` moves between |

**Where it fits:** templates package the layout from [50 - Project Structure](50_project-structure.md); they live in Git ([05 - Git](05_git.md)), use [12 - uv](12_uv.md) and [43 - Docker](43_docker.md), and are tested with [44 - GitHub Actions](44_github-actions.md). Configuration formats are in [08 - YAML and JSON](08_yaml-json.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Copier documentation | https://copier.readthedocs.io/en/stable/ |
| Copier: configuring a template | https://copier.readthedocs.io/en/stable/configuring/ |
| Copier: updating a project | https://copier.readthedocs.io/en/stable/updating/ |
| Cookiecutter documentation | https://cookiecutter.readthedocs.io/en/stable/ |
| Jinja template designer docs | https://jinja.palletsprojects.com/en/stable/templates/ |
| GitHub: creating a template repository | https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository |
| GitHub CLI: gh repo create | https://cli.github.com/manual/gh_repo_create |
| uv: creating projects | https://docs.astral.sh/uv/concepts/projects/init/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [When to Create a Template (and When Not)](#1-when-to-create-a-template-and-when-not)
2. [Kinds of Templates](#2-kinds-of-templates)
3. [GitHub Template Repository](#3-github-template-repository)
4. [Copier: How It Works](#4-copier-how-it-works)
5. [Writing copier.yml](#5-writing-copieryml)
6. [Template Files and Placeholders](#6-template-files-and-placeholders)
7. [Generating a Project or Service](#7-generating-a-project-or-service)
8. [Updating Projects from the Template](#8-updating-projects-from-the-template)
9. [Cookiecutter (Alternative)](#9-cookiecutter-alternative)
10. [What Belongs in a Good Template](#10-what-belongs-in-a-good-template)
11. [Testing Templates in CI](#11-testing-templates-in-ci)
12. [Versioning and Maintenance](#12-versioning-and-maintenance)
13. [Troubleshooting](#13-troubleshooting)
14. [Try It](#14-try-it)

---

## 0. Flags and Parameters

> The Copier, Cookiecutter and GitHub CLI commands used in this guide, broken into their parts.
>
> Use this when you see `uvx copier copy --data service_name=feedback ../service-template services/feedback-service` and want to know what each part does.

```text
uvx  copier  copy  --defaults  --data service_name=feedback  ../service-template  services/feedback-service
|    |       |     |           |                             |                    |
|    |       |     |           |                             |                    +-- destination folder
|    |       |     |           |                             +----------------------- template: path, Git URL or gh:owner/repo
|    |       |     |           +----------------------------------------------------- answer a question on the command line
|    |       |     +------------------------------------------------------------------- use defaults for every other question
|    |       +------------------------------------------------------------------------- subcommand: first generation
|    +--------------------------------------------------------------------------------- the tool
+-------------------------------------------------------------------------------------- run a Python tool without installing it (uv)
```

| Command / flag | Meaning |
|---|---|
| `copier copy <template> <dest>` | Generate a new project from a template |
| `copier update` | Re-apply a newer template version to the project in the current folder |
| `copier recopy` | Regenerate from scratch with the saved answers (discards the smart merge) |
| `copier check-update` | Tell whether a newer template version exists, without changing anything |
| `--data key=value` / `-d` | Answer a question without being asked |
| `--data-file answers.yml` | Read answers from a YAML file |
| `--defaults` / `-l` | Accept the default for every question not given with `--data` |
| `--vcs-ref v1.2.0` / `-r` | Use this tag, branch or commit of the template (default: latest tag) |
| `--trust` | Allow `_tasks`, `_migrations` and Jinja extensions (they run code on your machine) |
| `--pretend` / `-n` | Show what would happen without writing files |
| `--overwrite` / `-w` | Overwrite existing files without asking |
| `--conflict inline` / `rej` | On update, show conflicts as Git-style markers or as `.rej` files |
| `cookiecutter gh:owner/repo` | Generate from a Cookiecutter template on GitHub |
| `cookiecutter <tpl> --no-input key=value` | Generate without prompts, overriding values |
| `gh repo create my-app --template owner/repo --private --clone` | New repository from a GitHub template, cloned locally |

---

## 1. When to Create a Template (and When Not)

> A template pays off when you create similar things repeatedly and want them to stay alike. It costs time to build and maintain, so do not make one too early.
>
> Use it when deciding whether the next "copy that folder and rename things" should become a template instead.

Create a template when:

| Signal | Example |
|---|---|
| You have built the same thing **three or more times** | Third FastAPI microservice with the same Dockerfile, settings and health check |
| **Several people or teams** start projects | Every team should get the same CI, linting and security setup |
| Copy-paste keeps causing **mistakes** | Old service names left in imports, wrong env prefix, stale Dockerfile path |
| The layout is **stable** | You are no longer changing the structure every week |
| Improvements should **reach existing projects** | A Dockerfile security fix should go to all 12 services (Copier update) |

Do **not** create one (yet) when:

- it is a **one-off** project; just write it,
- the structure is **still changing**; you would maintain a moving target (wait until the second or third copy),
- the "template" would be **mostly questions and `{% if %}` blocks**; too many options make it hard to test and understand. Prefer two simple templates over one with 15 switches,
- a **framework already scaffolds it** well (`uv init`, `npm create vite@latest`, `npx create-next-app`). Use those and template only your additions.

**Rule of three:** the first time, just build it. The second time, copy it and notice what you changed. The third time, turn those changes into template questions.

---

## 2. Kinds of Templates

> Four ways to start from a template, from the simplest copy to generators that can update projects later.
>
> Use it to pick the lightest option that solves your problem.

| Kind | How it works | Asks questions | Updates old projects | Best for |
|---|---|---|---|---|
| Plain folder / repo copy | Copy, then rename by hand | No | No | Personal one-offs |
| GitHub template repository | "Use this template" creates a new repo | No | No | Whole-project starters, fast and zero tooling |
| Cookiecutter | Renders `{{cookiecutter.x}}` from `cookiecutter.json` | Yes | No (Cruft adds it) | Many existing public templates |
| Copier | Renders `{{ x }}` from `copier.yml`, records answers | Yes | **Yes** (`copier update`) | Templates you keep improving; generating parts of a repo |
| Framework CLIs | `uv init`, `npm create vite@latest` | A few | No | The base of a single-language project |

They combine well: a **GitHub template repository** for the whole monorepo starter (from [50](50_project-structure.md)), plus a **Copier template** for adding each new service inside it. That is exactly the setup in this pocket guide's `templates/` folder.

---

## 3. GitHub Template Repository

> Mark a repository as a template on GitHub; anyone can then create a new repository with the same files but a fresh history.
>
> Use it for whole-project starters where no renaming is needed, or as the first step before a Copier template.

Make a repository a template:

1. Push the starter to its own repository (for example `my-org/fullstack-starter`).
2. On GitHub: **Settings -> General -> Template repository** (tick the box).

Create a new project from it:

```bash
# In the browser: green "Use this template" button -> Create a new repository
# Or with the GitHub CLI:
gh repo create my-new-app --template my-org/fullstack-starter --private --clone
cd my-new-app
```

Differences from a fork:

| | Template copy | Fork |
|---|---|---|
| Git history | Fresh (one initial commit) | Full history of the original |
| Link to original | None | Stays linked; can open pull requests upstream |
| Purpose | Start a new, independent project | Contribute to or follow the original |

Limitations: no questions and no renaming, so names like `fullstack-microservices` stay until you change them, and later improvements to the template never reach the copies. Keep names generic (`app`, `api`) or add a small Copier template for the parts that must be renamed.

---

## 4. Copier: How It Works

> Copier reads `copier.yml`, asks the questions, renders every `.jinja` file and every `{{ }}` in paths with the answers, and writes an answers file so the project can be updated later.
>
> Use it to understand what happens when you run `copier copy` or `copier update`.

```text
copier copy <template> <dest>
  1. Read copier.yml               questions, defaults, validators, settings
  2. Ask questions                 or take them from --data / --defaults
  3. Compute derived values        e.g. package_name = service_name + "_service"
  4. Walk the template folder
       path with {{ x }}           -> rename with the answer
       file ending in .jinja       -> render content, drop the suffix
       other files                 -> copy unchanged
       _exclude patterns           -> skip
  5. Write .copier-answers.yml     template source, Git version, answers
  6. Print _message_after_copy
```

Install nothing: run it through uv.

```bash
uvx copier --version
uvx copier copy gh:my-org/service-template services/feedback-service
```

Templates can come from a local path, any Git URL or `gh:owner/repo` / `gl:owner/repo` shortcuts. If the template is a Git repository, Copier uses its **latest tag** by default; that is what makes updates possible.

---

## 5. Writing copier.yml

> The template's configuration: settings (keys starting with `_`) and questions (every other key), each with a type, help text, default and optional validator.
>
> Use it when designing the questions of a new template.

The service template in this repository (`templates/service-template/copier.yml`):

```yaml
_min_copier_version: "9.0"
_templates_suffix: .jinja
_answers_file: .copier-answers.yml
_exclude:
  - copier.yml
  - README.md

_message_after_copy: |
  Created {{ service_name }}-service. Next steps: uv lock, add it to compose.yaml and proxy/nginx.conf.

# === Questions ===
service_name:
  type: str
  help: Short name, lowercase letters and digits only (feedback -> feedback-service)
  validator: >-
    {% if not (service_name.isalnum() and service_name.islower()) %}
    Use lowercase letters and digits
    {% endif %}

description:
  type: str
  default: "Stores and lists {{ service_name }} items"

port:
  type: int
  default: 8000

# === Derived values (never asked, not saved in the answers file) ===
package_name:
  type: str
  default: "{{ service_name }}_service"
  when: false
```

| Key | Meaning |
|---|---|
| `type` | `str`, `int`, `float`, `bool`, `yaml`, `json` |
| `help` | Text shown when asking |
| `default` | Default answer; may use earlier answers with Jinja |
| `choices` | A list (or mapping) of allowed answers, shown as a menu |
| `validator` | Jinja that renders to an error message when the answer is invalid, empty when valid |
| `when` | Ask only if true; `when: false` = computed value, never asked, not saved |
| `secret: true` | Do not save the answer in the answers file (needs a default) |
| `multiselect: true` | With `choices`: pick several |

Choices example:

```yaml
database:
  type: str
  help: Which database should the service use?
  choices:
    None (in memory): none
    PostgreSQL: postgres
  default: none
```

Useful settings: `_subdirectory` (template files live in a subfolder, keeping the repo root for docs and CI), `_exclude`, `_skip_if_exists` (never overwrite files the user owns, like `.env`), `_tasks` (commands after generation, need `--trust`), `_migrations` (commands when updating between versions).

---

## 6. Template Files and Placeholders

> Inside the template, file contents and paths use Jinja. Only files ending in `.jinja` are rendered; everything else is copied as is.
>
> Use it when turning an existing service into template files.

Paths:

```text
src/{{package_name}}/main.py.jinja       ->  src/feedback_service/main.py
tests/test_{{service_name}}_api.py.jinja ->  tests/test_feedback_api.py
{{_copier_conf.answers_file}}.jinja      ->  .copier-answers.yml
```

Content (`main.py.jinja`):

```python
"""App factory for {{ service_name }}-service."""

from {{ package_name }}.api.routes import router
from {{ package_name }}.config import Settings

SERVICE_NAME = "{{ service_name }}-service"
```

Jinja you will use:

| Syntax | Meaning | Example output |
|---|---|---|
| `{{ service_name }}` | Insert an answer | `feedback` |
| `{{ service_name \| upper }}` | Filter: upper case | `FEEDBACK` |
| `{{ service_name \| capitalize }}` | Filter: first letter upper | `Feedback` |
| `{% if database == "postgres" %}...{% endif %}` | Include a block only sometimes | |
| `{% for x in items %}...{% endfor %}` | Repeat a block | |
| `{% raw %}${{ secrets.TOKEN }}{% endraw %}` | Output `{{ }}` literally (GitHub Actions, Helm) | `${{ secrets.TOKEN }}` |
| `{#- comment -#}` | Template comment, not in output | |

The answers file template, needed for `copier update`:

```jinja
# Written by Copier; lets `copier update` apply later template changes. Do not edit by hand.
{{ _copier_answers|to_nice_yaml -}}
```

**How to build a template from working code:** copy a real, tested service into the template folder; add `.jinja` to files that contain names; replace each occurrence of the name with a placeholder (search for `documents`, `DOCUMENTS_`, `documents_service`); rename folders to `{{package_name}}`; generate a test project and run its tests. Start from working code, never from scratch.

---

## 7. Generating a Project or Service

> Run `copier copy` with the template and a destination; answer the questions; finish the steps the template prints.
>
> Use it every time you start a new service in the starter.

```bash
cd templates/fullstack-microservices

# Interactive: Copier asks each question
uvx copier copy ../service-template services/feedback-service

# Non-interactive (scripts, CI)
uvx copier copy --defaults --data service_name=feedback ../service-template services/feedback-service

uv lock && uv sync --all-packages
uv run pytest services/feedback-service
```

What you get:

```text
services/feedback-service/
  .copier-answers.yml
  Dockerfile
  pyproject.toml
  src/feedback_service/
    __init__.py  config.py  main.py  schemas.py
    api/routes.py
    services/items.py
  tests/test_feedback_api.py
```

Then wire it into the system (Copier prints these steps): add it to `compose.yaml`, add `location /api/feedback/` to `proxy/nginx.conf`, add it to the CI image matrix. Those files belong to the whole repo, so the service template deliberately does not edit them; see [50 - Project Structure](50_project-structure.md) sections 6 and 9.

Commit the generated service **before** changing it, so `git diff` later shows your own changes separately from the generated code.

---

## 8. Updating Projects from the Template

> When the template gets a new version (a Git tag), `copier update` re-applies the template to an existing project and merges the changes with your edits.
>
> Use it to roll out a template fix (for example a Dockerfile improvement) to services created earlier.

Requirements:

- the template is a **Git repository with version tags** (`v1.0.0`, `v1.1.0`),
- the project has its **`.copier-answers.yml`** (it records `_src_path` and `_commit`),
- the project's Git working tree is **clean** (commit first).

```bash
# In the template repository: release a new version
git tag v1.1.0 && git push --tags

# In the generated project
cd services/feedback-service
uvx copier update                      # to the latest tag
uvx copier update --vcs-ref v1.1.0     # to a specific version
git diff                               # review what changed
```

How it merges: Copier regenerates the **old** template version with your saved answers, computes your changes against it, renders the **new** version and re-applies your changes on top. Where both touched the same lines you get conflict markers (`--conflict inline`) or `.rej` files (`--conflict rej`); resolve them like Git merge conflicts.

Change an answer during an update:

```bash
uvx copier update --data port=8080
```

Templates with a local path source (like `../service-template` in this repo) generate fine, but updates need the template to live in its own Git repository with tags.

---

## 9. Cookiecutter (Alternative)

> Cookiecutter is the older, very popular tool: variables in `cookiecutter.json`, placeholders `{{ cookiecutter.x }}`, generates once.
>
> Use it when an existing public Cookiecutter template fits, or your team already uses it.

```text
my-template/
  cookiecutter.json
  {{cookiecutter.project_slug}}/
    pyproject.toml
    src/{{cookiecutter.package_name}}/__init__.py
```

```json
{
  "project_name": "My Service",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-') }}",
  "package_name": "{{ cookiecutter.project_slug.replace('-', '_') }}",
  "database": ["none", "postgres"]
}
```

```bash
uvx cookiecutter gh:my-org/my-template
uvx cookiecutter ./my-template --no-input project_name="Feedback Service"
```

| | Copier | Cookiecutter |
|---|---|---|
| Config | `copier.yml` (YAML, validators, `when`) | `cookiecutter.json` (lists become choices) |
| Placeholders | `{{ name }}` | `{{ cookiecutter.name }}` |
| Which files are rendered | Only `.jinja` (configurable) | All files (exclude with `_copy_without_render`) |
| Generate into an existing repo | Yes (natural) | Awkward (always creates a new top folder) |
| Update existing projects | Yes, `copier update` | No (use the separate tool Cruft) |
| Hooks | `_tasks`, `_migrations` | `hooks/pre_gen_project.py`, `post_gen_project.py` |

---

## 10. What Belongs in a Good Template

> A good template produces a project that works immediately: it installs, passes its tests, builds its image and explains the next steps.
>
> Use it as a checklist when creating or reviewing a template.

| Include | Why |
|---|---|
| Working example code (health endpoint, one real route) | Shows the pattern; proves the wiring works |
| Tests that pass on first run | New code starts with a test next to it |
| Dockerfile, `.dockerignore` | Builds identically from day one |
| Lint and format config | Style is settled before the first review |
| CI workflow (or instructions to add to CI) | Nothing ships untested |
| `.env.example` with placeholders, `.gitignore` with `.env` | Secrets never enter the template or the new repo |
| README "first steps after generating" | Nobody has to guess what to do next |
| Answers file | Future `copier update` |

| Keep out | Why |
|---|---|
| Real secrets, API keys, `.env` files | They would be copied into every project |
| Generated files: `.venv`, `node_modules`, `dist`, `__pycache__` | Large, platform specific, rebuilt anyway |
| Company or project specific names (unless templated) | Every copy would need hand edits |
| Many optional features behind `{% if %}` | Each combination needs testing; split into separate templates |
| Commented-out "maybe you need this" code | Becomes dead code in every project |

---

## 11. Testing Templates in CI

> A template is code: generate a project from it in CI and run that project's own checks. Otherwise it breaks silently until someone needs it.
>
> Use it for every template you keep, especially before tagging a new version.

The job in this repository's `.github/workflows/templates.yml`:

```yaml
service-template:
  runs-on: ubuntu-latest
  defaults:
    run:
      working-directory: templates/fullstack-microservices
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v6
    - name: Generate a service into the starter
      run: uvx copier copy --defaults --data service_name=feedback ../service-template services/feedback-service
    - run: uv lock && uv sync --all-packages
    - run: uv run ruff check .
    - run: uv run ruff format --check .
    - run: uv run pytest services/feedback-service
    - run: docker build -f services/feedback-service/Dockerfile -t feedback-service .
```

Good additions:

- **A matrix of answers** (`database: [none, postgres]`) so every `{% if %}` branch is generated and tested.
- **A name that stresses the template**, for example a two-word name, to catch places where the name is used in paths, imports and env vars differently.
- **An update test**: generate from the previous tag, then `copier update` to the current commit, and run the tests again.

---

## 12. Versioning and Maintenance

> Treat the template like a library: version it with tags, keep a changelog, and make small, reviewable changes.
>
> Use it once more than a couple of projects depend on the template.

| Practice | Why |
|---|---|
| Semantic version tags (`v1.4.0`) | `copier update` moves between tags; users can pin a version |
| `CHANGELOG.md` in the template repo | People see what an update will change before running it |
| Small releases | Small updates merge cleanly; big rewrites cause conflicts everywhere |
| `_migrations` for breaking changes | Rename files or move config automatically during `copier update` |
| Update a real project before tagging | Catches merge problems CI does not |
| One owner or team | Someone reviews changes and answers questions |

When the template and generated projects drift a lot (people rewrote most generated files), updates stop being useful. Then keep the template for **new** projects only and fix old projects by hand.

---

## 13. Troubleshooting

> Problems that come up most when building and using templates.
>
> Use it when generation fails, output looks wrong, or an update misbehaves.

| Symptom | Likely cause | Fix |
|---|---|---|
| `{{ service_name }}` appears literally in output | File lacks the `.jinja` suffix | Rename to `name.ext.jinja` |
| `.jinja` files appear in the output unrendered | `_templates_suffix` differs from the file names | Use one suffix consistently (`.jinja`) |
| GitHub Actions `${{ ... }}` vanishes or errors | Jinja tried to render it | Wrap in `{% raw %}...{% endraw %}` |
| Template README / `copier.yml` copied into the project | Not excluded | Add them to `_exclude` or move files into `_subdirectory` |
| `copier update` says the project is not from a template | Missing `.copier-answers.yml` | Add the answers file template; regenerate |
| `copier update` refuses to run | Uncommitted changes in the destination | Commit or stash first |
| Update does nothing | Template has no newer tag | Tag a release, or use `--vcs-ref HEAD` for testing |
| Conflicts on every update | Big template changes or heavy local edits | Smaller template releases; use `--conflict inline` and resolve |
| `ValueError: Validation error for question` | Answer failed the validator | Use a valid value (the message says what is expected) |
| Generated code fails lint (import order) | Linter does not know the new package is first-party | Configure ruff `src = ["services/*/src"]` instead of listing packages |
| Copier refuses `_tasks` | Tasks run code, so they need consent | Review the template, then add `--trust` |

---

## 14. Try It

> Exercises on `templates/service-template/`. Try each one before opening the solution.
>
> Use it to practise generating, changing and testing a template.

### Exercise 1: Generate and run a service

Generate a `ratings` service into the starter and run its tests.

<details markdown="1">
<summary>Solution</summary>

```bash
cd templates/fullstack-microservices
uvx copier copy --defaults --data service_name=ratings ../service-template services/ratings-service
uv lock && uv sync --all-packages
uv run pytest services/ratings-service
```

Delete it afterwards with `rm -rf services/ratings-service && uv lock` if you do not want to keep it.

</details>

### Exercise 2: Add a question

Add a `max_items` question (integer, default 1000) and use it as the default of `max_items` in the generated `config.py`.

<details markdown="1">
<summary>Solution</summary>

In `copier.yml`:

```yaml
max_items:
  type: int
  help: Maximum number of items the service stores
  default: 1000
```

In `src/{{package_name}}/config.py.jinja`:

```python
    max_items: int = {{ max_items }}
```

Generate with `--data max_items=50` and check `config.py`.

</details>

### Exercise 3: Template or not?

For each case, decide: template, GitHub template repository, or neither? (a) A one-time data migration script. (b) Your team's fourth FastAPI service this quarter. (c) A complete starter your bootcamp students copy once.

<details markdown="1">
<summary>Solution</summary>

(a) Neither: one-off. (b) Copier template: repeated, and fixes should reach earlier services through `copier update`. (c) GitHub template repository: whole-project copy, no renaming needed, no later updates required.

</details>

### Exercise 4: Literal braces

Your template contains a GitHub Actions workflow with `${{ matrix.python-version }}`. After generation the value is empty. Why, and how do you fix it?

<details markdown="1">
<summary>Solution</summary>

The file ends in `.jinja`, so Jinja treated `{{ matrix.python-version }}` as a placeholder and rendered an undefined value. Wrap the expression: `{% raw %}${{ matrix.python-version }}{% endraw %}`, or drop the `.jinja` suffix if the file needs no placeholders at all.

</details>

---

<!-- nav:start -->
**Previous:** [50 - Project Structure: Python Microservices + Frontend](50_project-structure.md) | **Index:** [All guides](../README.md) | **Next:** [97 - Capstone Project: Document Chatbot](97_capstone-project.md)
<!-- nav:end -->
