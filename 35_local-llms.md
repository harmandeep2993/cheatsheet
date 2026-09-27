# 35 - Local and Self-Hosted LLMs

Quick reference for running open-weight LLMs on your own hardware or servers: Ollama in depth, llama.cpp and GGUF, LM Studio, vLLM for production serving, quantization, hardware sizing and performance.

## Introduction

### What does "running an LLM locally" mean?

Open-weight models (Llama, Qwen, Mistral, Gemma, Phi, DeepSeek ...) publish their **weights** (the trained numbers), so you can download them and run inference on **your own** laptop, workstation, GPU server or cloud VM. An **inference server** loads the weights into memory and exposes an API (often OpenAI-compatible), so your apps call it just like a hosted API, but nothing leaves your machine and there is no per-token bill.

### Mental model

```text
  MODEL FILE (weights)           INFERENCE ENGINE                 API                  YOUR APP
  qwen3-8b-Q4_K_M.gguf   --->   Ollama / llama.cpp / vLLM   --->   :11434 or :8000  <---  Python, LangChain,
  (downloaded once,              loads weights into GPU /          /api/chat or           Open WebUI, agents
   4-bit quantized ~5 GB)        CPU RAM, generates tokens         /v1/chat/completions

                       Everything must fit in memory:
     weights (params x bytes per param)  +  KV cache (grows with context length)  +  overhead
```

Rule of thumb: the **memory** you have decides which models you can run; the **memory bandwidth / GPU** decides how fast.

### Why run models yourself?

- **Privacy**: sensitive data never leaves your infrastructure.
- **Offline / air-gapped** use.
- **Cost at scale**: fixed hardware cost instead of per-token fees for high volume.
- **Control**: pick exact model versions, fine-tune, customise.
- **Learning**: understand how inference really works.

Trade-offs: the best hosted models are usually stronger than what fits on a laptop; you manage hardware, scaling and updates.

### Key terms

| Term | Meaning |
|---|---|
| Open-weight model | Model whose weights can be downloaded |
| Parameters (7B, 70B) | Number of weights, in billions; bigger = smarter but heavier |
| Quantization | Storing weights with fewer bits (8, 5, 4 ...) to save memory |
| GGUF | File format for quantized models used by llama.cpp and Ollama |
| Q4_K_M, Q5_K_M, Q8_0 | Common GGUF quantization levels (bits + method) |
| VRAM | GPU memory; the main limit for GPU inference |
| Offloading | Keeping some layers on CPU RAM when VRAM is too small (slower) |
| KV cache | Memory storing attention data for the current context; grows with context length |
| Context length (`num_ctx`) | Max tokens per request the server allocates for |
| Tokens per second (tok/s) | Generation speed |
| Inference server | Program serving a model over HTTP (Ollama, vLLM, llama-server, TGI) |
| OpenAI-compatible API | Same endpoints as OpenAI (`/v1/chat/completions`), so OpenAI clients work |

**Where it fits:** models from [24 - Hugging Face](24_hugging-face.md); concepts in [25 - LLM Fundamentals](25_llm-fundamentals.md); called like APIs in [26](26_llm-apis.md); embeddings for [29](29_embeddings-vector-db.md); GPU VM setup in [47 - Azure VM + Ollama](47_azure-vm-ollama.md); containers in [41 - Docker](41_docker.md); fine-tuned models from [36](36_fine-tuning.md).

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Options at a Glance](#1-options-at-a-glance)
2. [Hardware Sizing](#2-hardware-sizing)
3. [Quantization Levels](#3-quantization-levels)
4. [Choosing an Open Model](#4-choosing-an-open-model)
5. [Ollama: Install and CLI](#5-ollama-install-and-cli)
6. [Ollama: Python Library](#6-ollama-python-library)
7. [Ollama: REST API and OpenAI Compatibility](#7-ollama-rest-api-and-openai-compatibility)
8. [Ollama: Modelfile (Custom Models)](#8-ollama-modelfile-custom-models)
9. [Ollama: Configuration and Server](#9-ollama-configuration-and-server)
10. [llama.cpp and GGUF](#10-llamacpp-and-gguf)
11. [LM Studio and Chat UIs](#11-lm-studio-and-chat-uis)
12. [vLLM (Production Serving)](#12-vllm-production-serving)
13. [Running in Docker](#13-running-in-docker)
14. [Performance Tuning](#14-performance-tuning)
15. [Local vs Hosted: Decision Guide](#15-local-vs-hosted-decision-guide)
16. [Troubleshooting](#16-troubleshooting)

---

## 0. Flags and Parameters

> - **What:** Key options for Ollama, llama.cpp and vLLM.
> - **How:** Passed on the command line, in a Modelfile, or as request options.
> - **When to use:** You see `vllm serve ... --max-model-len 8192 --gpu-memory-utilization 0.9` and want to know what each part does.

```text
vllm  serve  Qwen/Qwen2.5-7B-Instruct  --max-model-len 8192  --gpu-memory-utilization 0.9  --port 8000
|     |      |                         |                     |                              |
|     |      |                         |                     |                              +-- HTTP port
|     |      |                         |                     +-- share of GPU memory vLLM may use
|     |      |                         +-------------------- max context (prompt + output) per request
|     |      +---------------------------------------------- Hugging Face model ID or local path
|     +----------------------------------------------------- start an OpenAI-compatible server
+----------------------------------------------------------- inference engine
```

| Tool | Option | Meaning |
|---|---|---|
| Ollama request / Modelfile | `num_ctx` | Context length (default is small; raise for RAG / long chats) |
| Ollama | `temperature`, `top_p`, `top_k`, `repeat_penalty` | Sampling settings |
| Ollama | `num_predict` | Max output tokens |
| Ollama | `keep_alive` | How long the model stays loaded after a request (`"30m"`, `-1` forever, `0` unload) |
| Ollama | `think` | Enable / disable reasoning for thinking models |
| Ollama | `format` | `"json"` or a JSON schema for structured output |
| llama.cpp | `-m model.gguf` | Model file |
| llama.cpp | `-c 8192` | Context size |
| llama.cpp | `-ngl 99` | Number of layers on GPU (99 = all) |
| llama.cpp | `-t 8` | CPU threads |
| vLLM | `--tensor-parallel-size 2` | Split the model across 2 GPUs |
| vLLM | `--quantization awq` / `--dtype bfloat16` | Weight format / precision |
| vLLM | `--max-num-seqs` | Max parallel requests in a batch |

---

## 1. Options at a Glance

> - **What:** The main tools for local / self-hosted inference.
> - **How:** They differ in ease of use, hardware support and throughput.
> - **When to use:** Picking a tool.

| Tool | Best for | Hardware | API |
|---|---|---|---|
| Ollama | Easiest local use, dev, small servers | CPU, NVIDIA, AMD, Apple | Own API + OpenAI-compatible |
| LM Studio | Desktop app with GUI, model browser | CPU, GPU, Apple | OpenAI-compatible local server |
| llama.cpp | Maximum control, edge devices, CPU | Everything | `llama-server` OpenAI-compatible |
| vLLM | High-throughput production on GPUs | NVIDIA (also AMD, others) | OpenAI-compatible |
| HF Text Generation Inference (TGI), SGLang | Production serving alternatives | GPUs | OpenAI-compatible |
| `transformers` directly | Research, fine-tuning experiments | GPU / CPU | Python only ([24](24_hugging-face.md)) |

## 2. Hardware Sizing

> - **What:** Estimating whether a model fits and how fast it runs.
> - **How:** Memory for weights = parameters x bytes per parameter; add 10 to 30% plus the KV cache for your context length.
> - **When to use:** Before downloading models or renting GPUs.

```text
weights_GB ~= params_in_billions x bits_per_weight / 8
  8B model at 4-bit  ~= 8 x 4 / 8  = 4 GB   (+ context + overhead -> ~5 to 6 GB)
  8B model at 16-bit ~= 8 x 16 / 8 = 16 GB
 70B model at 4-bit  ~= 70 x 4 / 8 = 35 GB  (+ overhead -> ~40+ GB, multi-GPU or big unified memory)
```

| Hardware | Comfortable model size (4-bit) |
|---|---|
| Laptop CPU, 16 GB RAM | 1B to 8B (slow but usable) |
| NVIDIA GPU 8 GB VRAM | up to ~8B |
| NVIDIA GPU 16 GB (T4, RTX 4080) | up to ~14B |
| NVIDIA GPU 24 GB (RTX 4090, L4) | up to ~30B |
| Apple Silicon 32 to 64 GB unified memory | 14B to 70B (unified memory is shared CPU / GPU) |
| 80 GB GPU (A100 / H100) | 70B at 4 to 8 bit, faster serving |

Speed depends mostly on memory bandwidth: GPUs >> Apple Silicon > CPUs. Anything that spills from VRAM to CPU RAM gets much slower.

## 3. Quantization Levels

> - **What:** How many bits each weight is stored with.
> - **How:** Fewer bits = smaller and faster, but slightly lower quality; the K-quants (`_K_M`) balance this well.
> - **When to use:** Choosing a model variant (tag) to download.

| Level | Bits | Quality | Use |
|---|---|---|---|
| F16 / BF16 | 16 | Original | Plenty of memory, fine-tuning base |
| Q8_0 | 8 | Nearly original | Quality-critical, memory available |
| Q6_K | ~6.5 | Very good | Good compromise |
| Q5_K_M | ~5.5 | Very good | Good compromise |
| Q4_K_M | ~4.8 | Good (most popular default) | Laptops, most local use |
| Q3 / Q2 | 3 / 2 | Noticeably worse | Only if nothing else fits |

A bigger model at Q4 often beats a smaller model at Q8. GPU servers (vLLM) use formats like AWQ, GPTQ or FP8 instead of GGUF.

## 4. Choosing an Open Model

> - **What:** Picking a model family and size.
> - **How:** Start with a well-known instruct model that fits your hardware; test on your own eval set ([34](34_evals-observability.md)).
> - **When to use:** Any local project.

| Need | Look for |
|---|---|
| General chat / assistant | Recent Llama, Qwen, Mistral, Gemma instruct models |
| Reasoning | Models with a thinking mode (e.g. Qwen3, DeepSeek-R1 distills) |
| Code | Code-specialised variants (Qwen Coder, Codestral, DeepSeek Coder ...) |
| Small / fast | 1B to 4B models (Phi, Gemma small, Qwen small, Llama small) |
| Embeddings | `bge-m3`, `nomic-embed-text`, `mxbai-embed-large` |
| Vision | Models with vision support (Llama vision, Qwen-VL, Gemma multimodal) |
| Tool calling | Check the model page for "tools" support |

Check the **licence** ([24](24_hugging-face.md) section 16) and the model's **context length**. New models appear constantly; the Ollama library and Hugging Face trending pages show what is current.

## 5. Ollama: Install and CLI

> - **What:** The easiest way to download and run local models.
> - **How:** Install the app; it runs a background server on port 11434; the `ollama` CLI manages models.
> - **When to use:** Local development, prototypes, small servers.

```powershell
winget install -e --id Ollama.Ollama            # Windows (Mac: download app / brew install ollama)
curl -fsSL https://ollama.com/install.sh | sh    # Linux

ollama --version
ollama pull qwen3:4b                    # download a model (name:tag)
ollama run qwen3:4b                     # interactive chat (/bye to exit, /? for help)
ollama run qwen3:4b "Summarise RAG in one sentence."    # one-shot
ollama list                             # downloaded models and sizes
ollama ps                               # loaded models, CPU / GPU split, expiry
ollama show qwen3:4b                    # details: parameters, context, template, licence
ollama stop qwen3:4b                    # unload from memory
ollama rm qwen3:4b                      # delete from disk
ollama cp qwen3:4b my-assistant         # copy / rename
ollama serve                            # start the server manually (if not running as a service)
```

In-chat commands: `/set parameter num_ctx 8192`, `/set nothink` (thinking models), `/show info`, `/bye`.

## 6. Ollama: Python Library

> - **What:** Calling Ollama from Python.
> - **How:** `pip install ollama`; `chat`, `generate`, `embed` functions; `Client(host=...)` for remote servers.
> - **When to use:** Apps, scripts and RAG pipelines using local models.

```python
import ollama

resp = ollama.chat(
    model="qwen3:4b",
    messages=[
        {"role": "system", "content": "You are concise."},
        {"role": "user", "content": "What is a vector database?"},
    ],
    options={"temperature": 0.3, "num_ctx": 8192},
    think=False,                          # thinking models: skip reasoning for speed
    keep_alive="30m",
)
print(resp["message"]["content"])

for chunk in ollama.chat(model="qwen3:4b", messages=msgs, stream=True):    # streaming
    print(chunk["message"]["content"], end="", flush=True)

emb = ollama.embed(model="bge-m3", input=["text one", "text two"])["embeddings"]

client = ollama.Client(host="http://localhost:11435")      # e.g. via SSH tunnel to a VM ([47])
```

Structured output with a schema:

```python
from pydantic import BaseModel


class City(BaseModel):
    name: str
    country: str


resp = ollama.chat(model="qwen3:4b", messages=[{"role": "user", "content": "Capital of Japan?"}],
                   format=City.model_json_schema(), think=False)
city = City.model_validate_json(resp["message"]["content"])
```

## 7. Ollama: REST API and OpenAI Compatibility

> - **What:** The HTTP endpoints behind Ollama.
> - **How:** Native `/api/...` endpoints plus OpenAI-compatible `/v1/...` endpoints.
> - **When to use:** Other languages, curl tests, reusing OpenAI-based code and frameworks.

```bash
curl http://localhost:11434/api/tags                                   # list models
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:4b",
  "messages": [{"role": "user", "content": "Hi"}],
  "stream": false
}'
curl http://localhost:11434/api/embed -d '{"model": "bge-m3", "input": "hello"}'
```

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")   # key is required but ignored
r = client.chat.completions.create(model="qwen3:4b", messages=[{"role": "user", "content": "Hi"}])
print(r.choices[0].message.content)
```

## 8. Ollama: Modelfile (Custom Models)

> - **What:** A recipe that creates your own model variant with a built-in system prompt and parameters.
> - **How:** Write a `Modelfile`, then `ollama create`.
> - **When to use:** Reusable assistants with fixed behaviour, bigger default context, or importing your own GGUF (e.g. a fine-tune).

```text
# Modelfile
FROM qwen3:4b
PARAMETER temperature 0.3
PARAMETER num_ctx 16384
SYSTEM """You are a SQL assistant for PostgreSQL. Reply with a query and one sentence of explanation."""
```

```powershell
ollama create sql-helper -f Modelfile
ollama run sql-helper
```

Import a local GGUF: `FROM ./my-finetune-Q4_K_M.gguf` in the Modelfile.

## 9. Ollama: Configuration and Server

> - **What:** Environment variables that control the Ollama server.
> - **How:** Set them for the service (Windows: system env vars then restart Ollama; Linux: `systemctl edit ollama`).
> - **When to use:** Sharing Ollama on a network, moving model storage, keeping models loaded.

| Variable | Meaning |
|---|---|
| `OLLAMA_HOST` | Address the server listens on (`0.0.0.0:11434` to accept remote connections; protect it!) / the client connects to |
| `OLLAMA_MODELS` | Folder where models are stored (move to a big disk) |
| `OLLAMA_KEEP_ALIVE` | Default time models stay in memory (`30m`, `-1`) |
| `OLLAMA_NUM_PARALLEL` | Parallel requests per model |
| `OLLAMA_MAX_LOADED_MODELS` | Models kept loaded at the same time |
| `OLLAMA_CONTEXT_LENGTH` | Default context length |
| `OLLAMA_ORIGINS` | Allowed browser origins (CORS) |

Ollama has no built-in authentication: never expose port 11434 to the internet. Use an SSH tunnel ([47](47_azure-vm-ollama.md)) or a reverse proxy with auth ([43](43_nginx-https.md)).

## 10. llama.cpp and GGUF

> - **What:** The C / C++ inference engine that Ollama and many tools build on; runs GGUF models almost anywhere.
> - **How:** Download a release (or build), get a GGUF from Hugging Face, run `llama-cli` (chat) or `llama-server` (OpenAI-compatible API + web UI).
> - **When to use:** Fine control of settings, newest features, embedded / edge devices.

```powershell
winget install llama.cpp                    # or download from github.com/ggml-org/llama.cpp releases; Mac: brew install llama.cpp
hf download Qwen/Qwen2.5-7B-Instruct-GGUF qwen2.5-7b-instruct-q4_k_m.gguf --local-dir models

llama-server -m models/qwen2.5-7b-instruct-q4_k_m.gguf -c 8192 -ngl 99 --port 8080
# open http://localhost:8080 for a chat UI; API at http://localhost:8080/v1/chat/completions
```

## 11. LM Studio and Chat UIs

> - **What:** Desktop and web interfaces for local models.
> - **How:** LM Studio downloads GGUF / MLX models and can start a local OpenAI-compatible server; Open WebUI gives a ChatGPT-like web UI on top of Ollama or any OpenAI-compatible API.
> - **When to use:** Trying models without code; giving non-technical users a chat interface.

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
# open http://localhost:3000 ; it finds Ollama on the host
```

## 12. vLLM (Production Serving)

> - **What:** A high-throughput inference server for GPUs.
> - **How:** Continuous batching and PagedAttention let one GPU serve many concurrent users efficiently; exposes an OpenAI-compatible API.
> - **When to use:** Many users / high request volume on NVIDIA GPUs (Linux). Ollama is simpler for single-user or dev.

```bash
pip install vllm                                  # Linux + NVIDIA GPU
vllm serve Qwen/Qwen2.5-7B-Instruct --max-model-len 8192 --gpu-memory-utilization 0.9 --port 8000

docker run --gpus all -p 8000:8000 -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:latest --model Qwen/Qwen2.5-7B-Instruct --max-model-len 8192
```

```python
client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")
client.chat.completions.create(model="Qwen/Qwen2.5-7B-Instruct", messages=[...])
```

## 13. Running in Docker

> - **What:** Containerised local inference.
> - **How:** Official images for Ollama and vLLM; mount a volume for model files; pass GPUs with `--gpus all` (NVIDIA Container Toolkit needed on Linux).
> - **When to use:** Servers, reproducible setups, Compose stacks with your app.

```yaml
# compose.yaml: app + Ollama
services:
  ollama:
    image: ollama/ollama
    volumes: ["ollama:/root/.ollama"]
    ports: ["127.0.0.1:11434:11434"]          # bind to localhost only
    deploy:
      resources:
        reservations:
          devices: [{driver: nvidia, count: all, capabilities: [gpu]}]
  api:
    build: .
    environment:
      OLLAMA_HOST: http://ollama:11434
    depends_on: [ollama]
volumes:
  ollama:
```

```bash
docker compose exec ollama ollama pull qwen3:4b
```

## 14. Performance Tuning

> - **What:** Getting faster responses and more throughput.
> - **How:** Keep everything on the GPU, right-size context, keep models loaded, batch requests.
> - **When to use:** Slow responses or many users.

| Symptom | Try |
|---|---|
| Very slow (< 5 tok/s) | Model spills to CPU: smaller model / lower quant; check `ollama ps` (should say 100% GPU) |
| Slow first response | Model loading; use `keep_alive` so it stays in memory |
| Long prompts slow | Lower `num_ctx`; shorter prompts; fewer RAG chunks |
| Thinking model too slow | `think=False` or a non-thinking model |
| Many users | vLLM (continuous batching) or more `OLLAMA_NUM_PARALLEL` with enough VRAM |
| Answers cut off / forget earlier text | Context too small: raise `num_ctx` (costs memory) |

## 15. Local vs Hosted: Decision Guide

| Factor | Local / self-hosted | Hosted API |
|---|---|---|
| Best quality | Good; top hosted models usually stronger | Strongest models |
| Privacy | Full control | Provider terms, enterprise / regional options |
| Cost pattern | Hardware (fixed); cheap at high volume | Per token; cheap at low volume |
| Setup / ops | You run and scale it | None |
| Latency | Depends on your hardware | Generally fast, network overhead |
| Offline | Yes | No |

Common hybrid: local models for embeddings, classification or sensitive steps; hosted frontier models for hard reasoning.

## 16. Troubleshooting

| Problem | Fix |
|---|---|
| `Error: model requires more system memory` | Smaller model / lower quantization; close other apps |
| `ollama: command not found` | Restart terminal; check install; on Linux `systemctl status ollama` |
| Can't connect to `localhost:11434` | Server not running (`ollama serve`), or different `OLLAMA_HOST` |
| Remote clients can't connect | Server bound to 127.0.0.1; set `OLLAMA_HOST=0.0.0.0` ONLY behind a firewall / tunnel |
| GPU not used | Drivers / CUDA missing (`nvidia-smi`); Docker needs `--gpus all`; check `ollama ps` |
| Output ignores the system prompt / weird format | Use the instruct / chat variant; check the template (`ollama show --modelfile`) |
| Model forgets start of long conversation | Default context too small; raise `num_ctx` |
| JSON output invalid | Use `format` with a JSON schema; lower temperature |
| vLLM `CUDA out of memory` at start | Lower `--max-model-len`, `--gpu-memory-utilization`, use a quantized model |
| Disk full | Models are large; move `OLLAMA_MODELS` / `HF_HOME`; `ollama rm` unused models |
