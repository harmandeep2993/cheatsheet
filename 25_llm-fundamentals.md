# 25 - LLM Fundamentals

<!-- nav:start -->
**Previous:** [24 - Hugging Face](24_hugging-face.md) | **Index:** [All guides](README.md) | **Next:** [26 - LLM APIs](26_llm-apis.md)
<!-- nav:end -->

Quick reference for how large language models work: tokens, next-token prediction, training, context windows, sampling, reasoning, limitations, costs and how to choose a model. No code needed to understand this guide; it is the mental foundation for every other AI guide.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is an LLM?

A **large language model** (LLM) is a neural network trained on huge amounts of text to do one thing: **predict the next token** (piece of a word) given all the text before it. Repeating that prediction over and over produces sentences, code, summaries and answers. Models like Claude, GPT, Gemini, Llama, Qwen and Mistral are all LLMs. Because predicting text well requires modelling grammar, facts, reasoning patterns and intent, these models end up able to follow instructions, write code, translate, analyse and use tools.

### Mental model: the autocomplete that learned to think

```text
Input (the "context"):   "The capital of France is"
                                   |
                                   v
        +-----------------------------------------------+
        |  LLM: billions of learned weights             |
        |  looks at ALL tokens in the context at once   |
        |  (attention) and scores every possible next   |
        |  token                                        |
        +-----------------------------------------------+
                                   |
                                   v
Probabilities:   " Paris" 0.92   " a" 0.03   " the" 0.02   " Lyon" 0.001 ...
                                   |
                  pick one (sampling) -> " Paris"
                                   |
                  append it, repeat until a stop token or max length
                                   v
Output:          "The capital of France is Paris."
```

Three consequences of this design explain most LLM behaviour:

1. **Everything is text in context.** The model only knows what is in its weights (training) plus what you put in the prompt. It has no memory between API calls unless you send the history again.
2. **It generates plausible text, not verified truth.** When it does not know, it can still produce a fluent, confident, wrong answer (**hallucination**). Give it sources (RAG) and tools to ground answers.
3. **The prompt steers the probabilities.** Clear instructions, examples and context shift which tokens become likely. That is why prompt engineering works.

### The layers of an AI application

```text
+------------------------------------------------------------------+
| Your app / UI                (Streamlit, web app, chat, CLI)     |
+------------------------------------------------------------------+
| Orchestration                (agents, tool loops, RAG, workflows)|
+------------------------------------------------------------------+
| Context you provide          (system prompt, history, documents, |
|                               tool results, examples)            |
+------------------------------------------------------------------+
| Model                        (Claude, GPT, open models)          |
|   accessed via an API (hosted) or run locally (Ollama / vLLM)    |
+------------------------------------------------------------------+
```

Most of your engineering work happens in the middle two layers: **deciding what goes into the context and what to do with the output**.

### Key terms

| Term | Meaning |
|---|---|
| Token | Chunk of text (word piece) the model reads and writes; ~4 characters of English |
| Context window | Max tokens the model can consider at once (prompt + output) |
| Prompt | Everything you send: system instructions, messages, documents |
| Completion / output | Tokens the model generates |
| Inference | Running the model to get output |
| Parameters / weights | Learned numbers in the model (billions) |
| Pretraining | Learning to predict text on a huge corpus |
| Fine-tuning / post-training | Further training to follow instructions, be helpful and safe |
| Temperature | Randomness of token choice |
| Hallucination | Confident but false output |
| Grounding | Basing answers on provided sources / tools |
| Knowledge cutoff | Date after which the model has no training data |
| Multimodal | Can take images / PDFs / audio as input |
| Reasoning / thinking | Model spends tokens thinking before answering |
| Latency | Time until the (first) response |

**Where it fits:** the concepts behind [26 - LLM APIs](26_llm-apis.md), [27 - Prompt Engineering](27_prompt-engineering.md), [29 - Embeddings](29_embeddings-vector-db.md), [30 - RAG](30_rag.md), [31 - AI Agents](31_ai-agents.md). Implementation details: [23 - PyTorch](23_pytorch.md), [24 - Hugging Face](24_hugging-face.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Claude documentation | https://platform.claude.com/docs |
| Claude models overview | https://platform.claude.com/docs/en/about-claude/models/overview |
| Context windows | https://platform.claude.com/docs/en/build-with-claude/context-windows |
| Claude pricing | https://platform.claude.com/docs/en/about-claude/pricing |
| OpenAI platform docs | https://platform.openai.com/docs |
| Hugging Face LLM course | https://huggingface.co/learn |

---

## Contents

1. [Tokens](#1-tokens)
2. [Next-Token Prediction](#2-next-token-prediction)
3. [The Transformer and Attention (Intuition)](#3-the-transformer-and-attention-intuition)
4. [How LLMs Are Trained](#4-how-llms-are-trained)
5. [Context Window](#5-context-window)
6. [Messages and Roles](#6-messages-and-roles)
7. [Sampling: Temperature, top_p, top_k](#7-sampling-temperature-top_p-top_k)
8. [Reasoning / Thinking Models](#8-reasoning--thinking-models)
9. [Embeddings (Meaning as Numbers)](#9-embeddings-meaning-as-numbers)
10. [Multimodal Models](#10-multimodal-models)
11. [Hallucinations and Grounding](#11-hallucinations-and-grounding)
12. [What LLMs Are Good and Bad At](#12-what-llms-are-good-and-bad-at)
13. [Cost and Latency](#13-cost-and-latency)
14. [Closed vs Open Models](#14-closed-vs-open-models)
15. [Choosing a Model](#15-choosing-a-model)
16. [Ways to Adapt a Model to Your Task](#16-ways-to-adapt-a-model-to-your-task)
17. [LLM Application Patterns](#17-llm-application-patterns)
18. [Glossary of AI Buzzwords](#18-glossary-of-ai-buzzwords)
19. [Common Misconceptions](#19-common-misconceptions)
20. [Try It](#20-try-it)

---

## 1. Tokens

> The units an LLM reads and writes. A tokenizer splits text into pieces from a fixed vocabulary (common words are one token, rare words several). Use it for estimating cost, fitting text into the context window, understanding odd behaviour (spelling, counting letters).

```text
"Tokenization is surprisingly useful!"
-> ["Token", "ization", " is", " surprisingly", " useful", "!"]      6 tokens
```

| Rule of thumb (English) | Value |
|---|---|
| 1 token | ~4 characters, ~0.75 words |
| 100 tokens | ~75 words |
| 1 page of text | ~500 to 700 tokens |
| 1,000 lines of code | ~10,000 tokens |

Other languages, numbers and code usually need more tokens per word. Each provider has its own tokenizer; use its token-counting endpoint for exact numbers. Because models see tokens, not letters, tasks like "count the r's in strawberry" can be surprisingly hard.

## 2. Next-Token Prediction

> The one operation an LLM performs. Given the tokens so far, output a probability for every token in the vocabulary; pick one; append; repeat. Use it for understanding streaming, stop reasons and why output length drives cost and time.

- Generation is **sequential**: output token 500 needs tokens 1 to 499 first. Long outputs take longer.
- **Streaming** simply shows each token as soon as it is picked.
- Generation stops at a **stop token** (the model decides it is done), a **stop sequence** you define, or **max tokens** (a hard cut; the answer may be incomplete).
- The model is **stateless** between requests; "memory" in chat apps is the app re-sending history.

## 3. The Transformer and Attention (Intuition)

> The neural network architecture behind all modern LLMs (2017, "Attention Is All You Need"). Each token looks at every other token in the context and decides which ones matter for it (**attention**); many stacked layers refine the meaning step by step. Use it for knowing why context matters and why long contexts cost more.

```text
"The trophy did not fit in the suitcase because it was too big."
                                                ^^
Attention for "it" -> strongly on "trophy" (big thing that does not fit), weakly on "suitcase"
```

- Each token becomes a vector (embedding); layers of attention + feed-forward networks transform these vectors.
- Attention compares tokens pairwise, so compute grows with context length; long prompts cost more and can be slower.
- Models can miss details buried in very long contexts; put key instructions and questions where they are easy to find (see [27 - Prompt Engineering](27_prompt-engineering.md)).

## 4. How LLMs Are Trained

> The stages that turn a random network into a helpful assistant. Pretraining for knowledge and language; post-training for following instructions, helpfulness and safety. Use it for understanding knowledge cutoffs, why models refuse some requests, and what fine-tuning can and cannot do.

```text
1. PRETRAINING         trillions of tokens of text and code     -> "base model": great at continuing text,
   (months, huge GPUs)  objective: predict next token               knows a lot, does not follow instructions well

2. SUPERVISED           curated (instruction, ideal answer) pairs -> follows instructions, chat format
   FINE-TUNING (SFT)

3. PREFERENCE / RL      humans / AI rank answers; reinforcement  -> more helpful, honest, safe;
   (RLHF, RLAIF,        learning on feedback and verifiable tasks    better at reasoning and tool use
    constitutional AI)
```

- **Knowledge cutoff**: the model knows nothing after its training data ends; give recent facts in the prompt or via search tools.
- **Your data is not learned** from API calls in normal use; to use private knowledge, put it in the context (RAG) or fine-tune.

## 5. Context Window

> The maximum number of tokens the model can handle in one request (input + output). Everything the model "sees" must fit: system prompt, tools, history, documents, and the answer it writes. Use it for designing chat history handling, RAG chunk counts and document processing.

```text
+------------------------------ context window -------------------------------+
| system prompt | tool definitions | conversation history | documents | query | -> output tokens
+-----------------------------------------------------------------------------+
```

- Current frontier models offer very large windows (hundreds of thousands to 1M tokens), smaller open models often 8K to 128K.
- Bigger context = more cost per call and sometimes weaker attention to details. Send what is **relevant**, not everything.
- Long conversations: summarise or trim old turns, or use provider features (compaction, context editing).
- **Max output tokens** is a separate, smaller limit on how much the model can write in one response.

## 6. Messages and Roles

> How chat APIs structure the context. A list of messages, each with a role; the system prompt sets behaviour for the whole conversation. Use it in every API call and chat app.

| Role | Contains |
|---|---|
| `system` | Instructions, persona, rules, background (set by the developer) |
| `user` | What the user / your app asks |
| `assistant` | What the model answered before (sent back as history) |
| tool results | Output of tools the model asked to call (see [28 - Tool Use](28_tool-use.md)) |

```text
system:    You are a support agent for Acme. Answer only about Acme products.
user:      My order hasn't arrived.
assistant: I'm sorry! Could you share your order number?
user:      A-1042                             <- the model sees ALL of this every time
```

## 7. Sampling: Temperature, top_p, top_k

> How the next token is chosen from the probabilities. Temperature reshapes the distribution; top_p / top_k cut off unlikely tokens before sampling. Use it for tuning consistency vs variety (on models and APIs that expose these settings).

```text
Probabilities for next word:   "Paris" 0.70   "France" 0.15   "a" 0.10   "banana" 0.05

temperature 0   -> always "Paris"           (deterministic-ish, factual tasks)
temperature 0.7 -> usually "Paris"          (balanced default)
temperature 1.5 -> sometimes "banana"       (creative, risky)
```

| Setting | Low value | High value |
|---|---|---|
| `temperature` | Focused, repeatable | Varied, creative, more errors |
| `top_p` | Only the most likely tokens | Wider choice |
| `top_k` | Choose among few tokens | Choose among many |

Some newer reasoning models fix these internally and do not accept them; you steer with instructions and effort settings instead.

## 8. Reasoning / Thinking Models

> Models that generate internal reasoning before the final answer. The model spends extra tokens working through the problem step by step; you can often control how much (effort / thinking settings). Use it for maths, coding, planning, multi-step analysis, agents. Not needed for simple lookups or classification.

- More thinking = usually better answers on hard problems, but more tokens (cost) and more latency.
- You pay for thinking tokens even if they are hidden or summarised.
- "Think step by step" in the prompt gave non-reasoning models some of this benefit; reasoning models do it natively.

## 9. Embeddings (Meaning as Numbers)

> A vector (list of numbers) that represents the meaning of a text. An embedding model maps text to a point in a high-dimensional space; similar meanings land close together. Use it for semantic search, RAG retrieval, clustering, recommendations, deduplication.

```text
"How do I reset my password?"   -> [0.12, -0.40, 0.88, ...]  \
"I forgot my login"             -> [0.10, -0.38, 0.90, ...]   } close together (similar meaning)
"Shipping takes three days"     -> [-0.70, 0.22, 0.05, ...]  far away
```

Embedding models are separate, smaller models from chat LLMs. Details: [29 - Embeddings and Vector DBs](29_embeddings-vector-db.md).

## 10. Multimodal Models

> Models that accept images, PDFs, audio or video as input (and some that produce images / audio). Non-text inputs are converted into tokens / embeddings the model can attend to alongside text. Use it for reading invoices and screenshots, charts, handwriting, diagrams, voice apps.

Images and PDF pages cost tokens too (roughly proportional to resolution / page count).

## 11. Hallucinations and Grounding

> Fluent, confident output that is false or made up (fake citations, wrong numbers, invented APIs). The model generates plausible text; without a source, plausible can be wrong. Use it for designing any app where correctness matters.

| Technique | Why it helps |
|---|---|
| Provide sources in the prompt (RAG) | Model answers from given text, not memory |
| Ask for quotes / citations | Answers are checkable |
| Allow "I don't know" | Removes pressure to invent |
| Tools for facts (search, calculator, DB) | Real data instead of guesses |
| Structured outputs + validation | Catch malformed or impossible values |
| Evals and human review | Measure and catch errors ([34](34_evals-observability.md)) |
| Stronger model / more reasoning | Fewer errors on hard tasks |

## 12. What LLMs Are Good and Bad At

> Realistic expectations. Strong at language and pattern tasks; weak where exactness, fresh facts or hidden state matter. Use this when deciding whether an LLM is the right tool, and where to add tools or code.

| Good at | Weak at (add tools / code) |
|---|---|
| Summarising, rewriting, translating | Exact arithmetic on big numbers (use code) |
| Extracting structured data from messy text | Facts after the cutoff (use search / RAG) |
| Classifying, tagging, routing | Counting characters / exact string ops |
| Writing and explaining code | Guaranteed determinism |
| Brainstorming, drafting | Knowing your private data (put it in context) |
| Reasoning over provided documents | Long-running state without memory design |
| Following multi-step instructions | Tasks needing verified truth without sources |

## 13. Cost and Latency

> How LLM usage is priced and what makes it slow. You pay per **input token** and per **output token** (output is several times more expensive); latency grows with output length and reasoning. Use it for budgeting, choosing models, optimising apps.

```text
cost of one call = input_tokens x input_price + output_tokens x output_price   (prices per 1M tokens)

Example: 3,000 input + 500 output tokens at $5 / $25 per 1M
       = 3,000 x 0.000005 + 500 x 0.000025 = $0.015 + $0.0125 = $0.0275
```

| Lever | Saves |
|---|---|
| Prompt caching (reuse the same long prefix) | Large share of repeated input cost and latency |
| Shorter prompts / fewer retrieved chunks | Input cost |
| Ask for concise output, set sensible max tokens | Output cost and latency |
| Smaller / cheaper model for simple steps | Cost and latency |
| Lower reasoning effort for easy tasks | Thinking tokens |
| Batch API for offline jobs | Often ~50% cheaper |
| Streaming | Perceived latency (first words appear fast) |

## 14. Closed vs Open Models

> Hosted proprietary models vs models whose weights you can download. Closed models are used through a provider's API; open-weight models run on your hardware or a host of your choice. Use it for balancing quality, privacy, cost and control.

| | Closed / hosted (Claude, GPT, Gemini) | Open-weight (Llama, Qwen, Mistral, Gemma, DeepSeek) |
|---|---|---|
| Access | API key, pay per token | Download weights (Hugging Face, Ollama) |
| Quality | Usually the strongest | Good and improving; best big ones need big GPUs |
| Setup | None | You run and scale it (or use a host) |
| Data privacy | Provider's terms; enterprise options, regional hosting | Fully in your control |
| Cost pattern | Per token | Per hour of hardware |
| Customisation | Prompting, some fine-tuning | Full fine-tuning, quantization |

## 15. Choosing a Model

> Picking the right model for each task. Start with a strong model to prove the task works, measure with evals, then optimise cost / latency. Use it in every new feature.

1. Prototype with a **top-tier model** so model weakness is not the problem.
2. Build a small **eval set** ([34](34_evals-observability.md)) with real examples.
3. Try cheaper / faster models or lower effort; keep the cheapest that passes your quality bar.
4. Consider hard constraints: data residency, offline, context length, multimodal input, tool use support.

| Task | Typical choice |
|---|---|
| Complex reasoning, coding, agents | Frontier model with reasoning |
| High-volume classification / extraction | Smaller, faster model (or fine-tuned small model) |
| Sensitive data, offline | Open model locally ([35](35_local-llms.md)) or enterprise cloud hosting |
| Search / RAG retrieval | Embedding model + chat model |

## 16. Ways to Adapt a Model to Your Task

> The options for making a general model good at your specific job, from cheapest to most effort. Most problems are solved by the first three; fine-tuning is for specific cases. Use it for deciding how to improve quality.

```text
effort / cost  ->

1. Prompt engineering     clear instructions, examples, output format     (minutes)      [27]
2. Context / RAG          give the model the right documents at runtime   (days)         [30]
3. Tools / agents         let the model fetch data and take actions        (days)         [28] [31]
4. Fine-tuning            change model weights with your examples          (weeks)        [36]
5. Train from scratch     almost never for applications                    (months, $$$)
```

| Problem | Usually solved by |
|---|---|
| "It doesn't follow my format" | Prompting, structured outputs |
| "It doesn't know our documents" | RAG |
| "It needs live data / to act" | Tools |
| "It must adopt a very specific style / narrow skill cheaply at scale" | Fine-tuning |

## 17. LLM Application Patterns

> The common shapes of LLM apps, from simple to complex. Add complexity only when the simpler pattern is not enough. Use it for designing a new AI feature.

| Pattern | How it works | Example |
|---|---|---|
| Single call | Prompt in, answer out | Summarise an email |
| Structured extraction | Prompt + schema -> JSON | Invoice fields |
| Chain / workflow | Fixed sequence of LLM calls and code | Draft -> critique -> revise |
| Routing | Classify first, then pick the handler | Support ticket routing |
| RAG | Retrieve documents, then answer with them | Chat with company docs |
| Tool use | Model calls functions you define | Look up order status |
| Agent | Model decides steps in a loop until done | Research and write a report |
| Multi-agent | Several agents with roles cooperate | Planner + workers + reviewer |

## 18. Glossary of AI Buzzwords

> Quick definitions of terms you will hear. One line each; follow the links for depth. Use it for reading docs, job posts, blog posts.

| Term | Meaning |
|---|---|
| Foundation model | Large general-purpose pretrained model |
| Prompt engineering | Designing inputs to get better outputs ([27](27_prompt-engineering.md)) |
| Context engineering | Deciding everything that goes into the context (instructions, docs, tools, memory) |
| Few-shot / zero-shot | With / without examples in the prompt |
| Chain of thought | Reasoning step by step before answering |
| Structured output | Output constrained to a schema (JSON) |
| Function calling / tool use | Model requests to run your functions ([28](28_tool-use.md)) |
| RAG | Retrieval-augmented generation ([30](30_rag.md)) |
| Vector database | Stores embeddings for similarity search ([29](29_embeddings-vector-db.md)) |
| Agent | LLM in a loop that uses tools to reach a goal ([31](31_ai-agents.md)) |
| MCP | Model Context Protocol: standard way to connect tools / data to AI apps ([33](33_mcp.md)) |
| Guardrails | Checks on inputs / outputs for safety and policy ([37](37_ai-security.md)) |
| Evals | Systematic tests of model / app quality ([34](34_evals-observability.md)) |
| LLM-as-judge | Using a model to grade outputs |
| Fine-tuning / LoRA | Training a model further / cheap way to do it ([36](36_fine-tuning.md)) |
| Quantization | Storing weights with fewer bits to save memory ([35](35_local-llms.md)) |
| Distillation | Training a small model to imitate a big one |
| Inference server | Software serving a model over an API (vLLM, Ollama) |
| Prompt injection | Malicious text that tries to override your instructions ([37](37_ai-security.md)) |
| Grounding | Tying answers to sources / data |
| Latency / TTFT | Response time / time to first token |
| Throughput | Tokens or requests processed per second |

## 19. Common Misconceptions

> Beliefs that lead to bad designs. Each has a short correction. Use it for sanity check when an AI feature misbehaves.

| Misconception | Reality |
|---|---|
| "The model remembers our previous chats" | Only if your app sends the history (or uses a memory feature) |
| "It learned from my API calls" | Standard API use does not train the model on your data (check provider terms) |
| "It looked it up online" | Only if you gave it a search / fetch tool |
| "Temperature 0 means always correct" | It means more consistent, not more truthful |
| "Bigger context always helps" | Irrelevant text can distract and costs more |
| "Fine-tuning teaches it our documents" | Fine-tuning shapes behaviour; RAG is better for facts that change |
| "It says it's sure, so it's right" | Confidence in text is not reliability; verify |
| "Agents are always better" | They are slower, costlier and less predictable; use the simplest pattern that works |

## 20. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution. Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Estimate a bill

A 2,000-word document goes in and a 300-word answer comes out at $5 / $25 per million tokens. Roughly what does one call cost?

<details markdown="1">
<summary>Solution</summary>

Tokens ~ words / 0.75: input ~ 2,700 tokens, output ~ 400 tokens.
Cost ~ 2,700 x 5 / 1,000,000 + 400 x 25 / 1,000,000 = $0.0135 + $0.01 = **about $0.024 per call**, so about $23.50 per day at 1,000 calls. Do this estimate before launch.

</details>

### Exercise 2: Pick the technique

Prompting, RAG, tools or fine-tuning? (a) answer from 5,000 policy PDFs, (b) show today's order status, (c) always reply in a strict JSON format, (d) cheap high-volume classification in a fixed style.

<details markdown="1">
<summary>Solution</summary>

(a) RAG, (b) tools (live data), (c) structured outputs / prompting, (d) prompting first; fine-tune a small model only if volume and cost justify it.

</details>

### Exercise 3: The forgetful chatbot

Your chatbot forgets what the user said two messages ago. Why?

<details markdown="1">
<summary>Solution</summary>

The API is stateless: the model only sees what you send in `messages`. Your app must store the history and send it with every request (and trim or summarise it when it gets long).

</details>

---

<!-- nav:start -->
**Previous:** [24 - Hugging Face](24_hugging-face.md) | **Index:** [All guides](README.md) | **Next:** [26 - LLM APIs](26_llm-apis.md)
<!-- nav:end -->
