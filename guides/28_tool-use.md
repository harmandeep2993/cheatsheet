# 28 - Tool Use (Function Calling)

<!-- nav:start -->
**Previous:** [27 - Prompt Engineering](27_prompt-engineering.md) | **Index:** [All guides](../README.md) | **Next:** [29 - Embeddings and Vector Databases](29_embeddings-vector-db.md)
<!-- nav:end -->

Quick reference for letting LLMs call your functions: defining tools, the tool-call loop, the SDK tool runner, parallel calls, errors, server-side tools, and designing good tools.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is tool use?

**Tool use** (also called **function calling**) lets an LLM ask your program to run a function, such as looking up an order, querying a database, searching the web or sending an email. The model does **not** run the code itself. It returns a structured request ("call `get_order_status` with `order_id = A-1042`"); **your code** runs the function and sends the result back; the model then continues, possibly calling more tools, until it can answer.

This is how LLMs get **live data** and **take actions**, and it is the foundation of **agents**.

### Mental model: the model is the brain, your code is the hands

```text
User: "Where is my order A-1042, and when will it arrive?"

 YOUR APP                                   LLM
 --------                                   ---
 send: user message + tool list  -------->  reads the tool descriptions, decides it needs data
                                  <--------  stop_reason = "tool_use"
                                             tool_use: get_order_status({"order_id": "A-1042"})
 run get_order_status("A-1042")
   -> {"status": "shipped", "eta": "2026-09-30"}
 send: tool_result (same id)     -------->  reads the result
                                  <--------  stop_reason = "end_turn"
                                             "Your order shipped and should arrive on Sept 30."
```

The model only sees each tool's **name, description and input schema**. Those three things are its entire understanding of what the tool does, so writing them well is the most important part.

### Why use it?

- **Fresh and private data**: databases, APIs, files the model never saw in training.
- **Exact computation**: calculators, code execution, SQL instead of the model guessing numbers.
- **Actions**: create tickets, send messages, update records (with care).
- **Reliable structured input**: tool arguments follow your JSON schema.

### Key terms

| Term | Meaning |
|---|---|
| Tool | A function the model may call, described by name + description + input schema |
| Tool definition | The JSON description you send in `tools=[...]` |
| `tool_use` block | The model's request: tool name, input arguments and an `id` |
| `tool_result` block | Your answer, sent back with the matching `tool_use_id` |
| Tool loop / agentic loop | Repeat: model -> tools -> model until no more tool calls |
| Tool runner | SDK helper that runs the loop for you |
| `tool_choice` | Whether / which tool the model must use |
| Parallel tool calls | Several `tool_use` blocks in one response |
| Client tools | Run by your code |
| Server tools | Run by the provider (web search, code execution) |
| Strict tool use | Guarantees arguments match the schema exactly |

**Where it fits:** built on [26 - LLM APIs](26_llm-apis.md) and schemas from [12 - Pydantic](12_pydantic.md) / [07 - JSON Schema](07_yaml-json.md); the core of [31 - AI Agents](31_ai-agents.md); tools can be shared across apps with [33 - MCP](33_mcp.md); safety in [37 - AI Security](37_ai-security.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Claude tool use overview | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview |
| Structured outputs / strict tools | https://platform.claude.com/docs/en/build-with-claude/structured-outputs |
| Code execution tool | https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool |
| OpenAI function calling | https://platform.openai.com/docs/guides/function-calling |

---

## Contents

1. [Defining a Tool](#1-defining-a-tool)
2. [The Manual Tool Loop](#2-the-manual-tool-loop)
3. [Tool Runner (SDK Helper)](#3-tool-runner-sdk-helper)
4. [Tools from Pydantic Models](#4-tools-from-pydantic-models)
5. [Parallel Tool Calls](#5-parallel-tool-calls)
6. [Returning Errors](#6-returning-errors)
7. [tool_choice](#7-tool_choice)
8. [Strict Tool Use](#8-strict-tool-use)
9. [Server-Side Tools (Web Search, Code Execution)](#9-server-side-tools-web-search-code-execution)
10. [Designing Good Tools](#10-designing-good-tools)
11. [Tool Descriptions That Work](#11-tool-descriptions-that-work)
12. [Common Tool Types](#12-common-tool-types)
13. [Safety: Confirmations and Limits](#13-safety-confirmations-and-limits)
14. [Tool Use in OpenAI (Comparison)](#14-tool-use-in-openai-comparison)
15. [Debugging Tool Calls](#15-debugging-tool-calls)
16. [Troubleshooting](#16-troubleshooting)
17. [Try It](#17-try-it)

---

## 1. Defining a Tool

> Describing a function so the model knows when and how to call it. A dict with `name`, `description` and `input_schema` (JSON Schema of the arguments).
>
> Use it in every tool you expose.

```python
get_order_status_tool = {
    "name": "get_order_status",
    "description": (
        "Look up the current shipping status and estimated delivery date of a customer order. "
        "Use this whenever the user asks where an order is or when it will arrive. "
        "Returns status (processing, shipped, delivered, cancelled) and eta (YYYY-MM-DD or null)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "Order number, format A-1234"},
        },
        "required": ["order_id"],
    },
}
```

## 2. The Manual Tool Loop

> Running tools yourself and feeding results back until the model is done. Call the API with `tools`; while `stop_reason == "tool_use"`, run each requested tool, append the assistant message and a user message with all `tool_result`s, and call again.
>
> Use it when you want full control (custom logging, approvals, non-standard flows). Otherwise use the tool runner (section 3).

```python
import json

import anthropic

client = anthropic.Anthropic()


def get_order_status(order_id: str) -> dict:
    return {"order_id": order_id, "status": "shipped", "eta": "2026-09-30"}   # real lookup here


TOOLS = [get_order_status_tool]
HANDLERS = {"get_order_status": get_order_status}
MAX_TURNS = 10                                  # safety cap so a loop cannot run forever

messages = [{"role": "user", "content": "Where is my order A-1042?"}]

for _ in range(MAX_TURNS):
    response = client.messages.create(
        model="claude-opus-5", max_tokens=16000, tools=TOOLS, messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content})   # keep tool_use blocks

    if response.stop_reason != "tool_use":
        break

    results = []
    for block in response.content:
        if block.type == "tool_use":
            output = HANDLERS[block.name](**block.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,               # must match the request
                "content": json.dumps(output),
            })
    messages.append({"role": "user", "content": results})   # ALL results in ONE user message

answer = "".join(b.text for b in response.content if b.type == "text")
```

## 3. Tool Runner (SDK Helper)

> The SDK runs the tool loop for you. Decorate plain Python functions with `@beta_tool`; the schema is generated from type hints and the docstring; iterate the runner until done.
>
> Use it in most tool-using apps; less code and fewer loop bugs.

```python
import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()


@beta_tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status and estimated delivery date of an order.

    Args:
        order_id: Order number, format A-1234.
    """
    return '{"status": "shipped", "eta": "2026-09-30"}'


@beta_tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount between currencies using today's rate.

    Args:
        amount: Amount to convert.
        from_currency: ISO code, e.g. EUR.
        to_currency: ISO code, e.g. USD.
    """
    return str(round(amount * get_rate(from_currency, to_currency), 2))


runner = client.beta.messages.tool_runner(
    model="claude-opus-5",
    max_tokens=16000,
    tools=[get_order_status, convert_currency],
    messages=[{"role": "user", "content": "Where is A-1042, and what is 50 EUR in USD?"}],
)
for message in runner:            # each iteration = one model response
    last = message
print("".join(b.text for b in last.content if b.type == "text"))
```

Async version: `@beta_async_tool` with `async def`. Note the tool runner is a beta helper; check the SDK docs for current behaviour.

## 4. Tools from Pydantic Models

> Generating the input schema from a Pydantic model. `Model.model_json_schema()` gives the schema; validate the model's input with the same model before running.
>
> Use it for tools with many or complex arguments; shared validation.

```python
from pydantic import BaseModel, Field


class SearchOrders(BaseModel):
    """Search orders by customer and status."""

    customer_email: str = Field(description="Customer email address")
    status: str | None = Field(None, description="processing, shipped, delivered or cancelled")
    limit: int = Field(10, ge=1, le=50)


search_tool = {
    "name": "search_orders",
    "description": SearchOrders.__doc__ + " Use when the user asks about several orders.",
    "input_schema": SearchOrders.model_json_schema(),
}

args = SearchOrders.model_validate(tool_use_block.input)     # validate before running
```

## 5. Parallel Tool Calls

> The model requesting several tools in one response. The response contains multiple `tool_use` blocks; run them (concurrently if possible) and return all results together.
>
> Use it for independent lookups ("weather in Paris and Berlin").

- Return **all** `tool_result` blocks in **one** user message, each with its matching `tool_use_id`.
- Splitting results across several messages teaches the model to stop making parallel calls.
- Run independent tools concurrently with `asyncio.gather` ([13](13_async-python.md)).

## 6. Returning Errors

> Telling the model that a tool failed, so it can recover. Return a `tool_result` with `is_error: True` and a helpful message; never drop the result.
>
> Use it for invalid input, not found, timeouts, permission denied.

```python
try:
    output = HANDLERS[block.name](**block.input)
    result = {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(output)}
except KeyError:
    result = {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
              "content": f"Unknown tool {block.name}"}
except OrderNotFound:
    result = {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
              "content": "Order not found. Ask the user to check the order number (format A-1234)."}
```

Good error messages say what went wrong **and what to do next**; the model will often fix its input and retry.

## 7. tool_choice

> Controlling whether the model must use tools. `tool_choice={"type": "auto"}` (default: model decides), `{"type": "none"}` (no tools), and on some models `{"type": "any"}` / `{"type": "tool", "name": ...}` to force a call. Usually leave `auto`; steer with the prompt ("Always check the order status before answering").

Some of the newest models do not support forced tool use; for guaranteed structured output use structured outputs instead ([26](26_llm-apis.md) section 8). `disable_parallel_tool_use: true` limits the model to one call at a time.

## 8. Strict Tool Use

> Guaranteeing the tool arguments match your schema exactly. Add `"strict": True` to the tool definition; the schema needs `additionalProperties: false` and a `required` list.
>
> Use it for tools where invalid arguments would break things (bookings, payments, DB writes).

```python
book_flight_tool = {
    "name": "book_flight",
    "description": "Book a flight for the user after they confirmed the details.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "destination": {"type": "string"},
            "date": {"type": "string", "format": "date"},
            "passengers": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6]},
        },
        "required": ["destination", "date", "passengers"],
        "additionalProperties": False,
    },
}
```

## 9. Server-Side Tools (Web Search, Code Execution)

> Tools that the provider runs on its own servers. Declare them in `tools` with their special `type`; results come back inside the same response, no loop code needed.
>
> Use it for current information from the web, running Python for data analysis, fetching a URL.

```python
response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}],
    messages=[{"role": "user", "content": "What changed in the latest pandas release?"}],
)

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    tools=[{"type": "code_execution_20260120", "name": "code_execution"}],
    messages=[{"role": "user", "content": "Compute the mean and std of [3, 7, 9, 12, 20]."}],
)
```

Tool type strings are versioned (date suffix) and change over time; copy them from current docs. A long server-tool turn may end with `stop_reason == "pause_turn"`: send the response back to let it continue.

## 10. Designing Good Tools

> Principles for tools the model uses correctly. Few, clear, well-described tools that return concise, useful results.
>
> Use it for designing any tool set, especially for agents.

| Principle | Why |
|---|---|
| One clear job per tool | Easier for the model to choose correctly |
| Few tools (start with < 10) | Many similar tools confuse the choice |
| Descriptive names (`search_orders`, not `tool2`) | Name is part of the "documentation" |
| Detailed descriptions | Say what it does, when to use it, what it returns, limitations |
| Simple, typed parameters with descriptions and formats | Fewer invalid calls |
| Return concise, relevant data (not huge raw dumps) | Saves context and helps reasoning |
| Include IDs / next-step hints in results | Model can chain calls |
| Helpful error messages | Model can self-correct |
| Idempotent, safe reads by default | Retries do no harm |
| Separate read tools from write tools | Easier to gate risky actions |

## 11. Tool Descriptions That Work

> Writing the text the model reads to decide on a tool. 3 to 5 sentences: purpose, when to use (and when not), argument meanings, return format, caveats.
>
> Use it in every tool; this matters more than the code.

```text
Weak:    "Gets customer data."

Strong:  "Retrieve a customer's profile (name, email, plan, signup date, open tickets count)
          by customer ID or email. Use this before answering questions about a customer's
          account or plan. Do not use it for order questions (use search_orders).
          Exactly one of customer_id or email must be given. Returns null fields when unknown."
```

## 12. Common Tool Types

> Tools most AI apps end up with. Pick the ones your use case needs.
>
> Use it for planning an assistant or agent.

| Tool | Example | Notes |
|---|---|---|
| Retrieval / search | `search_docs(query)` | The "R" in agentic RAG ([30](30_rag.md)) |
| Database query | `run_sql(query)` | Read-only user, row limits, allow-listed tables |
| API lookup | `get_weather(city)` | Wrap third-party APIs, hide keys |
| Calculator / code | `calculate(expression)`, code execution | Exact maths |
| Web search / fetch | server tools | Fresh information |
| File operations | `read_file(path)` | Restrict to a folder |
| Actions | `create_ticket(...)`, `send_email(...)` | Require confirmation |
| Memory | `save_note(text)`, `recall(query)` | Long-term agent memory |
| Handoff | `transfer_to_human(reason)` | Escalation path |

## 13. Safety: Confirmations and Limits

> Preventing tools from doing damage. Least privilege, human approval for risky actions, input validation, rate and loop limits.
>
> Use it in any tool that writes, deletes, pays, sends or runs code.

- **Validate** every argument in your code (the model can be wrong or manipulated).
- **Human-in-the-loop**: for write actions, return "needs confirmation" and ask the user before executing.
- **Least privilege**: read-only DB users, scoped API tokens, sandboxed file paths.
- **Limits**: max tool calls per request, timeouts, cost budgets.
- **Prompt injection**: tool results (web pages, emails, documents) can contain instructions; treat them as data, never as commands ([37](37_ai-security.md)).
- **Log** every tool call with inputs and outputs for audit.

## 14. Tool Use in OpenAI (Comparison)

> The same concept in the OpenAI API. Tools are passed as `tools=[{"type": "function", ...}]`; calls come back as `tool_calls` (Chat Completions) or `function_call` items (Responses API).
>
> Use it for porting code between providers.

| Concept | Anthropic | OpenAI Chat Completions |
|---|---|---|
| Schema key | `input_schema` | `function.parameters` |
| Model asks for a tool | `stop_reason == "tool_use"`, `tool_use` blocks | `finish_reason == "tool_calls"`, `message.tool_calls` |
| Arguments | `block.input` (dict) | `tool_call.function.arguments` (JSON string -> `json.loads`) |
| Send result | user message with `tool_result` + `tool_use_id` | message with `role: "tool"` + `tool_call_id` |

## 15. Debugging Tool Calls

> Finding out why the model called the wrong tool, wrong arguments, or no tool. Log the full request (tools + messages) and every `tool_use` / `tool_result`; replay failing cases.
>
> Use it in any unexpected behaviour.

- Print each `tool_use` block: name, input, id.
- Check the description: would a new colleague know when to use this tool?
- Add an example to the system prompt of when to use it.
- Use tracing tools (Langfuse, LangSmith, OpenTelemetry) to see the whole loop ([34](34_evals-observability.md)).

## 16. Troubleshooting

| Problem | Fix |
|---|---|
| Model never calls the tool | Improve description ("use this whenever..."); mention it in the system prompt; check the tool is in `tools` |
| Calls the wrong tool | Make tools more distinct; say when NOT to use each |
| Invalid / missing arguments | Better parameter descriptions and formats; `strict: True`; return a helpful error |
| `tool_use ids were found without tool_result blocks` | Every `tool_use` needs a matching `tool_result` in the next user message |
| `tool_result` block errors | Put tool results in a `user` message, right after the assistant message with the `tool_use` |
| Loop never ends | Add a max-turns cap; return clear results; check the model gets the data it needs |
| Model stops making parallel calls | Send all results in one message |
| Tool output too large (context full) | Summarise / paginate results; return only needed fields |
| JSON parsing of tool input fails | Use `block.input` (already a dict) or `json.loads`, never string matching |
| Server tool answer truncated | Handle `stop_reason == "pause_turn"` by sending the response back |

## 17. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Define a tool

Write a tool definition for `get_weather(city, unit)` where unit is celsius or fahrenheit.

<details markdown="1">
<summary>Solution</summary>

```python
{
    "name": "get_weather",
    "description": "Get the current weather for a city. Use when the user asks about weather now.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. Berlin"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["city"],
    },
}
```

</details>

### Exercise 2: Loop rules

Why must all `tool_result` blocks go back in one user message, and what is `is_error` for?

<details markdown="1">
<summary>Solution</summary>

One message per turn keeps the pairing with the `tool_use` blocks clear and keeps parallel tool calling working; splitting results teaches the model to stop calling tools in parallel. `is_error: true` tells the model a call failed (with a helpful message) so it can correct its input or try something else instead of trusting a bad result.

</details>

### Exercise 3: Add a tool to the example agent

In `examples/tool_agent/tools.py`, add a `get_delivery_cost(country)` tool and a test for it.

<details markdown="1">
<summary>Solution</summary>

Add the function, its schema to `TOOLS` and its entry to `HANDLERS`; then in `test_agent.py`:

```python
def test_delivery_cost():
    assert get_delivery_cost("AT") == "9.95 EUR"
```

Run `uv run pytest tool_agent`.

</details>

---

<!-- nav:start -->
**Previous:** [27 - Prompt Engineering](27_prompt-engineering.md) | **Index:** [All guides](../README.md) | **Next:** [29 - Embeddings and Vector Databases](29_embeddings-vector-db.md)
<!-- nav:end -->
