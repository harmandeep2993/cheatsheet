# 39 - AI User Interfaces (Streamlit, Gradio, Chainlit)

<!-- nav:start -->
**Previous:** [38 - AI Security and Responsible AI](38_ai-security.md) | **Index:** [All guides](../README.md) | **Next:** [40 - FastAPI](40_fastapi.md)
<!-- nav:end -->

Quick reference for building chat apps and AI demos in pure Python: Streamlit, Gradio and Chainlit, plus streaming, file upload, state, secrets and deployment.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What are these tools?

They let you build a **web interface for your AI app with only Python** (no HTML / JavaScript needed):

- **Streamlit**: turns a Python script into a web app; great for dashboards, data apps and chat UIs.
- **Gradio**: builds interfaces around a function (input -> output); famous for ML demos and Hugging Face Spaces.
- **Chainlit**: built specifically for chat / agent apps, with streaming, steps, file uploads and feedback built in.

For production products with custom design, teams usually build a separate frontend (React / Next.js) that calls a **FastAPI** backend ([40](40_fastapi.md)); these Python tools are ideal for prototypes, internal tools and demos.

### Mental model

```text
Streamlit: the WHOLE SCRIPT re-runs top to bottom on every interaction.
           State that must survive re-runs goes in st.session_state.

   user types -> script runs again -> reads st.session_state.messages -> draws all messages
                                   -> calls the LLM for the new one -> appends -> draws it

Gradio:    you give it a FUNCTION; it builds inputs / outputs around it.
   ChatInterface(fn): fn(message, history) -> reply (or yields chunks to stream)

Chainlit:  EVENT HANDLERS for a chat app.
   @cl.on_chat_start  -> set up the session
   @cl.on_message     -> receive a message, stream back a reply
```

### Why use them?

- **Ship a demo in minutes**: show your RAG / agent to colleagues or users.
- **Internal tools** without a frontend team.
- **Free hosting options** (Streamlit Community Cloud, Hugging Face Spaces).
- **Iterate fast** on prompts with a real UI.

### Key terms

| Term | Meaning |
|---|---|
| Rerun (Streamlit) | Script executes again after each user interaction |
| Session state | Per-user memory that survives reruns |
| Widget | UI element (button, text input, file uploader) |
| Streaming | Showing tokens as they arrive |
| Caching | Keep expensive objects (models, clients, indexes) between reruns |
| Secrets | API keys provided to the app securely, not in code |

**Where it fits:** fronts apps built with [27 - LLM APIs](27_llm-apis.md), [31 - RAG](31_rag.md), [32 - AI Agents](32_ai-agents.md); streaming concepts in [09 - HTTP](09_http-apis.md) and [14 - Async](14_async-python.md); deploy with [43 - Docker](43_docker.md), [48 - Azure](48_azure.md) or Hugging Face Spaces ([25](25_hugging-face.md)).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Streamlit | https://docs.streamlit.io/ |
| Gradio | https://www.gradio.app/docs |
| Chainlit | https://docs.chainlit.io/ |
| Hugging Face Spaces | https://huggingface.co/docs/hub/spaces |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Which Tool When](#1-which-tool-when)
2. [Streamlit: Basics](#2-streamlit-basics)
3. [Streamlit: Chat App with Streaming](#3-streamlit-chat-app-with-streaming)
4. [Streamlit: Session State and Caching](#4-streamlit-session-state-and-caching)
5. [Streamlit: Sidebar, Files and Layout](#5-streamlit-sidebar-files-and-layout)
6. [Streamlit: Secrets](#6-streamlit-secrets)
7. [Gradio: Basics](#7-gradio-basics)
8. [Gradio: ChatInterface with Streaming](#8-gradio-chatinterface-with-streaming)
9. [Chainlit: Chat and Agent UI](#9-chainlit-chat-and-agent-ui)
10. [FastAPI Backend + Simple Web Frontend](#10-fastapi-backend--simple-web-frontend)
11. [Showing Sources, Steps and Feedback](#11-showing-sources-steps-and-feedback)
12. [Authentication](#12-authentication)
13. [Deployment](#13-deployment)
14. [Troubleshooting](#14-troubleshooting)
15. [Try It](#15-try-it)

---

## 0. Flags and Parameters

> Commands to start each tool's development server. Each has a `run` command with options for port and auto-reload.
>
> Use it for running apps locally and in containers.

```text
streamlit  run  app.py  --server.port 8501  --server.address 0.0.0.0
|          |    |       |                   |
|          |    |       |                   +-- listen on all interfaces (containers / VMs)
|          |    |       +---------------------- port (default 8501)
|          |    +------------------------------ your script
|          +----------------------------------- start the app
+---------------------------------------------- CLI
```

| Command | Meaning |
|---|---|
| `streamlit run app.py` | Start Streamlit (auto-reloads on save) |
| `--server.headless true` | Do not open a browser (servers) |
| `python app.py` (Gradio) | `demo.launch()` starts on port 7860 |
| `demo.launch(server_name="0.0.0.0", server_port=7860, share=True)` | Bind all interfaces / port / temporary public link |
| `chainlit run app.py -w` | Start Chainlit with watch (auto-reload), port 8000 |
| `chainlit run app.py --port 8080 --host 0.0.0.0` | Custom port / host |

---

## 1. Which Tool When

| Need | Choose |
|---|---|
| Data app / dashboard with charts + a chat box | Streamlit |
| Quick ML demo, image / audio inputs, HF Spaces | Gradio |
| Chat / agent app with steps, streaming, file upload, feedback | Chainlit |
| Production product with custom UX, many users | FastAPI backend + React / Next.js frontend |

## 2. Streamlit: Basics

> Building a web page from a Python script. Each `st.` call adds an element; widgets return their current value; the script re-runs on each interaction.
>
> Use it for data apps and simple AI tools.

```powershell
pip install streamlit
streamlit run app.py
```

```python
import pandas as pd
import streamlit as st

st.title("Sales Explorer")
region = st.selectbox("Region", ["North", "South", "West"])
min_amount = st.slider("Minimum amount", 0, 1000, 100)

df = pd.read_csv("sales.csv")
filtered = df[(df["region"] == region) & (df["amount"] >= min_amount)]
st.metric("Total", f"{filtered['amount'].sum():,.0f} EUR")
st.dataframe(filtered)
st.bar_chart(filtered, x="month", y="amount")

if st.button("Explain with AI"):
    st.write(explain(filtered))            # your LLM function
```

## 3. Streamlit: Chat App with Streaming

> A ChatGPT-style interface for Claude. Store messages in `st.session_state`; redraw them each run; stream the new reply with `st.write_stream`.
>
> Use it for chatbots, RAG assistants, prompt testing.

```python
import anthropic
import streamlit as st

MODEL = "claude-opus-5"
st.title("Acme Assistant")


@st.cache_resource                              # create the client once, reuse across reruns
def get_client():
    return anthropic.Anthropic()


client = get_client()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:           # redraw history
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


def stream_reply(messages):
    with client.messages.stream(
        model=MODEL,
        max_tokens=16000,
        system="You are a helpful assistant for Acme employees. Be concise.",
        messages=messages,
    ) as stream:
        yield from stream.text_stream


if prompt := st.chat_input("Ask something"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        reply = st.write_stream(stream_reply(st.session_state.messages))
    st.session_state.messages.append({"role": "assistant", "content": reply})
```

## 4. Streamlit: Session State and Caching

> Keeping data between reruns and avoiding repeated expensive work. `st.session_state` = per-user variables; `@st.cache_resource` = shared objects (clients, models, DB connections); `@st.cache_data` = cached function results (DataFrames).
>
> Use it for chat history, loaded models, vector indexes, slow queries.

```python
if "count" not in st.session_state:
    st.session_state.count = 0
st.session_state.count += 1


@st.cache_resource
def load_index():
    return build_vector_index("docs/")          # built once for all users


@st.cache_data(ttl=600)                         # re-run at most every 10 minutes
def load_sales() -> pd.DataFrame:
    return pd.read_parquet("sales.parquet")
```

## 5. Streamlit: Sidebar, Files and Layout

> Common layout and input elements. `st.sidebar`, columns, tabs, expanders, file uploader.
>
> Use it for settings panels, document upload for RAG, multi-view apps.

```python
with st.sidebar:
    temperature_note = st.radio("Style", ["Precise", "Creative"])
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if st.button("Clear chat"):
        st.session_state.messages = []

if uploaded:
    text = extract_pdf_text(uploaded.read())     # bytes -> your loader
    st.success(f"Loaded {uploaded.name}")

col1, col2 = st.columns(2)
col1.metric("Docs", 42)
tab_chat, tab_sources = st.tabs(["Chat", "Sources"])
with st.expander("Show retrieved chunks"):
    st.write(chunks)
with st.spinner("Thinking..."):
    answer = slow_call()
```

## 6. Streamlit: Secrets

> Giving the app API keys without putting them in code. `.streamlit/secrets.toml` locally (git-ignored) or the hosting platform's secrets UI; read with `st.secrets`. Environment variables also work.
>
> Use it in every deployed Streamlit app.

```toml
# .streamlit/secrets.toml  (add to .gitignore!)
ANTHROPIC_API_KEY = "sk-ant-..."
```

```python
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
```

## 7. Gradio: Basics

> Wrapping a Python function in a web UI. `gr.Interface(fn, inputs, outputs)`; `launch()` starts the server.
>
> Use it for ML model demos (text, image, audio), quick tools.

```powershell
pip install gradio
```

```python
import gradio as gr


def classify(text: str) -> dict:
    """Return label probabilities for a review."""
    return {"positive": 0.8, "negative": 0.2}          # your model here


demo = gr.Interface(
    fn=classify,
    inputs=gr.Textbox(label="Review", lines=4),
    outputs=gr.Label(label="Sentiment"),
    title="Review Classifier",
    examples=[["Great product!"], ["Broke after a day."]],
)
demo.launch()                                   # http://127.0.0.1:7860
```

## 8. Gradio: ChatInterface with Streaming

> A full chat UI from one function. `gr.ChatInterface(fn)`; `fn(message, history)` receives the history as a list of role / content dicts; `yield` partial text to stream.
>
> Use it for chat demos, Hugging Face Spaces.

```python
import anthropic
import gradio as gr

client = anthropic.Anthropic()


def respond(message: str, history: list[dict]):
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": message})
    partial = ""
    with client.messages.stream(model="claude-opus-5", max_tokens=16000, messages=messages) as stream:
        for text in stream.text_stream:
            partial += text
            yield partial                          # Gradio shows the growing reply


gr.ChatInterface(respond, type="messages", title="Claude Chat").launch()
```

## 9. Chainlit: Chat and Agent UI

> A chat-first framework with streaming, visible steps, file upload and feedback. Decorated async handlers; `cl.Message` to send / stream; `cl.Step` to show intermediate agent steps; `cl.user_session` for per-user state.
>
> Use it for agent and RAG apps where users should see tool calls and sources.

```powershell
pip install chainlit
chainlit run app.py -w
```

```python
import anthropic
import chainlit as cl

client = anthropic.AsyncAnthropic()


@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    await cl.Message(content="Hi! Ask me about our docs.").send()


@cl.on_message
async def on_message(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    async with cl.Step(name="search_docs") as step:            # visible step in the UI
        chunks = await search_docs(message.content)
        step.output = f"{len(chunks)} chunks found"

    reply = cl.Message(content="")
    async with client.messages.stream(model="claude-opus-5", max_tokens=16000,
                                      messages=history) as stream:
        async for text in stream.text_stream:
            await reply.stream_token(text)
    await reply.send()
    history.append({"role": "assistant", "content": reply.content})
```

## 10. FastAPI Backend + Simple Web Frontend

> Separating the AI logic (API) from the UI. FastAPI streams tokens with `StreamingResponse`; any frontend reads the stream with `fetch`.
>
> Use it for production apps, multiple frontends (web, mobile, Slack), custom design.

```python
# api.py
import anthropic
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()
client = anthropic.AsyncAnthropic()


class ChatRequest(BaseModel):
    messages: list[dict]


@app.post("/chat")
async def chat(req: ChatRequest):
    async def token_stream():
        async with client.messages.stream(model="claude-opus-5", max_tokens=16000,
                                          messages=req.messages) as stream:
            async for text in stream.text_stream:
                yield text
    return StreamingResponse(token_stream(), media_type="text/plain")
```

```html
<!-- index.html (minimal) -->
<input id="q"><button onclick="ask()">Send</button><pre id="out"></pre>
<script>
async function ask() {
  const res = await fetch("/chat", {method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({messages: [{role: "user", content: document.getElementById("q").value}]})});
  const reader = res.body.getReader(); const dec = new TextDecoder();
  const out = document.getElementById("out"); out.textContent = "";
  for (;;) { const {done, value} = await reader.read(); if (done) break; out.textContent += dec.decode(value); }
}
</script>
```

More in [40 - FastAPI](40_fastapi.md). JavaScript frameworks (Next.js with an AI SDK, React chat components) are common for polished UIs.

## 11. Showing Sources, Steps and Feedback

> UI patterns that build trust and collect quality signals. Show citations / retrieved documents, show agent steps, add thumbs up / down stored with a trace ID.
>
> Use it for RAG and agent apps.

```python
with st.chat_message("assistant"):
    st.markdown(answer)
    with st.expander("Sources"):
        for s in sources:
            st.markdown(f"- **{s['file']}**, page {s['page']}")
    feedback = st.feedback("thumbs", key=f"fb_{len(st.session_state.messages)}")
    if feedback is not None:
        save_feedback(trace_id, feedback)          # send to your observability tool ([34])
```

## 12. Authentication

> Restricting who can use the app (and your API budget). Built-in auth options of the tool / platform, or put the app behind a login proxy.
>
> Use it for anything beyond a local demo.

| Tool | Options |
|---|---|
| Streamlit | Built-in OIDC login (`st.login`, configured in secrets), or platform auth |
| Gradio | `demo.launch(auth=("user", "pass"))` for simple cases; HF Spaces private / OAuth |
| Chainlit | Password / OAuth / header auth callbacks |
| Any | Reverse proxy with auth (Azure App Service / Container Apps authentication, OAuth2 proxy) |

Also add rate limits and spend caps ([38](38_ai-security.md)).

## 13. Deployment

> Putting the UI online. Managed hosting for quick demos; Docker containers for your own infrastructure.
>
> Use it for sharing with users.

| Option | Good for |
|---|---|
| Streamlit Community Cloud | Free public / small Streamlit apps from a GitHub repo |
| Hugging Face Spaces | Gradio / Streamlit / Docker demos; GPU hardware available |
| Azure Container Apps / App Service | Company apps with auth, private networking ([48](48_azure.md)) |
| Any VM / Kubernetes | Full control ([43](43_docker.md), [46](46_kubernetes.md)) |

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

Streaming behind a proxy: disable response buffering (Nginx `proxy_buffering off;`, [45](45_nginx-https.md)) and allow WebSockets (Streamlit, Chainlit use them).

## 14. Troubleshooting

| Problem | Fix |
|---|---|
| Streamlit chat history disappears | Store messages in `st.session_state`, not normal variables |
| Model / index reloads on every message | `@st.cache_resource` |
| Text appears all at once, not streamed | Use `st.write_stream` / `yield` in Gradio / `stream_token` in Chainlit; disable proxy buffering |
| `StreamlitAPIException` about duplicate widget keys | Give widgets unique `key=` values |
| App works locally, blank behind proxy | Enable WebSocket support in the proxy; set `--server.address 0.0.0.0` in containers |
| `KeyError` on `st.secrets` | Create `.streamlit/secrets.toml` or set secrets in the platform UI |
| Gradio history format errors | Use `type="messages"` and role / content dicts |
| Slow first response | Model / client created per request; cache it; warm up at startup |
| Costs rising from a public demo | Add authentication, rate limits and a spend cap |

## 15. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Echo chat

Build a Streamlit chat that keeps history and echoes the user (no LLM).

<details markdown="1">
<summary>Solution</summary>

```python
import streamlit as st

st.session_state.setdefault("messages", [])
for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])
if prompt := st.chat_input("Say something"):
    for role, text in (("user", prompt), ("assistant", f"You said: {prompt}")):
        st.session_state.messages.append({"role": role, "content": text})
        st.chat_message(role).write(text)
```

</details>

### Exercise 2: Clear button

Add a sidebar button that clears the chat.

<details markdown="1">
<summary>Solution</summary>

```python
with st.sidebar:
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()
```

</details>

### Exercise 3: UI for the capstone

Run the chatbot API from `examples/` and the Streamlit UI from the capstone guide against it.

<details markdown="1">
<summary>Solution</summary>

Terminal 1: `cd examples; uv run uvicorn docs_chatbot.api:app --reload`. Terminal 2: save the `ui.py` from [97 - Capstone](97_capstone-project.md) section 14, `uv add streamlit httpx`, `uv run streamlit run ui.py`.

</details>

---

<!-- nav:start -->
**Previous:** [38 - AI Security and Responsible AI](38_ai-security.md) | **Index:** [All guides](../README.md) | **Next:** [40 - FastAPI](40_fastapi.md)
<!-- nav:end -->
