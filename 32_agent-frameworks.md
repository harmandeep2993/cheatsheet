# 32 - Agent Frameworks

<!-- nav:start -->
**Previous:** [31 - AI Agents](31_ai-agents.md) | **Index:** [All guides](README.md) | **Next:** [33 - MCP (Model Context Protocol)](33_mcp.md)
<!-- nav:end -->

Quick reference for the main libraries used to build LLM apps and agents: Claude Agent SDK, OpenAI Agents SDK, LangChain / LangGraph, LlamaIndex, PydanticAI, CrewAI, Microsoft Agent Framework, plus how to choose between them.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is an agent framework?

An **agent framework** is a library that gives you ready-made building blocks for LLM apps: model wrappers, tool definitions, the agent loop, memory / state, multi-agent coordination, retrieval, tracing and integrations. Under the hood they all make the same API calls you saw in [26 - LLM APIs](26_llm-apis.md) and run the same tool loop from [28 - Tool Use](28_tool-use.md). They save code for complex cases and add conventions, at the cost of an extra dependency and some hidden behaviour.

### Mental model: same engine, different car bodies

```text
                         every framework ultimately does:

    your config (prompt, tools, model) -> [ LLM API call ] -> tool calls? -> run tools -> repeat
                                                                  |
                                                            final answer

   What differs is WHO controls the flow and WHAT comes built in:

   Raw SDK            you write the loop                     (max control, least magic)
   SDK tool runner    SDK runs the loop over your tools
   OpenAI Agents SDK  agents + handoffs + guardrails, simple Python
   PydanticAI         typed agents, Pydantic-validated outputs, DI
   LangGraph          you draw the flow as a GRAPH of nodes + state (explicit control, persistence)
   LangChain          building blocks + many integrations (models, loaders, vector stores)
   LlamaIndex         data / RAG first: loaders, indexes, query engines, agents over data
   CrewAI             role-playing multi-agent "crews" with tasks
   Claude Agent SDK   the full Claude Code harness as a library: built-in file / shell / web tools
```

Frameworks change fast. The **concepts** in this guide are stable; check each project's docs for exact current APIs and install the version you read about.

### Why use a framework?

- **Less boilerplate** for loops, retries, streaming, state and multi-agent handoffs.
- **Integrations**: dozens of model providers, vector stores and document loaders behind one interface.
- **Built-in tracing / debugging** tools (LangSmith, Logfire, OpenAI traces).
- **Durable state**: pause / resume, human approval steps (LangGraph checkpoints).

### When not to

- Simple apps (single calls, basic RAG, one tool loop) are often clearer with the raw SDK.
- Heavy abstractions can hide prompts and make debugging harder; learn the raw API first.

### Key terms

| Term | Meaning |
|---|---|
| Chain | Fixed sequence of steps (prompt -> model -> parser) |
| Graph | Nodes (steps) + edges (transitions) + shared state (LangGraph) |
| State | Data passed between steps (messages, intermediate results) |
| Checkpointer | Saves state so runs can resume / be inspected |
| Handoff | One agent passes control to another (OpenAI Agents SDK) |
| Guardrail | Check that runs on input / output and can block it |
| Retriever / query engine | Component that fetches documents for RAG |
| Crew | Group of role-based agents with tasks (CrewAI) |
| Session | Stored conversation state for an agent |

**Where it fits:** built on [26 - LLM APIs](26_llm-apis.md), [28 - Tool Use](28_tool-use.md) and [12 - Pydantic](12_pydantic.md); implements patterns from [30 - RAG](30_rag.md) and [31 - AI Agents](31_ai-agents.md); tools via [33 - MCP](33_mcp.md); traced with [34](34_evals-observability.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Claude Agent SDK | https://code.claude.com/docs/en/agent-sdk |
| OpenAI Agents SDK | https://openai.github.io/openai-agents-python/ |
| LangChain and LangGraph | https://docs.langchain.com/ |
| LlamaIndex | https://docs.llamaindex.ai/ |
| PydanticAI | https://ai.pydantic.dev/ |
| CrewAI | https://docs.crewai.com/ |
| Microsoft Agent Framework | https://learn.microsoft.com/en-us/agent-framework/ |
| LiteLLM | https://docs.litellm.ai/ |

---

## Contents

1. [Comparison Table](#1-comparison-table)
2. [Claude Agent SDK](#2-claude-agent-sdk)
3. [OpenAI Agents SDK](#3-openai-agents-sdk)
4. [LangChain Basics](#4-langchain-basics)
5. [LangChain Agents](#5-langchain-agents)
6. [LangGraph (Graphs of Steps)](#6-langgraph-graphs-of-steps)
7. [LlamaIndex (RAG-First)](#7-llamaindex-rag-first)
8. [PydanticAI](#8-pydanticai)
9. [CrewAI (Role-Based Multi-Agent)](#9-crewai-role-based-multi-agent)
10. [Microsoft Agent Framework / Semantic Kernel / AutoGen](#10-microsoft-agent-framework--semantic-kernel--autogen)
11. [LiteLLM (One API for Many Providers)](#11-litellm-one-api-for-many-providers)
12. [Hosted Agent Platforms](#12-hosted-agent-platforms)
13. [How to Choose](#13-how-to-choose)
14. [Framework Hygiene](#14-framework-hygiene)
15. [Troubleshooting](#15-troubleshooting)
16. [Try It](#16-try-it)

---

## 1. Comparison Table

> The frameworks side by side. Compare focus, control style and strengths.
>
> Use it for picking a framework for a project.

| Framework | Focus | Control style | Standout features |
|---|---|---|---|
| Raw SDK (+ tool runner) | Any | You write the flow | Simplest, full control, no extra deps |
| Claude Agent SDK | General / coding agents | Harness runs the loop | Built-in Read / Write / Edit / Bash / Web tools, sub-agents, hooks, permissions, MCP |
| OpenAI Agents SDK | Lightweight agents | Agents + handoffs | Handoffs, guardrails, sessions, tracing; works with other models via adapters |
| LangChain | Integrations | Building blocks | Huge ecosystem of model / tool / vector-store integrations |
| LangGraph | Stateful agents / workflows | Explicit graph | Checkpoints, human-in-the-loop, durable execution, multi-agent graphs |
| LlamaIndex | RAG / data agents | Indexes + engines | Loaders, indexing, retrieval strategies, agents over data |
| PydanticAI | Typed Python agents | Agents with typed deps / outputs | Validation, dependency injection, model-agnostic, Logfire tracing |
| CrewAI | Multi-agent teams | Roles + tasks | Quick multi-agent prototypes |
| Microsoft Agent Framework | Enterprise .NET / Python | Agents + workflows | Azure integration; successor to Semantic Kernel and AutoGen |

## 2. Claude Agent SDK

> Claude Code's agent harness packaged as a Python / TypeScript library. You call `query(prompt, options)`; the SDK runs the loop with built-in tools (read / write / edit files, bash, grep, web search / fetch), context management, sub-agents, hooks and permission controls; you can add your own tools via MCP.
>
> Use it for agents that work with files, code, shells and the web on your own infrastructure (coding agents, research agents, ops automation).

```powershell
pip install claude-agent-sdk
```

```python
import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query


async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are a careful data engineer. Explain what you change.",
        allowed_tools=["Read", "Grep", "Glob", "Bash"],     # restrict what the agent may use
        cwd="./my_project",                                 # working directory (sandbox it!)
        max_turns=20,
    )
    async for message in query(prompt="Find why tests fail and summarise the cause.", options=options):
        print(message)


asyncio.run(main())
```

Custom tools as an in-process MCP server:

```python
from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, tool


@tool("get_order_status", "Look up the status of an order by id", {"order_id": str})
async def get_order_status(args):
    return {"content": [{"type": "text", "text": f"Order {args['order_id']}: shipped"}]}


server = create_sdk_mcp_server(name="shop", version="1.0.0", tools=[get_order_status])
options = ClaudeAgentOptions(
    mcp_servers={"shop": server},
    allowed_tools=["mcp__shop__get_order_status"],          # mcp__<server>__<tool>
)
```

Run it in a container / VM with limited permissions: it can execute shell commands. Docs: code.claude.com/docs/en/agent-sdk.

## 3. OpenAI Agents SDK

> A lightweight Python framework from OpenAI for agents with tools, handoffs and guardrails. Define `Agent(name, instructions, tools, handoffs)`; run with `Runner`; tools are decorated Python functions.
>
> Use it for simple-to-medium agents and multi-agent handoffs, especially with OpenAI models.

```powershell
pip install openai-agents
```

```python
from agents import Agent, Runner, function_tool


@function_tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order."""
    return "shipped, arriving 2026-09-30"


billing = Agent(name="Billing", instructions="Handle refunds and invoices.")
support = Agent(
    name="Support",
    instructions="Help customers with orders. Hand off billing questions to Billing.",
    tools=[get_order_status],
    handoffs=[billing],
)

result = Runner.run_sync(support, "Where is order A-1042?")
print(result.final_output)
```

Also: input / output guardrails, sessions for memory, built-in tracing, and support for other providers through model adapters.

## 4. LangChain Basics

> A large toolkit of components for LLM apps: chat models, prompts, output parsers, retrievers, tools and integrations. Provider packages (`langchain-anthropic`, `langchain-openai`, ...) give a common chat-model interface; components can be combined.
>
> Use this when you need many integrations (loaders, vector stores, providers) behind one interface.

```powershell
pip install langchain langchain-anthropic langchain-openai
```

```python
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

llm = init_chat_model("anthropic:claude-opus-5")           # provider:model; reads ANTHROPIC_API_KEY
llm.invoke("Explain RAG in one sentence.").content

prompt = ChatPromptTemplate.from_messages([
    ("system", "You translate to {language}. Reply with the translation only."),
    ("user", "{text}"),
])
chain = prompt | llm                                        # LCEL: pipe components together
chain.invoke({"language": "German", "text": "Good morning"}).content

structured = llm.with_structured_output(Ticket)             # Pydantic model -> validated object
```

## 5. LangChain Agents

> A prebuilt tool-calling agent on top of LangGraph. Give a model, tools and a system prompt; invoke with messages.
>
> Use it for quick tool-using agents with LangChain integrations.

```python
from langchain.agents import create_agent
from langchain_core.tools import tool


@tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by id."""
    return "shipped"


agent = create_agent(
    model="anthropic:claude-opus-5",
    tools=[get_order_status],
    system_prompt="You are a helpful support agent.",
)
result = agent.invoke({"messages": [{"role": "user", "content": "Where is order A-1042?"}]})
print(result["messages"][-1].content)
```

Older tutorials use `AgentExecutor` / `initialize_agent`; those APIs are legacy. Check the current docs.

## 6. LangGraph (Graphs of Steps)

> A library for building agents and workflows as **graphs**: nodes are steps (LLM calls, tools, code), edges decide what runs next, and a typed **state** flows through. Define the state, add nodes and (conditional) edges, compile, invoke; add a checkpointer for memory, resume and human approval.
>
> Use it for complex, long-running or stateful flows where you want explicit control over every transition.

```powershell
pip install langgraph langchain-anthropic
```

```python
from typing import TypedDict

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

llm = init_chat_model("anthropic:claude-opus-5")


class State(TypedDict):
    ticket: str
    category: str
    reply: str


def classify(state: State) -> dict:
    label = llm.invoke(f"Label this ticket billing / technical / other. Label only:\n{state['ticket']}").content
    return {"category": label.strip().lower()}


def billing_reply(state: State) -> dict:
    return {"reply": llm.invoke(f"Write a billing support reply to:\n{state['ticket']}").content}


def tech_reply(state: State) -> dict:
    return {"reply": llm.invoke(f"Write a technical support reply to:\n{state['ticket']}").content}


def route(state: State) -> str:
    return "billing" if "billing" in state["category"] else "tech"


graph = StateGraph(State)
graph.add_node("classify", classify)
graph.add_node("billing", billing_reply)
graph.add_node("tech", tech_reply)
graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", route, {"billing": "billing", "tech": "tech"})
graph.add_edge("billing", END)
graph.add_edge("tech", END)

app = graph.compile(checkpointer=InMemorySaver())           # checkpointer = memory / resume
out = app.invoke({"ticket": "I was charged twice"}, config={"configurable": {"thread_id": "t1"}})
print(out["reply"])
```

```text
START -> classify --(billing)--> billing -> END
                  \--(other)---> tech    -> END
```

## 7. LlamaIndex (RAG-First)

> A framework focused on connecting LLMs to your data: loaders, indexes, retrievers, query engines and data agents. Load documents, build an index (embeds and stores chunks), ask questions through a query engine.
>
> Use it for RAG over many document types with advanced retrieval options.

```powershell
pip install llama-index llama-index-llms-anthropic llama-index-embeddings-huggingface
```

```python
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic

Settings.llm = Anthropic(model="claude-opus-5")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

docs = SimpleDirectoryReader("docs").load_data()            # PDFs, md, docx ...
index = VectorStoreIndex.from_documents(docs)                # chunk + embed + store (in memory)
index.storage_context.persist("./storage")                   # save

engine = index.as_query_engine(similarity_top_k=5)
response = engine.query("What is the refund window for jackets?")
print(response)
for node in response.source_nodes:                           # citations
    print(node.metadata.get("file_name"), node.score)
```

## 8. PydanticAI

> A Python agent framework from the Pydantic team with type-safe outputs and dependency injection. `Agent("provider:model", output_type=..., system_prompt=...)`; tools are decorated functions; outputs are validated Pydantic objects.
>
> Use this when you like typed Python, want validated structured outputs and clean testing.

```powershell
pip install pydantic-ai
```

```python
from pydantic import BaseModel
from pydantic_ai import Agent


class Answer(BaseModel):
    city: str
    country: str
    confidence: float


agent = Agent(
    "anthropic:claude-opus-5",
    output_type=Answer,
    system_prompt="Identify the city the user describes.",
)


@agent.tool_plain
def population(city: str) -> int:
    """Return the population of a city."""
    return 3_700_000


result = agent.run_sync("The capital of Germany, famous for its wall.")
print(result.output)          # Answer(city='Berlin', country='Germany', confidence=0.97)
```

## 9. CrewAI (Role-Based Multi-Agent)

> A framework for teams of agents with roles, goals and tasks. Define `Agent`s (role, goal, backstory, tools), `Task`s (description, expected output, agent) and a `Crew` that runs them.
>
> Use it for quick multi-agent prototypes (researcher + writer + editor).

```powershell
pip install crewai
```

```python
from crewai import Agent, Crew, Task

researcher = Agent(role="Researcher", goal="Find key facts about a topic",
                   backstory="Meticulous analyst.", llm="anthropic/claude-opus-5")
writer = Agent(role="Writer", goal="Write a clear 200-word brief",
               backstory="Technical writer.", llm="anthropic/claude-opus-5")

research = Task(description="Research the benefits of Parquet over CSV.",
                expected_output="5 bullet points with facts", agent=researcher)
brief = Task(description="Write a brief from the research.", expected_output="200-word brief",
             agent=writer, context=[research])

print(Crew(agents=[researcher, writer], tasks=[research, brief]).kickoff())
```

## 10. Microsoft Agent Framework / Semantic Kernel / AutoGen

> Microsoft's agent tooling for Python and .NET. The **Microsoft Agent Framework** unifies ideas from Semantic Kernel (enterprise SDK) and AutoGen (multi-agent research framework) into one framework with agents, workflows and Azure integrations.
>
> Use it for microsoft / Azure-centric teams, .NET codebases, Azure AI Foundry deployments. Check Microsoft Learn for the current packages and APIs.

## 11. LiteLLM (One API for Many Providers)

> A library and proxy that exposes 100+ LLM providers through one OpenAI-style interface. `completion(model="provider/model", messages=[...])`; the proxy adds keys, budgets, logging and fallbacks centrally.
>
> Use it for switching / comparing providers, central gateway for a team.

```python
from litellm import completion

resp = completion(model="anthropic/claude-opus-5", messages=[{"role": "user", "content": "Hi"}])
resp.choices[0].message.content
```

## 12. Hosted Agent Platforms

> Services where the provider runs the agent loop (and often a sandbox) for you. You configure the agent (model, prompt, tools, MCP servers) and start sessions through an API; the platform executes tools and streams events.
>
> Use it for long-running or scheduled agents without building infrastructure.

Examples: Anthropic's Managed Agents (beta), OpenAI's hosted agent tools, Azure AI Foundry Agent Service, AWS Bedrock Agents, Google Vertex AI Agent Builder. Features and pricing change quickly; compare against your needs for data residency, tools and control.

## 13. How to Choose

> A decision guide. Start from your need; pick the lightest option that covers it.
>
> Use it for project kickoff.

| Need | Start with |
|---|---|
| Learn how agents work | Raw SDK loop ([31](31_ai-agents.md) section 1) |
| One agent with your own tools | SDK tool runner / PydanticAI / OpenAI Agents SDK |
| Agent that edits files, runs commands, browses | Claude Agent SDK |
| RAG over lots of documents | LlamaIndex (or raw code + vector DB) |
| Complex branching, approvals, resumable long runs | LangGraph |
| Many third-party integrations quickly | LangChain |
| Role-based multi-agent prototype | CrewAI / OpenAI Agents SDK handoffs |
| Azure / .NET enterprise | Microsoft Agent Framework / Azure AI Foundry |
| Switching models often | LiteLLM or your own provider interface ([26](26_llm-apis.md) section 19) |

## 14. Framework Hygiene

> Practices that keep framework-based code maintainable. Pin versions, isolate framework code, keep prompts visible, trace everything.
>
> Use it in any project using these libraries.

- **Pin versions** in `pyproject.toml` / `uv.lock` ([11](11_uv.md)); these libraries change often.
- Keep **your business logic** outside framework classes (plain functions / services).
- Make **prompts visible** (files / constants), not buried in defaults; log the final prompt sent.
- Turn on **tracing** from day one ([34](34_evals-observability.md)).
- Write **evals** so you can swap frameworks or models safely.

## 15. Troubleshooting

| Problem | Fix |
|---|---|
| Code from a tutorial fails with `ImportError` / `AttributeError` | Framework API changed; check the version the tutorial used vs installed (`pip show <pkg>`), read current docs |
| Hard to see what prompt was sent | Enable tracing / debug logging (LangSmith, Logfire, OpenAI traces, Langfuse) |
| Agent loops or ignores tools | Same fixes as raw agents: better tool descriptions, step limits ([31](31_ai-agents.md)) |
| Too slow / too many LLM calls | Framework defaults may add calls (query rewriting, reflection); disable or simplify |
| Wrong provider / key used | Check model string (`provider:model`) and env vars |
| Dependency conflicts | Use a fresh venv / uv project; pin compatible versions |
| Claude Agent SDK tool not allowed | Add it to `allowed_tools` (MCP tools: `mcp__<server>__<tool>`) |
| State lost between runs (LangGraph) | Use a checkpointer and the same `thread_id` |

## 16. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Choose

(a) coding agent that edits files and runs tests, (b) support flow with approval steps that must survive restarts, (c) RAG over 10,000 mixed documents.

<details markdown="1">
<summary>Solution</summary>

(a) Claude Agent SDK, (b) LangGraph (checkpoints + human-in-the-loop), (c) LlamaIndex (or raw code + a vector DB).

</details>

### Exercise 2: Minimal OpenAI Agents SDK agent

Create an agent with one function tool and run it synchronously.

<details markdown="1">
<summary>Solution</summary>

```python
from agents import Agent, Runner, function_tool


@function_tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


print(Runner.run_sync(Agent(name="Calc", instructions="Use tools for maths.", tools=[add]), "What is 2+40?").final_output)
```

</details>

---

<!-- nav:start -->
**Previous:** [31 - AI Agents](31_ai-agents.md) | **Index:** [All guides](README.md) | **Next:** [33 - MCP (Model Context Protocol)](33_mcp.md)
<!-- nav:end -->
