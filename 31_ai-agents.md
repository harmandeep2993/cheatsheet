# 31 - AI Agents

Quick reference for AI agents: what they are, the agent loop, workflows vs agents, design patterns, memory, planning, multi-agent systems, human oversight, and building a small agent from scratch.

## Introduction

### What is an AI agent?

An **AI agent** is an LLM that works in a **loop**: it looks at a goal, decides what to do next, uses **tools** (search, code, APIs, files), looks at the results, and keeps going until the goal is reached. A normal LLM call answers once. An agent **takes several steps on its own**, choosing which tools to use and in what order, based on what it finds along the way.

### Mental model: a new employee with a task, tools and a notebook

```text
                 +--------------------------------------------------------+
   GOAL -------> |                     AGENT LOOP                         |
 "Find why the   |                                                        |
  nightly ETL    |   1. THINK   read goal + everything so far,            |
  failed and     |              decide the next step                      |
  fix it"        |                  |                                     |
                 |   2. ACT     call a tool: read_logs("etl", "last run") |
                 |                  |                                     |
                 |   3. OBSERVE get the result: "KeyError: 'region'"     |
                 |                  |                                     |
                 |   4. REPEAT  until done / stuck / out of budget        |
                 |                                                        |
                 |   CONTEXT (short-term memory): goal, steps, results    |
                 |   MEMORY  (long-term): notes, files, vector DB         |
                 |   GUARDRAILS: allowed tools, approvals, budgets        |
                 +--------------------------------------------------------+
                                     |
                                     v
                  RESULT: "Column renamed upstream; updated mapping in etl/transform.py; test passes."
```

Four ingredients make an agent: **model** (the brain), **tools** (the hands), **context / memory** (what it knows), and **the loop with stopping rules** (the harness). Everything else is detail.

### Workflow or agent?

```text
WORKFLOW (you decide the steps in code)        AGENT (the model decides the steps)

 input -> LLM step A -> code check -> LLM step B      input -> [ LLM <-> tools ]* -> output
 predictable, cheap, testable                   flexible, handles the unexpected,
 best when the steps are known                  slower, costlier, less predictable
```

Rule: **start with the simplest thing that works** (single call -> workflow -> agent). Use an agent only when the steps cannot be known in advance, the task is valuable enough to justify cost and latency, the model is capable of it, and mistakes can be caught or undone.

### Key terms

| Term | Meaning |
|---|---|
| Agent | LLM + tools + loop that pursues a goal autonomously |
| Harness | The code that runs the loop, executes tools, manages context and limits |
| Tool | A function the agent can call ([28](28_tool-use.md)) |
| Workflow | Fixed, code-defined sequence of LLM calls |
| ReAct | Pattern: Reason -> Act -> Observe, repeated |
| Planning | Making a step list before acting |
| Reflection | Agent reviews its own output and improves it |
| Memory (short / long term) | Current context window / stored knowledge across sessions |
| Multi-agent | Several agents with roles (orchestrator, workers, reviewers) |
| Sub-agent | Agent started by another agent for a sub-task, with its own context |
| Human-in-the-loop (HITL) | A person approves or corrects steps |
| Guardrails | Limits and checks on inputs, actions and outputs |
| Computer use | Agent operates a GUI (screenshots, clicks, typing) |

**Where it fits:** built from [26 - LLM APIs](26_llm-apis.md) and [28 - Tool Use](28_tool-use.md); frameworks in [32](32_agent-frameworks.md); tools shared via [33 - MCP](33_mcp.md); tested with [34 - Evals](34_evals-observability.md); secured with [37 - AI Security](37_ai-security.md); deployed with [39](39_fastapi.md), [40](40_redis-queues.md), [41](41_docker.md).

---

## Contents

1. [The Agent Loop in Code](#1-the-agent-loop-in-code)
2. [Workflow Patterns (Before Agents)](#2-workflow-patterns-before-agents)
3. [Agent Patterns](#3-agent-patterns)
4. [Designing the Agent's Tools](#4-designing-the-agents-tools)
5. [The Agent System Prompt](#5-the-agent-system-prompt)
6. [Context Management](#6-context-management)
7. [Memory](#7-memory)
8. [Planning and Task Lists](#8-planning-and-task-lists)
9. [Reflection and Self-Checking](#9-reflection-and-self-checking)
10. [Multi-Agent Systems](#10-multi-agent-systems)
11. [Human-in-the-Loop](#11-human-in-the-loop)
12. [Stopping Rules and Budgets](#12-stopping-rules-and-budgets)
13. [Types of Agents You Can Build](#13-types-of-agents-you-can-build)
14. [Coding Agents and Computer Use](#14-coding-agents-and-computer-use)
15. [Build vs Framework vs Hosted](#15-build-vs-framework-vs-hosted)
16. [Deploying Agents](#16-deploying-agents)
17. [Evaluating Agents](#17-evaluating-agents)
18. [Failure Modes](#18-failure-modes)
19. [Agent Design Checklist](#19-agent-design-checklist)

---

## 1. The Agent Loop in Code

> - **What:** A complete minimal agent: model + tools + loop + limits.
> - **How:** Call the model with tools; run requested tools; feed results back; stop at the final answer or when a limit is hit.
> - **When to use:** Understanding every framework (they all do this) and building small agents without dependencies.

```python
import subprocess
from pathlib import Path

import anthropic

client = anthropic.Anthropic()
MAX_STEPS = 15                     # hard cap on loop iterations
ALLOWED_DIR = "workspace"


def list_files() -> str:
    return "\n".join(str(p) for p in Path(ALLOWED_DIR).rglob("*") if p.is_file())


def read_file(path: str) -> str:
    target = (Path(ALLOWED_DIR) / path).resolve()
    if Path(ALLOWED_DIR).resolve() not in target.parents:
        raise ValueError("path outside workspace")          # sandbox: never trust model input
    return target.read_text(encoding="utf-8")[:20_000]      # cap size to protect the context


def run_tests() -> str:
    r = subprocess.run(["pytest", "-q"], cwd=ALLOWED_DIR, capture_output=True, text=True, timeout=300)
    return (r.stdout + r.stderr)[-5_000:]


TOOLS = [
    {"name": "list_files", "description": "List all files in the project workspace.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "read_file", "description": "Read a text file from the workspace. Path is relative to the workspace root.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "run_tests", "description": "Run the pytest suite and return the output (last 5000 chars).",
     "input_schema": {"type": "object", "properties": {}}},
]
HANDLERS = {"list_files": list_files, "read_file": read_file, "run_tests": run_tests}


def run_agent(goal: str) -> str:
    messages = [{"role": "user", "content": goal}]
    for step in range(MAX_STEPS):
        response = client.messages.create(
            model="claude-opus-5", max_tokens=16000, tools=TOOLS, messages=messages,
            system="You are a careful engineering assistant. Investigate before concluding. "
                   "When done, give a short report: cause, evidence, suggested fix.",
        )
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                output = HANDLERS[block.name](**block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(output)})
            except Exception as exc:                          # report tool failures to the model
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": f"Error: {exc}", "is_error": True})
        messages.append({"role": "user", "content": results})
    return "Stopped: step limit reached."


print(run_agent("The test suite fails. Find out why and suggest a fix."))
```

The SDK tool runner can replace the manual loop ([28](28_tool-use.md) section 3).

## 2. Workflow Patterns (Before Agents)

> - **What:** Code-controlled patterns that solve most problems without full autonomy.
> - **How:** You define the steps; LLM calls do the language work inside each step.
> - **When to use:** Try these first; they are cheaper, faster and easier to test than agents.

| Pattern | Shape | Example |
|---|---|---|
| Prompt chaining | A -> B -> C, with checks between | Outline -> draft -> edit |
| Routing | Classify input -> send to specialised prompt / model | Support: billing vs tech |
| Parallelisation | Same task on chunks / several perspectives, then combine | Review 50 documents; vote on risk |
| Orchestrator-workers | LLM splits a task into sub-tasks; workers do them; results merged | Research report sections |
| Evaluator-optimiser | Generate -> critique against criteria -> revise (loop N times) | Translation polishing, code review |

## 3. Agent Patterns

> - **What:** Common ways agents are structured.
> - **How:** Each pattern adds structure to the basic loop.
> - **When to use:** Choosing an architecture for your agent.

| Pattern | Idea | Good for |
|---|---|---|
| ReAct (tool loop) | Think -> act -> observe, repeat | General tool-using assistants |
| Plan-and-execute | Make a plan first, then execute steps, re-plan on surprises | Long multi-step tasks |
| Reflection | Draft, then self-critique and revise | Writing, code quality |
| Router agent | Decide which specialist agent / tool handles the request | Assistants with many domains |
| Orchestrator + sub-agents | Lead agent delegates to sub-agents with fresh context | Research, large codebases |
| Supervisor / reviewer | Separate agent checks outputs before they are used | High-stakes outputs |

## 4. Designing the Agent's Tools

> - **What:** Choosing the actions the agent can take.
> - **How:** A small set of clear, well-described, safe tools that return concise results (see [28](28_tool-use.md) section 10).
> - **When to use:** The tool set largely determines agent quality.

- Prefer **general, composable tools** (search, read, write, run code) over dozens of narrow ones.
- Make results **informative but short**: summaries, IDs, next-step hints; paginate big outputs.
- Separate **read** tools (safe) from **write / act** tools (need approval).
- Return **actionable errors** so the agent can recover.
- For many tools, load them on demand (tool search) or group them behind MCP servers ([33](33_mcp.md)).

## 5. The Agent System Prompt

> - **What:** The instructions that shape how the agent works.
> - **How:** State the role, goal, available resources, working style, constraints and what "done" means.
> - **When to use:** Every agent.

```text
You are a data-quality agent for Acme's analytics team.

Goal: find and explain data problems in the tables the user names.

How to work:
- Investigate with the tools before drawing conclusions; verify claims with queries.
- Prefer small, targeted queries (LIMIT 100) over scanning whole tables.
- If something is ambiguous, state your assumption and continue.
- Never modify data; you only have read access.

When you are done, reply with:
1. Findings (each with the query that proves it)
2. Likely causes
3. Recommended fixes, most important first
```

Describe **what done looks like**; agents otherwise stop too early or never stop.

## 6. Context Management

> - **What:** Keeping the agent's context window useful as the task grows.
> - **How:** Everything (goal, tool calls, results) accumulates in the context; big results crowd out the important parts and cost money.
> - **When to use:** Any agent running more than a few steps.

| Technique | How |
|---|---|
| Trim tool outputs | Truncate / summarise large results before returning them |
| Store, don't stuff | Write big data to files; return paths and summaries |
| Clear old tool results | Drop or shorten old tool outputs (provider "context editing" features) |
| Compaction | Summarise earlier conversation when near the limit |
| Sub-agents | Delegate a sub-task to a fresh context; get back only the summary |
| Prompt caching | Keep the stable prefix (system prompt, tools) cacheable ([26](26_llm-apis.md)) |

## 7. Memory

> - **What:** Information the agent keeps beyond one step or one session.
> - **How:** Short-term = the context window; long-term = external storage the agent reads / writes with tools.
> - **When to use:** Personal assistants, long projects, agents that should learn user preferences.

| Memory type | Stored as | Example |
|---|---|---|
| Working (short-term) | Messages in the context | Current task steps |
| Episodic | Log / summaries of past sessions | "Last week we fixed the ETL mapping" |
| Semantic | Facts / notes in a DB or vector store | "User prefers Polars over pandas" |
| Procedural | Instructions / skills files | "How we deploy to Azure" |

Simple and effective: a `notes.md` file (or memory tool) the agent may read and append to, with clear rules on what to save.

## 8. Planning and Task Lists

> - **What:** Having the agent write down its plan and track progress.
> - **How:** A planning step or a to-do tool; the agent checks items off and updates the plan when new facts appear.
> - **When to use:** Tasks with many steps where agents otherwise lose track.

```text
Plan:
[x] 1. Read the failing test output
[x] 2. Locate the function under test
[ ] 3. Reproduce with a minimal input
[ ] 4. Fix and re-run tests
[ ] 5. Write the report
```

## 9. Reflection and Self-Checking

> - **What:** Making the agent verify its own work before finishing.
> - **How:** Give it ways to check (tests, validators, a second LLM review with a rubric) and require verification before "done".
> - **When to use:** Code, data transformations, reports with numbers.

- Best checks are **objective**: run tests, validate JSON against a schema, re-run the query.
- LLM self-critique helps, but can miss its own mistakes; a separate reviewer prompt / model is stronger.

## 10. Multi-Agent Systems

> - **What:** Several agents with different roles working together.
> - **How:** Usually an **orchestrator** that splits the task and **workers / sub-agents** that each handle a part with their own context and tools; results flow back to the orchestrator.
> - **When to use:** Broad tasks that parallelise well (research over many sources), or tasks needing separated roles (writer + reviewer). Otherwise one agent is simpler.

```text
                      ORCHESTRATOR (plans, delegates, merges)
                     /            |              \
          researcher A      researcher B      researcher C     (parallel, fresh contexts,
          (topic 1)         (topic 2)         (topic 3)         cheaper model possible)
                     \            |              /
                      ORCHESTRATOR writes the final report
                              |
                          REVIEWER checks facts and citations
```

Costs grow with the number of agents; coordination adds failure points. Measure whether it beats a single agent.

## 11. Human-in-the-Loop

> - **What:** People approving, correcting or guiding the agent.
> - **How:** Pause before risky actions and ask; show plans for approval; allow the user to interrupt.
> - **When to use:** Any action that is expensive, irreversible or external (payments, emails, deletes, deploys).

```python
RISKY_TOOLS = {"send_email", "delete_record", "deploy"}


def execute(block):
    if block.name in RISKY_TOOLS:
        print(f"Agent wants to run {block.name} with {block.input}")
        if input("Approve? [y/N] ").strip().lower() != "y":
            return {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                    "content": "The user declined this action. Propose an alternative or stop."}
    return {"type": "tool_result", "tool_use_id": block.id, "content": str(HANDLERS[block.name](**block.input))}
```

## 12. Stopping Rules and Budgets

> - **What:** Limits that keep agents from running forever or spending too much.
> - **How:** Hard caps in code, plus clear completion criteria in the prompt.
> - **When to use:** Every agent, always.

| Limit | Example |
|---|---|
| Max steps / tool calls | 15 to 50 per task |
| Max tokens / cost | Stop at $X per task; track `usage` each step |
| Max wall-clock time | 10 minutes |
| Repeated action detection | Same tool + same input 3 times -> stop |
| Completion criteria | "Done when tests pass and the report is written" |

## 13. Types of Agents You Can Build

> - **What:** Practical agent ideas for data / AI developers.
> - **How:** Each combines a goal, a tool set and guardrails.
> - **When to use:** Inspiration for projects and portfolio work.

| Agent | Tools |
|---|---|
| Research assistant | web search, fetch, notes, citation formatting |
| Data analyst | SQL (read-only), pandas / code execution, charts |
| Support agent | knowledge-base search (RAG), order lookup, ticket creation (approval), handoff to human |
| Coding assistant | read / write files, run tests, git |
| DevOps helper | read logs, query metrics, run diagnostics (read-only), open incident |
| Personal productivity | calendar, email drafts (approval), to-do list, memory |
| Document processor | OCR / PDF parsing, extraction to schema, validation, DB insert |

## 14. Coding Agents and Computer Use

> - **What:** Agents that work in a real environment: codebases, terminals, browsers, desktops.
> - **How:** Tools for files, shell commands and tests (coding agents), or screenshots + mouse / keyboard actions (computer use), usually in a sandbox.
> - **When to use:** Automating software tasks; GUI tasks with no API.

- Coding agents you can use today: Claude Code, and others; their harnesses are also available as libraries (e.g. Claude Agent SDK, [32](32_agent-frameworks.md)).
- Always sandbox: containers or VMs, limited network, no production credentials, review diffs before merging.

## 15. Build vs Framework vs Hosted

> - **What:** Ways to get an agent running.
> - **How:** Trade control against convenience.
> - **When to use:** Starting an agent project.

| Option | You write | Good when |
|---|---|---|
| Raw API + your loop | Everything (section 1) | Learning, full control, simple agents |
| SDK tool runner | Tool functions only | Custom tools, less loop code |
| Agent framework (LangGraph, OpenAI Agents SDK, PydanticAI, CrewAI ...) | Graph / agents / tools | Complex flows, state, multi-agent, integrations |
| Batteries-included harness (Claude Agent SDK) | Prompt + options + custom tools | File / shell / web agents with built-in tools |
| Hosted agent platforms (e.g. managed agent services) | Config + tools | You want the provider to run the loop and sandbox |

Details and code: [32 - Agent Frameworks](32_agent-frameworks.md).

## 16. Deploying Agents

> - **What:** Running agents for real users.
> - **How:** Agents are long-running: run them as background jobs, stream progress, persist state, and isolate their execution environment.
> - **When to use:** Moving from notebook to product.

```text
User -> FastAPI endpoint -> enqueue job (Redis) -> worker runs agent loop in a sandbox container
                                 |                          |
                         return job id               stream progress events (SSE / WebSocket)
                                                            |
                                                  save state + final result (DB)
```

- Timeouts, retries and idempotent tools; persist state so a crash can resume.
- One container / sandbox per session for code-running agents.
- Log every step with tracing ([34](34_evals-observability.md)).
- See [39 - FastAPI](39_fastapi.md), [40 - Redis and Queues](40_redis-queues.md), [41 - Docker](41_docker.md).

## 17. Evaluating Agents

> - **What:** Measuring whether the agent reliably achieves goals.
> - **How:** Task suites with checkable outcomes; track success rate, steps, cost, time, and unsafe actions.
> - **When to use:** Before trusting an agent, and after every prompt / tool / model change.

| Metric | Meaning |
|---|---|
| Task success rate | Share of tasks fully completed (checked by tests / validators / rubric) |
| Steps / tool calls per task | Efficiency |
| Cost and latency per task | Budget fit |
| Error recovery rate | Recovers after a tool error |
| Safety violations | Unapproved risky actions, data leaks |

Run each task several times: agents are non-deterministic. More in [34](34_evals-observability.md).

## 18. Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Loops on the same action | Unclear results / no progress signal | Better tool outputs, repetition detection, step cap |
| Stops too early | No clear definition of done | Completion criteria + verification step |
| Wanders off-task | Vague goal, too many tools | Sharper goal, fewer tools, plan step |
| Hallucinates tool results | Tool not called / result ignored | Require evidence from tool outputs in the final report |
| Context overflow | Huge tool outputs | Truncate / summarise, sub-agents, compaction |
| Unsafe action | Missing approval / permissions | HITL for risky tools, least privilege, sandbox |
| Follows instructions from a web page / document | Prompt injection | Treat tool results as data; restrict tools ([37](37_ai-security.md)) |
| Too slow / expensive | Too many steps / big model everywhere | Workflow instead of agent; cheaper sub-agents; caching |

## 19. Agent Design Checklist

- [ ] Could a workflow do this instead? (If yes, use a workflow.)
- [ ] Clear goal and definition of done in the system prompt
- [ ] Small set of well-described tools with concise outputs
- [ ] Read vs write tools separated; approvals on risky actions
- [ ] Sandbox and least-privilege credentials
- [ ] Step, time and cost limits in code
- [ ] Context management for long runs
- [ ] Tracing of every step; eval suite with success criteria
- [ ] Prompt-injection defences for any external content
