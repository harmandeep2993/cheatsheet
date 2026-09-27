# pocket-guide

A complete pocket guide for data, AI and deployment work: from the terminal and Git to LLM apps, agents and cloud deployment. Numbered from basic to advanced; every guide explains **what** a tool is, **why** it exists, **how** it works (with mental-model diagrams) and **when** to use each command.

**New here? Start with [00 - Big Picture](00_big-picture.md)**: how everything connects, the journey of a request through an AI app, and learning paths.

## Start

| # | Guide | Covers |
|---|---|---|
| 00 | [Big Picture](00_big-picture.md) | Map of the stack, request journey, dev lifecycle, learning paths, "I want to..." finder |

## Foundations

| # | Guide | Covers |
|---|---|---|
| 01 | [Markdown](01_markdown.md) | Headings, formatting, lists, links, images, code, tables, anchors |
| 02 | [Terminal and PowerShell](02_terminal-powershell.md) | Navigation, files, search, pipes, env vars, processes, network, winget, CMD/Bash equivalents |
| 03 | [Linux](03_linux.md) | Navigation, files, grep/find, permissions, apt, processes, systemd, network, SSH, tar, cron |
| 04 | [Git and GitHub](04_git.md) | Commit, branch, merge/rebase, conflicts, undo, stash, .gitignore, gh CLI, PR workflow |
| 05 | [VS Code](05_vscode.md) | Shortcuts, multi-cursor, search, debugging, Python setup, Git, extensions, settings, remote |
| 06 | [Regex](06_regex.md) | Classes, anchors, quantifiers, groups, lookarounds, common patterns, Python re, pandas, grep, SQL |
| 07 | [YAML, JSON, TOML and .env](07_yaml-json.md) | Syntax, Python parsing, jq, JSONL, JSON Schema, config formats, secrets files |
| 08 | [HTTP and APIs](08_http-apis.md) | Methods, status codes, headers, REST, auth, curl, requests/httpx, retries, rate limits, SSE, webhooks |

## Python

| # | Guide | Covers |
|---|---|---|
| 09 | [Python Basics](09_python-basics.md) | Types, strings, f-strings, lists, dicts, loops, comprehensions, functions, errors, files, classes, logging |
| 10 | [Python Virtual Environment](10_python-virtual-environment.md) | venv create/activate, pip, requirements.txt, VS Code, troubleshooting |
| 11 | [uv](11_uv.md) | Projects, add/remove, run, lock/sync, Python versions, pip interface, uvx tools, Docker |
| 12 | [Pydantic](12_pydantic.md) | Models, validation, constraints, validators, JSON Schema, settings, LLM structured output |
| 13 | [Async Python](13_async-python.md) | async/await, gather, TaskGroup, semaphores, timeouts, async HTTP and LLM calls, queues |
| 14 | [pytest](14_pytest.md) | Fixtures, parametrize, markers, mocking APIs and LLMs, FastAPI tests, coverage |
| 15 | [Jupyter](15_jupyter.md) | Kernels from venv, shortcuts, magics, display options, autoreload, export, notebooks in Git |

## Data and Machine Learning

| # | Guide | Covers |
|---|---|---|
| 16 | [NumPy](16_numpy.md) | Create arrays, indexing, filtering, reshape, math, broadcasting, axis, random, linear algebra |
| 17 | [Pandas](17_pandas.md) | Read/write, inspect, select, filter, clean, groupby, pivot, merge |
| 18 | [Polars and DuckDB](18_polars-duckdb.md) | Parquet, expressions, lazy mode, pandas translation, SQL on files and DataFrames |
| 19 | [SQL](19_sql.md) | SELECT, WHERE, GROUP BY, JOINs, CTEs, window functions, DDL/DML, psql/sqlite3, SQL from pandas |
| 20 | [Matplotlib](20_matplotlib.md) | Line, scatter, bar, hist, box, pie, labels, legend, subplots, styles, save |
| 21 | [Seaborn](21_seaborn.md) | Distribution, categorical, relationship, regression, heatmap, pairplot, facets, palettes |
| 22 | [Scikit-learn](22_scikit-learn.md) | Split, preprocessing, pipelines, models, metrics, cross-validation, tuning, saving models |
| 23 | [PyTorch](23_pytorch.md) | Tensors, GPU, autograd, nn.Module, training loop, evaluation, saving, overfitting |
| 24 | [Hugging Face](24_hugging-face.md) | Hub, pipelines, tokenizers, open LLMs, chat templates, quantization, embeddings, datasets |

## AI Engineering

| # | Guide | Covers |
|---|---|---|
| 25 | [LLM Fundamentals](25_llm-fundamentals.md) | Tokens, next-token prediction, training, context, sampling, reasoning, hallucinations, cost, model choice |
| 26 | [LLM APIs](26_llm-apis.md) | Claude SDK in depth, streaming, structured outputs, vision/PDF, thinking, caching, batches, OpenAI equivalents |
| 27 | [Prompt Engineering](27_prompt-engineering.md) | Clarity, context, XML tags, examples, output formats, long docs, templates, chaining, checklist |
| 28 | [Tool Use](28_tool-use.md) | Tool definitions, the tool loop, tool runner, parallel calls, errors, server tools, tool design, safety |
| 29 | [Embeddings and Vector DBs](29_embeddings-vector-db.md) | Embedding models, similarity, ANN/HNSW, FAISS, Chroma, pgvector, Qdrant, hybrid search |
| 30 | [RAG](30_rag.md) | Loading, chunking, retrieval, reranking, citations, contextual/agentic RAG, evaluation, security |
| 31 | [AI Agents](31_ai-agents.md) | Agent loop, workflows vs agents, patterns, memory, planning, multi-agent, human-in-the-loop, limits |
| 32 | [Agent Frameworks](32_agent-frameworks.md) | Claude Agent SDK, OpenAI Agents SDK, LangChain/LangGraph, LlamaIndex, PydanticAI, CrewAI, choosing |
| 33 | [MCP](33_mcp.md) | Model Context Protocol: architecture, Python servers, Claude Code/Desktop/VS Code, clients, security |
| 34 | [Evals and Observability](34_evals-observability.md) | Eval sets, graders, LLM-as-judge, CI evals, tracing, logging, cost monitoring, feedback |
| 35 | [Local LLMs](35_local-llms.md) | Ollama in depth, hardware sizing, quantization, llama.cpp, LM Studio, vLLM, Docker |
| 36 | [Fine-tuning](36_fine-tuning.md) | When to fine-tune, LoRA/QLoRA, datasets, TRL training, evaluation, GGUF export, DPO, hosted options |
| 37 | [AI Security](37_ai-security.md) | OWASP LLM Top 10, prompt injection, excessive agency, data leakage, guardrails, regulation, red teaming |
| 38 | [AI UIs](38_ai-ui.md) | Streamlit, Gradio, Chainlit chat apps, streaming, state, secrets, FastAPI frontend, deployment |

## APIs and Deployment

| # | Guide | Covers |
|---|---|---|
| 39 | [FastAPI](39_fastapi.md) | Routes, Pydantic validation, dependencies, settings, routers, testing, ML model API, Docker |
| 40 | [Uvicorn](40_uvicorn.md) | ASGI server: running apps, reload, workers, Gunicorn, proxy headers, HTTPS, timeouts, logging, Docker, systemd |
| 41 | [Redis and Task Queues](41_redis-queues.md) | Caching, LLM response cache, rate limiting, sessions, RQ, Celery, arq, job status pattern |
| 42 | [Docker](42_docker.md) | Images, containers, run options, Dockerfile, volumes, networks, Compose, cleanup, registry |
| 43 | [GitHub Actions](43_github-actions.md) | Workflows, triggers, Python CI with uv, secrets, caching, evals in CI, Docker builds, Azure OIDC deploy |
| 44 | [Nginx and HTTPS](44_nginx-https.md) | Reverse proxy, Let's Encrypt, streaming/WebSockets, basic auth, rate limits, systemd, Caddy |
| 45 | [Kubernetes](45_kubernetes.md) | Pods, Deployments, Services, Ingress, config, probes, scaling, rollouts, GPUs, Helm, AKS |
| 46 | [Terraform](46_terraform.md) | HCL, providers, resources, variables, state, modules, environments, Azure example, CI/CD |
| 47 | [Azure](47_azure.md) | Concepts, CLI, resource groups, VMs, storage, ACR, Container Apps, App Service, Key Vault, databases, RBAC, Azure OpenAI, cost, Bicep |
| 48 | [Azure VM + Linux + Ollama](48_azure-vm-ollama.md) | Azure CLI, VM, NSG, SSH, Linux basics, Ollama, SSH tunnel |

## Conventions

- File names: `NN_topic.md` (two-digit number, lowercase, hyphens), ordered from basic to advanced.
- Each guide opens with an **Introduction**: what the tool is, why we use it, a **mental model**, key terms and where it fits with the other guides.
- Each Introduction ends with an **Official docs** table: the tool's home page and key reference pages for the latest information.
- Then a numbered **Contents** list; sections are numbered to match.
- Section **0. Flags and Parameters** breaks a sample command into its parts and explains every flag / parameter used in that guide.
- Each section opens with **What** (what it is), **How** (how it works) and **When to use** (a real scenario).
- Commands have a short comment on the right explaining what they do.
- Most guides end with a **Troubleshooting** table of common errors and fixes.
- Fast-moving tools (LLM models, agent frameworks, cloud services) change often: the concepts are stable, but check the **Official docs** links in each guide for exact current versions and names.
