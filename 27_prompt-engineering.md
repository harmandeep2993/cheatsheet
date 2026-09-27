# 27 - Prompt Engineering

<!-- nav:start -->
**Previous:** [26 - LLM APIs](26_llm-apis.md) | **Index:** [All guides](README.md) | **Next:** [28 - Tool Use (Function Calling)](28_tool-use.md)
<!-- nav:end -->

Quick reference for writing prompts that get reliable, high-quality results from LLMs: structure, examples, context, output formats, reasoning, templates, chaining and iteration.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is prompt engineering?

Prompt engineering is the skill of **writing the instructions and context you give an LLM** so it does exactly what you need, consistently. Because the model predicts output from its input, the input is your main control: what you ask, what background you give, which examples you show and what format you request all change the result. Today this is often called **context engineering**: designing *everything* the model sees (instructions, documents, tool results, history), not just one clever sentence.

### Mental model: brief a brilliant new colleague

Imagine handing the task to a very smart person who joined your company **today**: they know a lot about the world but nothing about your project, your users, your standards or why the task matters. They cannot ask you questions while working. Everything they need must be in the brief.

```text
Weak brief:   "Summarize this."

Strong brief: WHO it is for    -> "for our sales team, who read it on their phones"
              WHY it matters   -> "they decide which leads to call first"
              WHAT to do       -> "summarize the call transcript below"
              WHAT good looks  -> "3 bullet points: need, budget, next step; max 60 words"
                 like
              THE MATERIAL     -> <transcript> ... </transcript>
              EDGE CASES       -> "if budget is not mentioned, write 'budget: unknown'"
```

If a colleague would need to ask you a follow-up question, the prompt is missing that information.

### Why it matters

- **Biggest quality lever** for the least effort: often more impact than switching models.
- **Consistency**: clear format rules make outputs parseable by code.
- **Cost and speed**: good prompts avoid retries and overly long answers.
- **Safety**: clear boundaries reduce off-topic and risky outputs.

### Key terms

| Term | Meaning |
|---|---|
| System prompt | Standing instructions for the whole conversation |
| User prompt | The specific request / input for this turn |
| Zero-shot | Instructions only, no examples |
| Few-shot / multishot | Instructions plus a few input -> output examples |
| Chain of thought | Letting the model reason before the final answer |
| Delimiters / XML tags | Markers that separate instructions from data (`<document>...</document>`) |
| Prompt template | Prompt with placeholders filled at runtime |
| Prompt chaining | Splitting a task into several prompts, output of one feeds the next |
| Context engineering | Curating all information in the context window |
| Prompt injection | Untrusted text trying to override your instructions ([37](37_ai-security.md)) |

**Where it fits:** applies to every call in [26 - LLM APIs](26_llm-apis.md); tool descriptions in [28 - Tool Use](28_tool-use.md); RAG prompts in [30 - RAG](30_rag.md); agent system prompts in [31 - AI Agents](31_ai-agents.md); measured with [34 - Evals](34_evals-observability.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Claude docs (Build with Claude > Prompt engineering) | https://platform.claude.com/docs |
| Anthropic interactive prompt engineering tutorial | https://github.com/anthropics/prompt-eng-interactive-tutorial |
| Anthropic cookbook (example notebooks) | https://github.com/anthropics/anthropic-cookbook |
| OpenAI prompt engineering guide | https://platform.openai.com/docs/guides/prompt-engineering |

---

## Contents

1. [The Anatomy of a Good Prompt](#1-the-anatomy-of-a-good-prompt)
2. [Be Clear, Specific and Direct](#2-be-clear-specific-and-direct)
3. [Give Context and the Why](#3-give-context-and-the-why)
4. [Separate Instructions from Data (XML Tags)](#4-separate-instructions-from-data-xml-tags)
5. [Examples (Few-Shot)](#5-examples-few-shot)
6. [Role and Audience](#6-role-and-audience)
7. [Output Format](#7-output-format)
8. [Reasoning Before Answering](#8-reasoning-before-answering)
9. [Long Documents](#9-long-documents)
10. [Allowing "I Don't Know"](#10-allowing-i-dont-know)
11. [System Prompt Template](#11-system-prompt-template)
12. [Prompt Templates in Code](#12-prompt-templates-in-code)
13. [Prompt Chaining](#13-prompt-chaining)
14. [Common Task Recipes](#14-common-task-recipes)
15. [Prompting for Code Generation](#15-prompting-for-code-generation)
16. [Tone, Length and Style Control](#16-tone-length-and-style-control)
17. [Anti-Patterns](#17-anti-patterns)
18. [Iterating on Prompts](#18-iterating-on-prompts)
19. [Prompt Checklist](#19-prompt-checklist)
20. [Try It](#20-try-it)

---

## 1. The Anatomy of a Good Prompt

> The building blocks most strong prompts contain. Not every prompt needs all parts; include what the task needs, in a clear order.
>
> Use it for designing any non-trivial prompt.

| Part | Purpose | Example |
|---|---|---|
| Role / context | Who the model is working for and why | "You help our finance team review invoices." |
| Task | What to do, as a direct instruction | "Extract vendor, date and total." |
| Input data | The material, clearly delimited | `<invoice>...</invoice>` |
| Constraints / rules | Boundaries and edge cases | "If no total, return null." |
| Examples | Show the desired input -> output | 2 to 5 diverse examples |
| Output format | Exact shape of the answer | JSON schema, bullet list, max length |
| Reasoning instruction | When thinking helps | "Think through the calculation first." |

Order that works well: context -> data -> task / rules -> output format. For long documents, put the documents first and the question last (section 9).

## 2. Be Clear, Specific and Direct

> Saying exactly what you want, in plain words. Use imperative instructions, concrete criteria and numbers instead of vague adjectives.
>
> Use this when always; vague prompts are the #1 cause of disappointing output.

| Vague | Specific |
|---|---|
| "Summarize this article." | "Summarize this article in 3 bullet points for a busy executive. Each bullet max 20 words. Focus on decisions and risks." |
| "Make it better." | "Rewrite for clarity: shorter sentences, active voice, remove jargon, keep all facts." |
| "Write some tests." | "Write pytest unit tests for `add_tax` covering normal values, zero, negative input (should raise ValueError) and rounding." |
| "Be concise." | "Answer in at most 2 sentences." |

Tell the model what TO do, not only what not to do: "Write in flowing paragraphs" works better than "Don't use bullet points".

## 3. Give Context and the Why

> Explaining the purpose and audience behind an instruction. Add one sentence of reason; the model generalises better when it understands the goal.
>
> Use it for rules that could be misapplied, or tasks where judgement matters.

```text
Weak:   NEVER use abbreviations.

Better: Our readers are customers who are new to finance, so write out terms in full
        (for example "annual percentage rate", not "APR").
```

Useful context to include: the audience, how the output will be used, what a great result looks like, relevant background the model cannot know (company policies, definitions, current date).

## 4. Separate Instructions from Data (XML Tags)

> Clearly marking which parts are your instructions and which parts are material to process. Wrap inputs in descriptive tags like `<document>`, `<email>`, `<examples>`; refer to them by name.
>
> Use it in any prompt that contains user content, documents or examples. Also reduces prompt-injection risk.

```text
Analyze the customer email in <email> using the refund policy in <policy>.

<policy>
Refunds are allowed within 30 days for unused items...
</policy>

<email>
Hi, I bought a jacket 45 days ago and want my money back...
</email>

Reply with:
<decision>approve or deny</decision>
<reason>one sentence quoting the policy</reason>
```

Tags can be anything meaningful; be consistent. Asking for tagged output makes parsing easy.

## 5. Examples (Few-Shot)

> Showing the model a few input -> ideal output pairs. Put 2 to 5 examples in `<example>` tags; make them diverse and representative, including tricky cases.
>
> Use it for specific formats, labels, tone or edge-case handling that is hard to describe in words.

```text
Classify each support message as billing, technical or shipping.

<examples>
<example>
<message>I was charged twice this month.</message>
<label>billing</label>
</example>
<example>
<message>The app crashes when I upload a photo.</message>
<label>technical</label>
</example>
<example>
<message>My package says delivered but it's not here, and I also want a refund.</message>
<label>shipping</label>
</example>
</examples>

<message>{new_message}</message>
Answer with the label only.
```

- The model copies patterns from examples closely: vary them so it does not copy accidental details (length, wording).
- Examples beat long explanations for format and style.

## 6. Role and Audience

> Giving the model a perspective and telling it who the answer is for. One line in the system prompt: role + audience + goal.
>
> Use it for domain-specific tasks, tone control.

```text
You are a senior data engineer reviewing pull requests for a team of junior analysts.
Explain problems kindly and suggest the fix with a short code example.
```

A role alone is weak; combine it with concrete instructions and context.

## 7. Output Format

> Controlling the shape of the answer. State the format explicitly; show a template; for code-consumed output use structured outputs (schema-enforced JSON).
>
> Use this when every prompt whose output is parsed or displayed in a fixed layout.

| Need | Technique |
|---|---|
| JSON your code parses | API structured outputs with a Pydantic model ([26](26_llm-apis.md) section 8) |
| Fixed sections | "Use exactly these headings: ## Summary, ## Risks, ## Next steps" |
| Single value | "Answer with only the label, no explanation." |
| Parse part of free text | Ask for tags: `<answer>...</answer>` |
| Length | "Max 100 words" / "exactly 3 bullets" |
| Plain text (no Markdown) | "Write plain prose paragraphs without Markdown formatting." |

The style of your prompt influences the output: a prompt full of bullet points and headings tends to produce bullets and headings.

## 8. Reasoning Before Answering

> Letting the model think through a problem before committing to an answer. Use a reasoning model / thinking setting, or ask it to reason in `<thinking>` tags and put the final answer in `<answer>` tags.
>
> Use it for maths, multi-step logic, analysis, decisions with several factors. Skip for simple lookups.

```text
Decide whether this expense claim follows the policy.
First reason step by step inside <thinking> tags: check the amount limit, the category,
and the receipt date. Then give the final decision inside <answer> tags (approve / reject).
```

With models that have built-in thinking (adaptive thinking / effort settings), prefer those settings over manual "think step by step" instructions, and ask for final-answer-only output if you do not want reasoning in the visible text.

## 9. Long Documents

> Getting accurate answers from long inputs (reports, contracts, transcripts). Put documents at the top, the question at the end; tag each document with metadata; ask for quotes first.
>
> Use it for document Q&A, summarising multiple files, RAG answers.

```text
<documents>
  <document index="1">
    <source>annual_report_2025.pdf</source>
    <content>...</content>
  </document>
  <document index="2">
    <source>q1_update.pdf</source>
    <content>...</content>
  </document>
</documents>

First, find quotes from the documents that are relevant to the question and put them in <quotes> tags.
Then answer the question using only those quotes, citing the document index.

Question: How did revenue guidance change between the report and the Q1 update?
```

## 10. Allowing "I Don't Know"

> Giving the model permission to say it does not have the answer. Explicitly allow and define the fallback response.
>
> Use it for q&A over documents, support bots, anything where a made-up answer is worse than none.

```text
Answer only using the information in <context>. If the answer is not in the context,
reply exactly: "I don't have that information. Please contact support@acme.com."
Do not guess.
```

## 11. System Prompt Template

> A reusable structure for production system prompts. Fill in each section; delete what does not apply.
>
> Use it for chatbots, assistants, agents.

```text
You are {role} for {company / product}. {one sentence on the goal and who the users are}.

## Context
{background the model needs: product facts, definitions, today's date if relevant}

## What you do
- {main responsibility 1}
- {main responsibility 2}

## How to respond
- Tone: {friendly, professional, ...}
- Length: {e.g. under 150 words unless the user asks for detail}
- Format: {plain text / Markdown / JSON}
- Language: reply in the user's language.

## Boundaries
- Only discuss {scope}. For other topics, {what to say}.
- If unsure or information is missing, {ask a clarifying question / say you don't know}.
- Never {specific thing to avoid, with the reason}.

## Tools (if any)
- Use {tool} when {situation}.
```

Keep it as short as it can be while complete; long rule lists written for older models can make newer models rigid. State the goal and let the model use judgement.

## 12. Prompt Templates in Code

> Building prompts from variables safely and reproducibly. Keep templates as constants or files; fill them with f-strings or `str.format`; version them with your code.
>
> Use it in every app; never build prompts by scattered string concatenation.

```python
from pathlib import Path

SUMMARY_PROMPT = """Summarize the meeting transcript in <transcript> for {audience}.

<transcript>
{transcript}
</transcript>

Return exactly 3 bullet points: decisions, owners, deadlines. Max {max_words} words total."""


def build_summary_prompt(transcript: str, audience: str = "the project team") -> str:
    return SUMMARY_PROMPT.format(transcript=transcript, audience=audience, max_words=80)


SYSTEM_PROMPT = Path("prompts/support_system.md").read_text(encoding="utf-8")   # prompts as files
```

Libraries: Jinja2 for complex templates with loops / conditions. Keep templates stable at the top (good for caching) and variable data at the end.

## 13. Prompt Chaining

> Splitting a complex task into several simpler LLM calls. Each step has one job; code passes the output of one step to the next and can validate in between.
>
> Use it for long or multi-stage tasks (research -> outline -> draft -> edit), when one prompt gets inconsistent.

```text
Step 1: extract facts from each document          (parallel, cheap model)
         |
Step 2: combine facts into an outline             (code checks the outline has all sections)
         |
Step 3: write the report from the outline
         |
Step 4: review the report against a checklist -> fix issues
```

Benefits: each prompt is simpler and testable; failures are easy to locate; steps can use different models.

## 14. Common Task Recipes

> Proven prompt shapes for everyday tasks. Copy, then adapt the details.
>
> Use it for starting a new feature quickly.

| Task | Prompt pattern |
|---|---|
| Classification | Labels with definitions + examples + "answer with the label only" (or structured output with an enum) |
| Extraction | Schema of fields + "use null if not present" + structured output |
| Summarisation | Audience + purpose + length + what to focus on / omit |
| Rewriting | Target style + what must stay unchanged (facts, names, numbers) |
| Q&A over docs | Documents first, quotes first, answer from quotes only, "I don't know" fallback |
| Comparison | Criteria list + table output |
| Brainstorming | Number of ideas + diversity request + constraints |
| Translation | Target language + tone + glossary of terms not to translate |
| Grading (LLM-as-judge) | Rubric with criteria and scores + reasoning before score ([34](34_evals-observability.md)) |

## 15. Prompting for Code Generation

> Getting correct, usable code from an LLM. Give the environment, constraints, interfaces and examples of the surrounding code style.
>
> Use it for generating functions, tests, SQL, refactors.

```text
Write a Python 3.12 function using pandas 2.x.

Goal: clean a DataFrame of customer records before loading into our warehouse.
Input: DataFrame with columns name (str), email (str), signup_date (str, "DD.MM.YYYY").
Requirements:
- strip and title-case names
- lowercase emails; drop rows with invalid emails (simple regex is fine)
- parse signup_date to datetime; invalid dates become NaT
- return a new DataFrame, do not modify the input
Style: type hints, docstring, no print statements.
Also write 3 pytest tests covering the invalid email and invalid date cases.
```

Always run and test generated code; ask the model to explain assumptions.

## 16. Tone, Length and Style Control

> Controlling how the answer reads. Describe the target reader and give a concrete length / structure; show a sample if style matters.
>
> Use it for customer-facing text, reports, UX copy.

| Want | Say |
|---|---|
| Shorter | "Max 2 sentences" / "under 50 words" |
| Simpler | "Explain for a 15-year-old; no jargon" |
| More formal | "Formal business English, no contractions" |
| Less hedging | "State your recommendation directly, then the main reason" |
| Consistent brand voice | Include 2 short samples of approved copy |

## 17. Anti-Patterns

> Common mistakes that hurt results. Each has a fix.
>
> Use it for reviewing a prompt that underperforms.

| Anti-pattern | Fix |
|---|---|
| Vague request ("analyze this") | State goal, audience, format, length |
| Instructions mixed with data | Use XML tags |
| Huge list of ALL-CAPS rules | Fewer rules, each with its reason; let the model use judgement |
| Only negative instructions | Say what to do instead |
| Contradicting rules | Remove conflicts; prioritise explicitly |
| Examples all the same | Diverse examples incl. edge cases |
| Asking for JSON in text and regex-parsing it | Structured outputs |
| Everything in one giant prompt | Prompt chaining |
| Dumping all documents | Retrieve only relevant chunks (RAG) |
| Changing prompts without measuring | Keep an eval set; compare versions |
| Timestamp / random ID at the top of the system prompt | Put variable data at the end (keeps prompt caching working) |

## 18. Iterating on Prompts

> Improving prompts systematically instead of by feel. Collect test cases, run, look at failures, change one thing, re-run, compare.
>
> Use it in any prompt that goes to production.

```text
1. Write 10 to 50 real test inputs (include hard and weird ones)
2. Define what "good" means (exact label, contains X, rubric score)
3. Run prompt v1 -> score
4. Read the failures: missing context? unclear rule? format problem?
5. Change ONE thing -> v2 -> score again
6. Keep the better version; version-control prompts with your code
```

Tools and techniques: [34 - Evals and Observability](34_evals-observability.md). You can also ask a strong model to critique and improve a prompt, then verify with your eval set.

## 19. Prompt Checklist

> A final review before shipping a prompt. Tick every line that applies.
>
> Use it for code review of prompts.

- [ ] A new colleague could do the task from this prompt alone
- [ ] Goal, audience and use of the output are stated
- [ ] Inputs are wrapped in clear tags
- [ ] Output format is explicit (structured outputs for code-consumed data)
- [ ] Edge cases and "I don't know" behaviour are defined
- [ ] 2 to 5 diverse examples if format / labels are subtle
- [ ] No contradictions; rules explain their reasons
- [ ] Stable content first, variable content last (caching)
- [ ] Untrusted content cannot override instructions ([37](37_ai-security.md))
- [ ] Tested on an eval set, results recorded

## 20. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Rewrite a vague prompt

Improve: `Summarize this call.`

<details markdown="1">
<summary>Solution</summary>

```text
You summarise sales calls for our account managers, who read them on their phones before
calling the customer back.

<transcript>
{transcript}
</transcript>

Write exactly 3 bullet points: the customer's need, their budget, and the agreed next step.
Max 60 words in total. If the budget is not mentioned, write "budget: unknown".
```

</details>

### Exercise 2: Few-shot labels

Write a prompt that classifies messages as billing, technical or shipping with three examples.

<details markdown="1">
<summary>Solution</summary>

Use `<examples>` with one diverse example per label (including one tricky message), then the new message in `<message>` tags and "Answer with the label only." See section 5 for a full template.

</details>

### Exercise 3: Spot the anti-patterns

What is wrong with: `NEVER EVER use bullets!!! Be good. Here is data: ...long email... summarize`?

<details markdown="1">
<summary>Solution</summary>

All caps without a reason, a negative-only instruction (say what to do instead, e.g. "write flowing paragraphs"), the vague "be good", data not separated by tags, and no audience, length or format.

</details>

---

<!-- nav:start -->
**Previous:** [26 - LLM APIs](26_llm-apis.md) | **Index:** [All guides](README.md) | **Next:** [28 - Tool Use (Function Calling)](28_tool-use.md)
<!-- nav:end -->
