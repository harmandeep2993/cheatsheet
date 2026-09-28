# pocket-guide

A complete pocket guide for data, AI and deployment work: from the terminal and Git to LLM apps, agents and cloud deployment. Numbered from basic to advanced; every guide explains **what** a tool is, **why** it exists, **how** it works (with mental-model diagrams) and **when** to use each command.

**New here? Start with [00 - Big Picture](guides/00_big-picture.md)** (how everything connects, the journey of a request through an AI app, learning paths), then **[01 - Core Concepts](guides/01_core-concepts.md)** (the basic vocabulary: packages, APIs, SDKs, configuration, reading errors).

## Start

| # | Guide | Covers |
|---|---|---|
| 00 | [Big Picture](guides/00_big-picture.md) | Map of the stack, request journey, dev lifecycle, learning paths, "I want to..." finder |
| 97 | [Capstone Project](guides/97_capstone-project.md) | Build, test, evaluate, containerise, automate and deploy a document chatbot, step by step |
| 98 | [Glossary](guides/98_glossary.md) | Every key term from all guides, A to Z, linked to its guide |
| 99 | [Quick Reference](guides/99_quick-reference.md) | The most-used commands of every guide on one page |

**Practice:** every guide ends with a **Try It** section (exercises with hidden solutions), and [examples/](examples/README.md) has runnable, tested mini-projects: LLM basics, a tool-using agent, a RAG chatbot API and an MCP server.

**Website:** the same content as a searchable site with dark mode: https://harmandeep2993.github.io/pocket-guide/

## Foundations

| # | Guide | Covers |
|---|---|---|
| 01 | [Core Concepts](guides/01_core-concepts.md) | Code and runtimes, terminal, paths, packages and dependencies, libraries vs frameworks, APIs, SDKs in depth, config and secrets, reading errors |
| 02 | [Markdown](guides/02_markdown.md) | Headings, formatting, lists, links, images, code, tables, anchors |
| 03 | [Terminal and PowerShell](guides/03_terminal-powershell.md) | Navigation, files, search, pipes, env vars, processes, network, winget, CMD/Bash equivalents |
| 04 | [Linux](guides/04_linux.md) | Navigation, files, grep/find, permissions, apt, processes, systemd, network, SSH, tar, cron |
| 05 | [Git and GitHub](guides/05_git.md) | Commit, branch, merge/rebase, conflicts, undo, stash, .gitignore, gh CLI, PR workflow |
| 06 | [VS Code](guides/06_vscode.md) | Shortcuts, multi-cursor, search, debugging, Python setup, Git, extensions, settings, remote |
| 07 | [Regex](guides/07_regex.md) | Classes, anchors, quantifiers, groups, lookarounds, common patterns, Python re, pandas, grep, SQL |
| 08 | [YAML, JSON, TOML and .env](guides/08_yaml-json.md) | Syntax, Python parsing, jq, JSONL, JSON Schema, config formats, secrets files |
| 09 | [HTTP and APIs](guides/09_http-apis.md) | Methods, status codes, headers, REST, auth, curl, requests/httpx, retries, rate limits, SSE, webhooks |

## Python

| # | Guide | Covers |
|---|---|---|
| 10 | [Python Basics](guides/10_python-basics.md) | Types, strings, f-strings, lists, dicts, loops, comprehensions, functions, errors, files, classes, logging |
| 11 | [Python Virtual Environment](guides/11_python-virtual-environment.md) | venv create/activate, pip, requirements.txt, VS Code, troubleshooting |
| 12 | [uv](guides/12_uv.md) | Projects, add/remove, run, lock/sync, Python versions, pip interface, uvx tools, Docker |
| 13 | [Pydantic](guides/13_pydantic.md) | Models, validation, constraints, validators, JSON Schema, settings, LLM structured output |
| 14 | [Async Python](guides/14_async-python.md) | async/await, gather, TaskGroup, semaphores, timeouts, async HTTP and LLM calls, queues |
| 15 | [pytest](guides/15_pytest.md) | Fixtures, parametrize, markers, mocking APIs and LLMs, FastAPI tests, coverage |
| 16 | [Jupyter](guides/16_jupyter.md) | Kernels from venv, shortcuts, magics, display options, autoreload, export, notebooks in Git |

## Data and Machine Learning

| # | Guide | Covers |
|---|---|---|
| 17 | [NumPy](guides/17_numpy.md) | Create arrays, indexing, filtering, reshape, math, broadcasting, axis, random, linear algebra |
| 18 | [Pandas](guides/18_pandas.md) | Read/write, inspect, select, filter, clean, groupby, pivot, merge |
| 19 | [Polars and DuckDB](guides/19_polars-duckdb.md) | Parquet, expressions, lazy mode, pandas translation, SQL on files and DataFrames |
| 20 | [SQL](guides/20_sql.md) | SELECT, WHERE, GROUP BY, JOINs, CTEs, window functions, DDL/DML, psql/sqlite3, SQL from pandas |
| 21 | [Matplotlib](guides/21_matplotlib.md) | Line, scatter, bar, hist, box, pie, labels, legend, subplots, styles, save |
| 22 | [Seaborn](guides/22_seaborn.md) | Distribution, categorical, relationship, regression, heatmap, pairplot, facets, palettes |
| 23 | [Scikit-learn](guides/23_scikit-learn.md) | Split, preprocessing, pipelines, models, metrics, cross-validation, tuning, saving models |
| 24 | [PyTorch](guides/24_pytorch.md) | Tensors, GPU, autograd, nn.Module, training loop, evaluation, saving, overfitting |
| 25 | [Hugging Face](guides/25_hugging-face.md) | Hub, pipelines, tokenizers, open LLMs, chat templates, quantization, embeddings, datasets |

## AI Engineering

| # | Guide | Covers |
|---|---|---|
| 26 | [LLM Fundamentals](guides/26_llm-fundamentals.md) | Tokens, next-token prediction, training, context, sampling, reasoning, hallucinations, cost, model choice |
| 27 | [LLM APIs](guides/27_llm-apis.md) | Claude SDK in depth, streaming, structured outputs, vision/PDF, thinking, caching, batches, OpenAI equivalents |
| 28 | [Prompt Engineering](guides/28_prompt-engineering.md) | Clarity, context, XML tags, examples, output formats, long docs, templates, chaining, checklist |
| 29 | [Tool Use](guides/29_tool-use.md) | Tool definitions, the tool loop, tool runner, parallel calls, errors, server tools, tool design, safety |
| 30 | [Embeddings and Vector DBs](guides/30_embeddings-vector-db.md) | Embedding models, similarity, ANN/HNSW, FAISS, Chroma, pgvector, Qdrant, hybrid search |
| 31 | [RAG](guides/31_rag.md) | Loading, chunking, retrieval, reranking, citations, contextual/agentic RAG, evaluation, security |
| 32 | [AI Agents](guides/32_ai-agents.md) | Agent loop, workflows vs agents, patterns, memory, planning, multi-agent, human-in-the-loop, limits |
| 33 | [Agent Frameworks](guides/33_agent-frameworks.md) | Claude Agent SDK, OpenAI Agents SDK, LangChain/LangGraph, LlamaIndex, PydanticAI, CrewAI, choosing |
| 34 | [MCP](guides/34_mcp.md) | Model Context Protocol: architecture, Python servers, Claude Code/Desktop/VS Code, clients, security |
| 35 | [Evals and Observability](guides/35_evals-observability.md) | Eval sets, graders, LLM-as-judge, CI evals, tracing, logging, cost monitoring, feedback |
| 36 | [Local LLMs](guides/36_local-llms.md) | Ollama in depth, hardware sizing, quantization, llama.cpp, LM Studio, vLLM, Docker |
| 37 | [Fine-tuning](guides/37_fine-tuning.md) | When to fine-tune, LoRA/QLoRA, datasets, TRL training, evaluation, GGUF export, DPO, hosted options |
| 38 | [AI Security](guides/38_ai-security.md) | OWASP LLM Top 10, prompt injection, excessive agency, data leakage, guardrails, regulation, red teaming |
| 39 | [AI UIs](guides/39_ai-ui.md) | Streamlit, Gradio, Chainlit chat apps, streaming, state, secrets, FastAPI frontend, deployment |

## APIs and Deployment

| # | Guide | Covers |
|---|---|---|
| 40 | [FastAPI](guides/40_fastapi.md) | Routes, Pydantic validation, dependencies, settings, routers, testing, ML model API, Docker |
| 41 | [Uvicorn](guides/41_uvicorn.md) | ASGI server: running apps, reload, workers, Gunicorn, proxy headers, HTTPS, timeouts, logging, Docker, systemd |
| 42 | [Redis and Task Queues](guides/42_redis-queues.md) | Caching, LLM response cache, rate limiting, sessions, RQ, Celery, arq, job status pattern |
| 43 | [Docker](guides/43_docker.md) | Images, containers, run options, Dockerfile, volumes, networks, Compose, cleanup, registry |
| 44 | [GitHub Actions](guides/44_github-actions.md) | Workflows, triggers, Python CI with uv, secrets, caching, evals in CI, Docker builds, Azure OIDC deploy |
| 45 | [Nginx and HTTPS](guides/45_nginx-https.md) | Reverse proxy, Let's Encrypt, streaming/WebSockets, basic auth, rate limits, systemd, Caddy |
| 46 | [Kubernetes](guides/46_kubernetes.md) | Pods, Deployments, Services, Ingress, config, probes, scaling, rollouts, GPUs, Helm, AKS |
| 47 | [Terraform](guides/47_terraform.md) | HCL, providers, resources, variables, state, modules, environments, Azure example, CI/CD |
| 48 | [Azure](guides/48_azure.md) | Concepts, CLI, resource groups, VMs, storage, ACR, Container Apps, App Service, Key Vault, databases, RBAC, Azure OpenAI, cost, Bicep |
| 49 | [Azure VM + Linux + Ollama](guides/49_azure-vm-ollama.md) | Azure CLI, VM, NSG, SSH, Linux basics, Ollama, SSH tunnel |
| 50 | [Project Structure](guides/50_project-structure.md) | Monorepo for Python microservices in Docker + React frontend: layers, uv workspace, proxy, config, Compose, tests, CI, deploy (with a runnable starter) |
| 51 | [Project Templates](guides/51_project-templates.md) | When to make a template, GitHub template repos, Copier (questions, placeholders, update), Cookiecutter, testing templates in CI |

## What's in This Repository

```text
pocket-guide/
  README.md                  this page: the index of all guides
  guides/                    every guide, 00_big-picture.md ... 99_quick-reference.md
  examples/                  runnable mini-projects with tests (no API key needed)
    llm_basics/              one call, streaming, structured output
    tool_agent/              tool definitions and a manual agent loop
    docs_chatbot/            RAG chatbot: FastAPI, vector index, evals, Docker (the capstone code)
    mcp_server/              MCP server exposing document search
  templates/                 starting points to copy into your own projects
    fullstack-microservices/ Python services in Docker + React frontend + Nginx proxy
    service-template/        Copier template that adds a new service to the starter
  tools/                     scripts: doc checks, navigation, glossary, website build
  site_assets/               website stylesheet (extra.css)
  mkdocs.yml                 website configuration and page order
  requirements-docs.txt      packages needed to build the website
  lychee.toml                link checker settings
  .markdownlint-cli2.jsonc   Markdown style rules
  .github/workflows/         CI: doc checks, link check, examples, templates, website deploy
```

| Folder | Details |
|---|---|
| [guides/](guides/README.md) | Numbering groups, the parts every guide has, what is generated, how to add a guide |
| [examples/](examples/README.md) | What each example shows, setup, running tests and demos |
| [templates/](templates/README.md) | The microservices starter and the Copier service template, quick start |
| [tools/](tools/README.md) | What each script checks or generates, building the website locally, CI workflows |

## Conventions

- File names: `guides/NN_topic.md` (two-digit number, lowercase, hyphens), ordered from basic to advanced.
- Each guide opens with an **Introduction**: what the tool is, why we use it, a **mental model**, key terms and where it fits with the other guides.
- Each Introduction ends with an **Official docs** table: the tool's home page and key reference pages for the latest information.
- Then a numbered **Contents** list; sections are numbered to match.
- Section **0. Flags and Parameters** breaks a sample command into its parts and explains every flag / parameter used in that guide.
- Each section opens with a short summary: what it is, how it works, and when you would use it.
- **Previous / Next** links at the top and bottom of every guide follow the reading order (generated by `tools/build_nav.py`).
- Commands have a short comment on the right explaining what they do.
- Most guides end with a **Troubleshooting** table of common errors and fixes.
- Each guide shows a **Last verified** date and ends with a **Try It** exercise section.
- Quality checks run in CI: `tools/check_docs.py` (structure, links between guides, anchors), markdownlint, a weekly external link check, the site build and the example tests.
- Fast-moving tools (LLM models, agent frameworks, cloud services) change often: the concepts are stable, but check the **Official docs** links in each guide for exact current versions and names.
