# 43 - Nginx, Reverse Proxy and HTTPS

Quick reference for putting apps (FastAPI, Streamlit, Ollama) behind Nginx on a Linux server: reverse proxy, HTTPS with Let's Encrypt, streaming, WebSockets, basic auth, rate limiting and running apps as services.

## Introduction

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

**Where it fits:** fronts [39 - FastAPI](39_fastapi.md), [38 - AI UIs](38_ai-ui.md) and [35 - Local LLMs](35_local-llms.md) on a Linux VM ([03 - Linux](03_linux.md), [47 - Azure VM](47_azure-vm-ollama.md)); HTTP concepts in [08](08_http-apis.md); managed alternatives in [46 - Azure](46_azure.md) (Container Apps / App Service give HTTPS automatically).

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

---

## 0. Flags and Parameters

> - **What:** The nginx / certbot commands and the most common config directives.
> - **How:** Commands manage the service; directives inside config blocks define behaviour.
> - **When to use:** You see `proxy_pass http://127.0.0.1:8000;` or `certbot --nginx -d api.example.com` and want to know what each part does.

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

> - **What:** Deciding between managing Nginx yourself and using a managed platform.
> - **How:** Managed platforms (Azure Container Apps, App Service, Hugging Face Spaces, Cloud Run) already provide HTTPS, domains and scaling.
> - **When to use:** Nginx is for your own VM / server; skip it when a platform handles the edge for you.

| Situation | Use |
|---|---|
| App on a single Linux VM (e.g. Ollama + FastAPI on a GPU VM) | Nginx or Caddy |
| Docker Compose stack on a VM | Nginx / Caddy / Traefik container |
| Azure Container Apps / App Service | Built-in HTTPS; no Nginx needed |
| Kubernetes | Ingress controller (often Nginx-based) ([44](44_kubernetes.md)) |

## 2. Install Nginx

> - **What:** Installing and starting Nginx on Ubuntu.
> - **How:** `apt install`, enable the service, check the welcome page.
> - **When to use:** Fresh server setup.

```bash
sudo apt update && sudo apt install -y nginx
sudo systemctl enable --now nginx
curl -I http://localhost                  # HTTP/1.1 200 OK, Server: nginx
```

## 3. Config File Layout

> - **What:** Where Nginx configuration lives (Ubuntu / Debian).
> - **How:** One file per site in `sites-available`, enabled by a symlink in `sites-enabled`.
> - **When to use:** Adding or editing sites.

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

> - **What:** Forwarding requests from port 80 to your app on port 8000.
> - **How:** A `server` block with `proxy_pass` and forwarding headers.
> - **When to use:** Serving any web app / API.

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

> - **What:** Pointing a domain name at your server.
> - **How:** At your DNS provider, create an **A record** `api.example.com -> <server public IP>`; wait for it to propagate.
> - **When to use:** Before requesting certificates.

```bash
nslookup api.example.com             # should return your server IP
```

Azure VMs: give the public IP a DNS label to get a free name like `myvm.swedencentral.cloudapp.azure.com`.

## 6. HTTPS with Let's Encrypt (certbot)

> - **What:** Free, auto-renewing TLS certificates.
> - **How:** certbot proves you control the domain (via port 80), gets a certificate, edits the Nginx config for HTTPS and sets up renewal.
> - **When to use:** Every public site.

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.example.com         # answer prompts; choose redirect HTTP -> HTTPS
sudo certbot renew --dry-run                    # test automatic renewal (runs via systemd timer)
sudo certbot certificates                       # list certificates and expiry
```

After certbot, your server block has `listen 443 ssl;`, `ssl_certificate` lines and an HTTP -> HTTPS redirect. Port 80 must be reachable for issuance and renewal.

## 7. Streaming (SSE) and WebSockets

> - **What:** Proxy settings so LLM token streams and live UIs work.
> - **How:** Disable buffering for SSE; pass `Upgrade` / `Connection` headers for WebSockets; long timeouts.
> - **When to use:** Streaming chat APIs ([39](39_fastapi.md)), Streamlit / Chainlit / Gradio ([38](38_ai-ui.md)).

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

> - **What:** Routing by subdomain or path.
> - **How:** One server block per subdomain, or several `location` blocks in one server.
> - **When to use:** API + UI + docs on one VM.

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

> - **What:** Requiring a username and password in front of an app that has no auth of its own.
> - **How:** Create a password file with `htpasswd`; add `auth_basic` to the location. Always combine with HTTPS.
> - **When to use:** Exposing Ollama, admin dashboards, internal demos. (For Ollama from your laptop, an SSH tunnel is simpler, [47](47_azure-vm-ollama.md).)

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

> - **What:** Protecting the backend from floods and huge uploads.
> - **How:** `limit_req_zone` defines a limit per client IP; `limit_req` applies it; `client_max_body_size` caps uploads.
> - **When to use:** Public APIs, expensive LLM endpoints.

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

Per-user / per-API-key limits belong in the app (Redis, [40](40_redis-queues.md)).

## 11. Load Balancing

> - **What:** Spreading requests across several app instances.
> - **How:** An `upstream` block lists backends; `proxy_pass` to the upstream name.
> - **When to use:** Several uvicorn / container instances on one or more servers.

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

> - **What:** Keeping your FastAPI app running after logout, crashes and reboots.
> - **How:** A unit file describing how to start the app; systemd supervises it.
> - **When to use:** Any app on a Linux VM without Docker.

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

> - **What:** Allowing only the ports you need.
> - **How:** `ufw` on the server, plus NSG rules in Azure ([47](47_azure-vm-ollama.md)).
> - **When to use:** Every internet-facing server.

```bash
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"          # 80 and 443
sudo ufw enable
sudo ufw status
```

Apps listen on `127.0.0.1` so only Nginx can reach them.

## 14. Caddy (Simpler Alternative)

> - **What:** A web server that gets and renews HTTPS certificates automatically with almost no config.
> - **How:** A tiny `Caddyfile`; Caddy handles TLS for any domain listed.
> - **When to use:** Small projects where you want HTTPS with minimal setup.

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

> - **What:** Finding out why a request fails.
> - **How:** Nginx access / error logs, backend logs, curl from the server itself.
> - **When to use:** 502s, timeouts, redirects gone wrong.

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
| `504 Gateway Timeout` | Slow LLM responses; raise `proxy_read_timeout`; move long work to background jobs ([40](40_redis-queues.md)) |
| Streaming arrives all at once | `proxy_buffering off;` and HTTP/1.1 for that location |
| Streamlit / Chainlit stuck loading | WebSocket headers (`Upgrade`, `Connection "upgrade"`) missing |
| certbot fails | DNS not pointing to the server yet; port 80 blocked by firewall / NSG |
| `nginx: [emerg] ...` on reload | Syntax error; run `sudo nginx -t` and fix the line it shows |
| `413 Request Entity Too Large` | Raise `client_max_body_size` |
| App sees 127.0.0.1 as client IP / wrong scheme | Forward headers + uvicorn `--proxy-headers` |
| Redirect loops | Both app and Nginx redirect to HTTPS; let Nginx handle redirects |
| Certificate expired | `sudo certbot renew`; check the renewal timer `systemctl list-timers` |
