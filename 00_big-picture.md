# 00 - Big Picture: How Everything Connects

<!-- nav:start -->
**Index:** [All guides](README.md) | **Next:** [01 - Markdown](01_markdown.md)
<!-- nav:end -->

Start here. This guide is the map of the whole pocket guide: how the tools fit together, how a request travels through a real AI application, how code goes from your laptop to production, and which guide to open for any question.

## Contents

1. [How to Use This Pocket Guide](#1-how-to-use-this-pocket-guide)
2. [The Map: Layers of the Stack](#2-the-map-layers-of-the-stack)
3. [Journey of One Request Through an AI App](#3-journey-of-one-request-through-an-ai-app)
4. [From Idea to Production (Development Lifecycle)](#4-from-idea-to-production-development-lifecycle)
5. [The Data and ML Lifecycle](#5-the-data-and-ml-lifecycle)
6. [The AI Application Ladder](#6-the-ai-application-ladder)
7. [Where Code Runs](#7-where-code-runs)
8. [Which Tool for Which Job](#8-which-tool-for-which-job)
9. [How the Pieces Talk to Each Other](#9-how-the-pieces-talk-to-each-other)
10. [Learning Paths](#10-learning-paths)
11. ["I Want To..." Quick Finder](#11-i-want-to-quick-finder)
12. [Core Mental Models in One Page](#12-core-mental-models-in-one-page)
13. [Windows, macOS and Linux Differences](#13-windows-macos-and-linux-differences)
14. [Practice and Extras](#14-practice-and-extras)

---

## 1. How to Use This Pocket Guide

> How the guides are organised. Numbered from basic to advanced; every guide has the same structure. Use it on your first visit, or when you are not sure where to look.

Every guide follows the same layout:

```text
# NN - Topic
Introduction      what it is, WHY it exists, a mental model diagram, key terms, where it fits
  Official docs   links to the official home pages for the latest, authoritative information
Contents          numbered sections
0. Flags and Parameters   how commands / calls are built, every flag explained (where relevant)
1..N. Sections    each opens with a short summary (what, how, when to use it), then commands with comments
Troubleshooting   common errors and fixes
```

Reading strategy:

- **Learning a topic**: read the Introduction and mental model first, then skim section titles, then try the examples.
- **Looking something up**: use the Contents list or section 11 of this page.
- **Debugging**: jump to the Troubleshooting table at the end of the relevant guide.
- **Need the very latest details** (new versions, changed APIs, current model names): open the **Official docs** table at the end of each guide's Introduction.

## 2. The Map: Layers of the Stack

> Every guide placed in the layer of the stack it belongs to. Lower layers are foundations used by everything above them. Use it for seeing how a topic relates to the rest.

```text
+--------------------------------------------------------------------------------------------+
|  CLOUD & OPERATIONS     47 Azure  48 Azure VM+Ollama  46 Terraform  45 Kubernetes           |
|                         44 Nginx/HTTPS  43 GitHub Actions (CI/CD)                           |
+--------------------------------------------------------------------------------------------+
|  PACKAGING & SERVING    42 Docker  41 Redis/Queues  40 Uvicorn  39 FastAPI  38 AI UIs       |
+--------------------------------------------------------------------------------------------+
|  AI ENGINEERING         31 Agents  32 Frameworks  33 MCP  34 Evals/Observability  37 Security|
|                         30 RAG  29 Embeddings/Vector DBs  28 Tool Use  27 Prompting         |
|                         26 LLM APIs  25 LLM Fundamentals  35 Local LLMs  36 Fine-tuning     |
+--------------------------------------------------------------------------------------------+
|  DATA & ML              22 Scikit-learn  23 PyTorch  24 Hugging Face                        |
|                         20 Matplotlib  21 Seaborn  19 SQL  18 Polars/DuckDB  17 Pandas  16 NumPy |
+--------------------------------------------------------------------------------------------+
|  PYTHON                 09 Basics  10 venv  11 uv  12 Pydantic  13 Async  14 pytest  15 Jupyter|
+--------------------------------------------------------------------------------------------+
|  FOUNDATIONS            01 Markdown  02 Terminal/PowerShell  03 Linux  04 Git  05 VS Code    |
|                         06 Regex  07 YAML/JSON  08 HTTP/APIs                                |
+--------------------------------------------------------------------------------------------+
```

## 3. Journey of One Request Through an AI App

> What happens, step by step, when a user asks a question in a production AI assistant. Each step names the technology and the guide that explains it. Use it for understanding how all the pieces work together in one system.

```text
 USER: "What is our refund policy for jackets, and has my order A-1042 shipped?"
   |
   | 1. Browser / chat UI sends HTTPS POST /chat                      [38 AI UIs] [08 HTTP]
   v
 2. Nginx / cloud ingress: TLS, routing, rate limit                   [44 Nginx] [47 Azure] [45 K8s]
   v
 3. Uvicorn (ASGI server) receives the HTTP request, hands it to the app [40 Uvicorn]
   v
    FastAPI endpoint: auth, Pydantic validation of the JSON body      [39 FastAPI] [12 Pydantic]
   v
 4. Redis: rate limit per user, check cache for identical question    [41 Redis]
   v
 5. Agent / orchestration code decides what context is needed          [31 Agents] [32 Frameworks]
   |
   +--> 6a. RAG: embed the question, search the vector DB for policy chunks,
   |        rerank, keep top 5 (filtered by the user's permissions)   [29 Embeddings] [30 RAG]
   |
   +--> 6b. Tool: get_order_status("A-1042") -> SQL / internal API    [28 Tool Use] [19 SQL] [33 MCP]
   v
 7. Prompt built: system prompt + policy chunks + tool result + question
                                                                      [27 Prompting]
   v
 8. LLM API call (streamed), e.g. Claude via the anthropic SDK        [26 LLM APIs] [25 Fundamentals]
    (or a self-hosted model on a GPU VM via Ollama / vLLM)            [35 Local LLMs] [48 Azure VM]
   v
 9. Output checks: structured output validation, guardrails, citations [37 Security] [12 Pydantic]
   v
10. Stream tokens back to the browser (SSE)                           [08 HTTP] [39 FastAPI] [38 UIs]
   v
11. Log trace: prompt version, chunks, tool calls, tokens, cost, latency; user feedback
                                                                      [34 Evals/Observability]
   v
 USER sees: "Jackets can be returned within 30 days [1]. Your order A-1042 shipped and
             should arrive on Sept 30."

 Behind the scenes:
  - Documents were indexed earlier by a background worker            [41 Queues] [30 RAG]
  - Everything runs in Docker containers                              [42 Docker]
  - Built and deployed automatically on every merge                   [43 GitHub Actions] [04 Git]
  - Cloud resources defined as code                                   [46 Terraform] [47 Azure]
  - Nightly evals check quality didn't regress                        [34 Evals] [14 pytest]
```

## 4. From Idea to Production (Development Lifecycle)

> The path a project takes from a quick experiment to a running service. Each stage adds structure, safety and automation. Use it for planning a project; knowing what to learn next.

```text
 1. EXPLORE        Jupyter notebook, pandas, quick LLM calls             [15] [17] [26]
      |
 2. SCRIPT         Move working code to .py files, functions, logging     [09] [05 VS Code]
      |
 3. PROJECT        uv / venv, pyproject.toml, Git repo, .gitignore       [11] [10] [04] [07]
      |
 4. QUALITY        Type hints + Pydantic, pytest, Ruff, evals            [12] [14] [34]
      |
 5. SERVICE        FastAPI API on Uvicorn, async, settings from env, jobs  [39] [40] [13] [41]
      |
 6. CONTAINER      Dockerfile, Compose (app + DB + Redis)                [42]
      |
 7. AUTOMATE       GitHub Actions: test, eval, build image on every push  [43]
      |
 8. DEPLOY         Azure Container Apps / App Service / VM + Nginx / AKS  [47] [44] [45] [48]
      |            Infrastructure as code                                 [46]
      |
 9. OPERATE        Tracing, cost dashboards, alerts, feedback -> new evals [34] [37]
      |
      +---------- feedback loop: production issues become tests / eval cases ----------+
```

## 5. The Data and ML Lifecycle

> The typical flow of a data science / ML project. Each step maps to tools in this guide. Use it for data analysis and classic ML work.

```text
 COLLECT    SQL, APIs, files (CSV, Parquet, JSON)             [19] [08] [07] [18]
    v
 CLEAN      pandas / Polars: missing values, types, dedupe     [17] [18] [06 Regex]
    v
 EXPLORE    stats, groupby, charts                             [16] [17] [20] [21] [15]
    v
 FEATURES   encoding, scaling, embeddings of text              [22] [29]
    v
 MODEL      scikit-learn (tabular), PyTorch / HF (text, images) [22] [23] [24]
    v
 EVALUATE   cross-validation, metrics, error analysis          [22] [34]
    v
 SERVE      save model -> FastAPI endpoint -> Docker -> cloud   [22] [39] [42] [47]
    v
 MONITOR    data drift, performance, retraining schedule        [34] [43] [41]
```

## 6. The AI Application Ladder

> The levels of sophistication in LLM applications. Climb only as high as your problem requires; each level adds cost and complexity. Use it for designing an AI feature.

```text
 Level 6  MULTI-AGENT SYSTEMS    orchestrator + specialised agents          [31] [32]
 Level 5  AGENTS                 model decides steps in a loop with tools   [31] [28] [33]
 Level 4  RAG                    retrieve your documents, answer from them  [30] [29]
 Level 3  TOOLS / WORKFLOWS      fixed chains, routing, function calling    [28] [27]
 Level 2  STRUCTURED OUTPUT      extraction / classification into schemas   [26] [12]
 Level 1  SINGLE PROMPT          one well-written prompt, one call          [27] [26]
 Level 0  UNDERSTAND THE MODEL   tokens, context, cost, limits              [25]

 Cross-cutting at every level: evals [34], security [37], cost / latency [25] [26]
 Model choice at every level: hosted API [26] vs local [35] vs fine-tuned [36]
```

## 7. Where Code Runs

> The places your code can execute, from laptop to managed cloud. Moving right means less to manage but less control. Use it for choosing a deployment target.

```text
 YOUR LAPTOP        VIRTUAL MACHINE       CONTAINER PLATFORM        KUBERNETES           SERVERLESS / PaaS
 python app.py      Azure VM + SSH        Docker on a VM            AKS cluster          Container Apps,
 Jupyter            systemd + Nginx       Compose stacks            pods, services,      App Service,
 Ollama locally     GPU for LLMs          Container Apps            autoscaling          Functions
 [09][15][35]       [03][44][48]          [42][47]                  [45]                 [47]
 ------------------------------------------------------------------------------------------------>
 full control, you manage everything                               less to manage, less control
```

## 8. Which Tool for Which Job

> A one-table tech stack cheat sheet. Find the job, use the tool, open the guide. Use it for choosing tools for a new project.

| Job | Default choice | Alternatives | Guide |
|---|---|---|---|
| Write code | VS Code | PyCharm, Jupyter | [05](05_vscode.md) |
| Version control | Git + GitHub | GitLab, Azure DevOps | [04](04_git.md) |
| Python environments / deps | uv | venv + pip, conda | [11](11_uv.md), [10](10_python-virtual-environment.md) |
| Data validation / config | Pydantic, pydantic-settings | dataclasses | [12](12_pydantic.md) |
| Tests | pytest | unittest | [14](14_pytest.md) |
| Tabular data | pandas | Polars, DuckDB | [17](17_pandas.md), [18](18_polars-duckdb.md) |
| Relational database | PostgreSQL | SQLite (local), Azure SQL | [19](19_sql.md) |
| Charts | Matplotlib + Seaborn | Plotly | [20](20_matplotlib.md), [21](21_seaborn.md) |
| Classic ML | scikit-learn | XGBoost, LightGBM | [22](22_scikit-learn.md) |
| Deep learning | PyTorch | JAX | [23](23_pytorch.md) |
| Pretrained open models | Hugging Face | | [24](24_hugging-face.md) |
| Hosted LLM | Claude API | OpenAI, Azure OpenAI, Gemini | [26](26_llm-apis.md) |
| Local LLM | Ollama | llama.cpp, LM Studio, vLLM | [35](35_local-llms.md) |
| Embeddings | sentence-transformers / bge-m3 | OpenAI, Voyage | [29](29_embeddings-vector-db.md) |
| Vector store | Chroma (prototype), pgvector / Qdrant (prod) | Azure AI Search, Pinecone | [29](29_embeddings-vector-db.md) |
| Agent framework | Raw SDK / Claude Agent SDK | LangGraph, OpenAI Agents SDK, PydanticAI | [31](31_ai-agents.md), [32](32_agent-frameworks.md) |
| Tool integration standard | MCP | | [33](33_mcp.md) |
| Evals / tracing | pytest + scripts, Langfuse | promptfoo, LangSmith, Phoenix | [34](34_evals-observability.md) |
| Demo UI | Streamlit | Gradio, Chainlit | [38](38_ai-ui.md) |
| API | FastAPI | Flask, Django | [39](39_fastapi.md) |
| ASGI server (runs the API) | Uvicorn | Gunicorn + Uvicorn workers, Hypercorn, Granian | [40](40_uvicorn.md) |
| Cache / queue | Redis + RQ / Celery / arq | RabbitMQ | [41](41_redis-queues.md) |
| Containers | Docker + Compose | Podman | [42](42_docker.md) |
| CI/CD | GitHub Actions | Azure DevOps, GitLab CI | [43](43_github-actions.md) |
| HTTPS / reverse proxy | Nginx + certbot | Caddy, Traefik | [44](44_nginx-https.md) |
| Orchestration | Azure Container Apps | Kubernetes (AKS) | [47](47_azure.md), [45](45_kubernetes.md) |
| Infrastructure as code | Terraform | Bicep, Pulumi | [46](46_terraform.md) |
| Cloud | Azure | AWS, GCP | [47](47_azure.md) |

## 9. How the Pieces Talk to Each Other

> The few "languages" that connect every component. Almost all communication is HTTP + JSON, configured through environment variables and YAML / TOML files. Use it for understanding integration and debugging connections.

```text
 WHAT FLOWS BETWEEN COMPONENTS          HOW                          GUIDE
 ----------------------------------     --------------------------   ----------------
 Requests / responses                   HTTP(S) + JSON               [08] [07]
 Streaming tokens                       SSE / WebSockets             [08] [38] [44]
 Data shapes and validation             JSON Schema / Pydantic       [07] [12]
 Configuration                          env vars, .env, YAML, TOML   [07] [11]
 Secrets                                env vars -> Key Vault        [07] [47] [37]
 Tools for AI                           tool schemas / MCP           [28] [33]
 Background work                        Redis queues                 [41]
 Code and infra changes                 Git commits -> CI pipelines  [04] [43]
 Packaged apps                          Docker images in a registry  [42] [47]
 Infrastructure                         Terraform / Bicep files      [46] [47]
```

## 10. Learning Paths

> Suggested orders for reading the guides, depending on your goal. Each path builds on the previous steps; practise with a small project at each stage. Use it for planning your learning.

### Path A: Foundations (everyone, first)

```text
02 Terminal -> 04 Git -> 05 VS Code -> 09 Python -> 11 uv (or 10 venv) -> 01 Markdown -> 07 YAML/JSON
Project: a small Python CLI tool in a GitHub repo with a README
```

### Path B: Data Analyst

```text
Path A -> 15 Jupyter -> 16 NumPy -> 17 Pandas -> 19 SQL -> 20 Matplotlib -> 21 Seaborn -> 18 Polars/DuckDB
Project: analyse a public dataset, publish a notebook + charts
```

### Path C: Machine Learning

```text
Path B -> 22 Scikit-learn -> 12 Pydantic -> 14 pytest -> 39 FastAPI -> 40 Uvicorn -> 42 Docker -> 23 PyTorch -> 24 Hugging Face
Project: train a model, serve it with FastAPI in Docker
```

### Path D: AI Engineer (LLM apps and agents)

```text
Path A -> 08 HTTP -> 12 Pydantic -> 13 Async -> 25 LLM Fundamentals -> 26 LLM APIs -> 27 Prompting
       -> 28 Tool Use -> 29 Embeddings -> 30 RAG -> 38 AI UIs -> 34 Evals -> 37 Security
       -> 31 Agents -> 32 Frameworks -> 33 MCP -> 35 Local LLMs -> 36 Fine-tuning (optional)
Project: RAG chatbot over your own documents with citations, evals and a Streamlit UI
```

### Path E: Deployment and MLOps / LLMOps

```text
Path A -> 03 Linux -> 39 FastAPI -> 40 Uvicorn -> 41 Redis/Queues -> 42 Docker -> 43 GitHub Actions
       -> 47 Azure -> 44 Nginx/HTTPS -> 48 Azure VM + Ollama -> 46 Terraform -> 45 Kubernetes
Project: deploy your RAG app with CI/CD to Azure Container Apps, infra in Terraform
```

## 11. "I Want To..." Quick Finder

> Common tasks mapped to the right guide and section. Find your task, open the guide. Use it for looking something up fast.

| I want to ... | Go to |
|---|---|
| Undo my last commit / fix a mistake in Git | [04 - Git](04_git.md), section 11 |
| Find what uses port 8000 | [02 - Terminal](02_terminal-powershell.md), section 13 |
| Set up a new Python project | [11 - uv](11_uv.md), section 4 |
| Keep API keys out of my code | [07 - .env](07_yaml-json.md), section 11; [37 - Security](37_ai-security.md), section 11 |
| Validate JSON input / LLM output | [12 - Pydantic](12_pydantic.md) |
| Call 100 LLM requests in parallel | [13 - Async](13_async-python.md), section 10 |
| Test code that calls an LLM | [14 - pytest](14_pytest.md), section 11 |
| Clean and group a dataset | [17 - Pandas](17_pandas.md) |
| Query big CSV / Parquet files with SQL | [18 - Polars and DuckDB](18_polars-duckdb.md), section 12 |
| Train and evaluate a classifier | [22 - Scikit-learn](22_scikit-learn.md) |
| Understand tokens, context windows, costs | [25 - LLM Fundamentals](25_llm-fundamentals.md) |
| Call Claude / stream / get JSON back | [26 - LLM APIs](26_llm-apis.md) |
| Write a better prompt | [27 - Prompt Engineering](27_prompt-engineering.md) |
| Let the model call my functions | [28 - Tool Use](28_tool-use.md) |
| Build "chat with my documents" | [30 - RAG](30_rag.md) |
| Build an agent | [31 - AI Agents](31_ai-agents.md) |
| Connect my tools to Claude Code / Desktop | [33 - MCP](33_mcp.md) |
| Measure if my prompt change helped | [34 - Evals](34_evals-observability.md) |
| Run an LLM on my own machine | [35 - Local LLMs](35_local-llms.md) |
| Protect my app from prompt injection | [37 - AI Security](37_ai-security.md), sections 2-3 |
| Make a chat UI quickly | [38 - AI UIs](38_ai-ui.md), section 3 |
| Build an API for my model | [39 - FastAPI](39_fastapi.md) |
| Run my API in production (workers, proxy headers, timeouts) | [40 - Uvicorn](40_uvicorn.md) |
| Run slow jobs in the background | [41 - Redis and Queues](41_redis-queues.md) |
| Package my app in a container | [42 - Docker](42_docker.md) |
| Run tests automatically on every push | [43 - GitHub Actions](43_github-actions.md) |
| Put my app on a domain with HTTPS | [44 - Nginx and HTTPS](44_nginx-https.md) |
| Deploy a container to Azure | [47 - Azure](47_azure.md), section 23 |
| Run an LLM on a cloud GPU VM | [48 - Azure VM + Ollama](48_azure-vm-ollama.md) |

## 12. Core Mental Models in One Page

> The handful of ideas that explain most of this guide. One line each; the linked guide has the full picture. Use it for quick revision.

| Concept | Mental model | Guide |
|---|---|---|
| Shell | You type commands; programs read files and print text; pipes connect them | [02](02_terminal-powershell.md), [03](03_linux.md) |
| Git | A timeline of snapshots; branches are parallel timelines you can merge | [04](04_git.md) |
| Virtual environment | A private box of packages per project | [10](10_python-virtual-environment.md), [11](11_uv.md) |
| HTTP | Method + URL + headers + body -> status + headers + body | [08](08_http-apis.md) |
| JSON / YAML | Nested dicts and lists written as text | [07](07_yaml-json.md) |
| Pydantic | Customs checkpoint: validate once at the border, trust inside | [12](12_pydantic.md) |
| Async | One chef switching dishes while each one waits | [13](13_async-python.md) |
| DataFrame | A table where you operate on whole columns, not loops | [17](17_pandas.md) |
| ML model | Learns a function from examples; judged on data it never saw | [22](22_scikit-learn.md) |
| Neural network training | Guess -> measure error -> nudge weights -> repeat | [23](23_pytorch.md) |
| LLM | Autocomplete that predicts the next token from everything in its context | [25](25_llm-fundamentals.md) |
| Prompt | A brief for a brilliant new colleague who knows nothing about your project | [27](27_prompt-engineering.md) |
| Tool use | The model is the brain, your code is the hands | [28](28_tool-use.md) |
| Embeddings | A map of meaning: similar texts are close together | [29](29_embeddings-vector-db.md) |
| RAG | An open-book exam: retrieve the right pages, answer from them | [30](30_rag.md) |
| Agent | An LLM in a loop: think -> act with tools -> observe -> repeat until done | [31](31_ai-agents.md) |
| MCP | USB-C for AI: one standard plug between AI apps and tools | [33](33_mcp.md) |
| Evals | Unit tests for AI behaviour, scored instead of exact | [34](34_evals-observability.md) |
| Prompt injection | Untrusted text is read like instructions; limit what damage it can do | [37](37_ai-security.md) |
| ASGI server | The engine that speaks HTTP and hands each request to your async app | [40](40_uvicorn.md) |
| Container | App + everything it needs, runs the same everywhere | [42](42_docker.md) |
| CI/CD | Every push triggers automatic checks, builds and deployments | [43](43_github-actions.md) |
| Reverse proxy | A doorman in front of your apps handling HTTPS and routing | [44](44_nginx-https.md) |
| Kubernetes | Declare the desired state; controllers keep reality matching it | [45](45_kubernetes.md) |
| Infrastructure as code | Cloud resources described in files, planned then applied | [46](46_terraform.md) |
| Cloud | Rent computers and services by the hour; pay for what runs | [47](47_azure.md) |

## 13. Windows, macOS and Linux Differences

> The places where commands in these guides differ between operating systems. Most guides show Windows (PowerShell) and Linux / macOS (Bash) side by side; this table collects the differences you meet most. Use it for a command from a guide or tutorial fails on your machine.

| Topic | Windows (PowerShell) | macOS | Linux (Ubuntu) |
|---|---|---|---|
| Shell | PowerShell (also CMD, Git Bash, WSL) | zsh (Bash-like) | Bash |
| Path separator | `D:\Projects\app` (Python also accepts `/`) | `/Users/me/app` | `/home/me/app` |
| Home folder | `$HOME` = `C:\Users\me` | `~` = `/Users/me` | `~` = `/home/me` |
| Activate venv | `.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` | `source .venv/bin/activate` |
| Python command | `python` / `py` | `python3` | `python3` |
| Set env var (session) | `$env:KEY = "v"` | `export KEY=v` | `export KEY=v` |
| Install software | `winget install ...` | `brew install ...` | `sudo apt install ...` |
| Line endings | CRLF (`\r\n`) | LF | LF |
| Script permission error | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` | `chmod +x script.sh` | `chmod +x script.sh` |
| Find what uses a port | `Get-NetTCPConnection -LocalPort 8000` | `lsof -i :8000` | `ss -tulpn` / `lsof -i :8000` |
| curl | Use `curl.exe` (in PS 5.1 `curl` is an alias) | `curl` | `curl` |
| Docker | Docker Desktop (WSL 2 backend) | Docker Desktop | Docker Engine |
| NVIDIA GPU / CUDA | Supported (drivers + CUDA build of PyTorch) | No CUDA; Apple GPU via `mps` | Supported (best for servers) |
| uvloop / Gunicorn | Not available (Uvicorn falls back to asyncio) | Available | Available |
| Celery workers | Development only with `--pool=solo` | Available | Available |
| Redis server | Docker or WSL | Docker / `brew install redis` | `apt install redis-server` / Docker |

Tips:

- **WSL** (Windows Subsystem for Linux) gives you a real Ubuntu on Windows; Linux-only tools (Gunicorn, uvloop, vLLM) work there ([03 - Linux](03_linux.md)).
- Git on Windows: `git config --global core.autocrlf true` handles line endings; shell scripts for Linux must keep LF endings.
- Quoting JSON in commands differs: in PowerShell prefer `Invoke-RestMethod` with `ConvertTo-Json` ([08 - HTTP and APIs](08_http-apis.md) section 9).

## 14. Practice and Extras

> Pages that help you practise and look things up. Exercises at the end of every guide, runnable examples, a capstone project, a glossary and a one-page command summary. Use it after reading a guide (practise), when building your portfolio (capstone), when you only need a command (quick reference).

| Resource | What it gives you |
|---|---|
| "Try It" section at the end of every guide | 3 to 5 exercises with hidden solutions |
| [examples/](examples/README.md) | Runnable mini-projects: LLM basics, tool-using agent, RAG API, MCP server |
| [97 - Capstone Project](97_capstone-project.md) | Build, test, containerise, automate and deploy a document chatbot, step by step |
| [98 - Glossary](98_glossary.md) | Every key term A to Z, linked to its guide |
| [99 - Quick Reference](99_quick-reference.md) | The most-used commands of every guide on one page |

---

<!-- nav:start -->
**Index:** [All guides](README.md) | **Next:** [01 - Markdown](01_markdown.md)
<!-- nav:end -->
