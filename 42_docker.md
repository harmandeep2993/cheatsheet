# 42 - Docker

Quick reference for building and running containers with Docker and Docker Compose.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Docker?

Docker packages an application together with everything it needs to run (Python version, libraries, system tools, settings) into an **image**. You then start that image as a **container**: an isolated, lightweight process that runs the same way on your laptop, a colleague's laptop, a test server or the cloud. Unlike a virtual machine, a container shares the host's operating system kernel, so it starts in seconds and uses little memory.

### Why use it?

- **"Works on my machine" solved**: the same image runs identically everywhere.
- **Easy setup**: run PostgreSQL, Redis or Ollama with one command, no installation.
- **Isolation**: each app has its own dependencies; no conflicts between projects.
- **Simple deployment**: build once, push to a registry, run on any server or cloud service.
- **Multi-service apps**: Docker Compose starts API + database + cache together.
- **Clean machine**: remove a container and nothing is left behind.

### Container vs virtual machine

| | Container | Virtual machine |
|---|---|---|
| Contains | App + libraries | Full operating system + app |
| Start time | Seconds | Minutes |
| Size | MBs to a few GB | Many GB |
| Isolation | Process level (shares host kernel) | Full hardware virtualisation |

### Key terms

| Term | Meaning |
|---|---|
| Image | Read-only package / template of an app |
| Container | Running instance of an image |
| Dockerfile | Recipe that builds an image |
| Layer | One cached step of an image build |
| Registry | Storage for images (Docker Hub, Azure Container Registry) |
| Volume | Persistent storage that survives container removal |
| Port mapping | Connect a host port to a container port (`-p 8000:8000`) |
| Compose | Tool to run several containers from one YAML file |

**Where it fits:** packages apps from [39 - FastAPI](39_fastapi.md); uses [03 - Linux](03_linux.md) inside containers; runs on VMs like [48 - Azure VM](48_azure-vm-ollama.md). Built and pushed by [43 - GitHub Actions](43_github-actions.md); orchestrated by [45 - Kubernetes](45_kubernetes.md) or [47 - Azure](47_azure.md) Container Apps; fronted by [44 - Nginx](44_nginx-https.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Docker documentation | https://docs.docker.com/ |
| Dockerfile reference | https://docs.docker.com/reference/dockerfile/ |
| Docker Compose | https://docs.docker.com/compose/ |
| Docker Hub | https://hub.docker.com/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Concepts](#1-concepts)
2. [Install and Check](#2-install-and-check)
3. [Images](#3-images)
4. [Run a Container](#4-run-a-container)
5. [Manage Containers](#5-manage-containers)
6. [Inside a Container](#6-inside-a-container)
7. [Logs and Monitoring](#7-logs-and-monitoring)
8. [Dockerfile](#8-dockerfile)
9. [Example: Python App Dockerfile](#9-example-python-app-dockerfile)
10. [.dockerignore](#10-dockerignore)
11. [Build Images](#11-build-images)
12. [Volumes and Bind Mounts](#12-volumes-and-bind-mounts)
13. [Networks](#13-networks)
14. [Environment Variables](#14-environment-variables)
15. [Docker Compose](#15-docker-compose)
16. [Compose Commands](#16-compose-commands)
17. [Registry (Docker Hub, ACR)](#17-registry-docker-hub-acr)
18. [Cleanup](#18-cleanup)
19. [Useful Ready-Made Containers](#19-useful-ready-made-containers)
20. [Troubleshooting](#20-troubleshooting)
21. [Try It](#21-try-it)

---

## 0. Flags and Parameters

> - **What:** The meaning of every flag and value used in the Docker commands below.
> - **How:** A command is split into program, action, flags and target; tables list every flag.
> - **When to use:** You see a command like `docker run -d -p 8080:80 --name web nginx` and want to know what each part does.

### How a command is built

```text
docker  run  -d  -p 8080:80  --name web  nginx
|       |    |   |          |           |
|       |    |   |          |           +-- image to start a container from
|       |    |   |          +-------------- --name: call the container "web"
|       |    |   +------------------------- -p host:container: laptop 8080 -> container 80
|       |    +----------------------------- -d: detached, run in the background
|       +---------------------------------- action: create and start a new container
+------------------------------------------ program
```

- Short flags can be combined: `-it` = `-i -t`.
- In `host:container` pairs (ports, volumes) the **left side is your machine**, the right side is inside the container.
- Show every flag of any command: `docker run --help`.

### docker run

| Flag | Long form | Meaning | Example |
|---|---|---|---|
| `-d` | `--detach` | Run in the background and return the prompt | `docker run -d nginx` |
| `-i` | `--interactive` | Keep input (STDIN) open so you can type | `-i` |
| `-t` | `--tty` | Give the container a terminal (prompt, colours) | `-t` |
| `-it` | | Both: an interactive shell | `docker run -it python:3.12 bash` |
| `--rm` | | Delete the container automatically when it stops | `--rm` |
| `--name` | | Name to use instead of a random one | `--name web` |
| `-p` | `--publish` | Publish a port `host:container` | `-p 8000:8000` |
| `-e` | `--env` | Set an environment variable | `-e APP_ENV=prod` |
| `--env-file` | | Load environment variables from a file | `--env-file .env` |
| `-v` | `--volume` | Mount a volume or folder `source:target[:ro]`; `:ro` = read-only | `-v mydata:/data` |
| `--network` | | Attach to a network | `--network mynet` |
| `--restart` | | Restart policy: `no`, `always`, `unless-stopped`, `on-failure` | `--restart unless-stopped` |
| `--memory` | `-m` | Memory limit | `--memory 512m` |
| `--cpus` | | CPU limit (number of cores) | `--cpus 1` |
| `--gpus` | | Give access to GPUs | `--gpus all` |
| `${PWD}` | | Current folder (PowerShell and Bash) | `-v ${PWD}:/app` |

### Other docker commands

| Command | Flag | Meaning |
|---|---|---|
| `docker ps` | `-a` (`--all`) | Include stopped containers |
| `docker rm` | `-f` (`--force`) | Stop the container first if it is running |
| `docker exec` | `-it` | Interactive terminal inside a running container |
| `docker logs` | `-f` (`--follow`) | Keep printing new log lines |
| `docker logs` | `--tail 50` | Only the last 50 lines |
| `docker logs` | `--since 10m` | Only logs from the last 10 minutes (`s`, `m`, `h`) |
| `docker build` | `-t name:tag` | Name and tag for the new image |
| `docker build` | `-f path` | Use a Dockerfile at another path |
| `docker build` | `.` (last argument) | Build context: the folder `COPY` can read from |
| `docker build` | `--no-cache` | Rebuild every layer, ignore the cache |
| `docker build` | `--build-arg K=V` | Value for an `ARG` in the Dockerfile |
| `docker build` | `--platform linux/amd64` | Build for another CPU architecture |
| `docker image prune` | `-a` (`--all`) | Remove all unused images, not only untagged ones |
| `docker system prune` | `--volumes` | Also remove unused volumes (data is lost) |

### docker compose

| Command | Flag | Meaning |
|---|---|---|
| `up` | `-d` | Start in the background |
| `up` | `--build` | Rebuild images before starting |
| `down` | `-v` | Also delete the volumes declared in the file |
| `logs` | `-f` | Follow logs |
| `logs` / `exec` / `restart` | `<service>` | Act on one service only, e.g. `api` |

## 1. Concepts

> - **What:** The core Docker ideas: image, container, Dockerfile, registry.
> - **How:** Build an image from a Dockerfile, run it as a container, share it through a registry.
> - **When to use:** Read once; it explains the words used in every command below.

| Term | Meaning |
|---|---|
| **Image** | Read-only template (app + dependencies). Built from a Dockerfile. |
| **Container** | A running instance of an image. Many containers can run from one image. |
| **Dockerfile** | Recipe to build an image. |
| **Registry** | Where images are stored (Docker Hub, Azure Container Registry, GHCR). |
| **Tag** | Version label of an image: `python:3.12-slim`, `myapp:1.0`, `latest`. |
| **Volume** | Storage that survives when the container is deleted. |
| **Port mapping** | `-p 8000:80` = laptop port 8000 -> container port 80. |
| **Compose** | Run several containers together from one `compose.yaml` file. |

```text
Dockerfile --(docker build)--> Image --(docker run)--> Container
                                 |
                          (docker push/pull)
                                 |
                              Registry
```

## 2. Install and Check

> - **What:** Installing Docker and checking it works.
> - **How:** Docker Desktop on Windows / Mac, Docker Engine on Linux; `docker run hello-world` to test.
> - **When to use:** New machine or VM, before any other Docker command.

- Windows / Mac: install **Docker Desktop** (`winget install -e --id Docker.DockerDesktop`), uses WSL 2 on Windows.
- Ubuntu: `curl -fsSL https://get.docker.com | sh`, then `sudo usermod -aG docker $USER` and log out / in.

```bash
docker --version                    # client version
docker compose version              # compose version
docker info                         # engine details (fails if engine not running)
docker run hello-world              # test everything works
```

## 3. Images

> - **What:** Listing, downloading, tagging and deleting images.
> - **How:** `docker pull` downloads from a registry; `docker images` lists local ones.
> - **When to use:** Getting a base image (python, postgres), checking what you have, freeing space.

```bash
docker images                       # list local images (also: docker image ls)
docker pull python:3.12-slim        # download image
docker search nginx                 # search Docker Hub
docker image inspect python:3.12-slim   # details
docker history myapp:1.0            # layers and sizes
docker rmi myapp:1.0                # delete image
docker tag myapp:1.0 myapp:latest   # add another tag
```

Image name format: `[registry/][user/]name[:tag]`, for example `docker.io/library/python:3.12-slim`. No tag = `latest`.

## 4. Run a Container

> - **What:** Starting a container from an image.
> - **How:** `docker run [options] image`; options set ports, env vars, volumes, name, restart.
> - **When to use:** Running an app, a database or a tool without installing it on your machine.

```bash
docker run nginx                                # run in foreground (Ctrl+C stops)
docker run -d nginx                             # detached (background)
docker run -d --name web nginx                  # give it a name
docker run -d -p 8080:80 nginx                  # laptop 8080 -> container 80 (open http://localhost:8080)
docker run -it python:3.12 bash                 # interactive shell
docker run --rm -it python:3.12 python          # delete container when it exits
docker run -d -e APP_ENV=prod myapp             # environment variable
docker run -d --env-file .env myapp             # variables from file
docker run -d -v mydata:/data myapp             # named volume
docker run -d -v ${PWD}:/app myapp              # bind mount current folder (PowerShell / Bash)
docker run -d --restart unless-stopped myapp    # restart automatically
docker run -d --memory 512m --cpus 1 myapp      # resource limits
docker run -d --gpus all myapp                  # use NVIDIA GPU
```

| Flag | Meaning |
|---|---|
| `-d` | detached (background) |
| `-it` | interactive terminal |
| `--rm` | remove container after it stops |
| `--name` | container name |
| `-p host:container` | publish port |
| `-e KEY=value` | environment variable |
| `-v source:target` | volume or bind mount |
| `--network` | attach to network |
| `--restart` | `no`, `always`, `unless-stopped`, `on-failure` |

## 5. Manage Containers

> - **What:** Listing, stopping, starting and removing containers.
> - **How:** `docker ps`, `stop`, `start`, `rm` by name or ID.
> - **When to use:** Day-to-day control of what is running.

```bash
docker ps                           # running containers
docker ps -a                        # all, including stopped
docker stop web                     # graceful stop
docker start web                    # start stopped container
docker restart web
docker kill web                     # force stop
docker rm web                       # delete stopped container
docker rm -f web                    # stop and delete
docker rename web web-old
docker inspect web                  # full JSON details (IP, mounts, env)
docker port web                     # port mappings
```

You can use the name or the first few characters of the container ID.

## 6. Inside a Container

> - **What:** Running commands and copying files inside a running container.
> - **How:** `docker exec -it <name> bash` opens a shell; `docker cp` copies files.
> - **When to use:** Debugging: checking files, env vars or running a quick command inside the app.

```bash
docker exec -it web bash            # open shell in running container
docker exec -it web sh              # if bash is missing (alpine, slim images)
docker exec web ls /app             # run one command
docker cp web:/app/log.txt .        # copy from container
docker cp ./config.json web:/app/   # copy into container
```

Type `exit` to leave the shell (the container keeps running).

## 7. Logs and Monitoring

> - **What:** Seeing container output and resource usage.
> - **How:** `docker logs` shows stdout / stderr; `docker stats` shows CPU and memory.
> - **When to use:** A container exits or misbehaves; the logs usually tell you why.

```bash
docker logs web                     # all logs
docker logs -f web                  # follow (Ctrl+C to stop following)
docker logs --tail 50 web           # last 50 lines
docker logs --since 10m web         # last 10 minutes
docker stats                        # live CPU / memory per container
docker top web                      # processes in container
docker events                       # live engine events
```

## 8. Dockerfile

> - **What:** The instructions used to build an image.
> - **How:** Each line is an instruction; each instruction adds a layer.
> - **When to use:** Writing or reading a Dockerfile.

| Instruction | Purpose |
|---|---|
| `FROM image:tag` | Base image (always first) |
| `WORKDIR /app` | Working folder (created if missing) |
| `COPY src dest` | Copy files from build folder into image |
| `ADD src dest` | Like COPY, also extracts archives / URLs (prefer COPY) |
| `RUN command` | Run at **build** time (install packages) |
| `ENV KEY=value` | Environment variable |
| `ARG NAME=default` | Build-time variable (`--build-arg`) |
| `EXPOSE 8000` | Documents the port (does not publish it) |
| `USER appuser` | Run as non-root user |
| `CMD ["python", "app.py"]` | Default command at **run** time (can be overridden) |
| `ENTRYPOINT ["python"]` | Fixed command; `CMD` becomes its default arguments |
| `HEALTHCHECK CMD curl -f http://localhost:8000/ \|\| exit 1` | Health status |

## 9. Example: Python App Dockerfile

> - **What:** A complete, production-style Dockerfile for a Python web app.
> - **How:** Slim base, dependencies before code (cache), non-root user, CMD with uvicorn.
> - **When to use:** Containerising a FastAPI / Flask project; copy and adjust.

```dockerfile
FROM python:3.12-slim

# Do not write .pyc files; show logs immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first so this layer is cached when only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as non-root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t myapp:1.0 .
docker run -d -p 8000:8000 --env-file .env --name myapp myapp:1.0
```

Inside a container the app must listen on `0.0.0.0`, not `127.0.0.1`, or the port mapping will not reach it.

## 10. .dockerignore

> - **What:** Files excluded from the build.
> - **How:** Patterns in `.dockerignore`, like `.gitignore` for Docker builds.
> - **When to use:** Every project; keeps images small and secrets (`.env`) out of them.

Keeps files out of the build (smaller, faster, no secrets in the image):

```text
.git
.venv
__pycache__/
*.pyc
.env
node_modules/
data/
*.log
```

## 11. Build Images

> - **What:** Creating an image from a Dockerfile.
> - **How:** `docker build -t name:tag .` where `.` is the build context folder.
> - **When to use:** After changing the Dockerfile or code, before running or pushing the image.

```bash
docker build -t myapp:1.0 .                         # build from Dockerfile in current folder
docker build -t myapp:1.0 -f docker/Dockerfile .    # other Dockerfile path
docker build --no-cache -t myapp:1.0 .              # ignore cache
docker build --build-arg VERSION=2 -t myapp .       # pass ARG
docker build --platform linux/amd64 -t myapp .      # build for another CPU (e.g. Mac M1 -> Azure)
```

The `.` at the end is the **build context**: the folder whose files `COPY` can see.

## 12. Volumes and Bind Mounts

> - **What:** Keeping data outside the container's life cycle.
> - **How:** Named volumes managed by Docker, or bind mounts of a host folder.
> - **When to use:** Databases (volume) so data survives restarts; live code editing (bind mount).

| Type | Syntax | Use for |
|---|---|---|
| Named volume | `-v mydata:/data` | Databases, persistent data managed by Docker |
| Bind mount | `-v ${PWD}/src:/app/src` | Live code editing during development |
| Read-only | `-v ${PWD}/config:/config:ro` | Config files |

```bash
docker volume ls                    # list volumes
docker volume create mydata
docker volume inspect mydata        # where it is stored
docker volume rm mydata
docker volume prune                 # delete unused volumes (data is lost)
```

Without a volume, data written inside the container is lost when the container is removed.

## 13. Networks

> - **What:** Letting containers talk to each other.
> - **How:** Containers on the same user-defined network reach each other by name.
> - **When to use:** App + database in separate containers (Compose does this automatically).

```bash
docker network ls
docker network create mynet
docker run -d --name db --network mynet postgres:16
docker run -d --name api --network mynet myapp       # api reaches db at host "db"
docker network inspect mynet
docker network connect mynet web
docker network rm mynet
```

- Containers on the same user network find each other **by container name**.
- From a container to a service on your laptop: `host.docker.internal` (Docker Desktop).
- Compose creates a network automatically; services use their service name as host.

## 14. Environment Variables

> - **What:** Configuring a container at run time.
> - **How:** `-e KEY=value` or `--env-file`; the app reads them from the environment.
> - **When to use:** Same image in dev and prod with different settings; passing secrets safely.

```bash
docker run -e DB_HOST=db -e DB_PORT=5432 myapp
docker run --env-file .env myapp
docker exec web env                 # show variables inside container
```

Never bake secrets into the image (`ENV API_KEY=...` or `COPY .env`). Pass them at run time.

## 15. Docker Compose

> - **What:** Describing a multi-container app in one file.
> - **How:** `compose.yaml` lists services, ports, volumes, env and dependencies.
> - **When to use:** Any project with more than one container (API + database + cache).

`compose.yaml` (or `docker-compose.yml`):

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      DB_HOST: db
    volumes:
      - ./src:/app/src
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: change-me
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  pgdata:
```

## 16. Compose Commands

> - **What:** Starting, stopping and inspecting a Compose app.
> - **How:** `docker compose up / down / logs / exec` act on all services in the file.
> - **When to use:** Daily development with a multi-container setup.

```bash
docker compose up                   # start all (foreground)
docker compose up -d                # start in background
docker compose up -d --build        # rebuild images then start
docker compose ps                   # status
docker compose logs -f              # all logs
docker compose logs -f api          # one service
docker compose exec api bash        # shell in a service
docker compose restart api
docker compose stop                 # stop, keep containers
docker compose down                 # stop and remove containers + network
docker compose down -v              # also delete volumes (data lost)
docker compose pull                 # update images
docker compose config               # show final merged config (check for errors)
```

Old syntax `docker-compose` (with hyphen) = Compose v1; use `docker compose`.

## 17. Registry (Docker Hub, ACR)

> - **What:** Uploading and downloading images to / from a registry.
> - **How:** Tag the image with the registry address, `docker login`, then `docker push`.
> - **When to use:** Deploying to a server or cloud service, sharing images with a team.

```bash
# Docker Hub
docker login
docker tag myapp:1.0 <username>/myapp:1.0
docker push <username>/myapp:1.0
docker pull <username>/myapp:1.0

# Azure Container Registry
az acr login --name <registry>
docker tag myapp:1.0 <registry>.azurecr.io/myapp:1.0
docker push <registry>.azurecr.io/myapp:1.0

docker logout
```

## 18. Cleanup

> - **What:** Freeing disk space used by Docker.
> - **How:** `prune` commands remove stopped containers, unused images, volumes and cache.
> - **When to use:** Disk is full, or Docker Desktop uses tens of GB.

```bash
docker container prune              # remove stopped containers
docker image prune                  # remove dangling (untagged) images
docker image prune -a               # remove all unused images
docker volume prune                 # remove unused volumes (data lost)
docker network prune                # remove unused networks
docker builder prune                # clear build cache
docker system prune                 # all of the above except volumes
docker system prune -a --volumes    # everything unused (careful)
docker system df                    # disk usage by Docker
```

## 19. Useful Ready-Made Containers

> - **What:** One-line commands for popular services.
> - **How:** Official images with the right ports, env vars and volumes preset.
> - **When to use:** You need a database, cache or Ollama quickly for development.

```bash
docker run -d --name pg -p 5432:5432 -e POSTGRES_PASSWORD=pass -v pgdata:/var/lib/postgresql/data postgres:16
docker run -d --name redis -p 6379:6379 redis:7
docker run -d --name mongo -p 27017:27017 mongo:7
docker run -d --name web -p 8080:80 -v ${PWD}/site:/usr/share/nginx/html:ro nginx
docker run -d --name ollama -p 11434:11434 -v ollama:/root/.ollama ollama/ollama
docker run -it --rm -p 8888:8888 jupyter/scipy-notebook
```

## 20. Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot connect to the Docker daemon` / `error during connect` | Start Docker Desktop (Windows / Mac) or `sudo systemctl start docker` (Linux) |
| `permission denied ... docker.sock` (Linux) | `sudo usermod -aG docker $USER`, then log out and in |
| `port is already allocated` | Another container or app uses the port; change `-p 8001:8000` or stop it |
| `Conflict. The container name "/web" is already in use` | `docker rm -f web` or use another name |
| Container exits immediately | `docker logs <name>`; the main process ended or crashed |
| App not reachable on `localhost:port` | Missing `-p`, or app listens on `127.0.0.1` instead of `0.0.0.0` |
| Code changes not visible | Rebuild (`docker build` / `compose up --build`) or use a bind mount |
| `COPY failed: file not found` | File is outside the build context or listed in `.dockerignore` |
| Build is slow every time | Copy `requirements.txt` and install BEFORE `COPY . .` |
| `exec format error` | Image built for another CPU; use `--platform linux/amd64` |
| `no space left on device` | `docker system df`, then `docker system prune` |
| Bind mount path fails in PowerShell | Use `${PWD}` (not `$(pwd)`), or the full path `D:\Projects\app:/app` |

## 21. Try It

> - **What:** Short exercises to practise this guide.
> - **How:** Try each task yourself first, then open the solution.
> - **When to use:** Right after reading the guide, or later as a quick self-test.

### Exercise 1: Build and run the capstone

Build the chatbot image from `examples/` and call its health endpoint.

<details markdown="1">
<summary>Solution</summary>

```bash
cd examples
docker build -f docs_chatbot/Dockerfile -t docs-chatbot .
docker run -d --name bot -p 8000:8000 -e ANTHROPIC_API_KEY docs-chatbot
curl http://127.0.0.1:8000/health
docker logs -f bot
```

</details>

### Exercise 2: Compose

Write a `compose.yaml` with an `api` built from the current folder and a `redis` service.

<details markdown="1">
<summary>Solution</summary>

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      REDIS_URL: redis://redis:6379/0
    depends_on: [redis]
  redis:
    image: redis:7
```

</details>

### Exercise 3: Free disk space

Docker uses 40 GB. Find out where and clean safely.

<details markdown="1">
<summary>Solution</summary>

```bash
docker system df
docker image prune -a        # unused images
docker builder prune         # build cache
```

Only run `docker volume prune` if you are sure the data is not needed.

</details>
