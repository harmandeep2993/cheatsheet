# 36 - Fine-tuning

<!-- nav:start -->
**Previous:** [35 - Local and Self-Hosted LLMs](35_local-llms.md) | **Index:** [All guides](README.md) | **Next:** [37 - AI Security and Responsible AI](37_ai-security.md)
<!-- nav:end -->

Quick reference for fine-tuning language models: when it is worth it, types of fine-tuning, LoRA / QLoRA, preparing data, training with Hugging Face TRL, hosted fine-tuning, evaluation, and exporting the result.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is fine-tuning?

**Fine-tuning** means continuing to train an already-trained model on **your own examples**, so its weights change and it gets better at a specific task, format or style. A pretrained model is like a university graduate with broad knowledge; fine-tuning is **on-the-job training** for one role. Because you start from a strong model, you need far less data and compute than training from scratch: often a few hundred to a few thousand good examples.

### Mental model: what fine-tuning changes (and what it doesn't)

```text
                   PROMPTING / RAG                          FINE-TUNING
changes        what the model SEES (context)         how the model BEHAVES (weights)
good for       facts, fresh / private knowledge,     consistent format / style / tone,
               instructions that may change          narrow skills, shorter prompts,
                                                     smaller cheaper model for one task
update cost    edit a prompt / re-index docs         retrain (hours, GPU, data work)
risk           low                                   overfitting, forgetting, bad data baked in

   Most apps:  prompt engineering -> RAG -> tools -> (only then) fine-tuning
```

LoRA (the most common method) keeps the original weights **frozen** and trains small add-on matrices (**adapters**), so fine-tuning fits on a single GPU:

```text
original weight matrix W (frozen, e.g. 4096 x 4096 = 16.7M numbers)
       +
low-rank update  B x A  (trainable, rank r = 16:  4096x16 + 16x4096 = 131K numbers, <1%)
       =
effective weight W + B x A          -> adapter file of a few MB to a few hundred MB
```

### Why (and when) fine-tune?

| Good reasons | Bad reasons (use something else) |
|---|---|
| Strict output format / style every time | "Teach it our documents" -> RAG ([30](30_rag.md)) |
| Narrow, high-volume task where a small fine-tuned model can replace a big one (cost, latency) | Facts that change often -> RAG / tools |
| Domain language / jargon the base model handles poorly | "The prompt is not working yet" -> iterate the prompt first ([27](27_prompt-engineering.md)) |
| Shorten long prompts full of examples | You have < 50 examples -> few-shot prompting |
| Run on-prem with a small open model | You cannot evaluate quality -> build evals first ([34](34_evals-observability.md)) |

### Key terms

| Term | Meaning |
|---|---|
| Base model | Model before your fine-tuning (use an instruct model for chat tasks) |
| SFT | Supervised fine-tuning on (input, ideal output) examples |
| Instruction tuning | SFT with instruction-following examples |
| Preference tuning (DPO, ORPO, RLHF) | Training on "better vs worse" answer pairs |
| Continued pretraining | More next-token training on raw domain text |
| Distillation | Training a small model on outputs of a big model |
| Full fine-tuning | Update all weights (needs lots of GPU memory) |
| PEFT | Parameter-efficient fine-tuning (train a small number of extra weights) |
| LoRA / QLoRA | Low-rank adapters / LoRA on a 4-bit quantized base model |
| Adapter | The small trained LoRA weights |
| Epoch | One pass over the training data |
| Overfitting | Memorises training examples, worse on new inputs |
| Catastrophic forgetting | Loses general abilities after narrow training |

**Where it fits:** needs [23 - PyTorch](23_pytorch.md) and [24 - Hugging Face](24_hugging-face.md); decision context in [25 - LLM Fundamentals](25_llm-fundamentals.md) section 16; run the result with [35 - Local LLMs](35_local-llms.md); measure with [34 - Evals](34_evals-observability.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Hugging Face TRL | https://huggingface.co/docs/trl |
| Hugging Face PEFT (LoRA) | https://huggingface.co/docs/peft |
| Unsloth | https://docs.unsloth.ai/ |
| Axolotl | https://docs.axolotl.ai/ |
| LoRA paper | https://arxiv.org/abs/2106.09685 |
| OpenAI fine-tuning guide | https://platform.openai.com/docs/guides/fine-tuning |

---

## Contents

1. [Decision Checklist](#1-decision-checklist)
2. [Types of Fine-tuning](#2-types-of-fine-tuning)
3. [Full Fine-tuning vs LoRA vs QLoRA](#3-full-fine-tuning-vs-lora-vs-qlora)
4. [Preparing the Dataset](#4-preparing-the-dataset)
5. [Data Quality Rules](#5-data-quality-rules)
6. [Train / Validation / Test Split](#6-train--validation--test-split)
7. [Hardware and Cost](#7-hardware-and-cost)
8. [SFT with LoRA using TRL](#8-sft-with-lora-using-trl)
9. [Key Hyperparameters](#9-key-hyperparameters)
10. [Monitoring Training](#10-monitoring-training)
11. [Evaluating the Fine-tuned Model](#11-evaluating-the-fine-tuned-model)
12. [Using, Merging and Sharing the Adapter](#12-using-merging-and-sharing-the-adapter)
13. [Export to GGUF for Ollama](#13-export-to-gguf-for-ollama)
14. [Preference Tuning (DPO)](#14-preference-tuning-dpo)
15. [Hosted Fine-tuning Services](#15-hosted-fine-tuning-services)
16. [Tools: Unsloth, Axolotl, LLaMA-Factory](#16-tools-unsloth-axolotl-llama-factory)
17. [Fine-tuning Classic Models (BERT-style)](#17-fine-tuning-classic-models-bert-style)
18. [Troubleshooting](#18-troubleshooting)
19. [Try It](#19-try-it)

---

## 1. Decision Checklist

> Questions to answer before fine-tuning. If any answer is "no", fix that first. Use it before spending time on data and GPUs.

- [ ] Prompt engineering with a strong model has been tried and measured
- [ ] The knowledge is stable (not changing weekly) or is style / format, not facts
- [ ] An eval set with a clear quality metric exists
- [ ] You have (or can create) 200 to 5,000+ high-quality examples
- [ ] You know where the model will run (API host, GPU server, Ollama)
- [ ] The expected gain (quality, cost, latency, privacy) justifies the effort

## 2. Types of Fine-tuning

> Different training objectives. Each uses a different kind of data. Use it for match the method to the problem.

| Method | Data | Teaches |
|---|---|---|
| SFT (supervised) | Prompt -> ideal response (chat messages) | Format, style, task skills (start here) |
| Preference (DPO / ORPO / KTO) | Prompt + chosen + rejected response | Prefer better answers, tone, safety |
| RL with verifiable rewards | Prompts + automatic checker | Reasoning, maths, code (advanced) |
| Continued pretraining | Raw domain text | Domain vocabulary / knowledge (large data) |
| Distillation | Big-model outputs as SFT data | Small model mimics big model on a task |

## 3. Full Fine-tuning vs LoRA vs QLoRA

> How much of the model you train. Full updates all weights; LoRA trains small adapters; QLoRA does LoRA on a 4-bit base to save more memory. Use it for loRA / QLoRA for almost all practical projects.

| | Full | LoRA | QLoRA |
|---|---|---|---|
| Trainable params | 100% | ~0.1 to 2% | ~0.1 to 2% |
| GPU memory (7B model) | ~100+ GB | ~16 to 24 GB | ~8 to 12 GB |
| Output | Full model copy | Small adapter (MBs) | Small adapter |
| Quality | Highest ceiling | Close to full for most tasks | Slightly lower, usually fine |

## 4. Preparing the Dataset

> Training examples in the chat format the model expects. JSONL, one conversation per line with `messages` (system / user / assistant); the model learns to produce the assistant turns. Use it for SFT with modern chat models.

```text
{"messages": [{"role": "system", "content": "You convert support emails to JSON tickets."}, {"role": "user", "content": "Hi, charged twice for order A-1042!"}, {"role": "assistant", "content": "{\"category\": \"billing\", \"order_id\": \"A-1042\", \"urgency\": 4}"}]}
{"messages": [{"role": "system", "content": "You convert support emails to JSON tickets."}, {"role": "user", "content": "App crashes on photo upload"}, {"role": "assistant", "content": "{\"category\": \"technical\", \"order_id\": null, \"urgency\": 3}"}]}
```

```python
import json

SYSTEM = "You convert support emails to JSON tickets."

with open("train.jsonl", "w", encoding="utf-8") as f:
    for row in labelled_rows:                            # e.g. from a DataFrame / DB
        example = {"messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": row["email"]},
            {"role": "assistant", "content": json.dumps(row["ticket"])},
        ]}
        f.write(json.dumps(example, ensure_ascii=False) + "\n")
```

Ways to get data: historical human-written outputs, expert labelling, outputs of a strong model reviewed by humans (distillation; check provider terms), synthetic variations of real cases.

## 5. Data Quality Rules

> What makes a good fine-tuning dataset. Quality beats quantity; the model copies everything, including mistakes. Use it for building and reviewing the dataset.

- **Correct**: every assistant answer is exactly what you want the model to produce.
- **Consistent**: same format, style and rules across examples.
- **Diverse**: cover the real variety of inputs, including hard and edge cases.
- **Representative**: match production inputs (length, language, noise).
- **Deduplicated** and free of personal data / secrets unless required and permitted.
- Use the **same system prompt** at training and inference.
- Start with ~200 to 500 excellent examples, measure, then add more where the model fails.

## 6. Train / Validation / Test Split

> Separating data for training, tuning and final evaluation. Typical 80 / 10 / 10; the test set is never used during training decisions. Use it in every fine-tuning run.

```python
from datasets import load_dataset

ds = load_dataset("json", data_files="all.jsonl", split="train").shuffle(seed=42)
splits = ds.train_test_split(test_size=0.2, seed=42)
val_test = splits["test"].train_test_split(test_size=0.5, seed=42)
train, val, test = splits["train"], val_test["train"], val_test["test"]
```

## 7. Hardware and Cost

> Where to run training. Match model size and method to GPU memory; rent GPUs by the hour. Use it for planning a run.

| Model size | Method | Typical GPU |
|---|---|---|
| 0.5B to 3B | LoRA | Free Colab / Kaggle T4 (16 GB), consumer GPUs |
| 7B to 8B | QLoRA | 16 to 24 GB (T4, L4, RTX 4090) |
| 7B to 8B | LoRA (bf16) | 24 to 48 GB (L4, A10, A6000) |
| 70B | QLoRA | 48 to 80 GB (A100 / H100) |

Options: Google Colab / Kaggle, cloud GPU VMs ([47 - Azure](47_azure.md), [48](48_azure-vm-ollama.md)), GPU rental platforms, managed services (section 15). Always stop / delete GPU machines after training.

## 8. SFT with LoRA using TRL

> A complete LoRA fine-tuning script with Hugging Face TRL and PEFT. Load the chat-format dataset, configure LoRA, train with `SFTTrainer`, save the adapter. Use this when your first fine-tuning run on an open model.

```powershell
pip install torch transformers datasets peft trl accelerate
pip install bitsandbytes                   # only for QLoRA (NVIDIA GPU)
```

```python
from datasets import load_dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer

BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"     # start small to test the pipeline

train = load_dataset("json", data_files="train.jsonl", split="train")
val = load_dataset("json", data_files="val.jsonl", split="train")

peft_config = LoraConfig(
    r=16,                          # adapter rank: capacity of the update
    lora_alpha=32,                 # scaling (often 2 x r)
    lora_dropout=0.05,
    target_modules="all-linear",   # apply LoRA to all linear layers
    task_type="CAUSAL_LM",
)

args = SFTConfig(
    output_dir="out/ticket-lora",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,       # effective batch size 16
    learning_rate=2e-4,                  # typical for LoRA
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="epoch",
    bf16=True,                           # if the GPU supports it; else fp16=True
)

trainer = SFTTrainer(
    model=BASE_MODEL,
    train_dataset=train,
    eval_dataset=val,
    args=args,
    peft_config=peft_config,
)
trainer.train()
trainer.save_model("out/ticket-lora/final")     # saves the adapter
```

The trainer applies the model's chat template to `messages` automatically and (by default) learns from the assistant parts.

## 9. Key Hyperparameters

> Settings that most affect results. Start with common defaults; change one at a time based on validation results. Use it for tuning a run that under- or over-fits.

| Setting | Typical start | If ... |
|---|---|---|
| `learning_rate` (LoRA) | 1e-4 to 2e-4 | Loss unstable -> lower; learns too slowly -> higher |
| `num_train_epochs` | 1 to 3 | Val loss rises -> fewer epochs (overfitting) |
| `r` (LoRA rank) | 8 to 32 | Underfits on complex task -> higher |
| `lora_alpha` | 2 x r | Keep ratio when changing r |
| Effective batch size | 16 to 64 | Memory errors -> smaller batch + more accumulation |
| `max_length` / sequence length | Cover your longest examples | Truncated examples -> raise (costs memory) |

## 10. Monitoring Training

> Watching loss curves during training. Training loss should go down; validation loss should go down then flatten; if validation rises while training falls, stop (overfitting). Use it in every run.

```text
loss
 |\
 | \___ train
 |  \____________
 |   \__ val ____/   <- val starts rising: stop / keep the checkpoint at the minimum
 +---------------------> steps
```

Log to TensorBoard or Weights & Biases (`report_to="tensorboard"` / `"wandb"` in `SFTConfig`).

## 11. Evaluating the Fine-tuned Model

> Proving the fine-tune is better than the baseline. Run base model (with your best prompt) and fine-tuned model on the held-out test set with the same graders. Use it before deploying.

- Compare against: base model + good prompt, and a strong hosted model.
- Check task metrics (accuracy, valid JSON rate, rubric scores) with [34 - Evals](34_evals-observability.md).
- Check general abilities did not collapse (a few off-task questions).
- Read outputs yourself: numbers can hide format glitches.

## 12. Using, Merging and Sharing the Adapter

> Loading the adapter for inference, or merging it into the base model. PEFT loads base + adapter; `merge_and_unload()` produces a standalone model. Use it for serving the fine-tuned model.

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

model = AutoPeftModelForCausalLM.from_pretrained("out/ticket-lora/final", device_map="auto")
tok = AutoTokenizer.from_pretrained(BASE_MODEL)

merged = model.merge_and_unload()               # base + adapter -> one model
merged.save_pretrained("out/ticket-merged")
tok.save_pretrained("out/ticket-merged")
merged.push_to_hub("your-username/ticket-model")   # optional, after hf auth login
```

vLLM can also serve base model + LoRA adapters directly (`--enable-lora`).

## 13. Export to GGUF for Ollama

> Converting the merged model to GGUF so Ollama / llama.cpp can run it. Use llama.cpp's conversion script, quantize, then create an Ollama model from it. Use it for running your fine-tune locally on laptops / CPU.

```bash
git clone https://github.com/ggml-org/llama.cpp
pip install -r llama.cpp/requirements.txt
python llama.cpp/convert_hf_to_gguf.py out/ticket-merged --outfile ticket-f16.gguf --outtype f16
llama-quantize ticket-f16.gguf ticket-Q4_K_M.gguf Q4_K_M
```

```text
# Modelfile
FROM ./ticket-Q4_K_M.gguf
SYSTEM """You convert support emails to JSON tickets."""
```

```bash
ollama create ticket-model -f Modelfile
ollama run ticket-model
```

Unsloth (section 16) can export to GGUF in one call.

## 14. Preference Tuning (DPO)

> Teaching the model which of two answers is better. Dataset rows with `prompt`, `chosen`, `rejected`; `DPOTrainer` pushes probability toward chosen answers. Use it after SFT, to refine tone, helpfulness, refusals or style where "better" is easier to judge than to write.

```text
{"prompt": [{"role": "user", "content": "Explain LoRA briefly."}],
 "chosen": [{"role": "assistant", "content": "LoRA trains small low-rank adapters ..."}],
 "rejected": [{"role": "assistant", "content": "LoRA is a radio technology ..."}]}
```

```python
from trl import DPOConfig, DPOTrainer

trainer = DPOTrainer(model="out/ticket-merged", train_dataset=pref_ds,
                     args=DPOConfig(output_dir="out/dpo", beta=0.1, learning_rate=5e-6),
                     peft_config=peft_config)
trainer.train()
```

## 15. Hosted Fine-tuning Services

> Fine-tuning without managing GPUs. Upload JSONL data, start a job, get a model ID you call via the provider's API. Use this when you want to fine-tune a provider's model or avoid infrastructure.

| Service | Notes |
|---|---|
| OpenAI / Azure OpenAI fine-tuning | Upload chat JSONL, fine-tune supported GPT models, call the new model ID |
| Google Vertex AI, Amazon Bedrock | Fine-tuning of selected hosted models |
| Hugging Face AutoTrain, Together, Fireworks, others | Fine-tune open models on managed GPUs |

Supported models, formats and prices change often; check each provider's current docs. Not every hosted model can be fine-tuned.

## 16. Tools: Unsloth, Axolotl, LLaMA-Factory

> Tools that make open-model fine-tuning faster or config-driven. Unsloth patches models for faster, lower-memory training with notebooks; Axolotl and LLaMA-Factory run training from YAML configs / a web UI. Use it for limited GPU memory (Unsloth), repeatable config-driven runs (Axolotl / LLaMA-Factory).

## 17. Fine-tuning Classic Models (BERT-style)

> Fine-tuning small encoder models for classification, NER or embeddings. `AutoModelForSequenceClassification` + `Trainer`; trains in minutes on a small GPU. Use it for high-volume classification where a tiny specialised model beats LLM calls on cost and latency.

```python
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, Trainer,
                          TrainingArguments)

MODEL = "distilbert-base-uncased"
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=3)

ds = load_dataset("csv", data_files={"train": "train.csv", "test": "test.csv"})   # columns: text, label
ds = ds.map(lambda b: tok(b["text"], truncation=True, padding="max_length", max_length=128), batched=True)

trainer = Trainer(
    model=model,
    args=TrainingArguments(output_dir="out/clf", num_train_epochs=3, learning_rate=2e-5,
                           per_device_train_batch_size=16, eval_strategy="epoch"),
    train_dataset=ds["train"],
    eval_dataset=ds["test"],
)
trainer.train()
```

## 18. Troubleshooting

| Problem | Fix |
|---|---|
| `CUDA out of memory` | QLoRA, smaller batch + gradient accumulation, shorter `max_length`, smaller base model, gradient checkpointing |
| Loss is NaN | Lower learning rate; use bf16 instead of fp16; check data for empty examples |
| Val loss goes up after epoch 1 | Overfitting: fewer epochs, more / more diverse data, lower lr |
| Model ignores the fine-tuned format | Different system prompt / chat template at inference than at training |
| Great on train examples, bad on new inputs | Data not representative; duplicates between train and test; overfitting |
| Lost general abilities | Too narrow data / too many epochs; mix in general examples; lower lr / rank |
| Fine-tune worse than prompting | Data quality issues; compare fairly with the same eval; maybe fine-tuning is not the right tool |
| GGUF conversion fails | Merge the adapter first; update llama.cpp; check the architecture is supported |

## 19. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution. Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Should you fine-tune?

(a) the bot must know our 300-page handbook, (b) 2 million support emails per month must be tagged cheaply in a fixed format, (c) outputs must follow a JSON schema.

<details markdown="1">
<summary>Solution</summary>

(a) No: use RAG. (b) Possibly: first try a small model with a good prompt; fine-tune a small model if cost / latency require it. (c) No: use structured outputs.

</details>

### Exercise 2: Build training data

Convert a CSV with columns `email,label` into chat-format JSONL.

<details markdown="1">
<summary>Solution</summary>

```python
import csv, json

with open("labels.csv", newline="", encoding="utf-8") as src, open("train.jsonl", "w", encoding="utf-8") as out:
    for row in csv.DictReader(src):
        out.write(json.dumps({"messages": [
            {"role": "system", "content": "Label the support email."},
            {"role": "user", "content": row["email"]},
            {"role": "assistant", "content": row["label"]},
        ]}) + "\n")
```

</details>

### Exercise 3: Read the curves

Train loss: 1.2 -> 0.6 -> 0.2. Validation loss: 1.1 -> 0.8 -> 1.0. What happened and what do you do?

<details markdown="1">
<summary>Solution</summary>

Overfitting after epoch 2: the model memorises the training data. Keep the epoch-2 checkpoint, train fewer epochs, lower the learning rate, or add more varied data.

</details>

---

<!-- nav:start -->
**Previous:** [35 - Local and Self-Hosted LLMs](35_local-llms.md) | **Index:** [All guides](README.md) | **Next:** [37 - AI Security and Responsible AI](37_ai-security.md)
<!-- nav:end -->
