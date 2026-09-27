# 07 - YAML, JSON, TOML and .env

<!-- nav:start -->
**Previous:** [06 - Regex](06_regex.md) | **Index:** [All guides](README.md) | **Next:** [08 - HTTP and APIs](08_http-apis.md)
<!-- nav:end -->

Quick reference for the text formats used for data exchange and configuration: JSON, YAML, TOML and `.env` files.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What are these formats?

They are ways to write **structured data as plain text**, so both humans and programs can read it.

- **JSON** (JavaScript Object Notation): the language of APIs. Every web API, LLM API and most databases speak JSON. Strict syntax: double quotes, no comments.
- **YAML** (YAML Ain't Markup Language): the language of **configuration**. Docker Compose, GitHub Actions, Kubernetes and many AI tools use it. Uses indentation instead of brackets and allows comments.
- **TOML**: simple config format used by Python projects (`pyproject.toml`) and tools like Ruff and uv.
- **.env**: plain `KEY=value` lines for environment variables and secrets, loaded by apps at startup.

### Mental model

All four describe the same few building blocks:

```text
Building block      JSON                 YAML                  Python
------------------  -------------------  --------------------  ----------------
Object / mapping    {"name": "Ana"}      name: Ana             dict
List / array        [1, 2, 3]            - 1                   list
                                         - 2
String              "hello"              hello  or  "hello"    str
Number              42, 3.14             42, 3.14              int, float
Boolean             true / false         true / false          True / False
Nothing             null                 null  or  ~           None
```

Once you see a file as "nested dicts and lists", every format is just different punctuation for the same tree. `json.load` / `yaml.safe_load` / `tomllib.load` all give you plain Python dicts and lists.

### Why learn them?

- **APIs**: requests and responses (FastAPI, OpenAI, Claude) are JSON.
- **Config everywhere**: CI pipelines, Docker Compose, Kubernetes, agent configs are YAML.
- **Python projects**: `pyproject.toml` defines dependencies and tool settings.
- **Secrets**: `.env` keeps API keys out of your code.
- **LLM structured output**: you ask models to return JSON that your code parses.

### Key terms

| Term | Meaning |
|---|---|
| Serialize / dump | Python object -> text (`json.dumps`) |
| Deserialize / load / parse | Text -> Python object (`json.loads`) |
| Schema | Rules describing valid structure (JSON Schema, Pydantic model) |
| Key / value | Name and its data in a mapping |
| Nesting | Objects / lists inside other objects / lists |
| Indentation | Leading spaces that define structure in YAML |

**Where it fits:** used by [08 - HTTP and APIs](08_http-apis.md), [12 - Pydantic](12_pydantic.md), [11 - uv](11_uv.md) (`pyproject.toml`), [42 - Docker](42_docker.md) (Compose), [43 - GitHub Actions](43_github-actions.md) and [45 - Kubernetes](45_kubernetes.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| JSON | https://www.json.org/ |
| JSON Schema | https://json-schema.org/ |
| YAML | https://yaml.org/ |
| TOML | https://toml.io/ |
| Python json module | https://docs.python.org/3/library/json.html |
| Python tomllib module | https://docs.python.org/3/library/tomllib.html |
| PyYAML | https://pyyaml.org/ |
| jq | https://jqlang.org/ |
| python-dotenv | https://pypi.org/project/python-dotenv/ |

---

## Contents

1. [JSON Syntax](#1-json-syntax)
2. [JSON in Python](#2-json-in-python)
3. [JSON on the Command Line (jq)](#3-json-on-the-command-line-jq)
4. [JSON Lines (JSONL)](#4-json-lines-jsonl)
5. [JSON Schema](#5-json-schema)
6. [YAML Syntax](#6-yaml-syntax)
7. [YAML Multi-line Strings, Anchors, Multiple Documents](#7-yaml-multi-line-strings-anchors-multiple-documents)
8. [YAML in Python](#8-yaml-in-python)
9. [TOML Syntax](#9-toml-syntax)
10. [TOML in Python](#10-toml-in-python)
11. [.env Files](#11-env-files)
12. [Which Format When](#12-which-format-when)
13. [Troubleshooting](#13-troubleshooting)
14. [Try It](#14-try-it)

---

## 1. JSON Syntax

> The rules for writing valid JSON. Objects in `{}`, lists in `[]`, keys always double-quoted strings, values separated by commas.
>
> Use it for writing API request bodies, test data, config for tools that need JSON.

```json
{
  "name": "Sales API",
  "version": 2,
  "active": true,
  "owner": null,
  "tags": ["api", "ml"],
  "limits": {
    "requests_per_minute": 60,
    "max_tokens": 4096
  },
  "models": [
    {"id": "small", "cost": 0.5},
    {"id": "large", "cost": 2.0}
  ]
}
```

| Rule | Valid | Invalid |
|---|---|---|
| Keys in double quotes | `"name": 1` | `name: 1`, `'name': 1` |
| Strings in double quotes | `"hi"` | `'hi'` |
| No trailing comma | `[1, 2]` | `[1, 2,]` |
| No comments | | `// note`, `# note` |
| Booleans / null lowercase | `true`, `null` | `True`, `None` |

## 2. JSON in Python

> Converting between JSON text and Python dicts / lists. `json.loads` / `json.dumps` for strings, `json.load` / `json.dump` for files.
>
> Use it for reading API responses, saving results, parsing LLM JSON output.

```python
import json

data = json.loads('{"a": 1, "b": [1, 2]}')     # str -> dict
text = json.dumps(data)                         # dict -> str (one line)
text = json.dumps(data, indent=2)               # pretty
text = json.dumps(data, ensure_ascii=False)     # keep accents as-is
text = json.dumps(data, sort_keys=True)         # stable key order (good for caching / diffs)

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)                         # file -> dict
with open("out.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)                # dict -> file

json.dumps({"when": now}, default=str)          # convert unsupported types (datetime) to str
```

`requests` / `httpx`: `response.json()` parses the body for you. pandas: `pd.read_json`, `pd.json_normalize(nested)` flattens nested JSON into a table.

## 3. JSON on the Command Line (jq)

> `jq` is a small tool to pretty-print, filter and transform JSON in the terminal. Pipe JSON into `jq` with a filter expression.
>
> Use it for inspecting API responses from curl, extracting fields in scripts.

```bash
curl -s https://api.github.com/repos/python/cpython | jq .              # pretty print
curl -s ... | jq '.stargazers_count'                                     # one field
jq '.items[] | {name, price}' data.json                                   # reshape each item
jq '.items[] | select(.price > 10) | .name' data.json                     # filter
jq -r '.name' data.json                                                   # raw string (no quotes)
```

Install: `winget install jqlang.jq` / `sudo apt install jq`. PowerShell alternative: `Get-Content data.json | ConvertFrom-Json`.

## 4. JSON Lines (JSONL)

> One JSON object per line, no surrounding list. Each line is parsed independently, so files can be streamed and appended.
>
> Use it for datasets for fine-tuning and evals, logs, batch API inputs and outputs.

```text
{"prompt": "What is 2+2?", "answer": "4"}
{"prompt": "Capital of France?", "answer": "Paris"}
```

```python
with open("data.jsonl", encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

with open("out.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(row) + "\n")

df = pd.read_json("data.jsonl", lines=True)
```

## 5. JSON Schema

> A JSON document that describes what valid JSON looks like (types, required fields, allowed values). Tools validate data against the schema; LLM APIs use it to define tool inputs and structured outputs.
>
> Use it for tool definitions for LLMs, API contracts, validating config files.

```json
{
  "type": "object",
  "properties": {
    "city": {"type": "string", "description": "City name"},
    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
    "days": {"type": "integer", "minimum": 1, "maximum": 7}
  },
  "required": ["city"],
  "additionalProperties": false
}
```

In Python you rarely write schemas by hand: a Pydantic model generates one with `Model.model_json_schema()` (see [12 - Pydantic](12_pydantic.md)).

## 6. YAML Syntax

> The rules for writing YAML config files. Indentation (spaces only, usually 2) creates nesting; `key: value` for mappings, `- item` for lists; `#` for comments.
>
> Use it for Docker Compose, GitHub Actions, Kubernetes manifests, app and agent configs.

```yaml
# Application config
name: sales-api
version: 2
active: true
owner: null
tags:
  - api
  - ml
limits:
  requests_per_minute: 60
  max_tokens: 4096
models:
  - id: small
    cost: 0.5
  - id: large
    cost: 2.0
inline_list: [a, b, c]            # flow style, like JSON
inline_map: {x: 1, y: 2}
quoted: "yes"                     # quote to keep as a string
version_string: "3.10"            # without quotes 3.10 becomes the number 3.1
```

| Gotcha | Explanation |
|---|---|
| Tabs | Not allowed; use spaces |
| `yes`, `no`, `on`, `off` | May be read as booleans by some parsers; quote them |
| `3.10` | Becomes float 3.1; quote versions |
| Colon + space inside values | Quote strings containing a colon followed by a space, or starting with `*`, `&`, `!`, `@`, `` ` `` |
| Indentation | Children must be indented more than their parent, consistently |

## 7. YAML Multi-line Strings, Anchors, Multiple Documents

> YAML features for long text, reuse and several documents per file. `|` keeps line breaks, `>` folds lines; `&name` defines an anchor, `*name` reuses it; `---` separates documents.
>
> Use it for prompts inside config, shell scripts in CI steps, Kubernetes files with several resources.

```yaml
system_prompt: |
  You are a helpful assistant.
  Answer in short sentences.
summary: >
  This long line
  becomes one line.

defaults: &defaults
  retries: 3
  timeout: 30
service_a:
  <<: *defaults            # merge the anchor
  timeout: 60              # override one key
---
kind: Service              # second document in the same file
```

## 8. YAML in Python

> Reading and writing YAML from Python. Install PyYAML; always use `safe_load` (plain `load` can execute code from untrusted files).
>
> Use it for loading app / prompt / agent configs.

```powershell
pip install pyyaml
```

```python
import yaml

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)                  # -> dict
config["limits"]["max_tokens"]

with open("out.yaml", "w", encoding="utf-8") as f:
    yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)

docs = list(yaml.safe_load_all(open("multi.yaml", encoding="utf-8")))   # several documents
```

## 9. TOML Syntax

> A config format with `[sections]` and `key = value` lines. Explicit types, no indentation rules; `[a.b]` for nested tables, `[[items]]` for lists of tables.
>
> Use it for `pyproject.toml`, Ruff / pytest / uv settings, simple app configs.

```toml
# pyproject.toml
[project]
name = "sales-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["fastapi>=0.115", "pandas>=2.2"]

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]

[[models]]                 # list of tables
id = "small"
cost = 0.5

[[models]]
id = "large"
cost = 2.0
```

## 10. TOML in Python

> Reading TOML (built in since Python 3.11). `tomllib` reads; use the `tomli-w` package to write.
>
> Use it for reading project settings or your own TOML config.

```python
import tomllib

with open("pyproject.toml", "rb") as f:        # binary mode is required
    data = tomllib.load(f)
data["project"]["dependencies"]
```

## 11. .env Files

> A file of `KEY=value` lines that become environment variables for your app. `python-dotenv` or `pydantic-settings` loads it at startup; `os.getenv` reads the values.
>
> Use it for API keys, database URLs, model names that differ per machine. Never commit it.

```text
# .env  (add ".env" to .gitignore!)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@localhost:5432/app
LLM_MODEL=claude-opus-5
DEBUG=false
```

```python
import os

from dotenv import load_dotenv

load_dotenv()                                   # reads .env into os.environ
api_key = os.getenv("ANTHROPIC_API_KEY")
debug = os.getenv("DEBUG", "false").lower() == "true"   # everything is a string
```

Commit a `.env.example` with the key names and fake values so others know what to set.

## 12. Which Format When

> Choosing the right format. Match the audience: machines -> JSON; humans editing config -> YAML / TOML; secrets -> `.env`.
>
> Use it for designing a new config file or data export.

| Need | Format |
|---|---|
| API request / response | JSON |
| Dataset of records, logs, eval sets | JSONL |
| Python project metadata and tool config | TOML (`pyproject.toml`) |
| CI/CD, Compose, Kubernetes, complex app config | YAML |
| Secrets and per-machine settings | `.env` (local) / Key Vault (production) |
| Tabular data | CSV / Parquet (see [17 - Pandas](17_pandas.md)) |

## 13. Troubleshooting

| Error | Fix |
|---|---|
| `json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes` | Single quotes or trailing comma; use valid JSON (`json.dumps`, not `str(dict)`) |
| `Object of type datetime is not JSON serializable` | `json.dumps(obj, default=str)` or convert first |
| LLM returns JSON wrapped in text / code fences | Use structured outputs (see [26 - LLM APIs](26_llm-apis.md)) or strip the fences before `json.loads` |
| `yaml.scanner.ScannerError: mapping values are not allowed here` | A value contains a colon followed by a space; quote it |
| `found character '\t' that cannot start any token` | Tabs in YAML; replace with spaces |
| YAML value is a bool / float instead of string | Quote it: `"yes"`, `"3.10"` |
| `TypeError: File must be opened in binary mode` (tomllib) | `open(path, "rb")` |
| `os.getenv` returns `None` | `.env` not loaded, wrong working directory, or typo in the key |

## 14. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: JSON to YAML

Convert `config.json` to `config.yaml` in Python.

<details markdown="1">
<summary>Solution</summary>

```python
import json
import yaml

with open("config.json", encoding="utf-8") as f:
    data = json.load(f)
with open("config.yaml", "w", encoding="utf-8") as f:
    yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
```

</details>

### Exercise 2: Fix invalid JSON

Make this valid JSON: `{'name': 'x', 'tags': ['a',],}`

<details markdown="1">
<summary>Solution</summary>

```json
{"name": "x", "tags": ["a"]}
```

Double quotes only, no trailing commas.

</details>

### Exercise 3: The 3.10 surprise

Why does `python: 3.10` in YAML load as `3.1`, and how do you fix it?

<details markdown="1">
<summary>Solution</summary>

Unquoted `3.10` is parsed as the number 3.10, which equals 3.1. Quote it: `python: "3.10"`. Same for `yes` / `no` / `on` / `off` when you mean strings.

</details>

---

<!-- nav:start -->
**Previous:** [06 - Regex](06_regex.md) | **Index:** [All guides](README.md) | **Next:** [08 - HTTP and APIs](08_http-apis.md)
<!-- nav:end -->
