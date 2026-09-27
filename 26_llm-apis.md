# 26 - LLM APIs

Quick reference for calling hosted LLMs from Python: the Anthropic (Claude) SDK in depth, the OpenAI SDK, streaming, structured outputs, vision and PDFs, thinking, caching, batches, token counting, errors and cost.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is an LLM API?

An LLM API is an HTTP endpoint where you send a conversation (messages) and get back the model's reply. Providers like Anthropic (Claude), OpenAI (GPT), Google (Gemini) and Azure OpenAI run the models on their GPUs; you pay per token. The official **SDKs** (`anthropic`, `openai` Python packages) wrap the HTTP details: authentication, retries, streaming, types.

### Mental model

```text
Your code                                   Provider (e.g. api.anthropic.com)
---------                                   ---------------------------------
client.messages.create(                     POST /v1/messages
    model=...,            ------------------>  pick model
    system=...,                                build context: system + tools + messages
    messages=[...],                            generate tokens until stop
    max_tokens=...,                            count tokens, bill you
)                         <------------------  JSON: content blocks, stop_reason, usage
response.content  -> list of blocks (text, thinking, tool_use ...)
response.stop_reason -> WHY it stopped (end_turn, max_tokens, tool_use, refusal ...)
response.usage    -> tokens in / out (= cost)
```

The API is **stateless**: each request must contain the full conversation you want the model to see. Your app is responsible for storing history, choosing what context to send, and handling the response.

### Why learn the raw API?

- Every framework (LangChain, agent SDKs) is built on these calls; knowing them makes debugging easy.
- Direct SDK code is often simpler and more reliable than a framework for most apps.
- You control cost, latency and behaviour precisely.

### Key terms

| Term | Meaning |
|---|---|
| API key | Secret that identifies and bills you; keep in env vars |
| Model ID | Exact model string, e.g. `claude-opus-5` |
| `max_tokens` | Hard cap on output tokens for this response |
| Content block | One piece of the response: `text`, `thinking`, `tool_use`, ... |
| Stop reason | Why generation ended |
| Usage | Input / output / cached token counts |
| Streaming | Receive tokens as they are generated (SSE) |
| Structured output | Response guaranteed to match a JSON schema |
| Prompt caching | Provider reuses a repeated prompt prefix: cheaper and faster |
| Batch API | Async bulk processing at lower cost |
| Rate limit | Max requests / tokens per minute for your account |

**Where it fits:** concepts in [25 - LLM Fundamentals](25_llm-fundamentals.md); HTTP basics in [08 - HTTP and APIs](08_http-apis.md); schemas via [12 - Pydantic](12_pydantic.md); prompting in [27](27_prompt-engineering.md); tools in [28](28_tool-use.md); serving your own API with [39 - FastAPI](39_fastapi.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Claude API documentation | https://platform.claude.com/docs |
| Anthropic Python SDK | https://github.com/anthropics/anthropic-sdk-python |
| Models overview | https://platform.claude.com/docs/en/about-claude/models/overview |
| Streaming | https://platform.claude.com/docs/en/build-with-claude/streaming |
| Structured outputs | https://platform.claude.com/docs/en/build-with-claude/structured-outputs |
| Prompt caching | https://platform.claude.com/docs/en/build-with-claude/prompt-caching |
| Adaptive thinking | https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking |
| Batch processing | https://platform.claude.com/docs/en/build-with-claude/batch-processing |
| Vision / PDF support | https://platform.claude.com/docs/en/build-with-claude/vision |
| Errors and rate limits | https://platform.claude.com/docs/en/api/errors |
| OpenAI API docs | https://platform.openai.com/docs |
| OpenAI Python SDK | https://github.com/openai/openai-python |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Setup and API Keys](#1-setup-and-api-keys)
2. [Claude Models](#2-claude-models)
3. [First Request (Claude)](#3-first-request-claude)
4. [The Response Object](#4-the-response-object)
5. [System Prompts](#5-system-prompts)
6. [Multi-Turn Conversations](#6-multi-turn-conversations)
7. [Streaming](#7-streaming)
8. [Structured Outputs (JSON)](#8-structured-outputs-json)
9. [Images and PDFs](#9-images-and-pdfs)
10. [Thinking and Effort](#10-thinking-and-effort)
11. [Prompt Caching](#11-prompt-caching)
12. [Token Counting and Cost](#12-token-counting-and-cost)
13. [Batch Processing](#13-batch-processing)
14. [Errors, Retries and Timeouts](#14-errors-retries-and-timeouts)
15. [Stop Reasons and Refusals](#15-stop-reasons-and-refusals)
16. [Async Client](#16-async-client)
17. [Tool Use (Preview)](#17-tool-use-preview)
18. [OpenAI SDK Equivalents](#18-openai-sdk-equivalents)
19. [Provider-Agnostic Design](#19-provider-agnostic-design)
20. [Claude on Cloud Platforms](#20-claude-on-cloud-platforms)
21. [Production Checklist](#21-production-checklist)
22. [Troubleshooting](#22-troubleshooting)
23. [Try It](#23-try-it)

---

## 0. Flags and Parameters

> - **What:** The parameters of `client.messages.create(...)`.
> - **How:** Keyword arguments; only `model`, `max_tokens` and `messages` are required.
> - **When to use:** You see a request with `system=`, `thinking=`, `output_config=`, `cache_control=` and want to know what each does.

```text
client.messages.create(model="claude-opus-5", max_tokens=16000, system="...", messages=[...])
       |        |      |                      |                 |            |
       |        |      |                      |                 |            +-- conversation so far
       |        |      |                      |                 +--------------- behaviour instructions
       |        |      |                      +--------------------------------- hard cap on OUTPUT tokens
       |        |      +-------------------------------------------------------- which model
       |        +--------------------------------------------------------------- create a message (one request)
       +------------------------------------------------------------------------ Messages API
```

| Parameter | Meaning |
|---|---|
| `model` | Model ID (section 2) |
| `max_tokens` | Max output tokens; too low truncates answers (`stop_reason="max_tokens"`) |
| `messages` | List of `{"role": "user" / "assistant", "content": ...}` |
| `system` | System prompt (string or list of blocks) |
| `tools`, `tool_choice` | Functions the model may call ([28](28_tool-use.md)) |
| `thinking` | Reasoning config, e.g. `{"type": "adaptive"}` |
| `output_config` | `{"effort": "low" .. "max"}`, `{"format": {json schema}}` |
| `cache_control` | `{"type": "ephemeral"}` to cache the prompt prefix |
| `stop_sequences` | Custom strings that end generation |
| `metadata` | e.g. `{"user_id": "..."}` for abuse tracking |
| `temperature`, `top_p`, `top_k` | Sampling; not accepted by some newest models (use effort / prompting) |

---

## 1. Setup and API Keys

> - **What:** Installing the SDK and authenticating.
> - **How:** Get a key from the provider console; store it in an environment variable; the SDK reads it automatically.
> - **When to use:** Once per project / machine.

```powershell
pip install anthropic openai python-dotenv          # or: uv add anthropic openai python-dotenv
$env:ANTHROPIC_API_KEY = "sk-ant-..."               # session only; better: put it in .env
```

```text
# .env (git-ignored)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

```python
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY
```

Never hard-code keys, commit `.env`, or put keys in frontend code. Set spend limits in the provider console.

## 2. Claude Models

> - **What:** The model IDs you pass as `model`.
> - **How:** Pick by capability vs cost vs speed; use exact IDs (no date suffixes for current models).
> - **When to use:** Every request. Prices and models change: check the provider's models page / Models API.

| Model | ID | Context | Input / Output $ per 1M tokens* | Use for |
|---|---|---|---|---|
| Claude Fable 5.1 | `claude-fable-5-1` | 1M | $10 / $50 | Hardest reasoning, long-horizon agentic work |
| Claude Opus 5 | `claude-opus-5` | 1M | $5 / $25 | Default for complex tasks, coding, agents |
| Claude Sonnet 5 | `claude-sonnet-5` | 1M | $2 / $10 | High-volume production, good quality / price |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 200K | $1 / $5 | Fast, simple tasks, classification, sub-agents |

\*As of mid-2026; always check current pricing.

```python
client.models.list()                              # available models
client.models.retrieve("claude-opus-5")           # context window (max_input_tokens), max_tokens, capabilities
```

## 3. First Request (Claude)

> - **What:** The minimal working call.
> - **How:** `messages.create` with a model, an output limit and one user message.
> - **When to use:** Starting point for any feature.

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Explain RAG in two sentences."}],
)

for block in response.content:
    if block.type == "text":
        print(block.text)
```

## 4. The Response Object

> - **What:** What comes back from the API.
> - **How:** A `Message` with a list of content blocks, a stop reason and token usage.
> - **When to use:** Reading answers, handling tool calls, tracking cost.

```python
response.id                 # "msg_..."
response.model              # model that answered
response.content            # [TextBlock(type="text", text="..."), ...]
response.stop_reason        # "end_turn" | "max_tokens" | "tool_use" | "refusal" | ...
response.usage.input_tokens
response.usage.output_tokens
response.usage.cache_read_input_tokens
response._request_id        # quote this when reporting a problem
response.to_dict()          # plain dict

text = "".join(b.text for b in response.content if b.type == "text")   # all text blocks
```

Always check `block.type` before reading `.text`: responses can contain `thinking` and `tool_use` blocks too.

## 5. System Prompts

> - **What:** Instructions that shape the model's behaviour for the whole conversation.
> - **How:** Pass `system="..."`; it is placed before the messages.
> - **When to use:** Role, rules, tone, output format, background knowledge.

```python
response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    system=(
        "You are a support assistant for Acme Bikes.\n"
        "Answer only questions about Acme products and orders.\n"
        "If you don't know, say so and offer to connect a human.\n"
        "Keep answers under 120 words."
    ),
    messages=[{"role": "user", "content": "Do you ship to Austria?"}],
)
```

How to write good system prompts: [27 - Prompt Engineering](27_prompt-engineering.md).

## 6. Multi-Turn Conversations

> - **What:** Chat with memory.
> - **How:** Keep a list of messages; append each user message and each assistant reply; send the whole list every time.
> - **When to use:** Chatbots, assistants, any back-and-forth.

```python
history = []


def chat(user_text: str) -> str:
    """Send a message with full history and return the reply."""
    history.append({"role": "user", "content": user_text})
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=16000,
        system="You are a friendly tutor.",
        messages=history,
    )
    history.append({"role": "assistant", "content": response.content})   # keep full content blocks
    return "".join(b.text for b in response.content if b.type == "text")


chat("My name is Ana.")
chat("What's my name?")          # "Your name is Ana."
```

- The first message must be `user`; roles normally alternate.
- History grows every turn -> more tokens -> more cost. Trim, summarise or use caching / compaction for long chats.

## 7. Streaming

> - **What:** Receiving the answer token by token as it is generated.
> - **How:** `client.messages.stream(...)` as a context manager; iterate `text_stream`; get the full message at the end.
> - **When to use:** Chat UIs (text appears instantly), long outputs (avoids HTTP timeouts), large `max_tokens`.

```python
with client.messages.stream(
    model="claude-opus-5",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Write a short story about a robot chef."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()       # complete Message with usage and stop_reason

print("\n", final.usage.output_tokens)
```

Stream from your own backend to a browser with FastAPI `StreamingResponse` ([39](39_fastapi.md)) or a UI library ([38](38_ai-ui.md)).

## 8. Structured Outputs (JSON)

> - **What:** Getting output that is guaranteed to match a schema, parsed into Python objects.
> - **How:** Pass a Pydantic model to `messages.parse(...)` (or a raw JSON schema via `output_config`); the API constrains generation to the schema.
> - **When to use:** Extraction, classification, anything your code reads. More reliable than "please reply in JSON".

```python
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    category: str = Field(description="billing, technical or shipping")
    urgency: int = Field(ge=1, le=5)
    summary: str


response = client.messages.parse(
    model="claude-opus-5",
    max_tokens=16000,
    messages=[{"role": "user", "content": f"Classify this support email:\n\n{email_text}"}],
    output_format=Ticket,
)
ticket = response.parsed_output            # Ticket instance
ticket.category, ticket.urgency
```

Raw schema version:

```python
import json

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Extract name and email: Jane Doe, jane@co.com"}],
    output_config={"format": {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "email": {"type": "string"}},
            "required": ["name", "email"],
            "additionalProperties": False,
        },
    }},
)
data = json.loads(next(b.text for b in response.content if b.type == "text"))
```

## 9. Images and PDFs

> - **What:** Sending images and documents for the model to read.
> - **How:** Content becomes a list of blocks: `image` / `document` blocks (base64 or URL) plus a `text` block with your question.
> - **When to use:** Invoices, screenshots, charts, contracts, scanned forms.

```python
import base64
from pathlib import Path


def b64(path: str) -> str:
    return base64.standard_b64encode(Path(path).read_bytes()).decode("utf-8")


response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64("chart.png")}},
            {"type": "text", "text": "What trend does this chart show?"},
        ],
    }],
)

pdf_message = {
    "role": "user",
    "content": [
        {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64("contract.pdf")}},
        {"type": "text", "text": "List the termination clauses."},
    ],
}
```

Also: `{"type": "image", "source": {"type": "url", "url": "https://..."}}`. The Files API (`client.files.upload(...)`) lets you upload once and reference by `file_id`.

## 10. Thinking and Effort

> - **What:** Letting the model reason before answering, and controlling how hard it works.
> - **How:** `thinking={"type": "adaptive"}` lets the model decide when and how much to think; `output_config={"effort": ...}` trades quality for cost / speed.
> - **When to use:** High effort for complex reasoning, coding, agents; low effort for simple, high-volume tasks.

```python
response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    thinking={"type": "adaptive", "display": "summarized"},   # show a summary of the reasoning
    output_config={"effort": "high"},                          # low | medium | high | xhigh | max
    messages=[{"role": "user", "content": "Plan a 3-step migration from pandas to Polars for a 2 GB ETL job."}],
)
for block in response.content:
    if block.type == "thinking":
        print("THINKING:", block.thinking)
    elif block.type == "text":
        print("ANSWER:", block.text)
```

- Thinking tokens are billed as output tokens.
- On current Claude models thinking is adaptive; old `budget_tokens` settings are deprecated / rejected on the newest models.
- Pass thinking blocks back unchanged in history when continuing a conversation with the same model.

## 11. Prompt Caching

> - **What:** The provider remembers a long, repeated prompt prefix so later requests read it from cache.
> - **How:** Mark the prompt with `cache_control`; identical prefix = cache hit (about 10% of normal input price, faster). Any change in the prefix breaks the cache from that point.
> - **When to use:** Long system prompts, big documents asked about repeatedly, agents and chats that resend history.

```python
response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    cache_control={"type": "ephemeral"},            # cache the prompt prefix automatically
    system=long_policy_document,                     # e.g. 50 pages, same for every question
    messages=[{"role": "user", "content": question}],
)
response.usage.cache_creation_input_tokens   # written to cache (first call)
response.usage.cache_read_input_tokens       # read from cache (later calls)
```

- Put **stable** content first (system prompt, tools, documents), **changing** content last (the question).
- Do not put timestamps or random IDs in the system prompt; they break the cache on every call.
- Default cache lifetime is 5 minutes (refreshed on each hit); a 1-hour option exists.

## 12. Token Counting and Cost

> - **What:** Knowing how many tokens a request uses before and after sending it.
> - **How:** `count_tokens` for estimates; `response.usage` for actuals.
> - **When to use:** Budgeting, guarding context limits, choosing chunk sizes.

```python
count = client.messages.count_tokens(
    model="claude-opus-5",
    system=system_prompt,
    messages=messages,
)
count.input_tokens

INPUT_PRICE_PER_M = 5.00           # USD, check current pricing
OUTPUT_PRICE_PER_M = 25.00
u = response.usage
cost = u.input_tokens / 1e6 * INPUT_PRICE_PER_M + u.output_tokens / 1e6 * OUTPUT_PRICE_PER_M
```

Log `usage` for every call in production; it is your cost dashboard.

## 13. Batch Processing

> - **What:** Submitting many requests at once for asynchronous processing at a discount (about 50%).
> - **How:** Create a batch of requests with your own `custom_id`s, poll until it has ended, then read the results.
> - **When to use:** Offline jobs: classify 50,000 reviews, nightly summaries, eval runs. Not for real-time users.

```python
import time

batch = client.messages.batches.create(requests=[
    {
        "custom_id": f"review-{i}",
        "params": {
            "model": "claude-opus-5",
            "max_tokens": 256,
            "messages": [{"role": "user", "content": f"Sentiment (positive/negative/neutral) only:\n{text}"}],
        },
    }
    for i, text in enumerate(reviews)
])

while client.messages.batches.retrieve(batch.id).processing_status != "ended":
    time.sleep(60)

for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        label = result.result.message.content[0].text
        save(result.custom_id, label)            # results come in ANY order: key by custom_id
```

## 14. Errors, Retries and Timeouts

> - **What:** Handling failures correctly.
> - **How:** The SDK retries 408 / 409 / 429 / 5xx and connection errors automatically (default 2 retries); catch specific exception classes for the rest.
> - **When to use:** Every production call.

```python
import anthropic

client = anthropic.Anthropic(max_retries=4, timeout=120.0)     # seconds

try:
    response = client.messages.create(...)
except anthropic.BadRequestError as e:          # 400: fix the request (bad params, too long)
    logger.error("bad request: %s", e.message)
except anthropic.AuthenticationError:           # 401: wrong / missing key
    raise
except anthropic.NotFoundError:                 # 404: wrong model ID
    raise
except anthropic.RateLimitError as e:           # 429 after retries: slow down
    wait = int(e.response.headers.get("retry-after", "60"))
except anthropic.APIStatusError as e:           # other HTTP errors (5xx after retries)
    logger.error("API error %s", e.status_code)
except anthropic.APIConnectionError:            # network problem
    logger.error("network error")
```

Per-request override: `client.with_options(timeout=30, max_retries=5).messages.create(...)`.

## 15. Stop Reasons and Refusals

> - **What:** Why the model stopped, which decides what your code does next.
> - **How:** Check `response.stop_reason` before using the content.
> - **When to use:** Every response in production code.

| `stop_reason` | Meaning | Your code should |
|---|---|---|
| `end_turn` | Finished normally | Use the answer |
| `max_tokens` | Hit your `max_tokens` cap; answer cut off | Raise `max_tokens`, stream, or ask to continue |
| `stop_sequence` | Hit one of your `stop_sequences` | Use the answer |
| `tool_use` | Wants to call a tool | Run the tool, send the result back ([28](28_tool-use.md)) |
| `pause_turn` | Long server-side tool turn paused | Send the response back to let it continue |
| `refusal` | Declined for safety reasons | Show a polite message; see `response.stop_details` |

The newest Claude models support server-side **fallbacks**: on a refusal, the API retries automatically on another model inside the same call (beta: `client.beta.messages.create(..., betas=["server-side-fallback-2026-07-01"], fallbacks="default")`). Check the docs for current details.

## 16. Async Client

> - **What:** The same API for async code.
> - **How:** `AsyncAnthropic` + `await`; combine with `asyncio.gather` and a semaphore for concurrency.
> - **When to use:** FastAPI endpoints, processing many inputs in parallel. See [13 - Async Python](13_async-python.md).

```python
import asyncio

import anthropic

aclient = anthropic.AsyncAnthropic()


async def ask(q: str) -> str:
    r = await aclient.messages.create(model="claude-opus-5", max_tokens=16000,
                                      messages=[{"role": "user", "content": q}])
    return "".join(b.text for b in r.content if b.type == "text")


answers = asyncio.run(asyncio.gather(*(ask(q) for q in questions)))   # use a Semaphore for many
```

## 17. Tool Use (Preview)

> - **What:** Letting the model call your Python functions.
> - **How:** Describe functions as tools; the model returns a `tool_use` block; you run the function and send back a `tool_result`; repeat until done.
> - **When to use:** Live data, calculations, actions. Full guide: [28 - Tool Use](28_tool-use.md).

```python
from anthropic import beta_tool


@beta_tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order.

    Args:
        order_id: Order number like A-1042.
    """
    return lookup_status(order_id)


runner = client.beta.messages.tool_runner(
    model="claude-opus-5",
    max_tokens=16000,
    tools=[get_order_status],
    messages=[{"role": "user", "content": "Where is order A-1042?"}],
)
for message in runner:          # the SDK runs the tool loop for you
    final = message
```

## 18. OpenAI SDK Equivalents

> - **What:** The same tasks with the OpenAI Python SDK.
> - **How:** OpenAI has the newer **Responses API** and the older, widely copied **Chat Completions API**; both are shown.
> - **When to use:** Projects using GPT models, Azure OpenAI, or OpenAI-compatible servers (Ollama, vLLM). Model names change often; check the current list.

```python
import os

from openai import OpenAI

client = OpenAI()                                    # reads OPENAI_API_KEY
MODEL = os.environ["OPENAI_MODEL"]                   # set to a current model name

# Responses API
resp = client.responses.create(
    model=MODEL,
    instructions="You are concise.",                 # like a system prompt
    input="Explain RAG in two sentences.",
)
print(resp.output_text)

# Chat Completions API (very common in tutorials and compatible servers)
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are concise."},
        {"role": "user", "content": "Explain RAG in two sentences."},
    ],
)
print(resp.choices[0].message.content)
print(resp.usage.prompt_tokens, resp.usage.completion_tokens)

# Streaming (Chat Completions)
for chunk in client.chat.completions.create(model=MODEL, messages=msgs, stream=True):
    print(chunk.choices[0].delta.content or "", end="")

# Structured output with Pydantic
parsed = client.responses.parse(model=MODEL, input="Extract: Jane, jane@co.com", text_format=Contact)
parsed.output_parsed
```

| Concept | Anthropic | OpenAI (Chat Completions) |
|---|---|---|
| System prompt | `system=` parameter | message with `role: "system"` |
| Output limit | `max_tokens` (required) | `max_completion_tokens` / `max_output_tokens` (optional) |
| Answer text | `content` blocks with `type == "text"` | `choices[0].message.content` |
| Tool call signal | `stop_reason == "tool_use"` | `finish_reason == "tool_calls"` |
| Tokens used | `usage.input_tokens / output_tokens` | `usage.prompt_tokens / completion_tokens` |
| Local / compatible servers | Anthropic SDK | `OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")` |

## 19. Provider-Agnostic Design

> - **What:** Structuring code so the model provider can change without rewriting the app.
> - **How:** Put LLM calls behind one small interface in your code; keep prompts and model names in config.
> - **When to use:** Apps that may switch models, compare providers in evals, or use local and cloud models.

```python
from typing import Protocol


class LLM(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class ClaudeLLM:
    """LLM implementation backed by the Anthropic SDK."""

    def __init__(self, client, model: str):
        self.client, self.model = client, model

    def complete(self, system: str, user: str) -> str:
        r = self.client.messages.create(model=self.model, max_tokens=16000, system=system,
                                        messages=[{"role": "user", "content": user}])
        return "".join(b.text for b in r.content if b.type == "text")
```

Libraries like LiteLLM or LangChain offer one interface for many providers ([32](32_agent-frameworks.md)); the trade-off is an extra dependency and hidden details.

## 20. Claude on Cloud Platforms

> - **What:** Using Claude through AWS, Google Cloud or Microsoft Azure.
> - **How:** Dedicated client classes with the same `messages.create` interface; model IDs and auth follow the platform.
> - **When to use:** Your company's data or billing must stay in one cloud.

| Platform | Python client |
|---|---|
| Amazon Bedrock | `from anthropic import AnthropicBedrockMantle` -> `AnthropicBedrockMantle(aws_region="...")`, model IDs prefixed `anthropic.` |
| Google Vertex AI | `from anthropic import AnthropicVertex` -> `AnthropicVertex(project_id="...", region="global")` |
| Microsoft Foundry | `from anthropic import AnthropicFoundry` -> `AnthropicFoundry(api_key=..., resource="...")` |

Feature availability can differ per platform; check the platform docs.

## 21. Production Checklist

> - **What:** What to have in place before real users hit your LLM feature.
> - **How:** A list to review.
> - **When to use:** Before launch and in code review.

- [ ] Keys in env vars / Key Vault; spend limits set in the console
- [ ] Model ID and prompts in config, not scattered in code
- [ ] `max_tokens` large enough; streaming for long outputs
- [ ] Every `stop_reason` handled (`max_tokens`, `refusal`, `tool_use`)
- [ ] Timeouts, retries, and user-friendly error messages
- [ ] Structured outputs + validation where code consumes the output
- [ ] Prompt caching for long, repeated prefixes
- [ ] Logging of `usage`, latency, request IDs (no secrets / personal data in logs)
- [ ] Rate limiting / concurrency limits in your own API
- [ ] Evals for quality and regressions ([34](34_evals-observability.md))
- [ ] Guardrails against prompt injection and data leaks ([37](37_ai-security.md))

## 22. Troubleshooting

| Problem | Fix |
|---|---|
| `AuthenticationError` / 401 | Key not set in this process (`echo $env:ANTHROPIC_API_KEY`), typo, or revoked key |
| `NotFoundError` model | Use an exact current model ID (section 2) |
| Answer cut off mid-sentence | `stop_reason == "max_tokens"`: raise `max_tokens`, use streaming |
| `BadRequestError: prompt is too long` | Over the context window: trim history, fewer / shorter documents, summarise |
| `RateLimitError` / 429 | Lower concurrency, add backoff, request higher limits, use batches for bulk |
| 529 / overloaded | Temporary; SDK retries; add fallback model or retry later |
| Request times out | Stream long outputs; raise `timeout` |
| `AttributeError: 'ThinkingBlock' object has no attribute 'text'` | Filter blocks by `type == "text"` |
| JSON parse errors | Use structured outputs (`messages.parse` / `output_config.format`) |
| Cache never hits (`cache_read_input_tokens == 0`) | Prefix changes every call (timestamps, unsorted JSON, different tools); prefix too short |
| 400 about `temperature` / `budget_tokens` / prefill on new models | Newest models removed these; use effort / adaptive thinking / structured outputs |
| Costs higher than expected | Log `usage`; history growing each turn; large `max_tokens` on reasoning; use caching and smaller models for easy steps |

## 23. Try It

> - **What:** Short exercises to practise this guide.
> - **How:** Try each task yourself first, then open the solution.
> - **When to use:** Right after reading the guide, or later as a quick self-test.

### Exercise 1: First call with usage

Call Claude with a system prompt and print the text and the token usage. (Or run `uv run python -m llm_basics.basics` in `examples/`.)

<details markdown="1">
<summary>Solution</summary>

```python
r = client.messages.create(model="claude-opus-5", max_tokens=16000, system="Be concise.",
                           messages=[{"role": "user", "content": "What is an embedding?"}])
print("".join(b.text for b in r.content if b.type == "text"))
print(r.usage.input_tokens, r.usage.output_tokens)
```

</details>

### Exercise 2: Structured extraction

Extract name, email and company from free text into a Pydantic model.

<details markdown="1">
<summary>Solution</summary>

```python
class Contact(BaseModel):
    name: str
    email: str
    company: str | None = None

r = client.messages.parse(model="claude-opus-5", max_tokens=1024, output_format=Contact,
                          messages=[{"role": "user", "content": f"Extract the contact:\n{text}"}])
contact = r.parsed_output
```

</details>

### Exercise 3: Handle the edges

What should your code do for `stop_reason == "max_tokens"` and for `anthropic.RateLimitError`?

<details markdown="1">
<summary>Solution</summary>

`max_tokens`: the answer is cut off; raise `max_tokens`, stream, or ask the model to continue. `RateLimitError` (after the SDK's automatic retries): back off using the `retry-after` header, reduce concurrency, or move bulk work to the batch API.

</details>
