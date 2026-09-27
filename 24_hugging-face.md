# 24 - Hugging Face

<!-- nav:start -->
**Previous:** [23 - PyTorch](23_pytorch.md) | **Index:** [All guides](README.md) | **Next:** [25 - LLM Fundamentals](25_llm-fundamentals.md)
<!-- nav:end -->

Quick reference for the Hugging Face ecosystem: the Model Hub, `transformers` pipelines, tokenizers, running open models, embeddings, datasets and sharing models.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Hugging Face?

Hugging Face is the **GitHub of AI models**: a platform (huggingface.co) hosting over a million free pretrained models, datasets and demo apps, plus Python libraries to use them. Instead of training a model from scratch (which costs weeks and lots of GPUs), you **download a pretrained model** that already understands language, images or audio and use it directly, or fine-tune it on your data.

| Library | Does |
|---|---|
| `transformers` | Load and run pretrained models (text, vision, audio, LLMs) |
| `tokenizers` | Fast text -> token conversion |
| `datasets` | Download / process datasets efficiently |
| `sentence-transformers` | Text embeddings for search and RAG |
| `huggingface_hub` | Download / upload models and files, auth |
| `accelerate`, `peft`, `trl` | Multi-GPU, efficient fine-tuning (LoRA), RLHF / SFT training |

### Mental model

Every text model works as a 3-step pipeline:

```text
"I love this phone"
        |
        v   TOKENIZER (text -> numbers)
[101, 1045, 2293, 2023, 3042, 102]         token IDs
        |
        v   MODEL (PyTorch network with pretrained weights)
[[-2.1, 3.4]]                              logits (raw scores)
        |
        v   POST-PROCESSING (numbers -> answer)
{"label": "POSITIVE", "score": 0.998}
```

A **checkpoint** on the Hub (like `distilbert-base-uncased-finetuned-sst-2-english`) = model architecture + trained weights + tokenizer. `pipeline(...)` hides all three steps; `AutoTokenizer` + `AutoModel...` give you each step separately.

### Why use it?

- **Free, ready-made models** for classification, NER, summarisation, translation, embeddings, speech, vision, open LLMs.
- **Private / offline**: models run on your own machine or server; no data leaves.
- **Cheap at scale**: small specialised models can be much cheaper than LLM API calls for narrow tasks.
- **Foundation for fine-tuning** and for tools like Ollama and vLLM.

### Key terms

| Term | Meaning |
|---|---|
| Model Hub | Website hosting models, datasets and Spaces |
| Checkpoint / model ID | `organisation/model-name`, e.g. `sentence-transformers/all-MiniLM-L6-v2` |
| Model card | README of a model: purpose, licence, limitations |
| Tokenizer | Converts text to token IDs and back |
| Pipeline | One-line helper for a task |
| Task | What a model does: `text-classification`, `summarization`, `text-generation` ... |
| Logits | Raw output scores before softmax |
| Base vs instruct model | Base continues text; instruct / chat follows instructions |
| Gated model | Needs you to accept a licence and log in (e.g. some Llama models) |
| Space | Hosted demo app (Gradio / Streamlit) |
| safetensors | Safe, fast file format for weights |

**Where it fits:** runs on [23 - PyTorch](23_pytorch.md); embeddings for [29 - Embeddings and Vector DBs](29_embeddings-vector-db.md); open LLMs also via [35 - Local LLMs](35_local-llms.md); training in [36 - Fine-tuning](36_fine-tuning.md); demos in [38 - AI UIs](38_ai-ui.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Hugging Face documentation | https://huggingface.co/docs |
| Transformers | https://huggingface.co/docs/transformers |
| Hub (models, datasets, Spaces) | https://huggingface.co/docs/hub |
| Datasets | https://huggingface.co/docs/datasets |
| Sentence Transformers | https://sbert.net/ |
| Hugging Face Learn (free courses) | https://huggingface.co/learn |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install and Log In](#1-install-and-log-in)
2. [Finding Models on the Hub](#2-finding-models-on-the-hub)
3. [Pipelines (One-Liners)](#3-pipelines-one-liners)
4. [Pipeline Tasks Cheat Sheet](#4-pipeline-tasks-cheat-sheet)
5. [Tokenizers](#5-tokenizers)
6. [AutoModel: Step-by-Step Inference](#6-automodel-step-by-step-inference)
7. [Text Generation with Open LLMs](#7-text-generation-with-open-llms)
8. [Chat Templates](#8-chat-templates)
9. [Generation Parameters](#9-generation-parameters)
10. [Running Big Models on Small Hardware](#10-running-big-models-on-small-hardware)
11. [Embeddings with sentence-transformers](#11-embeddings-with-sentence-transformers)
12. [Datasets Library](#12-datasets-library)
13. [Hub: Download, Upload, Cache](#13-hub-download-upload-cache)
14. [Inference Providers and Endpoints](#14-inference-providers-and-endpoints)
15. [Spaces](#15-spaces)
16. [Licences](#16-licences)
17. [Troubleshooting](#17-troubleshooting)
18. [Try It](#18-try-it)

---

## 0. Flags and Parameters

> The most common `from_pretrained` / `pipeline` / generation parameters. Passed as keyword arguments when loading or calling models.
>
> Use this when you see `pipeline("text-generation", model=..., device_map="auto", torch_dtype="auto")` and want to know what each part does.

```text
pipeline("summarization", model="facebook/bart-large-cnn", device=0)
|        |                |                                 |
|        |                |                                 +-- run on GPU 0 (-1 or omit = CPU)
|        |                +------------------------------------ which checkpoint from the Hub
|        +----------------------------------------------------- task: decides pre/post-processing
+-------------------------------------------------------------- one-line helper
```

| Parameter | Used in | Meaning |
|---|---|---|
| `model` | pipeline | Model ID on the Hub or local folder |
| `device` | pipeline | `0` = first GPU, `"cpu"`, `"mps"` |
| `device_map="auto"` | from_pretrained / pipeline | Spread the model over available GPUs / CPU automatically (needs `accelerate`) |
| `torch_dtype` / `dtype` | from_pretrained | Precision: `"auto"`, `torch.float16`, `torch.bfloat16` (half memory) |
| `quantization_config` | from_pretrained | Load in 8-bit / 4-bit to save memory |
| `trust_remote_code` | from_pretrained | Allow custom code from the repo (only for trusted repos) |
| `revision` | from_pretrained | Git branch / commit of the model repo |
| `token` | from_pretrained | HF access token for gated / private models |
| `max_new_tokens` | generate | Max tokens to generate |
| `temperature`, `top_p`, `do_sample` | generate | Randomness settings (section 9) |
| `truncation`, `padding`, `max_length` | tokenizer | Cut / pad inputs to a length |
| `return_tensors="pt"` | tokenizer | Return PyTorch tensors |
| `batch_size` | pipeline | Process several inputs at once |

---

## 1. Install and Log In

> Installing the libraries and authenticating to the Hub. pip install; log in with an access token from huggingface.co -> Settings -> Access Tokens.
>
> Use this when once per machine; login is needed for gated / private models and uploads.

```powershell
pip install transformers accelerate sentence-transformers datasets huggingface_hub
pip install torch                          # the backend (see 23 - PyTorch for GPU builds)

hf auth login                              # paste token (older CLI: huggingface-cli login)
```

Or set the environment variable `HF_TOKEN`. Never commit tokens.

## 2. Finding Models on the Hub

> Choosing a good model for your task. Filter by task, language, licence, size; sort by downloads / trending; read the model card.
>
> Use it before writing any code.

Checklist for a model card:

- **Task and language** match yours.
- **Licence** allows your use (commercial?).
- **Size** (parameters, file size) fits your hardware.
- **Evaluation results** and **limitations** / biases.
- **Recent activity** and many downloads = well-tested.

## 3. Pipelines (One-Liners)

> The easiest way to run a model: task + model -> results. `pipeline(task, model=...)` downloads the model and tokenizer (cached), and handles pre / post-processing.
>
> Use it for prototyping, simple production tasks.

```python
from transformers import pipeline

clf = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
clf("I love this phone")                       # [{'label': 'POSITIVE', 'score': 0.9998}]
clf(["great!", "terrible..."], batch_size=8)   # many at once

ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
ner("Ana works at Microsoft in Berlin")        # entities with type PER / ORG / LOC

zs = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
zs("The invoice is overdue", candidate_labels=["billing", "tech support", "sales"])

summ = pipeline("summarization", model="facebook/bart-large-cnn")
summ(long_text, max_length=120, min_length=30)
```

## 4. Pipeline Tasks Cheat Sheet

> Common task names and what they return. Use the task string in `pipeline(...)`.
>
> Use it for picking the right task for your problem.

| Task string | Input -> output | Example use |
|---|---|---|
| `text-classification` / `sentiment-analysis` | text -> label + score | Sentiment, spam, topic |
| `zero-shot-classification` | text + your labels -> scores | Classify without training |
| `token-classification` / `ner` | text -> entities | Extract names, places |
| `question-answering` | question + context -> answer span | Extractive QA |
| `summarization` | long text -> short text | Summaries |
| `translation` | text -> text in another language | Translation |
| `text-generation` | prompt -> continuation / chat reply | Open LLMs |
| `feature-extraction` | text -> vectors | Embeddings |
| `fill-mask` | "Paris is the [MASK] of France" -> words | Masked language models |
| `automatic-speech-recognition` | audio -> text | Whisper transcription |
| `image-classification` | image -> labels | Vision |
| `object-detection` | image -> boxes + labels | Vision |
| `image-to-text` | image -> caption | Captioning |

## 5. Tokenizers

> Converting text into the token IDs a model understands. Text is split into sub-word pieces from a fixed vocabulary; each piece has an ID. The tokenizer must match the model.
>
> Use it for step-by-step inference, counting tokens, understanding context limits.

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("bert-base-uncased")
tok.tokenize("Tokenization is fun!")         # ['token', '##ization', 'is', 'fun', '!']
enc = tok("Tokenization is fun!", return_tensors="pt")
enc["input_ids"]                             # tensor([[101, 19204, 3989, 2003, 4569, 999, 102]])
enc["attention_mask"]                        # 1 = real token, 0 = padding
tok.decode(enc["input_ids"][0])              # back to text
tok(["short", "a bit longer text"], padding=True, truncation=True, max_length=128, return_tensors="pt")
```

Rule of thumb for English: 1 token is about 4 characters or 0.75 words. Other languages and code use more tokens per word.

## 6. AutoModel: Step-by-Step Inference

> Loading tokenizer and model separately for full control. `AutoTokenizer` and `AutoModelFor<Task>` pick the right classes from the model's config.
>
> Use it for custom batching, access to logits / hidden states, production code.

```python
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_ID = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID).eval()

inputs = tok(["I love it", "I hate it"], padding=True, return_tensors="pt")
with torch.no_grad():
    logits = model(**inputs).logits
probs = logits.softmax(dim=-1)
labels = [model.config.id2label[i] for i in probs.argmax(dim=-1).tolist()]
```

| Class | For |
|---|---|
| `AutoModel` | Base model, returns hidden states |
| `AutoModelForSequenceClassification` | Text classification |
| `AutoModelForTokenClassification` | NER |
| `AutoModelForQuestionAnswering` | Extractive QA |
| `AutoModelForCausalLM` | Text generation (GPT-style LLMs) |
| `AutoModelForSeq2SeqLM` | Translation / summarisation (T5, BART) |

## 7. Text Generation with Open LLMs

> Running an open-weight LLM (Llama, Qwen, Mistral, Gemma, Phi ...) yourself. Load with `AutoModelForCausalLM` or the `text-generation` pipeline; the model predicts the next token repeatedly.
>
> Use it for private data, offline use, research, fine-tuning. For simple local chat, Ollama is easier ([35 - Local LLMs](35_local-llms.md)).

```python
from transformers import pipeline

chat = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-1.5B-Instruct",       # small instruct model; pick one that fits your hardware
    torch_dtype="auto",
    device_map="auto",
)
messages = [
    {"role": "system", "content": "You are a concise assistant."},
    {"role": "user", "content": "Explain overfitting in one sentence."},
]
out = chat(messages, max_new_tokens=100)
print(out[0]["generated_text"][-1]["content"])
```

Memory needed (weights only, roughly): parameters x bytes per parameter. 7B model: ~14 GB in float16, ~4 to 5 GB in 4-bit.

## 8. Chat Templates

> Each chat model expects messages formatted with its own special tokens. `tokenizer.apply_chat_template` turns a list of role / content messages into the exact prompt format the model was trained on.
>
> Use it in any chat / instruct model used with `generate` directly.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype="auto", device_map="auto")

messages = [{"role": "user", "content": "Name three uses of Python."}]
input_ids = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)
output = model.generate(input_ids, max_new_tokens=150, do_sample=True, temperature=0.7)
print(tok.decode(output[0][input_ids.shape[-1]:], skip_special_tokens=True))
```

Using the wrong format (plain text instead of the template) makes chat models behave badly.

## 9. Generation Parameters

> Settings that control how text is generated. At each step the model gives probabilities for every next token; these settings decide how to pick one.
>
> Use it for tuning creativity vs precision, output length.

| Parameter | Effect |
|---|---|
| `max_new_tokens` | Upper limit on generated length |
| `do_sample=False` | Greedy: always pick the most likely token (deterministic) |
| `temperature` | < 1 sharper / safer, > 1 more random / creative (needs `do_sample=True`) |
| `top_p` | Sample only from the smallest set of tokens covering p of probability (e.g. 0.9) |
| `top_k` | Sample only from the k most likely tokens |
| `repetition_penalty` | > 1 discourages repeating |
| `num_beams` | Beam search: explore several candidates (translation / summarisation) |
| `stop_strings` / `eos_token_id` | When to stop |

More about sampling in [25 - LLM Fundamentals](25_llm-fundamentals.md).

## 10. Running Big Models on Small Hardware

> Fitting models into limited GPU / CPU memory. Lower precision (float16 / bfloat16), quantization (8-bit / 4-bit), automatic offloading with `device_map="auto"`.
>
> Use this when model does not fit, or you want faster inference.

```python
import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)   # needs bitsandbytes + NVIDIA GPU
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3",
                                             quantization_config=bnb, device_map="auto")
```

| Precision | Bytes / parameter | 7B model |
|---|---|---|
| float32 | 4 | ~28 GB |
| float16 / bfloat16 | 2 | ~14 GB |
| 8-bit | 1 | ~7 GB |
| 4-bit | 0.5 | ~4 GB |

For CPU / laptop use, GGUF models via Ollama or llama.cpp are usually easier ([35 - Local LLMs](35_local-llms.md)).

## 11. Embeddings with sentence-transformers

> Turning text into vectors that capture meaning, for search, clustering and RAG. An embedding model maps each sentence to a fixed-length vector; similar meanings give nearby vectors.
>
> Use it for semantic search, duplicate detection, RAG retrieval ([29](29_embeddings-vector-db.md), [30](30_rag.md)).

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")   # small, fast, English
docs = ["How do I reset my password?", "Shipping takes 3 days", "Forgot my login"]
doc_emb = model.encode(docs, normalize_embeddings=True)               # shape (3, 384)
query_emb = model.encode("I can't log in", normalize_embeddings=True)

scores = model.similarity(query_emb, doc_emb)          # cosine similarity
best = docs[int(scores.argmax())]                      # "Forgot my login"
```

Multilingual / stronger options: `BAAI/bge-m3`, `intfloat/multilingual-e5-large`. Check the MTEB leaderboard for rankings.

## 12. Datasets Library

> Loading and processing datasets from the Hub or local files. `load_dataset` returns an Arrow-backed dataset; `map` applies functions efficiently in batches.
>
> Use it for evaluation sets, fine-tuning data, benchmarks.

```python
from datasets import load_dataset

ds = load_dataset("imdb")                                   # DatasetDict with train / test
ds["train"][0]
small = ds["train"].shuffle(seed=42).select(range(1000))
local = load_dataset("csv", data_files="reviews.csv")
local = load_dataset("json", data_files="data.jsonl")

tokenized = small.map(lambda b: tok(b["text"], truncation=True), batched=True)
small.to_pandas()
```

## 13. Hub: Download, Upload, Cache

> Managing model files and sharing your own. Models are Git repos; files are cached locally (default `~/.cache/huggingface`).
>
> Use it for offline machines, Docker images, publishing a fine-tuned model.

```python
from huggingface_hub import hf_hub_download, snapshot_download

path = hf_hub_download(repo_id="BAAI/bge-m3", filename="config.json")
folder = snapshot_download("sentence-transformers/all-MiniLM-L6-v2")    # whole repo

model.push_to_hub("your-username/my-finetuned-model")                    # upload (after login)
tok.push_to_hub("your-username/my-finetuned-model")
```

```powershell
hf download BAAI/bge-m3 --local-dir ./models/bge-m3       # CLI download
$env:HF_HOME = "D:\hf-cache"                               # move the cache (big files!)
$env:HF_HUB_OFFLINE = "1"                                  # use only cached files
```

## 14. Inference Providers and Endpoints

> Running Hub models on hosted hardware instead of your machine. `InferenceClient` calls serverless providers; Inference Endpoints give you a dedicated, autoscaling deployment.
>
> Use it when you have no GPU locally, for quick tests, or for production hosting of open models.

```python
from huggingface_hub import InferenceClient

client = InferenceClient()                      # uses HF_TOKEN
client.chat_completion(
    model="Qwen/Qwen2.5-72B-Instruct",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=100,
)
```

Availability of specific models on serverless providers changes; check the model page's "Deploy" / "Inference Providers" section.

## 15. Spaces

> Free hosted demo apps on Hugging Face. A Git repo with `app.py` using Gradio or Streamlit (or a Dockerfile); HF builds and serves it.
>
> Use it for sharing a demo of your model or AI app. Building UIs: [38 - AI UIs](38_ai-ui.md).

## 16. Licences

> The legal terms for using a model. Shown on the model card; some require accepting terms.
>
> Use it before using any model in a product.

| Licence type | Examples | Commercial use |
|---|---|---|
| Permissive | Apache 2.0, MIT | Yes |
| Custom "open weight" | Llama, Gemma community licences | Usually yes, with conditions |
| Non-commercial | CC BY-NC | No |
| Research only | Various | No |

## 17. Troubleshooting

| Problem | Fix |
|---|---|
| `OSError: ... is not a valid model identifier` | Typo in model ID, or gated / private: log in and accept the licence |
| `401` / `403` downloading | `hf auth login` or set `HF_TOKEN`; accept terms on the model page |
| Download very slow / disk full | Move cache with `HF_HOME`; use smaller models |
| `CUDA out of memory` | `torch_dtype="auto"`, 4-bit quantization, smaller model, smaller batch |
| Slow on CPU | Expected for big models; use smaller / quantized models or Ollama |
| Chat model gives strange output | Use `apply_chat_template`; use the instruct version of the model |
| `Token indices sequence length is longer than the specified maximum` | `truncation=True, max_length=...`; chunk long texts |
| `trust_remote_code` required | The repo has custom code; read it and only enable for trusted sources |
| `bitsandbytes` errors on Windows / CPU | 4-bit bitsandbytes needs an NVIDIA GPU; use GGUF via Ollama instead |
| Different results each run | Sampling is on; set `do_sample=False` or a seed (`transformers.set_seed(42)`) |

## 18. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Sentiment

Classify three sentences with a sentiment pipeline.

<details markdown="1">
<summary>Solution</summary>

```python
from transformers import pipeline

clf = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
clf(["Great service!", "Terrible delay.", "It was okay."])
```

</details>

### Exercise 2: Count tokens

How many tokens does `"Tokenization is surprisingly useful!"` have for `bert-base-uncased`?

<details markdown="1">
<summary>Solution</summary>

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("bert-base-uncased")
len(tok.tokenize("Tokenization is surprisingly useful!"))
```

</details>

### Exercise 3: Most similar pair

Embed three sentences and find the most similar pair.

<details markdown="1">
<summary>Solution</summary>

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
emb = model.encode(sentences, normalize_embeddings=True)
sim = model.similarity(emb, emb)
sim.fill_diagonal_(-1)
i, j = divmod(int(sim.argmax()), len(sentences))
sentences[i], sentences[j]
```

</details>

---

<!-- nav:start -->
**Previous:** [23 - PyTorch](23_pytorch.md) | **Index:** [All guides](README.md) | **Next:** [25 - LLM Fundamentals](25_llm-fundamentals.md)
<!-- nav:end -->
