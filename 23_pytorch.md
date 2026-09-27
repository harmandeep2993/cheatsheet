# 23 - PyTorch

<!-- nav:start -->
**Previous:** [22 - Scikit-learn](22_scikit-learn.md) | **Index:** [All guides](README.md) | **Next:** [24 - Hugging Face](24_hugging-face.md)
<!-- nav:end -->

Quick reference for PyTorch: tensors, GPUs, automatic gradients, building and training neural networks, and saving models.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is PyTorch?

PyTorch is the most widely used **deep learning** library. Deep learning uses **neural networks**: stacks of simple mathematical layers with millions or billions of adjustable numbers (**weights**). Training shows the network examples, measures how wrong it is (**loss**), and nudges every weight a little in the direction that reduces the error. PyTorch gives you **tensors** (NumPy-like arrays that can run on GPUs) and **autograd** (automatic calculation of those nudges). Almost every modern AI model, including LLMs on Hugging Face, is built with PyTorch.

### Mental model

Training is a loop of five steps, repeated over many batches of data:

```text
          +--------------------------------------------------------------+
          |                                                              |
   batch of data (X, y)                                                  |
          |                                                              |
          v                                                              |
 1. forward pass:      y_pred = model(X)          "make a guess"         |
 2. loss:              loss = loss_fn(y_pred, y)   "how wrong?"           |
 3. backward pass:     loss.backward()             "who is to blame?"     |
                        (autograd computes a gradient for every weight)  |
 4. optimizer step:    optimizer.step()            "nudge weights"        |
 5. reset gradients:   optimizer.zero_grad()       "clear for next batch" |
          |                                                              |
          +--------------------------- next batch -----------------------+
    one pass over the whole dataset = one EPOCH
```

A **gradient** says, for each weight, "if you increase this weight a tiny bit, the loss goes up / down this much". The optimizer moves weights opposite to the gradient (downhill). That is all "learning" is.

### Why learn it?

- **Understand how LLMs work** under the hood (they are PyTorch models).
- **Fine-tuning** and running Hugging Face models requires basic PyTorch.
- **GPUs**: moving work to a GPU can make training 10 to 100x faster.
- **Flexible**: plain Python code, easy to debug; industry and research standard.

### Key terms

| Term | Meaning |
|---|---|
| Tensor | N-dimensional array (like NumPy) that can live on CPU or GPU |
| Device | Where computation runs: `cpu`, `cuda` (NVIDIA GPU), `mps` (Apple GPU) |
| Model / module | A network: layers + a `forward` method (`nn.Module`) |
| Parameters / weights | The learnable numbers inside the model |
| Forward pass | Input through the model to get predictions |
| Loss | Number measuring how wrong the predictions are |
| Gradient | Direction and size to change each weight to reduce loss |
| Backpropagation | Computing gradients from the loss back through the layers (`loss.backward()`) |
| Optimizer | Algorithm that updates weights (SGD, Adam, AdamW) |
| Learning rate | Size of each update step |
| Batch / epoch | Group of samples per step / one full pass over the data |
| Overfitting | Great on training data, poor on new data |
| Inference | Using a trained model to predict (no training) |

**Where it fits:** builds on [16 - NumPy](16_numpy.md) and [22 - Scikit-learn](22_scikit-learn.md) ideas; used by [24 - Hugging Face](24_hugging-face.md), [36 - Fine-tuning](36_fine-tuning.md) and [35 - Local LLMs](35_local-llms.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| PyTorch documentation | https://docs.pytorch.org/docs/stable/index.html |
| PyTorch tutorials | https://docs.pytorch.org/tutorials/ |
| Install command generator | https://pytorch.org/get-started/locally/ |

---

## Contents

1. [Install and GPU Check](#1-install-and-gpu-check)
2. [Tensors](#2-tensors)
3. [Tensor Operations and Shapes](#3-tensor-operations-and-shapes)
4. [Devices (CPU / GPU)](#4-devices-cpu--gpu)
5. [Autograd (Automatic Gradients)](#5-autograd-automatic-gradients)
6. [Building a Model (nn.Module)](#6-building-a-model-nnmodule)
7. [Common Layers and Activations](#7-common-layers-and-activations)
8. [Loss Functions](#8-loss-functions)
9. [Optimizers](#9-optimizers)
10. [Dataset and DataLoader](#10-dataset-and-dataloader)
11. [The Training Loop](#11-the-training-loop)
12. [Evaluation and Inference](#12-evaluation-and-inference)
13. [Save and Load](#13-save-and-load)
14. [Full Example: Tabular Classifier](#14-full-example-tabular-classifier)
15. [Overfitting and Regularisation](#15-overfitting-and-regularisation)
16. [Speed and Memory Tips](#16-speed-and-memory-tips)
17. [PyTorch vs scikit-learn](#17-pytorch-vs-scikit-learn)
18. [Troubleshooting](#18-troubleshooting)
19. [Try It](#19-try-it)

---

## 1. Install and GPU Check

> Installing PyTorch with the right GPU support. Pick your OS / CUDA version on pytorch.org to get the exact install command; check the GPU from Python.
>
> Use it for setting up a machine for deep learning.

```powershell
pip install torch torchvision                  # CPU (or default CUDA build on Linux)
# GPU on Windows: copy the command from https://pytorch.org/get-started/locally/, e.g.
pip install torch --index-url https://download.pytorch.org/whl/cu124
```

```python
import torch

torch.__version__
torch.cuda.is_available()                      # True if an NVIDIA GPU is usable
torch.cuda.get_device_name(0)                  # e.g. "NVIDIA T4"
torch.backends.mps.is_available()              # Apple Silicon GPU
```

`nvidia-smi` in a terminal shows GPU memory and usage.

## 2. Tensors

> The core data structure: an array of numbers with a shape, type and device. Created from lists, NumPy arrays or generator functions; very similar to NumPy.
>
> Use it for all data and weights in PyTorch are tensors.

```python
x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
torch.zeros(2, 3) ; torch.ones(2, 3) ; torch.rand(2, 3) ; torch.randn(2, 3)   # normal distribution
torch.arange(0, 10, 2) ; torch.linspace(0, 1, 5)
torch.from_numpy(np_array)                    # shares memory with NumPy
x.numpy()                                     # back to NumPy (CPU tensors only)

x.shape       # torch.Size([2, 2])
x.dtype       # torch.float32 (default for floats; models usually use float32)
x.device      # cpu
x.float() ; x.long() ; x.to(torch.float16)
x.item()      # Python number from a 1-element tensor
```

## 3. Tensor Operations and Shapes

> Maths, indexing and reshaping. Same ideas as NumPy: element-wise ops, broadcasting, `@` for matrix multiply.
>
> Use it for preparing data, writing custom layers, debugging shape errors.

```python
a + b ; a * b ; a @ b ; a.T                    # element-wise, matrix multiply, transpose
x.sum() ; x.mean(dim=0) ; x.max(dim=1)         # dim = axis
x[0] ; x[:, 1] ; x[x > 2]                      # indexing and masks
x.view(4) ; x.reshape(-1, 1)                   # reshape (-1 = infer)
x.unsqueeze(0)                                 # add a dimension: (2, 2) -> (1, 2, 2) = batch of 1
x.squeeze()                                    # remove size-1 dimensions
torch.cat([a, b], dim=0) ; torch.stack([a, b])
torch.softmax(logits, dim=-1)                  # scores -> probabilities
torch.argmax(logits, dim=-1)                   # predicted class
```

Typical shapes: tabular `(batch, features)`, images `(batch, channels, height, width)`, text `(batch, sequence_length)` of token IDs, embeddings `(batch, seq_len, hidden_size)`.

## 4. Devices (CPU / GPU)

> Choosing where tensors and models live and compute. `.to(device)` moves a tensor or model; all tensors in one operation must be on the same device.
>
> Use it in every training / inference script; write it device-agnostic.

```python
device = (
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
model = model.to(device)
X, y = X.to(device), y.to(device)
preds.cpu().numpy()                    # back to CPU before NumPy / pandas
```

## 5. Autograd (Automatic Gradients)

> PyTorch's engine that computes gradients automatically. Tensors with `requires_grad=True` record operations; `backward()` walks back through them and fills `.grad`.
>
> Use it for behind every training step (you rarely call it directly except `loss.backward()`).

```python
w = torch.tensor(2.0, requires_grad=True)
x = torch.tensor(3.0)
loss = (w * x - 12) ** 2          # (6 - 12)^2 = 36
loss.backward()                   # compute d(loss)/dw
w.grad                            # tensor(-36.)  -> increasing w lowers the loss

with torch.no_grad():             # no gradient tracking (inference, faster, less memory)
    preds = model(X)

x.detach()                        # same data, cut from the gradient graph
```

## 6. Building a Model (nn.Module)

> Defining a neural network. Subclass `nn.Module`, create layers in `__init__`, describe the data flow in `forward`. Or chain layers with `nn.Sequential`.
>
> Use it in any custom model.

```python
from torch import nn


class MLP(nn.Module):
    """Simple feed-forward network for tabular data."""

    def __init__(self, n_features: int, n_classes: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 64),     # 64 hidden units
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, n_classes),      # outputs raw scores (logits)
        )

    def forward(self, x):
        return self.net(x)


model = MLP(n_features=10, n_classes=3)
print(model)
sum(p.numel() for p in model.parameters())   # number of weights
```

## 7. Common Layers and Activations

> The building blocks of networks. Layers transform tensors with learnable weights; activations add non-linearity so networks can learn complex patterns.
>
> Use it for picking layers for your data type.

| Layer | Use for |
|---|---|
| `nn.Linear(in, out)` | Fully connected layer (tabular, final layers) |
| `nn.Conv2d(in_ch, out_ch, kernel)` | Images (CNNs) |
| `nn.Embedding(vocab, dim)` | Turning token IDs into vectors |
| `nn.LSTM`, `nn.GRU` | Sequences (older approach) |
| `nn.TransformerEncoderLayer`, `nn.MultiheadAttention` | Attention, the basis of LLMs |
| `nn.Dropout(p)` | Randomly zero units during training (less overfitting) |
| `nn.BatchNorm1d`, `nn.LayerNorm` | Stabilise training |

| Activation | Notes |
|---|---|
| `nn.ReLU()` | Default choice for hidden layers |
| `nn.GELU()` | Used in transformers |
| `nn.Sigmoid()` | Output between 0 and 1 |
| `nn.Softmax(dim=-1)` | Probabilities over classes (usually only at inference) |

## 8. Loss Functions

> The number the training tries to minimise. Compares predictions with true targets; pick it by task type.
>
> Use it in every training setup.

| Task | Output layer | Loss | Target |
|---|---|---|---|
| Regression | `Linear(..., 1)` | `nn.MSELoss()` / `nn.L1Loss()` | float values |
| Binary classification | `Linear(..., 1)` (logit) | `nn.BCEWithLogitsLoss()` | 0.0 / 1.0 floats |
| Multi-class | `Linear(..., n_classes)` (logits) | `nn.CrossEntropyLoss()` | class index (int64) |

`CrossEntropyLoss` and `BCEWithLogitsLoss` expect **raw logits**; do not add softmax / sigmoid before them.

## 9. Optimizers

> The algorithm that updates weights using gradients. Created with the model's parameters and a learning rate; `step()` applies one update.
>
> Use this when every training loop; AdamW is a safe default.

```python
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)   # lower lr over time
scheduler.step()   # once per epoch
```

Learning rate is the most important setting: too high -> loss jumps / NaN; too low -> learns very slowly. Typical start: `1e-3` (Adam) for small nets, `1e-5` to `5e-5` for fine-tuning pretrained transformers.

## 10. Dataset and DataLoader

> Feeding data to the model in shuffled batches. A `Dataset` returns one sample by index; `DataLoader` groups samples into batches and shuffles.
>
> Use it in any dataset larger than a toy example.

```python
from torch.utils.data import DataLoader, Dataset, TensorDataset

ds = TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long))


class CsvDataset(Dataset):
    """Rows of a DataFrame as (features, label) tensors."""

    def __init__(self, df, feature_cols, label_col):
        self.X = torch.tensor(df[feature_cols].values, dtype=torch.float32)
        self.y = torch.tensor(df[label_col].values, dtype=torch.long)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        return self.X[i], self.y[i]


train_loader = DataLoader(ds, batch_size=64, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=256, shuffle=False)
```

## 11. The Training Loop

> The five-step loop from the mental model, in code. For each epoch and batch: forward, loss, backward, step, zero grads; then validate.
>
> Use it for training any model from scratch or fine-tuning.

```python
EPOCHS = 20
loss_fn = nn.CrossEntropyLoss()

for epoch in range(EPOCHS):
    model.train()                                  # enable dropout etc.
    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        logits = model(X_batch)                    # 1. forward
        loss = loss_fn(logits, y_batch)            # 2. loss
        optimizer.zero_grad()                      # 5. clear old gradients
        loss.backward()                            # 3. gradients
        optimizer.step()                           # 4. update weights

    val_loss, val_acc = evaluate(model, val_loader)
    print(f"epoch {epoch+1}: train_loss={loss.item():.3f} val_loss={val_loss:.3f} val_acc={val_acc:.3f}")
```

## 12. Evaluation and Inference

> Measuring performance and making predictions without training. `model.eval()` switches layers like dropout to inference mode; `torch.no_grad()` turns off gradient tracking.
>
> Use it for validation every epoch, testing, production predictions.

```python
def evaluate(model, loader):
    """Return average loss and accuracy on a loader."""
    model.eval()
    total_loss, correct, n = 0.0, 0, 0
    with torch.no_grad():
        for X_b, y_b in loader:
            X_b, y_b = X_b.to(device), y_b.to(device)
            logits = model(X_b)
            total_loss += loss_fn(logits, y_b).item() * len(y_b)
            correct += (logits.argmax(dim=1) == y_b).sum().item()
            n += len(y_b)
    return total_loss / n, correct / n


model.eval()
with torch.no_grad():
    probs = torch.softmax(model(new_X.to(device)), dim=-1)
```

## 13. Save and Load

> Storing trained weights and loading them later. Save the `state_dict` (dict of weight tensors); to load, create the same model class and load the dict into it.
>
> Use it after training; checkpoints during long training runs.

```python
torch.save(model.state_dict(), "model.pt")

model = MLP(n_features=10, n_classes=3)
model.load_state_dict(torch.load("model.pt", map_location=device, weights_only=True))
model.eval()

torch.save({"epoch": epoch, "model": model.state_dict(), "optim": optimizer.state_dict()}, "ckpt.pt")
```

Only load model files you trust; `weights_only=True` avoids running arbitrary code. Hugging Face models use the safer `.safetensors` format.

## 14. Full Example: Tabular Classifier

> A complete, runnable training script. Scale data with scikit-learn, train an MLP, evaluate on held-out data.
>
> Use it as a template for a first PyTorch project.

```python
import torch
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

SEED = 42
EPOCHS = 50
torch.manual_seed(SEED)

X, y = load_iris(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
scaler = StandardScaler().fit(X_tr)
X_tr, X_te = scaler.transform(X_tr), scaler.transform(X_te)

to_t = lambda a, dt: torch.tensor(a, dtype=dt)
train_loader = DataLoader(TensorDataset(to_t(X_tr, torch.float32), to_t(y_tr, torch.long)), batch_size=16, shuffle=True)

model = nn.Sequential(nn.Linear(4, 32), nn.ReLU(), nn.Linear(32, 3))
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-2)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(EPOCHS):
    model.train()
    for xb, yb in train_loader:
        loss = loss_fn(model(xb), yb)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

model.eval()
with torch.no_grad():
    acc = (model(to_t(X_te, torch.float32)).argmax(1) == to_t(y_te, torch.long)).float().mean()
print(f"test accuracy: {acc:.3f}")
```

## 15. Overfitting and Regularisation

> Stopping the model from memorising the training data. Watch validation loss; when it rises while training loss falls, you are overfitting.
>
> Use it in every training run.

| Technique | How |
|---|---|
| Early stopping | Stop when validation loss has not improved for N epochs; keep the best checkpoint |
| Dropout | `nn.Dropout(0.1 to 0.5)` between layers |
| Weight decay | `AdamW(..., weight_decay=0.01)` |
| More / augmented data | Flip / crop images, paraphrase text |
| Smaller model | Fewer layers / units |

## 16. Speed and Memory Tips

> Making training faster and fit on your GPU. Mixed precision, right batch size, efficient data loading.
>
> Use it for slow training or "CUDA out of memory".

```python
with torch.autocast(device_type="cuda", dtype=torch.bfloat16):   # mixed precision: faster, less memory
    logits = model(X)
    loss = loss_fn(logits, y)

model = torch.compile(model)            # optional graph compilation for speed (PyTorch 2)
torch.cuda.empty_cache()                # release cached memory
DataLoader(ds, batch_size=64, num_workers=4, pin_memory=True)   # faster loading (Linux)
```

Out of memory: lower `batch_size`, use mixed precision, gradient accumulation (several small batches before one `optimizer.step()`), or a smaller model.

## 17. PyTorch vs scikit-learn

> When deep learning is worth it. Compare data type and size.
>
> Use it for choosing the tool for a new ML task.

| Situation | Choose |
|---|---|
| Tabular data (rows and columns), small / medium | scikit-learn / gradient boosting ([22](22_scikit-learn.md)) |
| Images, audio, text, video | PyTorch (usually a pretrained model from [24 - Hugging Face](24_hugging-face.md)) |
| Need an LLM | Use an API ([26](26_llm-apis.md)) or pretrained open model; fine-tune only if needed ([36](36_fine-tuning.md)) |
| Custom architecture / research | PyTorch |

## 18. Troubleshooting

| Error | Fix |
|---|---|
| `Expected all tensors to be on the same device` | Move model AND data with `.to(device)` |
| `mat1 and mat2 shapes cannot be multiplied (64x10 and 12x64)` | Input features do not match the first `Linear`; print `X.shape` |
| `expected scalar type Long but found Float` | CrossEntropy targets must be `torch.long` class indices |
| `Found dtype Double but expected Float` | Convert with `.float()` / `dtype=torch.float32` (NumPy defaults to float64) |
| `CUDA out of memory` | Smaller batch, mixed precision, `torch.no_grad()` for inference, free unused tensors |
| `torch.cuda.is_available()` is False | CPU-only build installed; reinstall with the CUDA command from pytorch.org; check `nvidia-smi` |
| Loss is `nan` | Learning rate too high, bad inputs (NaN / inf), missing scaling |
| Loss does not go down | Forgot `optimizer.zero_grad()` / `step()`, lr too low, labels wrong, data not shuffled |
| Validation worse than expected | Forgot `model.eval()`; data leakage in the other direction; overfitting |
| `Can't call numpy() on Tensor that requires grad` | `.detach().cpu().numpy()` |

## 19. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Device-agnostic tensor

Create a random 3x3 tensor on the best available device and compute its mean.

<details markdown="1">
<summary>Solution</summary>

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
x = torch.rand(3, 3, device=device)
x.mean().item()
```

</details>

### Exercise 2: Find the bug

This loop never learns. Why?
`for X, y in loader: loss = loss_fn(model(X), y); loss.backward(); optimizer.step()`

<details markdown="1">
<summary>Solution</summary>

Gradients accumulate across batches because `optimizer.zero_grad()` is never called. Correct order:

```python
for X, y in loader:
    loss = loss_fn(model(X), y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

</details>

### Exercise 3: Eval mode

Why call both `model.eval()` and `torch.no_grad()` before predicting?

<details markdown="1">
<summary>Solution</summary>

`model.eval()` switches layers like dropout and batch norm to inference behaviour (otherwise predictions are random / wrong). `torch.no_grad()` stops gradient tracking, saving memory and time. They do different jobs, so use both.

</details>

---

<!-- nav:start -->
**Previous:** [22 - Scikit-learn](22_scikit-learn.md) | **Index:** [All guides](README.md) | **Next:** [24 - Hugging Face](24_hugging-face.md)
<!-- nav:end -->
