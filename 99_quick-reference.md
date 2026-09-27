# 99 - Quick Reference

<!-- nav:start -->
**Previous:** [98 - Glossary](98_glossary.md) | **Index:** [All guides](README.md)
<!-- nav:end -->

The most-used commands and snippets from every guide on one page. For explanations, flags and troubleshooting, follow the link in each heading. Windows / macOS / Linux differences: [00 - Big Picture](00_big-picture.md) section 13.

Jump to: [Foundations](#foundations) | [Python](#python) | [Data and ML](#data-and-ml) | [AI Engineering](#ai-engineering) | [APIs and Deployment](#apis-and-deployment)

## Foundations

### [01 - Markdown](01_markdown.md)

```markdown
# H1   ## H2   **bold**   *italic*   `code`   [link](url)   ![img](path)
- bullet        1. numbered        - [ ] task        > quote        ---
| A | B |       |---|---|        ```python  code block  ```
```

### [02 - Terminal and PowerShell](02_terminal-powershell.md)

```powershell
cd D:\Projects ; ls -Force ; pwd                  # navigate, list incl. hidden, where am I
New-Item file.txt ; mkdir folder ; Remove-Item x -Recurse -Force
Get-Content app.log -Tail 20 -Wait                # follow a log
Select-String "error" *.log                       # grep
$env:MY_VAR = "value" ; $env:PATH -split ";"      # env vars
Get-NetTCPConnection -LocalPort 8000              # who uses port 8000
winget install -e --id Git.Git                    # install software
```

### [03 - Linux](03_linux.md)

```bash
ls -lah ; cd ~ ; mkdir -p a/b ; cp -r src dst ; rm -rf dir
grep -rn "error" . ; find . -name "*.csv" ; tail -f app.log
chmod +x run.sh ; sudo apt update && sudo apt install -y htop
systemctl status nginx ; journalctl -u nginx -f ; ss -tulpn
df -h ; free -h ; htop ; ssh -i key.pem user@host ; tar -czvf a.tgz dir/
```

### [04 - Git and GitHub](04_git.md)

```bash
git status ; git add . ; git commit -m "feat: add x" ; git push
git switch -c feature/x ; git switch main ; git pull
git log --oneline --graph --all ; git diff --staged
git restore file.py ; git restore --staged file.py      # discard / unstage
git reset --soft HEAD~1 ; git revert <hash>             # undo commit (local / pushed)
git stash -u ; git stash pop ; gh pr create --fill
```

### [05 - VS Code](05_vscode.md)

```text
Ctrl+Shift+P  command palette     Ctrl+P  open file          Ctrl+`  terminal
Ctrl+D        next occurrence     Alt+Click  add cursor      Ctrl+/  comment
F12  go to definition  F2  rename  F5  debug  F9  breakpoint  Shift+Alt+F  format
Python: Select Interpreter -> .venv
```

### [06 - Regex](06_regex.md)

```text
\d digit  \w word char  \s space  .  any   ^ start  $ end  \b word boundary
*  0+   +  1+   ?  0 or 1   {2,4}  2 to 4   *?  lazy   [a-z]  class   [^,]  not comma
( )  group   (?:)  non-capturing   (?P<name>)  named   a|b  or   (?=x)  followed by x
```

```python
re.search(r"(\d{4})-(\d{2})", s) ; re.findall(r"\d+", s) ; re.sub(r"\s+", " ", s)
df["col"].str.extract(r"(\d{4})") ; df["col"].str.contains(r"^A", regex=True)
```

### [07 - YAML, JSON, TOML and .env](07_yaml-json.md)

```python
json.loads(s) ; json.dumps(obj, indent=2) ; json.load(f) ; json.dump(obj, f)
yaml.safe_load(f) ; tomllib.load(open("pyproject.toml", "rb"))
load_dotenv() ; os.getenv("API_KEY")
```

### [08 - HTTP and APIs](08_http-apis.md)

```bash
curl -i https://api.example.com/items
curl -X POST URL -H "Content-Type: application/json" -d '{"name": "x"}'
```

```python
r = requests.get(url, params={"q": "x"}, headers=h, timeout=10); r.raise_for_status(); r.json()
# 2xx ok | 400 bad request | 401 auth | 403 forbidden | 404 not found | 422 invalid | 429 slow down | 5xx server
```

## Python

### [09 - Python Basics](09_python-basics.md)

```python
f"{name}: {score:.2f}" ; [x * 2 for x in xs if x > 0] ; {k: v for k, v in d.items()}
for i, x in enumerate(xs): ...          for a, b in zip(xs, ys): ...
with open("f.txt", encoding="utf-8") as f: text = f.read()
try: ... except ValueError as e: ...    Path("data") / "x.csv"
logger = logging.getLogger(__name__)
```

### [10 - Python Virtual Environment](10_python-virtual-environment.md)

```powershell
python -m venv .venv ; .venv\Scripts\Activate.ps1      # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt ; pip freeze > requirements.txt ; deactivate
```

### [11 - uv](11_uv.md)

```bash
uv init ; uv add pandas ; uv add --dev pytest ; uv remove pandas
uv run app.py ; uv sync ; uv lock --upgrade ; uv python install 3.12 ; uvx ruff check .
```

### [12 - Pydantic](12_pydantic.md)

```python
class User(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0)
User.model_validate(d) ; User.model_validate_json(s) ; u.model_dump() ; User.model_json_schema()
```

### [13 - Async Python](13_async-python.md)

```python
async def main():
    sem = asyncio.Semaphore(5)
    results = await asyncio.gather(*(call(x) for x in items), return_exceptions=True)
asyncio.run(main())                      # in Jupyter / FastAPI: just await
```

### [14 - pytest](14_pytest.md)

```bash
pytest -q ; pytest -x -k "login" ; pytest --lf ; pytest --cov=src --cov-report=term-missing
```

```python
@pytest.fixture ... ; @pytest.mark.parametrize("a,b", [(1, 2)]) ; with pytest.raises(ValueError): ...
client = MagicMock(); client.messages.create.return_value = fake_message("ok")
```

### [15 - Jupyter](15_jupyter.md)

```text
Shift+Enter run   Esc then A/B  cell above/below   D D delete   M markdown   Y code   0 0 restart
%pip install x   %timeit f()   %%time   %load_ext autoreload + %autoreload 2   func?  func??
python -m ipykernel install --user --name myproject
```

## Data and ML

### [16 - NumPy](16_numpy.md)

```python
a = np.array([1, 2, 3]) ; np.zeros((2, 3)) ; np.arange(0, 10, 2) ; a.shape ; a.reshape(-1, 1)
a[a > 2] ; m[:, 1] ; m.sum(axis=0) ; np.where(a > 2, "hi", "lo") ; rng = np.random.default_rng(42)
```

### [17 - Pandas](17_pandas.md)

```python
df = pd.read_csv("f.csv") ; df.head() ; df.info() ; df.describe() ; df["col"].value_counts()
df[df["a"] > 1] ; df.loc[rows, cols] ; df.groupby("g")["x"].agg(["mean", "sum"])
df.merge(o, on="key", how="left") ; df.fillna(0) ; df.drop_duplicates() ; df.to_parquet("f.parquet")
```

### [18 - Polars and DuckDB](18_polars-duckdb.md)

```python
pl.scan_parquet("*.parquet").filter(pl.col("y") == 2025).group_by("r").agg(pl.col("x").sum()).collect()
duckdb.sql("SELECT r, SUM(x) FROM 'data/*.parquet' GROUP BY r").df()
```

### [19 - SQL](19_sql.md)

```sql
SELECT d.name, AVG(e.salary) AS avg_salary
FROM employees e JOIN departments d ON e.department_id = d.id
WHERE e.hire_date >= '2024-01-01'
GROUP BY d.name HAVING AVG(e.salary) > 50000 ORDER BY avg_salary DESC LIMIT 10;
ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)          -- top N per group
```

### [20 - Matplotlib](20_matplotlib.md)

```python
fig, ax = plt.subplots(figsize=(10, 5)) ; ax.plot(x, y, label="a") ; ax.bar(cats, vals)
ax.set_title("T") ; ax.set_xlabel("x") ; ax.legend() ; fig.tight_layout() ; fig.savefig("c.png", dpi=300)
```

### [21 - Seaborn](21_seaborn.md)

```python
sns.histplot(data=df, x="a", hue="g", kde=True) ; sns.boxplot(data=df, x="cat", y="val")
sns.scatterplot(data=df, x="a", y="b", hue="g") ; sns.heatmap(df.corr(numeric_only=True), annot=True)
sns.catplot(data=df, x="cat", y="val", kind="bar", col="g")
```

### [22 - Scikit-learn](22_scikit-learn.md)

```python
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
pipe = Pipeline([("prep", ColumnTransformer([...])), ("model", HistGradientBoostingClassifier())])
cross_val_score(pipe, X_tr, y_tr, cv=5, scoring="f1") ; pipe.fit(X_tr, y_tr)
print(classification_report(y_te, pipe.predict(X_te))) ; joblib.dump(pipe, "model.joblib")
```

### [23 - PyTorch](23_pytorch.md)

```python
for X, y in loader:
    loss = loss_fn(model(X.to(device)), y.to(device))
    optimizer.zero_grad(); loss.backward(); optimizer.step()
model.eval(); torch.no_grad() ; torch.save(model.state_dict(), "m.pt")
```

### [24 - Hugging Face](24_hugging-face.md)

```python
pipeline("sentiment-analysis", model="...")("I love it")
SentenceTransformer("BAAI/bge-m3").encode(texts, normalize_embeddings=True)
tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
```

## AI Engineering

### [25 - LLM Fundamentals](25_llm-fundamentals.md)

```text
1 token ~ 4 chars ~ 0.75 words   cost = in_tokens x in_price + out_tokens x out_price (per 1M)
context window = system + tools + history + docs + question + OUTPUT
fix order: prompt -> RAG (knowledge) -> tools (live data / actions) -> fine-tune (behaviour)
```

### [26 - LLM APIs](26_llm-apis.md)

```python
client = anthropic.Anthropic()
r = client.messages.create(model="claude-opus-5", max_tokens=16000, system="...",
                           messages=[{"role": "user", "content": "..."}])
text = "".join(b.text for b in r.content if b.type == "text") ; r.stop_reason ; r.usage
with client.messages.stream(...) as s: [print(t, end="") for t in s.text_stream]
client.messages.parse(..., output_format=MyPydanticModel).parsed_output
```

### [27 - Prompt Engineering](27_prompt-engineering.md)

```text
Context + goal + audience -> task -> <tagged data> -> rules / edge cases -> examples -> output format
Documents first, question last. Allow "I don't know". Explain WHY a rule exists. Test on an eval set.
```

### [28 - Tool Use](28_tool-use.md)

```python
@beta_tool
def get_order(order_id: str) -> str:
    """Look up an order. Args: order_id: format A-1234."""
runner = client.beta.messages.tool_runner(model=..., max_tokens=16000, tools=[get_order], messages=msgs)
# manual loop: while stop_reason == "tool_use": run tools -> ALL tool_result blocks in ONE user message
```

### [29 - Embeddings and Vector DBs](29_embeddings-vector-db.md)

```python
vecs = model.encode(docs, normalize_embeddings=True) ; scores = vecs @ model.encode(q, normalize_embeddings=True)
col = chromadb.PersistentClient("./db").get_or_create_collection("kb", metadata={"hnsw:space": "cosine"})
col.add(ids=ids, documents=docs, metadatas=meta) ; col.query(query_texts=[q], n_results=5, where={...})
```

### [30 - RAG](30_rag.md)

```text
INDEX: load -> clean -> chunk (300-800 tokens, 10-20% overlap) -> embed -> store (+ metadata)
QUERY: rewrite? -> embed -> retrieve top 20 (+ permission filter) -> rerank to 5 -> prompt with
       numbered <source> tags -> answer with [n] citations -> evaluate recall@k + faithfulness
```

### [31 - AI Agents](31_ai-agents.md)

```text
loop: model -> tool calls -> results -> model ... until end_turn | step cap | cost cap | time cap
simplest first: single call -> workflow (chain / route / parallel) -> agent -> multi-agent
risky tools need human approval; sandbox; log every step; eval task success rate
```

### [32 - Agent Frameworks](32_agent-frameworks.md)

```python
async for m in query(prompt="...", options=ClaudeAgentOptions(allowed_tools=["Read", "Bash"])): ...
Runner.run_sync(Agent(name="A", instructions="...", tools=[fn]), "question").final_output   # OpenAI Agents SDK
StateGraph(State) -> add_node / add_edge / add_conditional_edges -> compile(checkpointer=...)  # LangGraph
```

### [33 - MCP](33_mcp.md)

```python
mcp = MCPServer("name")            # from mcp.server.mcpserver import MCPServer
@mcp.tool()
def my_tool(x: str) -> str: """Docstring = description."""
mcp.run()                                   # stdio ; mcp.run(transport="streamable-http")
```

```bash
uv run mcp dev server.py ; claude mcp add name -- uv run server.py ; claude mcp list
```

### [34 - Evals and Observability](34_evals-observability.md)

```text
eval set (JSONL: input, reference, tags) -> run system -> grade (code checks first, LLM judge with
rubric, humans) -> compare versions per case -> change ONE thing -> repeat; smoke set in CI
log per call: trace id, prompt version, model, tokens, cost, latency, stop_reason, tool calls
```

### [35 - Local LLMs](35_local-llms.md)

```bash
ollama pull qwen3:4b ; ollama run qwen3:4b ; ollama list ; ollama ps ; ollama rm x
curl http://localhost:11434/api/tags ; OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
memory_GB ~ params_B x bits / 8 (+ context and overhead)   Q4_K_M = good default quantization
```

### [36 - Fine-tuning](36_fine-tuning.md)

```text
only after prompting / RAG; data = chat JSONL {"messages": [...]}; start with 200-500 excellent examples
LoRA r=16 alpha=32 lr=2e-4 epochs 1-3; watch val loss; compare with base model on held-out evals
```

### [37 - AI Security](37_ai-security.md)

```text
lethal trifecta = private data + untrusted content + outbound actions -> never all three without approval
treat model output and tool results as untrusted; least privilege tools; secrets never in prompts / code
rate limits + max tokens + step / cost caps; RAG filtered by user permissions; red-team cases in evals
```

### [38 - AI UIs](38_ai-ui.md)

```python
if p := st.chat_input("Ask"):                       # Streamlit
    st.session_state.messages.append({"role": "user", "content": p})
    reply = st.write_stream(stream_reply(st.session_state.messages))
gr.ChatInterface(respond, type="messages").launch()    # Gradio
```

## APIs and Deployment

### [39 - FastAPI](39_fastapi.md)

```python
app = FastAPI()
@app.post("/items", status_code=201)
def create(item: Item, db=Depends(get_db)) -> ItemOut: ...
raise HTTPException(404, "Not found") ; TestClient(app).post("/items", json={...})
```

### [40 - Uvicorn](40_uvicorn.md)

```bash
uvicorn app.main:app --reload                                            # development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --timeout-graceful-shutdown 30
```

### [41 - Redis and Task Queues](41_redis-queues.md)

```python
r = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)
r.set(k, v, ex=3600) ; r.get(k) ; r.incr(k) ; q.enqueue(fn, arg, job_timeout=600) ; task.delay(arg)
```

### [42 - Docker](42_docker.md)

```bash
docker build -t app:1.0 . ; docker run -d -p 8000:8000 --env-file .env --name app app:1.0
docker ps -a ; docker logs -f app ; docker exec -it app sh ; docker compose up -d --build
docker compose down ; docker system prune
```

### [43 - GitHub Actions](43_github-actions.md)

```yaml
on: {push: {branches: [main]}, pull_request: {}}
jobs:
  test:
    runs-on: ubuntu-latest
    steps: [{uses: actions/checkout@v4}, {uses: astral-sh/setup-uv@v6}, {run: uv sync --locked}, {run: uv run pytest -q}]
```

### [44 - Nginx and HTTPS](44_nginx-https.md)

```bash
sudo nginx -t && sudo systemctl reload nginx ; sudo certbot --nginx -d api.example.com
# location / { proxy_pass http://127.0.0.1:8000; proxy_set_header Host $host; proxy_buffering off; }
```

### [45 - Kubernetes](45_kubernetes.md)

```bash
kubectl get pods -A ; kubectl describe pod x ; kubectl logs -f deploy/api ; kubectl apply -f k8s/
kubectl rollout status deploy/api ; kubectl rollout undo deploy/api ; kubectl port-forward svc/api 8000:80
```

### [46 - Terraform](46_terraform.md)

```bash
terraform init ; terraform fmt -recursive ; terraform validate
terraform plan -var-file=dev.tfvars -out=tfplan ; terraform apply tfplan ; terraform destroy
```

### [47 - Azure](47_azure.md)

```bash
az login ; az account set --subscription <id> ; az group create -n rg-x -l swedencentral
az containerapp up -n api -g rg-x --source . --ingress external --target-port 8000
az vm list -d -o table ; az group delete -n rg-x --yes --no-wait
```

### [48 - Azure VM + Linux + Ollama](48_azure-vm-ollama.md)

```powershell
az vm start -g $RG -n $VM ; ssh -i $KEY "$USER@$IP"
ssh -i $KEY -N -L 11435:localhost:11434 "$USER@$IP"      # tunnel to the VM's Ollama
az vm deallocate -g $RG -n $VM                             # ALWAYS at the end (stops compute billing)
```

---

<!-- nav:start -->
**Previous:** [98 - Glossary](98_glossary.md) | **Index:** [All guides](README.md)
<!-- nav:end -->
