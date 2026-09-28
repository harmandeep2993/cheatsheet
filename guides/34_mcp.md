# 34 - MCP (Model Context Protocol)

<!-- nav:start -->
**Previous:** [33 - Agent Frameworks](33_agent-frameworks.md) | **Index:** [All guides](../README.md) | **Next:** [35 - Evals and Observability](35_evals-observability.md)
<!-- nav:end -->

Quick reference for the Model Context Protocol: what it is, its architecture, building MCP servers in Python, connecting them to Claude Code, Claude Desktop, VS Code and your own apps, and security.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is MCP?

The **Model Context Protocol** (MCP) is an open standard for connecting AI applications to **tools and data**. Instead of writing a custom integration for every pair of "AI app x service", a service is wrapped once as an **MCP server**, and any MCP-compatible app (Claude Code, Claude Desktop, VS Code, Cursor, agent frameworks, your own Python app) can use it. It is often described as **"USB-C for AI"**: one standard plug between AI apps and the outside world.

### Mental model

```text
Without MCP: every app needs custom code for every service    (M apps x N services integrations)

   Claude Code ---custom---> GitHub          VS Code ---custom---> GitHub
   Claude Code ---custom---> Postgres        VS Code ---custom---> Postgres ...

With MCP: each side implements the protocol once                (M + N integrations)

   HOSTS (AI apps)                 PROTOCOL              SERVERS (capabilities)
   +---------------------+                               +------------------------+
   | Claude Code         |--client--\                /-->| GitHub server          |
   | Claude Desktop      |--client---+--- MCP -------+-->| Postgres server        |
   | VS Code / your app  |--client--/   (JSON-RPC)    \-->| your_company server    |
   +---------------------+                               +------------------------+
```

- **Host**: the AI application the user works in.
- **Client**: a connector inside the host, one per server.
- **Server**: a small program that exposes capabilities:
  - **Tools**: functions the model can call (like [29 - Tool Use](29_tool-use.md)), e.g. `create_issue`.
  - **Resources**: data the app can read, e.g. `file://report.md`, `db://customers/42`.
  - **Prompts**: reusable prompt templates, e.g. `/summarize-pr`.

The model still does tool use exactly as before; MCP standardises **how tools are discovered and called** across apps.

### Why use it?

- **Build once, use everywhere**: one server works in Claude Code, Claude Desktop, VS Code, agent SDKs.
- **Huge ecosystem**: ready-made servers for GitHub, file systems, databases, Slack, browsers, cloud services.
- **Separation**: tool code runs in its own process with its own credentials; the AI app never sees your DB password.
- **Company integrations**: expose internal APIs to all your AI tools in a controlled way.

### Key terms

| Term | Meaning |
|---|---|
| Host | AI app using MCP (Claude Code, Claude Desktop, IDE, your app) |
| Client | Connection inside the host to one server |
| Server | Program exposing tools / resources / prompts |
| Tool | Callable function (model-controlled) |
| Resource | Readable data identified by a URI (app-controlled) |
| Prompt | Reusable template (user-controlled, often shown as slash commands) |
| Transport | How messages travel: **stdio** (local process) or **Streamable HTTP** (remote server) |
| JSON-RPC | The message format MCP uses |
| MCP Inspector | Developer tool to test servers interactively |

**Where it fits:** a standard way to provide the tools from [29 - Tool Use](29_tool-use.md) to agents ([32](32_ai-agents.md), [33](33_agent-frameworks.md)); secured per [38 - AI Security](38_ai-security.md); remote servers deployed like any web service ([40](40_fastapi.md), [43](43_docker.md)).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Model Context Protocol (docs and spec) | https://modelcontextprotocol.io/ |
| MCP Python SDK | https://github.com/modelcontextprotocol/python-sdk |
| Official / reference MCP servers | https://github.com/modelcontextprotocol/servers |
| MCP Inspector | https://github.com/modelcontextprotocol/inspector |
| MCP in Claude Code | https://code.claude.com/docs/en/mcp |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Architecture and Message Flow](#1-architecture-and-message-flow)
2. [Transports: stdio vs Streamable HTTP](#2-transports-stdio-vs-streamable-http)
3. [Install the Python SDK](#3-install-the-python-sdk)
4. [Your First Server (Tools)](#4-your-first-server-tools)
5. [Resources](#5-resources)
6. [Prompts](#6-prompts)
7. [Structured and Rich Tool Results](#7-structured-and-rich-tool-results)
8. [Test with MCP Inspector](#8-test-with-mcp-inspector)
9. [Connect to Claude Code](#9-connect-to-claude-code)
10. [Connect to Claude Desktop](#10-connect-to-claude-desktop)
11. [Connect to VS Code](#11-connect-to-vs-code)
12. [Use MCP from Your Own Python App](#12-use-mcp-from-your-own-python-app)
13. [Remote MCP Servers (HTTP)](#13-remote-mcp-servers-http)
14. [MCP with the Claude API](#14-mcp-with-the-claude-api)
15. [Useful Existing Servers](#15-useful-existing-servers)
16. [Designing a Good MCP Server](#16-designing-a-good-mcp-server)
17. [Security](#17-security)
18. [Troubleshooting](#18-troubleshooting)
19. [Try It](#19-try-it)

---

## 0. Flags and Parameters

> The `claude mcp` commands and config fields you use to register servers. Name the server, choose a transport, give the command or URL.
>
> Use this when you see `claude mcp add --transport http github https://...` and want to know what each part does.

```text
claude  mcp  add  weather  --scope project  --  uv run server.py
|       |    |    |        |                |   |
|       |    |    |        |                |   +-- command that starts the server (stdio)
|       |    |    |        |                +------ "--" separates claude options from the server command
|       |    |    |        +----------------------- where to save the config (local, project, user)
|       |    |    +-------------------------------- name you give this server
|       |    +------------------------------------- action: add a server
|       +------------------------------------------ MCP subcommands
+-------------------------------------------------- Claude Code CLI
```

| Command / field | Meaning |
|---|---|
| `claude mcp add <name> -- <command> [args]` | Add a local stdio server |
| `claude mcp add --transport http <name> <url>` | Add a remote HTTP server |
| `--scope local / project / user` | Only you in this project / shared via `.mcp.json` in the repo / all your projects |
| `-e KEY=value` | Environment variable for the server process |
| `--header "Authorization: Bearer ..."` | Header for remote servers |
| `claude mcp list` / `get <name>` / `remove <name>` | Manage servers |
| `/mcp` (inside Claude Code) | Status, authentication, tools of connected servers |
| `command`, `args`, `env` (JSON config) | How a host starts a stdio server |
| `url`, `type: "http"` (JSON config) | How a host reaches a remote server |

---

## 1. Architecture and Message Flow

> What happens between host, client and server. On start the client and server exchange capabilities; the host lists the tools and gives them to the model; tool calls are forwarded to the server and results returned.
>
> Use it for understanding and debugging MCP setups.

```text
Host starts / connects to server
  client -> server : initialize (protocol version, capabilities)
  client -> server : tools/list, resources/list, prompts/list
  host gives tool definitions to the LLM

User: "What's the weather in Berlin?"
  LLM -> host      : tool_use get_forecast({"city": "Berlin"})
  client -> server : tools/call get_forecast {"city": "Berlin"}
  server -> client : result "12 C, cloudy"
  host -> LLM      : tool_result "12 C, cloudy"
  LLM -> user      : "It's 12 C and cloudy in Berlin."
```

## 2. Transports: stdio vs Streamable HTTP

> The two ways a client talks to a server. stdio = host starts the server as a child process and talks over stdin / stdout; Streamable HTTP = server runs as a web service at a URL.
>
> Use it for stdio for local tools on your machine; HTTP for shared / remote / cloud servers.

| | stdio | Streamable HTTP |
|---|---|---|
| Where it runs | On the same machine, started by the host | Anywhere (server, cloud) |
| Setup | `command` + `args` | `url` (+ auth) |
| Users | One (you) | Many |
| Auth | Env vars on your machine | OAuth / tokens / headers |
| Examples | File system, local DB, scripts | Company APIs, SaaS integrations |

With stdio, **never print to stdout** in your server (it corrupts the protocol); log to stderr or a file.

## 3. Install the Python SDK

> The official Python SDK with the high-level `MCPServer` class (called `FastMCP` in SDK v1). Install with uv or pip; `mcp[cli]` adds the dev tools.
>
> Use it for building servers or clients in Python.

```powershell
uv init mcp-weather
cd mcp-weather
uv add "mcp[cli]" httpx
```

SDK versions: v2 renamed `FastMCP` to `MCPServer` (`from mcp.server.mcpserver import MCPServer`); decorators and `run()` work the same. Many tutorials still show v1 code (`from mcp.server.fastmcp import FastMCP`): either switch to the v2 import or pin `"mcp<2"`. Check the SDK migration guide when upgrading.

## 4. Your First Server (Tools)

> A minimal MCP server exposing two tools. Create an `MCPServer` instance; decorate functions with `@mcp.tool()`; type hints and docstrings become the tool schema and description.
>
> Use it for wrapping any Python function / API for AI apps.

```python
# server.py
import logging

import httpx
from mcp.server.mcpserver import MCPServer

logging.basicConfig(level=logging.INFO, filename="server.log")   # never log to stdout with stdio
mcp = MCPServer("weather")

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


@mcp.tool()
async def get_forecast(city: str) -> str:
    """Get the current temperature and wind speed for a city.

    Args:
        city: City name, e.g. Berlin.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        geo = (await client.get(GEOCODE_URL, params={"name": city, "count": 1})).json()
        if not geo.get("results"):
            return f"City '{city}' not found."
        loc = geo["results"][0]
        data = (await client.get(FORECAST_URL, params={
            "latitude": loc["latitude"], "longitude": loc["longitude"], "current_weather": True,
        })).json()["current_weather"]
    return f"{loc['name']}: {data['temperature']} C, wind {data['windspeed']} km/h"


@mcp.tool()
def convert_c_to_f(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


if __name__ == "__main__":
    mcp.run()                          # stdio transport by default
```

## 5. Resources

> Read-only data the host can load into context. `@mcp.resource("uri://...")` functions return content; URI templates with `{params}` expose many items.
>
> Use it for documents, configs, database records the user / app attaches as context.

```python
@mcp.resource("config://app")
def app_config() -> str:
    """Current application configuration."""
    return Path("config.yaml").read_text(encoding="utf-8")


@mcp.resource("customers://{customer_id}")
def customer(customer_id: str) -> str:
    """Customer profile as JSON."""
    return json.dumps(load_customer(customer_id))
```

## 6. Prompts

> Reusable prompt templates exposed by the server. `@mcp.prompt()` functions return the prompt text (or messages); hosts often show them as slash commands.
>
> Use it for standard team workflows ("review this SQL", "summarise incident").

```python
@mcp.prompt()
def review_sql(query: str) -> str:
    """Review a SQL query for correctness and performance."""
    return f"Review this SQL for bugs, performance issues and security risks:\n\n{query}"
```

## 7. Structured and Rich Tool Results

> Returning typed data instead of plain strings. Return a Pydantic model / dict / list; the server converts it to structured content with an output schema.
>
> Use it for results that other tools or code will use.

```python
from pydantic import BaseModel


class Forecast(BaseModel):
    city: str
    temperature_c: float
    wind_kmh: float


@mcp.tool()
async def get_forecast_structured(city: str) -> Forecast:
    """Get the current weather for a city as structured data."""
    ...
    return Forecast(city=city, temperature_c=12.0, wind_kmh=9.5)
```

## 8. Test with MCP Inspector

> A browser-based tool to list and call your server's tools, resources and prompts. Start the inspector with your server command; click tools, fill arguments, see raw results.
>
> Use it always, before connecting a server to an AI app.

```powershell
uv run mcp dev server.py                                  # starts the Inspector for this server
npx @modelcontextprotocol/inspector uv run server.py      # alternative (needs Node.js)
```

## 9. Connect to Claude Code

> Making your server's tools available in Claude Code. Register it with `claude mcp add`; for teams, commit a `.mcp.json` file at the project root.
>
> Use it for giving your coding agent access to internal APIs, databases, docs.

```powershell
claude mcp add weather -- uv --directory D:\Projects\mcp-weather run server.py
claude mcp add --transport http company-docs https://mcp.example.com/mcp
claude mcp list
```

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": ["--directory", "D:/Projects/mcp-weather", "run", "server.py"],
      "env": {"LOG_LEVEL": "info"}
    }
  }
}
```

Inside Claude Code, run `/mcp` to see server status and authenticate remote servers.

## 10. Connect to Claude Desktop

> Using your server in the Claude desktop app. Add it to `claude_desktop_config.json` (Settings -> Developer -> Edit Config), then restart the app.
>
> Use it for personal productivity tools with a chat interface.

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": ["--directory", "D:\\Projects\\mcp-weather", "run", "server.py"]
    }
  }
}
```

Config location on Windows: `%APPDATA%\Claude\claude_desktop_config.json`; Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`. Use absolute paths.

## 11. Connect to VS Code

> Using MCP servers with VS Code's agent / chat features. Add servers to `.vscode/mcp.json` (workspace) or user settings.
>
> Use it for sharing tools with everyone who opens the repo in VS Code.

```json
{
  "servers": {
    "weather": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "server.py"]
    }
  }
}
```

## 12. Use MCP from Your Own Python App

> Being the host yourself: connecting to MCP servers from Python and giving their tools to an LLM. Open a client session over stdio / HTTP, list tools, convert them to your LLM's tool format, forward tool calls.
>
> Use it for custom agents that should reuse existing MCP servers.

```python
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(command="uv", args=["run", "server.py"])


async def main():
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print([t.name for t in tools.tools])
            result = await session.call_tool("get_forecast", {"city": "Berlin"})
            print(result.content[0].text)


asyncio.run(main())
```

The Anthropic Python SDK has helpers to pass MCP tools straight to its tool runner (`pip install "anthropic[mcp]"`, `anthropic.lib.tools.mcp`), and agent frameworks ([33](33_agent-frameworks.md)) accept MCP servers directly.

## 13. Remote MCP Servers (HTTP)

> Running a server as a web service many users can reach. Start the server with the Streamable HTTP transport; deploy like any web app (container, HTTPS, auth).
>
> Use it for team-wide or company-wide tools, SaaS integrations.

```python
if __name__ == "__main__":
    mcp.run(transport="streamable-http")      # serves on http://127.0.0.1:8000/mcp by default
```

Production: put it behind HTTPS ([45](45_nginx-https.md)), add authentication (OAuth / tokens), rate limits and logging; containerise with [43 - Docker](43_docker.md).

## 14. MCP with the Claude API

> Letting the Claude API connect directly to a remote MCP server during a request. Pass the server in `mcp_servers` AND add a matching `mcp_toolset` tool; uses a beta header.
>
> Use it for server-side apps that want remote MCP tools without writing client code.

```python
response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    betas=["mcp-client-2025-11-20"],
    mcp_servers=[{"type": "url", "url": "https://mcp.example.com/mcp", "name": "company-docs"}],
    tools=[{"type": "mcp_toolset", "mcp_server_name": "company-docs"}],
    messages=[{"role": "user", "content": "Find our vacation policy."}],
)
```

Beta names change; check current docs.

## 15. Useful Existing Servers

> Ready-made servers you can install instead of building. Find them in the official MCP servers repository / registry and vendor documentation.
>
> Use it before writing your own.

| Area | Examples |
|---|---|
| Developer | GitHub, GitLab, Git, file system, Sentry |
| Data | PostgreSQL, SQLite, BigQuery, Snowflake, vector DBs |
| Productivity | Slack, Google Drive, Notion, Linear, Jira |
| Web | Fetch, browser automation (Playwright), search |
| Cloud | Azure, AWS, Cloudflare, Docker, Kubernetes |

Only install servers from sources you trust: they run code with your permissions.

## 16. Designing a Good MCP Server

> Principles for servers that models use well. Same as good tool design ([29](29_tool-use.md) section 10) plus MCP specifics.
>
> Use it for building a server for your team.

- Focused server per domain (orders, docs, metrics), a handful of well-described tools each.
- Clear tool names and docstrings; typed parameters; concise results with IDs.
- Read-only by default; separate write tools; confirmation for destructive actions.
- Credentials via env vars / secret store, never hard-coded.
- Log to stderr / files; handle errors with helpful messages.
- Version your server; document setup in its README.

## 17. Security

> Risks of connecting AI apps to tools and data. A server can read / change whatever its credentials allow; tool descriptions and results can contain malicious instructions.
>
> Use it before installing or publishing any server.

| Risk | Mitigation |
|---|---|
| Malicious or buggy third-party server | Install only trusted servers; review code; pin versions |
| Over-privileged credentials | Least privilege: read-only DB users, scoped tokens |
| Prompt injection via tool results / resources | Treat results as data; approval for risky actions ([38](38_ai-security.md)) |
| Tool poisoning (hidden instructions in descriptions) | Review tool descriptions of servers you add |
| Data exfiltration (one tool reads secrets, another sends them out) | Limit which servers are active together; watch network access |
| Unauthenticated remote servers | OAuth / tokens, HTTPS, rate limits |

## 18. Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'mcp.server.fastmcp'` | You have MCP SDK v2: use `from mcp.server.mcpserver import MCPServer`, or pin `"mcp<2"` for v1 code |
| Server not showing in the host | Restart the host; check config JSON syntax and absolute paths; `claude mcp list` / `/mcp` |
| "Connection closed" immediately | Server crashed on start; run the command manually to see the error; check `server.log` |
| Garbled protocol / parse errors (stdio) | Something prints to stdout; log to stderr / file instead |
| `uv` / `python` not found by the host | Use the full path to the executable in `command` |
| Tool never called | Improve the docstring (what, when, returns); check the tool is allowed in the host |
| Tool errors not visible | Return helpful error strings; check host logs (Claude Desktop: logs folder, Claude Code: `/mcp`) |
| Works in Inspector, not in host | Different working directory / env vars; set `--directory` and `env` |
| Remote server 401 | Configure auth header / complete OAuth via `/mcp` |

## 19. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Inspect the example server

Open `examples/mcp_server/server.py` in the MCP Inspector and call `search_docs`.

<details markdown="1">
<summary>Solution</summary>

```bash
cd examples
uv run mcp dev mcp_server/server.py
```

In the Inspector: Tools -> `search_docs` -> query "reset password" -> Run.

</details>

### Exercise 2: Register it with Claude Code

Make the server available in Claude Code and check it is connected.

<details markdown="1">
<summary>Solution</summary>

```bash
claude mcp add pocket-docs -- uv --directory D:/Projects/pocket-guide/examples run python -m mcp_server.server
claude mcp list
```

Then ask Claude Code: "Using pocket-docs, what is the refund window for jackets?"

</details>

### Exercise 3: stdout rule

Why must a stdio MCP server never `print()` to stdout?

<details markdown="1">
<summary>Solution</summary>

With stdio transport, stdout carries the JSON-RPC protocol messages; any extra output corrupts them and the host disconnects. Log to stderr or a file instead.

</details>

---

<!-- nav:start -->
**Previous:** [33 - Agent Frameworks](33_agent-frameworks.md) | **Index:** [All guides](../README.md) | **Next:** [35 - Evals and Observability](35_evals-observability.md)
<!-- nav:end -->
