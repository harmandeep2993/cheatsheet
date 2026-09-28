# 27 - LLM APIs

<!-- nav:start -->
**Previous:** [26 - LLM Fundamentals](26_llm-fundamentals.md) | **Index:** [All guides](../README.md) | **Next:** [28 - Prompt Engineering](28_prompt-engineering.md)
<!-- nav:end -->

Quick reference for calling hosted LLMs from Python: the Anthropic (Claude) SDK in depth, the OpenAI SDK, streaming, structured outputs, vision and PDFs, thinking, caching, batches, token counting, errors and cost.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### Before you start

**You should know:** what an API and an SDK are and how to use one ([01 - Core Concepts](01_core-concepts.md) sections 7 to 10), HTTP basics ([09](09_http-apis.md)), and the LLM ideas of tokens and context windows ([26 - LLM Fundamentals](26_llm-fundamentals.md)). You need an API key from the Anthropic Console.

**The problem it solves:** the best models are too large to run on a laptop; they run on the provider's GPU clusters. To use one from your own program you send it requests over the internet, and you need to control everything about those requests: the instructions, the conversation so far, the answer format, the cost and what happens when something fails.

**Before LLM APIs:** using a language model meant training and hosting it yourself, which needed ML expertise, labelled data and expensive hardware. Hosted APIs turned a frontier model into something you can call with a few lines of code and pay for per use.

**Think of it like:** calling an expert consultant by phone. You describe the task and give all the background in each call (the model remembers nothing between calls unless you send the history), you pay for the minutes (tokens), and the SDK is the phone that handles dialling, bad connections and redialling for you.

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

**Where it fits:** concepts in [26 - LLM Fundamentals](26_llm-fundamentals.md); HTTP basics in [09 - HTTP and APIs](09_http-apis.md); schemas via [13 - Pydantic](13_pydantic.md); prompting in [28](28_prompt-engineering.md); tools in [29](29_tool-use.md); serving your own API with [40 - FastAPI](40_fastapi.md).

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
14. [Reducing Inference Cost](#14-reducing-inference-cost)
15. [Errors, Retries and Timeouts](#15-errors-retries-and-timeouts)
16. [Stop Reasons and Refusals](#16-stop-reasons-and-refusals)
17. [Async Client](#17-async-client)
18. [Tool Use (Preview)](#18-tool-use-preview)
19. [OpenAI SDK Equivalents](#19-openai-sdk-equivalents)
20. [Provider-Agnostic Design](#20-provider-agnostic-design)
21. [Claude on Cloud Platforms](#21-claude-on-cloud-platforms)
22. [Production Checklist](#22-production-checklist)
23. [Troubleshooting](#23-troubleshooting)
24. [Try It](#24-try-it)

---

## 0. Flags and Parameters

> The parameters of `client.messages.create(...)`. Keyword arguments; only `model`, `max_tokens` and `messages` are required.
>
> Use this when you see a request with `system=`, `thinking=`, `output_config=`, `cache_control=` and want to know what each does.

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
| `tools`, `tool_choice` | Functions the model may call ([29](29_tool-use.md)) |
| `thinking` | Reasoning config, e.g. `{"type": "adaptive"}` |
| `output_config` | `{"effort": "low" .. "max"}`, `{"format": {json schema}}` |
| `cache_control` | `{"type": "ephemeral"}` to cache the prompt prefix |
| `stop_sequences` | Custom strings that end generation |
| `metadata` | e.g. `{"user_id": "..."}` for abuse tracking |
| `temperature`, `top_p`, `top_k` | Sampling; not accepted by some newest models (use effort / prompting) |

---

## 1. Setup and API Keys

> Installing the SDK and authenticating. Get a key from the provider console; store it in an environment variable; the SDK reads it automatically.
>
> Use it once per project / machine.

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

> The model IDs you pass as `model`. Pick by capability vs cost vs speed; use exact IDs (no date suffixes for current models).
>
> Use it in every request. Prices and models change: check the provider's models page / Models API.

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

> The minimal working call. `messages.create` with a model, an output limit and one user message.
>
> Use it as the starting point for any feature.

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

> What comes back from the API. A `Message` with a list of content blocks, a stop reason and token usage.
>
> Use this when reading answers, handling tool calls, tracking cost.

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

> Instructions that shape the model's behaviour for the whole conversation. Pass `system="..."`; it is placed before the messages.
>
> Use it for role, rules, tone, output format, background knowledge.

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

How to write good system prompts: [28 - Prompt Engineering](28_prompt-engineering.md).

## 6. Multi-Turn Conversations

> Chat with memory. Keep a list of messages; append each user message and each assistant reply; send the whole list every time.
>
> Use it for chatbots, assistants, any back-and-forth.

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

> Receiving the answer token by token as it is generated. `client.messages.stream(...)` as a context manager; iterate `text_stream`; get the full message at the end.
>
> Use it for chat UIs (text appears instantly), long outputs (avoids HTTP timeouts), large `max_tokens`.

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

Stream from your own backend to a browser with FastAPI `StreamingResponse` ([40](40_fastapi.md)) or a UI library ([39](39_ai-ui.md)).

## 8. Structured Outputs (JSON)

> Getting output that is guaranteed to match a schema, parsed into Python objects. Pass a Pydantic model to `messages.parse(...)` (or a raw JSON schema via `output_config`); the API constrains generation to the schema.
>
> Use it for extraction, classification, anything your code reads. More reliable than "please reply in JSON".

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

> Sending images and documents for the model to read. Content becomes a list of blocks: `image` / `document` blocks (base64 or URL) plus a `text` block with your question.
>
> Use it for invoices, screenshots, charts, contracts, scanned forms.

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

> Letting the model reason before answering, and controlling how hard it works. `thinking={"type": "adaptive"}` lets the model decide when and how much to think; `output_config={"effort": ...}` trades quality for cost / speed.
>
> Use it for high effort for complex reasoning, coding, agents; low effort for simple, high-volume tasks.

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

> The provider remembers a long, repeated prompt prefix so later requests read it from cache. Mark the prompt with `cache_control`; identical prefix = cache hit (about 10% of normal input price, faster). Any change in the prefix breaks the cache from that point.
>
> Use it for long system prompts, big documents asked about repeatedly, agents and chats that resend history.

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

> Knowing how many tokens a request uses before and after sending it. `count_tokens` for estimates; `response.usage` for actuals.
>
> Use it for budgeting, guarding context limits, choosing chunk sizes.

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

> The Message Batches API takes many independent requests in one call, processes them in the background and charges **50% of the normal price for every token**, including cache reads and writes. You get the results later (most batches finish within an hour, all within 24 hours) and match them to your items by the `custom_id` you gave each request.
>
> Use it for work nobody is waiting on: classifying or tagging thousands of items, nightly summaries and reports, evaluation runs, backfills, generating test data. Keep anything a user is waiting for on normal requests.

### Key facts

| Fact | Value |
|---|---|
| Discount | 50% on input, output, cache writes and cache reads (stacks with prompt caching) |
| Size limit | Up to 100,000 requests or 256 MB per batch, whichever comes first |
| Turnaround | Most batches within 1 hour; anything not done after 24 hours expires |
| Result retention | Results can be downloaded for 29 days after the batch was created |
| Features | Everything the Messages API supports: system prompts, tools, images, PDFs, structured output, thinking, caching |
| Not possible | Streaming, and multi-turn tool loops inside one request (each request is single-shot) |
| Not available | Fast mode; Claude Managed Agents sessions |

### The lifecycle

```text
create(requests=[...])  ->  processing_status: "in_progress"   (poll with retrieve())
                        ->  processing_status: "ended"         (every request finished somehow)
results(batch_id)       ->  one result per custom_id, in ANY order:
                              succeeded  the Message, exactly as a normal call would return it
                              errored    invalid_request_error = fix the request; other errors = resubmit
                              expired    not processed within 24 hours = resubmit
                              canceled   you canceled the batch before it ran = resubmit if still needed
```

### Create, wait, collect

The full, tested version is `examples/batch_jobs/batch.py`:

```python
import time

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

client = anthropic.Anthropic()

requests = [
    Request(
        custom_id=review_id,                       # your own ID: unique, max 64 chars, letters/digits/-/_
        params=MessageCreateParamsNonStreaming(
            model="claude-haiku-4-5",              # easy task -> small model (section 14)
            max_tokens=64,
            system="Classify the sentiment. Answer with one word: positive, negative or neutral.",
            messages=[{"role": "user", "content": text}],
        ),
    )
    for review_id, text in reviews.items()
]
batch = client.messages.batches.create(requests=requests)
print(batch.id)                                    # save it: it is all you need to get results later

while (batch := client.messages.batches.retrieve(batch.id)).processing_status != "ended":
    time.sleep(60)                                 # poll once a minute
print(batch.request_counts)                        # succeeded / errored / expired / canceled

labels, retry, failed = {}, [], {}
for item in client.messages.batches.results(batch.id):
    result = item.result
    if result.type == "succeeded":
        labels[item.custom_id] = "".join(b.text for b in result.message.content if b.type == "text").strip()
    elif result.type == "errored" and result.error.error.type == "invalid_request_error":
        failed[item.custom_id] = result.error.error.message    # retrying will fail the same way
    else:
        retry.append(item.custom_id)                            # server error, expired or canceled
```

Note the nesting in errored results: `result.error` is an error response whose `.error.type` holds the actual kind (`invalid_request_error`, `overloaded_error`, ...).

### Other operations

| Call | Use |
|---|---|
| `client.messages.batches.retrieve(batch_id)` | Status and `request_counts` |
| `client.messages.batches.results(batch_id)` | Iterate over results (streamed, safe for 100,000 items) |
| `client.messages.batches.cancel(batch_id)` | Stop a batch; already-finished requests keep their results |
| `client.messages.batches.list(limit=20)` | Your recent batches (iterating pages automatically) |
| `client.messages.batches.delete(batch_id)` | Remove a finished batch and its stored data (cancel a running one first) |

### Batch + prompt caching

Give every request the same system prompt or document with `cache_control`, exactly as in section 11. Cache reads are then discounted twice (0.1x, then halved). Inside one batch the requests run in parallel and in any order, so cache hits are best-effort. Because a batch can run longer than 5 minutes, use the 1-hour cache duration (`{"type": "ephemeral", "ttl": "1h"}`) for shared context.

### Designing batch jobs

- **Make results idempotent**: store each result under its `custom_id` so re-running the collector or resubmitting a few failed items never duplicates work.
- **Resubmit, do not retry in place**: put `retry` IDs into a new, smaller batch.
- **Validate outputs**: batches run unattended, so check each answer (allowed labels, valid JSON) and send bad ones to `failed` instead of trusting them.
- **Split huge jobs**: several batches of 10,000 give you partial results sooner and smaller retries.
- **Flatten tool loops**: a batch request cannot call your tools and continue. If the model would need to look things up, fetch that data first and put it in the prompt.

## 14. Reducing Inference Cost

> Most LLM bills can be cut by a large factor without making answers worse: measure where tokens go, cache what repeats, batch what can wait, and only then trade quality for price (smaller models, lower effort). Work through the levers in that order.
>
> Use it when a bill is higher than expected, before scaling a feature to many users, and when planning a bulk job.

### How the bill is made

```text
cost per request = uncached input tokens x input price
                 + cache writes         x input price x 1.25   (5-minute cache; 1-hour cache: x 2)
                 + cache reads          x input price x 0.1
                 + output tokens        x output price          (thinking tokens count as output)
                 all of it x 0.5 when sent through the Batch API
```

Output tokens cost several times more than input tokens (5x on current models), and **input usually dominates anyway** because the system prompt, tools, documents and conversation history are resent on every call. That is why caching is the biggest lever for most apps.

### Worked example

From `uv run python -m batch_jobs.costs` in `examples/`: 10,000 requests, each with the same 4,000-token instructions and examples, 500 tokens of unique input and 300 tokens of output. Prices from the pricing page on 2026-09-28 (Opus 5: $5 / $25 per million input / output tokens; Haiku 4.5: $1 / $5).

| Setup | Cost | vs start |
|---|---|---|
| Opus 5, one request at a time | $300.00 | 100% |
| + prompt caching on the shared 4,000 tokens | $120.02 | 40% |
| + Batch API | $60.01 | 20% |
| Haiku 4.5 instead of Opus 5 (if its quality passes your eval) | $12.00 | 4% |

### The levers, in the order to try them

| # | Lever | Typical saving | Quality risk | How |
|---|---|---|---|---|
| 1 | Measure | Shows where the money goes | None | Log `response.usage` for every call (section 12); group by feature |
| 2 | Prompt caching | Up to 90% of repeated input | None | Stable content first, `cache_control` (section 11); check `cache_read_input_tokens` |
| 3 | Trim input | Proportional to tokens removed | Low | Shorter system prompts, fewer RAG chunks ([31](31_rag.md)), summarise or trim old chat history, downscale images, only the tools a call needs |
| 4 | Batch API | 50% of everything | None (just slower) | Anything not user-facing (section 13) |
| 5 | Control output | Proportional to tokens removed | Low | Ask for the exact format and length, with an example; structured output (section 8); stop sequences |
| 6 | Cache whole answers | 100% on repeated questions | Stale answers | Store answers to identical questions in Redis with a TTL ([42](42_redis-queues.md)) |
| 7 | Lower effort | Often 30-50% on reasoning-heavy work | Measurable | `output_config={"effort": "medium"}` or `"low"` (section 10); compare on an eval |
| 8 | Smaller model | 5x or more per token | Measurable | Route easy steps (classification, extraction, routing) to Haiku; keep hard reasoning on the larger model |
| 9 | Fewer calls | Proportional | Low to medium | One call that returns several fields instead of several calls; skip the LLM when rules or a cache can answer |

Levers 1 to 6 are **free wins**: they lower the price without changing what the model can do. Levers 7 and 8 are **trade-offs**: always compare quality on an evaluation set ([35 - Evals](35_evals-observability.md)) before and after, and judge by **cost per successful task**, not cost per token. A cheap model that fails and needs a retry (or a human) is not cheap.

### Common cost traps

| Trap | What happens | Fix |
|---|---|---|
| Timestamp or request ID in the system prompt | Every call misses the cache | Move changing values into the user message, after the cached part |
| Chat history grows forever | Each turn resends every earlier turn | Cache the history, summarise old turns, or start fresh sessions |
| Whole documents stuffed into the prompt | Pay for pages the answer never uses | Retrieve only relevant chunks (RAG) |
| Tiny `max_tokens` to "save money" | Answers get cut off and must be redone | `max_tokens` is a safety cap, not a cost control; shorten output through instructions |
| Sending bulk jobs as live requests | Full price plus rate-limit errors | Batch API |
| Switching model or effort mid-conversation | Cache is per model and setting, so it starts over | Keep them fixed within a session |
| No usage logging | You cannot see which feature costs what | Log `usage` with a feature name on every call |

## 15. Errors, Retries and Timeouts

> Handling failures correctly. The SDK retries 408 / 409 / 429 / 5xx and connection errors automatically (default 2 retries); catch specific exception classes for the rest.
>
> Use it in every production call.

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

## 16. Stop Reasons and Refusals

> Why the model stopped, which decides what your code does next. Check `response.stop_reason` before using the content.
>
> Use it in every response in production code.

| `stop_reason` | Meaning | Your code should |
|---|---|---|
| `end_turn` | Finished normally | Use the answer |
| `max_tokens` | Hit your `max_tokens` cap; answer cut off | Raise `max_tokens`, stream, or ask to continue |
| `stop_sequence` | Hit one of your `stop_sequences` | Use the answer |
| `tool_use` | Wants to call a tool | Run the tool, send the result back ([29](29_tool-use.md)) |
| `pause_turn` | Long server-side tool turn paused | Send the response back to let it continue |
| `refusal` | Declined for safety reasons | Show a polite message; see `response.stop_details` |

The newest Claude models support server-side **fallbacks**: on a refusal, the API retries automatically on another model inside the same call (beta: `client.beta.messages.create(..., betas=["server-side-fallback-2026-07-01"], fallbacks="default")`). Check the docs for current details.

## 17. Async Client

> The same API for async code. `AsyncAnthropic` + `await`; combine with `asyncio.gather` and a semaphore for concurrency.
>
> Use it for FastAPI endpoints, processing many inputs in parallel. See [14 - Async Python](14_async-python.md).

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

## 18. Tool Use (Preview)

> Letting the model call your Python functions. Describe functions as tools; the model returns a `tool_use` block; you run the function and send back a `tool_result`; repeat until done.
>
> Use it for live data, calculations, actions. Full guide: [29 - Tool Use](29_tool-use.md).

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

## 19. OpenAI SDK Equivalents

> The same tasks with the OpenAI Python SDK. OpenAI has the newer **Responses API** and the older, widely copied **Chat Completions API**; both are shown.
>
> Use it for projects using GPT models, Azure OpenAI, or OpenAI-compatible servers (Ollama, vLLM). Model names change often; check the current list.

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

## 20. Provider-Agnostic Design

> Structuring code so the model provider can change without rewriting the app. Put LLM calls behind one small interface in your code; keep prompts and model names in config.
>
> Use it for apps that may switch models, compare providers in evals, or use local and cloud models.

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

Libraries like LiteLLM or LangChain offer one interface for many providers ([33](33_agent-frameworks.md)); the trade-off is an extra dependency and hidden details.

## 21. Claude on Cloud Platforms

> Using Claude through AWS, Google Cloud or Microsoft Azure. Dedicated client classes with the same `messages.create` interface; model IDs and auth follow the platform.
>
> Use this when your company's data or billing must stay in one cloud.

| Platform | Python client |
|---|---|
| Amazon Bedrock | `from anthropic import AnthropicBedrockMantle` -> `AnthropicBedrockMantle(aws_region="...")`, model IDs prefixed `anthropic.` |
| Google Vertex AI | `from anthropic import AnthropicVertex` -> `AnthropicVertex(project_id="...", region="global")` |
| Microsoft Foundry | `from anthropic import AnthropicFoundry` -> `AnthropicFoundry(api_key=..., resource="...")` |

Feature availability can differ per platform; check the platform docs.

## 22. Production Checklist

> What to have in place before real users hit your LLM feature. A list to review.
>
> Use it before launch and in code review.

- [ ] Keys in env vars / Key Vault; spend limits set in the console
- [ ] Model ID and prompts in config, not scattered in code
- [ ] `max_tokens` large enough; streaming for long outputs
- [ ] Every `stop_reason` handled (`max_tokens`, `refusal`, `tool_use`)
- [ ] Timeouts, retries, and user-friendly error messages
- [ ] Structured outputs + validation where code consumes the output
- [ ] Prompt caching for long, repeated prefixes
- [ ] Logging of `usage`, latency, request IDs (no secrets / personal data in logs)
- [ ] Rate limiting / concurrency limits in your own API
- [ ] Evals for quality and regressions ([35](35_evals-observability.md))
- [ ] Guardrails against prompt injection and data leaks ([38](38_ai-security.md))

## 23. Troubleshooting

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
| Costs higher than expected | Log `usage` per feature; then caching, trimming input, Batch API and smaller models for easy steps, in that order (section 14) |
| Batch results attached to the wrong items | Results come back in any order: match them by `custom_id`, never by position (section 13) |

## 24. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

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

---

<!-- nav:start -->
**Previous:** [26 - LLM Fundamentals](26_llm-fundamentals.md) | **Index:** [All guides](../README.md) | **Next:** [28 - Prompt Engineering](28_prompt-engineering.md)
<!-- nav:end -->
