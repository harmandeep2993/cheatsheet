# 45 - Nginx, Reverse Proxy and HTTPS

<!-- nav:start -->
**Previous:** [44 - GitHub Actions (CI/CD)](44_github-actions.md) | **Index:** [All guides](../README.md) | **Next:** [46 - Kubernetes](46_kubernetes.md)
<!-- nav:end -->

Quick reference for putting apps (FastAPI, Streamlit, Ollama) behind Nginx on a Linux server: reverse proxy, HTTPS with Let's Encrypt, streaming, WebSockets, basic auth, rate limiting and running apps as services.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### Before you start

**You should know:** HTTP and status codes ([09](09_http-apis.md)), running a server such as Uvicorn ([41](41_uvicorn.md)), Linux basics and SSH ([04](04_linux.md)), and what ports are ([01 - Core Concepts](01_core-concepts.md) section 13). You need a Linux server and, for HTTPS, a domain name.

**The problem it solves:** your app runs on a port like 8000, but users expect `https://api.example.com` on the standard ports, with encryption. You may run several apps on one server, want to limit abusive traffic, and do not want every app to implement HTTPS, compression and security headers itself.

**Before free HTTPS:** certificates cost money and had to be renewed by hand each year, so many sites used plain HTTP and passwords travelled unencrypted. Let's Encrypt (2015) made certificates free and automatic. Nginx (2004) was built to handle many connections efficiently and became the common front door for web apps.

**Think of it like:** the reception desk and security gate of an office building. Visitors only ever meet reception (the proxy on ports 80 / 443), which checks them, and forwards them to the right office inside (your apps), which never face the street directly.

### What is a reverse proxy and why HTTPS?

A **reverse proxy** is a web server that sits **in front of your apps** and forwards incoming requests to them. Users talk only to the proxy (on ports 80 / 443); the proxy talks to your app running privately on `localhost:8000`. **Nginx** is the most widely used one (Caddy and Traefik are popular alternatives).

**HTTPS** encrypts traffic between the browser and the server using a **TLS certificate**, so passwords, API keys and data cannot be read or changed in transit. **Let's Encrypt** issues free certificates, and `certbot` installs and renews them automatically.

### Mental model

```text
Internet                               Your Linux server / VM
--------                               ------------------------------------------------
browser  --https://api.example.com-->  :443  NGINX  (TLS certificate, public entry point)
                                              |  - terminates HTTPS
                                              |  - routes by domain / path
                                              |  - adds headers, limits, auth, gzip
                                              |
                                              +--> http://127.0.0.1:8000   FastAPI (uvicorn)
                                              +--> http://127.0.0.1:8501   Streamlit
                                              +--> http://127.0.0.1:11434  Ollama (with auth!)

Only ports 80 and 443 are open to the internet; apps listen on 127.0.0.1 only.
```

### Why use it?

- **Security**: HTTPS everywhere; apps not directly exposed; one place for auth and limits.
- **One IP, many apps**: route by domain (`api.` vs `chat.`) or path (`/api` vs `/`).
- **Performance**: static files, compression, caching, connection handling.
- **Reliability**: restart apps without users noticing; load-balance across instances.

### Key terms

| Term | Meaning |
|---|---|
| Reverse proxy | Server forwarding client requests to backend apps |
| Upstream / backend | The app behind the proxy |
| Server block | Nginx config for one site / domain |
| Location | Rules for a URL path inside a server block |
| TLS / SSL certificate | Proves the domain identity and enables encryption |
| Let's Encrypt / certbot | Free certificate authority / tool to get and renew certificates |
| DNS A record | Maps a domain name to your server's IP address |
| Port 80 / 443 | HTTP / HTTPS |
| systemd service | Keeps your app running and restarts it on failure / reboot |
| Buffering | Proxy collects the response before sending (breaks streaming if on) |

**Where it fits:** fronts [40 - FastAPI](40_fastapi.md), [39 - AI UIs](39_ai-ui.md) and [36 - Local LLMs](36_local-llms.md) on a Linux VM ([04 - Linux](04_linux.md), [49 - Azure VM](49_azure-vm-ollama.md)); HTTP concepts in [09](09_http-apis.md); managed alternatives in [48 - Azure](48_azure.md) (Container Apps / App Service give HTTPS automatically).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| nginx documentation | https://nginx.org/en/docs/ |
| Certbot | https://certbot.eff.org/ |
| Let's Encrypt | https://letsencrypt.org/docs/ |
| Caddy | https://caddyserver.com/docs/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [When You Need This (and When Not)](#1-when-you-need-this-and-when-not)
2. [Install Nginx](#2-install-nginx)
3. [Config File Layout](#3-config-file-layout)
4. [Reverse Proxy for FastAPI](#4-reverse-proxy-for-fastapi)
5. [Domain and DNS](#5-domain-and-dns)
6. [HTTPS with Let's Encrypt (certbot)](#6-https-with-lets-encrypt-certbot)
7. [Streaming (SSE) and WebSockets](#7-streaming-sse-and-websockets)
8. [Several Apps on One Server](#8-several-apps-on-one-server)
9. [Basic Auth (Protect Ollama or Admin UIs)](#9-basic-auth-protect-ollama-or-admin-uis)
10. [Rate Limiting and Upload Size](#10-rate-limiting-and-upload-size)
11. [Load Balancing](#11-load-balancing)
12. [Run Your App as a systemd Service](#12-run-your-app-as-a-systemd-service)
13. [Firewall](#13-firewall)
14. [Caddy (Simpler Alternative)](#14-caddy-simpler-alternative)
15. [Logs and Debugging](#15-logs-and-debugging)
16. [Troubleshooting](#16-troubleshooting)
17. [Try It](#17-try-it)

---

## 0. Flags and Parameters

> The nginx / certbot commands and the most common config directives. Commands manage the service; directives inside config blocks define behaviour.
>
> Use this when you see `proxy_pass http://127.0.0.1:8000;` or `certbot --nginx -d api.example.com` and want to know what each part does.

```text
sudo  certbot  --nginx  -d api.example.com  -d www.example.com
|     |        |        |
|     |        |        +-- -d: domain(s) to include in the certificate
|     |        +----------- plugin: edit the nginx config automatically
|     +-------------------- Let's Encrypt client
+-------------------------- run as administrator
```

| Command / directive | Meaning |
|---|---|
| `sudo nginx -t` | Test config syntax (run before every reload) |
| `sudo systemctl reload nginx` | Apply config without dropping connections |
| `sudo systemctl restart nginx` / `status nginx` | Restart / check status |
| `listen 80;` / `listen 443 ssl;` | Port (and TLS) to listen on |
| `server_name api.example.com;` | Domain this block answers |
| `location /api/ { ... }` | Rules for URLs starting with `/api/` |
| `proxy_pass http://127.0.0.1:8000;` | Forward requests to the backend |
| `proxy_set_header Host $host;` | Pass original host / client info to the app |
| `proxy_buffering off;` | Stream responses immediately (SSE / LLM tokens) |
| `proxy_read_timeout 300s;` | Allow slow responses (long LLM calls) |
| `client_max_body_size 50M;` | Max upload size |
| `certbot renew --dry-run` | Test automatic renewal |

---

## 1. When You Need This (and When Not)

> Deciding between managing Nginx yourself and using a managed platform. Managed platforms (Azure Container Apps, App Service, Hugging Face Spaces, Cloud Run) already provide HTTPS, domains and scaling. Nginx is for your own VM / server; skip it when a platform handles the edge for you.

| Situation | Use |
|---|---|
| App on a single Linux VM (e.g. Ollama + FastAPI on a GPU VM) | Nginx or Caddy |
| Docker Compose stack on a VM | Nginx / Caddy / Traefik container |
| Azure Container Apps / App Service | Built-in HTTPS; no Nginx needed |
| Kubernetes | Ingress controller (often Nginx-based) ([46](46_kubernetes.md)) |

## 2. Install Nginx

> Installing and starting Nginx on Ubuntu. `apt install`, enable the service, check the welcome page.
>
> Use it for fresh server setup.

```bash
sudo apt update && sudo apt install -y nginx
sudo systemctl enable --now nginx
curl -I http://localhost                  # HTTP/1.1 200 OK, Server: nginx
```

## 3. Config File Layout

> Where Nginx configuration lives (Ubuntu / Debian). One file per site in `sites-available`, enabled by a symlink in `sites-enabled`.
>
> Use it for adding or editing sites.

| Path | Contains |
|---|---|
| `/etc/nginx/nginx.conf` | Global settings (usually leave as is) |
| `/etc/nginx/sites-available/` | One config file per site |
| `/etc/nginx/sites-enabled/` | Symlinks to active sites |
| `/var/log/nginx/access.log`, `error.log` | Logs |

```bash
sudo nano /etc/nginx/sites-available/api
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default          # remove the welcome site
sudo nginx -t && sudo systemctl reload nginx
```

## 4. Reverse Proxy for FastAPI

> Forwarding requests from port 80 to your app on port 8000. A `server` block with `proxy_pass` and forwarding headers.
>
> Use it for serving any web app / API.

```nginx
# /etc/nginx/sites-available/api
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;               # long LLM requests
    }
}
```

Run uvicorn with `--proxy-headers --forwarded-allow-ips="127.0.0.1"` so FastAPI sees the real client IP and HTTPS scheme.

## 5. Domain and DNS

> Pointing a domain name at your server. At your DNS provider, create an **A record** `api.example.com -> <server public IP>`; wait for it to propagate.
>
> Use it before requesting certificates.

```bash
nslookup api.example.com             # should return your server IP
```

Azure VMs: give the public IP a DNS label to get a free name like `myvm.swedencentral.cloudapp.azure.com`.

## 6. HTTPS with Let's Encrypt (certbot)

> Free, auto-renewing TLS certificates. certbot proves you control the domain (via port 80), gets a certificate, edits the Nginx config for HTTPS and sets up renewal.
>
> Use it in every public site.

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.example.com         # answer prompts; choose redirect HTTP -> HTTPS
sudo certbot renew --dry-run                    # test automatic renewal (runs via systemd timer)
sudo certbot certificates                       # list certificates and expiry
```

After certbot, your server block has `listen 443 ssl;`, `ssl_certificate` lines and an HTTP -> HTTPS redirect. Port 80 must be reachable for issuance and renewal.

## 7. Streaming (SSE) and WebSockets

> Proxy settings so LLM token streams and live UIs work. Disable buffering for SSE; pass `Upgrade` / `Connection` headers for WebSockets; long timeouts.
>
> Use it for streaming chat APIs ([40](40_fastapi.md)), Streamlit / Chainlit / Gradio ([39](39_ai-ui.md)).

```nginx
location /chat {                               # SSE / streamed responses
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;                       # send tokens as they arrive
    proxy_cache off;
    proxy_read_timeout 3600s;
}

location / {                                   # Streamlit (uses WebSockets)
    proxy_pass http://127.0.0.1:8501;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400s;
}
```

Your app can also send the header `X-Accel-Buffering: no` to disable buffering per response.

## 8. Several Apps on One Server

> Routing by subdomain or path. One server block per subdomain, or several `location` blocks in one server.
>
> Use it for API + UI + docs on one VM.

```nginx
server {
    listen 443 ssl;
    server_name example.com;
    # ssl_certificate lines added by certbot

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;     # trailing slash: /api/items -> /items
    }
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 9. Basic Auth (Protect Ollama or Admin UIs)

> Requiring a username and password in front of an app that has no auth of its own. Create a password file with `htpasswd`; add `auth_basic` to the location. Always combine with HTTPS.
>
> Use it for exposing Ollama, admin dashboards, internal demos. (For Ollama from your laptop, an SSH tunnel is simpler, [49](49_azure-vm-ollama.md).).

```bash
sudo apt install -y apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd harman        # prompts for password
```

```nginx
server {
    listen 443 ssl;
    server_name llm.example.com;

    location / {
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:11434;
        proxy_buffering off;
        proxy_read_timeout 600s;
    }
}
```

## 10. Rate Limiting and Upload Size

> Protecting the backend from floods and huge uploads. `limit_req_zone` defines a limit per client IP; `limit_req` applies it; `client_max_body_size` caps uploads.
>
> Use it for public APIs, expensive LLM endpoints.

```nginx
# in the http context (e.g. top of the site file, outside server {})
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    client_max_body_size 25M;                  # allow PDF uploads up to 25 MB
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000/;
    }
}
```

Per-user / per-API-key limits belong in the app (Redis, [42](42_redis-queues.md)).

## 11. Load Balancing

> Spreading requests across several app instances. An `upstream` block lists backends; `proxy_pass` to the upstream name.
>
> Use it for several uvicorn / container instances on one or more servers.

```nginx
upstream api_backend {
    least_conn;                           # send to the least busy instance
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://api_backend;
    }
}
```

## 12. Run Your App as a systemd Service

> Keeping your FastAPI app running after logout, crashes and reboots. A unit file describing how to start the app; systemd supervises it.
>
> Use it in any app on a Linux VM without Docker.

```ini
# /etc/systemd/system/api.service
[Unit]
Description=Sales API (FastAPI)
After=network.target

[Service]
User=azureuser
WorkingDirectory=/home/azureuser/sales-api
EnvironmentFile=/home/azureuser/sales-api/.env
ExecStart=/home/azureuser/sales-api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2 --proxy-headers
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now api
systemctl status api
journalctl -u api -f
```

## 13. Firewall

> Allowing only the ports you need. `ufw` on the server, plus NSG rules in Azure ([49](49_azure-vm-ollama.md)).
>
> Use it in every internet-facing server.

```bash
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"          # 80 and 443
sudo ufw enable
sudo ufw status
```

Apps listen on `127.0.0.1` so only Nginx can reach them.

## 14. Caddy (Simpler Alternative)

> A web server that gets and renews HTTPS certificates automatically with almost no config. A tiny `Caddyfile`; Caddy handles TLS for any domain listed.
>
> Use it for small projects where you want HTTPS with minimal setup.

```text
# /etc/caddy/Caddyfile
api.example.com {
    reverse_proxy 127.0.0.1:8000
}
chat.example.com {
    reverse_proxy 127.0.0.1:8501
}
```

```bash
sudo systemctl reload caddy
```

## 15. Logs and Debugging

> Finding out why a request fails. Nginx access / error logs, backend logs, curl from the server itself.
>
> Use it for 502s, timeouts, redirects gone wrong.

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
curl -I http://127.0.0.1:8000              # is the backend up (from the server)?
curl -vk https://api.example.com/          # full TLS / header details from outside
```

## 16. Troubleshooting

| Problem | Fix |
|---|---|
| `502 Bad Gateway` | Backend not running / wrong port; `systemctl status api`; `curl 127.0.0.1:8000` |
| `504 Gateway Timeout` | Slow LLM responses; raise `proxy_read_timeout`; move long work to background jobs ([42](42_redis-queues.md)) |
| Streaming arrives all at once | `proxy_buffering off;` and HTTP/1.1 for that location |
| Streamlit / Chainlit stuck loading | WebSocket headers (`Upgrade`, `Connection "upgrade"`) missing |
| certbot fails | DNS not pointing to the server yet; port 80 blocked by firewall / NSG |
| `nginx: [emerg] ...` on reload | Syntax error; run `sudo nginx -t` and fix the line it shows |
| `413 Request Entity Too Large` | Raise `client_max_body_size` |
| App sees 127.0.0.1 as client IP / wrong scheme | Forward headers + uvicorn `--proxy-headers` |
| Redirect loops | Both app and Nginx redirect to HTTPS; let Nginx handle redirects |
| Certificate expired | `sudo certbot renew`; check the renewal timer `systemctl list-timers` |

## 17. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Reverse proxy

Proxy `api.example.com` to a FastAPI app on `127.0.0.1:8000`.

<details markdown="1">
<summary>Solution</summary>

```nginx
server {
    listen 80;
    server_name api.example.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

</details>

### Exercise 2: HTTPS

Add a free certificate and an automatic HTTP -> HTTPS redirect.

<details markdown="1">
<summary>Solution</summary>

```bash
sudo certbot --nginx -d api.example.com
sudo certbot renew --dry-run
```

</details>

### Exercise 3: Debug a 502

The site shows `502 Bad Gateway`. What do you check?

<details markdown="1">
<summary>Solution</summary>

1. Is the app running? `systemctl status api` / `docker ps`. 2. Does it answer locally? `curl 127.0.0.1:8000/health`. 3. Right port in `proxy_pass`? 4. `sudo tail -f /var/log/nginx/error.log` for the exact reason.

</details>

---

<!-- nav:start -->
**Previous:** [44 - GitHub Actions (CI/CD)](44_github-actions.md) | **Index:** [All guides](../README.md) | **Next:** [46 - Kubernetes](46_kubernetes.md)
<!-- nav:end -->
