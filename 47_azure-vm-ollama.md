# 47 - Azure VM + Linux + Ollama

Quick reference for running Ollama on an Azure Ubuntu VM and using it from a local app via SSH tunnel.

## Introduction

### What is this setup?

This guide combines three things:

- **Azure** is Microsoft's cloud platform. A **Virtual Machine (VM)** is a computer in Azure's data centre that you rent by the hour and control remotely.
- **Linux (Ubuntu)** is the operating system on that VM; you manage it over **SSH** from your laptop.
- **Ollama** is a tool that downloads and runs open-source large language models (LLMs such as Qwen, Llama, Mistral) locally and serves them through an HTTP API on port 11434.

Together: the heavy AI model runs on a powerful (optionally GPU) cloud machine, and your local app talks to it securely through an **SSH tunnel**, as if the model were running on your laptop.

### Why use it?

- **More power than a laptop**: bigger CPUs, more RAM, or GPUs for larger models.
- **Private**: the model runs on your own VM; no prompts go to a third-party AI service.
- **Pay per use**: start the VM when you work, deallocate it afterwards to stop compute costs.
- **Secure by design**: SSH keys, firewall (NSG) rules limited to your IP, and no public LLM port.
- **Real-world skills**: cloud CLI, Linux administration, networking and LLM serving.

### Architecture

```text
Laptop                                         Azure VM (Ubuntu)
+----------------------+   SSH tunnel (22)    +------------------------+
| app.py               | ===================> | Ollama :11434          |
| OLLAMA_HOST=         |   localhost:11435    |  - qwen3:4b (chat)     |
|   localhost:11435    |   -> VM :11434       |  - bge-m3 (embeddings) |
+----------------------+                      +------------------------+
         NSG firewall: only port 22, only from your IP
```

### Key terms

| Term | Meaning |
|---|---|
| Resource group | Folder in Azure that holds related resources |
| VM size | CPU / RAM / GPU combination you rent (e.g. Standard_D2s_v5) |
| Deallocate | Stop the VM and its compute billing (disk still billed) |
| NSG | Network Security Group: firewall rules for the VM |
| SSH key | Private / public key pair used instead of a password |
| SSH tunnel | Forwarding a local port through SSH to a port on the VM |
| LLM | Large language model that generates text |
| Embedding model | Model that turns text into vectors for search / RAG |

**Where it fits:** a hands-on project on top of [46 - Azure](46_azure.md) (concepts and all other services); uses [02 - PowerShell](02_terminal-powershell.md), [03 - Linux](03_linux.md), [10 - venv](10_python-virtual-environment.md) and can be wrapped in an API with [39 - FastAPI](39_fastapi.md).

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Variables (PowerShell)](#1-variables-powershell)
2. [Azure CLI](#2-azure-cli)
3. [VM](#3-vm)
4. [Resources and Cleanup](#4-resources-and-cleanup)
5. [NSG (Security Rules)](#5-nsg-security-rules)
6. [SSH](#6-ssh)
7. [Linux (Inside VM)](#7-linux-inside-vm)
8. [Ollama (Inside VM)](#8-ollama-inside-vm)
9. [GPU Driver (GPU VMs Only)](#9-gpu-driver-gpu-vms-only)
10. [SSH Tunnel (Laptop to VM Ollama)](#10-ssh-tunnel-laptop-to-vm-ollama)
11. [Local App Using VM Ollama](#11-local-app-using-vm-ollama)
12. [Verify Requests Hit the VM](#12-verify-requests-hit-the-vm)
13. [Laptop (PowerShell)](#13-laptop-powershell)
14. [Troubleshooting](#14-troubleshooting)
15. [End of Session](#15-end-of-session)

---

## 0. Flags and Parameters

> - **What:** The meaning of every flag and value used in the commands below.
> - **How:** Each command is split into program, group, action, flags and values; tables list every flag.
> - **When to use:** You see a command like `az vm list -d -o table` and want to know what each part does.

### How a command is built

```text
az   vm   list   -d   -o table
|    |    |      |    |  |
|    |    |      |    |  +-- value given to -o: show the result as a readable table
|    |    |      |    +----- -o (--output): choose the output format
|    |    |      +---------- -d (--show-details): add power state and IP addresses
|    |    +----------------- action: list
|    +---------------------- command group: virtual machines
+--------------------------- program: Azure CLI
```

- **Short flag** = one dash + one letter (`-d`). **Long flag** = two dashes + word (`--show-details`). Both mean the same.
- **Switch** flags are on / off and take no value (`-d`). Other flags need a **value** right after them (`-o table`, `-g $RG`).
- Show every flag of any command: `az vm list --help`.

### Azure CLI (az)

| Flag | Long form | Meaning | Example |
|---|---|---|---|
| `-g` | `--resource-group` | Resource group the resource belongs to | `-g $RG` |
| `-n` | `--name` | Name of the resource (VM, group, rule, provider namespace) | `-n $VM` |
| `-d` | `--show-details` | Also fetch power state, public IP and private IP (makes extra calls, slower) | `az vm list -d` |
| `-o` | `--output` | Output format: `json` (default), `jsonc` (coloured JSON), `table` (readable), `tsv` (plain values, for scripts), `yaml`, `none` | `-o table` |
| `-l` | `--location` | Azure region | `-l swedencentral` |
| `--query` | | Pick fields or filter the JSON result (JMESPath syntax) | `--query publicIps` |
| `--subscription` | | Subscription to use / switch to | `--subscription "<id>"` |
| `--nsg-name` | | Network security group to read or change | `--nsg-name $NSG` |
| `--priority` | | Rule order; lower number is checked first (100 to 4096) | `--priority 1010` |
| `--source-address-prefixes` | | Who may connect: IP or range in CIDR notation; `/32` = exactly one IP | `"$myip/32"` |
| `--destination-port-ranges` | | Port(s) on the VM the rule applies to | `22` |
| `--protocol` | | `Tcp`, `Udp` or `*` (any) | `Tcp` |
| `--access` | | `Allow` or `Deny` | `Allow` |
| `--include-default` | | Also list Azure's built-in default rules | |

Same command, different `-o`:

```text
az vm list -d -o table                          readable table: Name, ResourceGroup, PowerState, PublicIps
az vm list -d                                   full JSON (long, every property)
az vm show -d -g $RG -n $VM --query publicIps -o tsv    only the value, e.g. 20.1.2.3 (good for $IP = ...)
```

### SSH and SCP

| Flag | Meaning | Example |
|---|---|---|
| `-i <file>` | Identity file: the private key used to log in | `-i $KEY` |
| `-N` | Run no remote command; only hold the connection open (used for tunnels) | `ssh -N -L ...` |
| `-L local:host:remote` | Local port forward: laptop port `local` is sent to `host:remote` as seen from the VM | `-L 11435:localhost:11434` |
| `user@ip` | Log in as `user` on machine `ip` | `azureuser@20.1.2.3` |
| `user@ip:path` (scp) | A path on the remote machine; `~` = home folder | `"$USER@${IP}:~"` |
| `-r` (scp) | Recursive: copy a whole folder | `scp -r .\folder ...` |

### Other flags in this guide

| Command | Flag | Meaning |
|---|---|---|
| `winget install` | `-e` (`--exact`) | Match the ID exactly, no fuzzy matching |
| `winget install` | `--id` | Install by package ID instead of by name |
| `icacls` | `/inheritance:r` | Remove permissions inherited from the parent folder |
| `icacls` | `/grant:r "user:(R)"` | Replace existing grants with Read-only for this user |
| `curl` | `-fsSL` | `-f` fail on HTTP errors, `-s` silent, `-S` still show errors, `-L` follow redirects |
| `curl URL \| sh` | `\|` | Pipe: the downloaded install script is run by the shell |
| `apt install` / `upgrade` | `-y` | Answer "yes" to all prompts automatically |
| `cmd1 && cmd2` | `&&` | Run `cmd2` only if `cmd1` succeeded |
| `journalctl` | `-u ollama` | Only logs of this unit (service) |
| `journalctl` | `-f` | Follow: keep printing new log lines |
| `free`, `df` | `-h` | Human-readable sizes (G, M) instead of bytes |
| `ollama run` | `--verbose` | Print speed statistics (tokens per second) after the answer |
| `python` | `-m venv .venv` | `-m` runs a module (`venv`) as a program; `.venv` is the folder to create |
| `pip install` | `-r requirements.txt` | Install every package listed in the file |
| `uvicorn` | `app:app` | `file:object`: the object named `app` inside `app.py` |
| `uvicorn` | `--reload` | Restart automatically when code changes (development only) |
| PowerShell | `` ` `` at line end | Continue the command on the next line |

## 1. Variables (PowerShell)

> - **What:** Session variables used by every command in this guide.
> - **How:** Set them once in PowerShell; later commands reuse `$RG`, `$VM`, `$IP`.
> - **When to use:** Start of every session, so you can copy commands without editing them.

Set once per session, then copy commands as they are.

```powershell
$RG   = "my-resource-group"
$VM   = "my-vm"
$NSG  = "my-vm-nsg"
$KEY  = "$HOME\.ssh\my-vm_key.pem"
$USER = "azureuser"
$IP   = az vm show -d -g $RG -n $VM --query publicIps -o tsv
```

## 2. Azure CLI

> - **What:** Installing and logging in to the Azure command line.
> - **How:** `az login` opens the browser; `az account` selects the subscription.
> - **When to use:** First-time setup, or when commands target the wrong subscription.

```powershell
winget install -e --id Microsoft.AzureCLI   # install (Windows)
brew install azure-cli                      # install (Mac)
az login                                    # log in
az --version                                # check install
az account show -o table                    # current subscription
az account list -o table                    # all subscriptions
az account set --subscription "<name-or-id>"   # switch subscription
```

## 3. VM

> - **What:** Starting, stopping and checking the VM.
> - **How:** `az vm` commands; `deallocate` stops compute billing, `stop` does not.
> - **When to use:** Start before work, deallocate after work to save money.

```powershell
az vm list -d -o table                      # status + IP
az vm start      -g $RG -n $VM              # start
az vm deallocate -g $RG -n $VM              # stop, no compute cost
az vm stop       -g $RG -n $VM              # OS off, STILL billed
az vm restart    -g $RG -n $VM              # reboot
az vm show -g $RG -n $VM --query hardwareProfile.vmSize -o tsv   # size
az vm list-sizes -l swedencentral -o table  # sizes in a region
```

## 4. Resources and Cleanup

> - **What:** Seeing and deleting Azure resources.
> - **How:** Resources live in resource groups; deleting the group deletes everything in it.
> - **When to use:** Checking what costs money, cleaning up after a project.

```powershell
az group list -o table                      # resource groups
az resource list -o table                   # all resources
az resource list -g $RG -o table            # resources in group
az group delete -n $RG                      # delete group + everything (permanent)
az provider register -n Microsoft.Compute   # register provider
az provider list --query "[?registrationState=='Registered'].namespace" -o table
```

## 5. NSG (Security Rules)

> - **What:** Firewall rules that decide who can reach the VM.
> - **How:** Network Security Group rules allow a port from a source IP.
> - **When to use:** Allowing SSH only from your home IP, or updating the rule when your IP changes.

```powershell
az network nsg rule list -g $RG --nsg-name $NSG -o table                    # custom rules
az network nsg rule list -g $RG --nsg-name $NSG --include-default -o table  # + defaults

# Allow SSH from my IPv4 only
$myip = Invoke-RestMethod https://api.ipify.org
az network nsg rule create -g $RG --nsg-name $NSG -n AllowSSHMyIP `
  --priority 1010 --source-address-prefixes "$myip/32" `
  --destination-port-ranges 22 --protocol Tcp --access Allow

# Home IP changed
$myip = Invoke-RestMethod https://api.ipify.org
az network nsg rule update -g $RG --nsg-name $NSG -n AllowSSHMyIP --source-address-prefixes "$myip/32"

az network nsg rule delete -g $RG --nsg-name $NSG -n AllowSSHMyIP          # remove rule
```

Never open 22 or 11434 to `*`.

## 6. SSH

> - **What:** Connecting to the VM and copying files.
> - **How:** `ssh -i key user@ip` with the private key; `scp` copies over the same connection.
> - **When to use:** Every time you work on the VM or upload project files.

```powershell
ssh -i $KEY "$USER@$IP"                     # connect
exit                                        # back to laptop

# Fix "UNPROTECTED PRIVATE KEY FILE" (Windows)
icacls $KEY /inheritance:r
icacls $KEY /grant:r "$($env:USERNAME):(R)"

# Copy files
scp -i $KEY .\file.zip "$USER@${IP}:~"     # laptop to VM
scp -i $KEY "$USER@${IP}:~/file.txt" .     # VM to laptop
scp -i $KEY -r .\folder "$USER@${IP}:~"    # whole folder
```

Linux / Mac key permissions: `chmod 400 key.pem`

## 7. Linux (Inside VM)

> - **What:** Commands you run on the VM once connected.
> - **How:** Standard Ubuntu commands (see [03 - Linux](03_linux.md) for the full list).
> - **When to use:** Checking resources, installing tools, managing the Ollama service.

```bash
# System info
whoami; hostname; uptime                    # who, where, load
lscpu | grep "Model name"; nproc            # CPU, vCPUs
free -h                                     # RAM
df -h /                                     # disk
htop                                        # live monitor (q to quit)
nvidia-smi                                  # GPU (GPU VMs only)

# Files and folders
pwd                                         # current folder
ls -la                                      # list (with hidden files)
cd ~ ; cd ..                                # home, up one level
mkdir -p app/data                           # create folder
cp a.txt b.txt ; mv a.txt dir/              # copy, move / rename
rm file.txt ; rm -r folder                  # delete file, folder
cat file.txt ; less file.txt                # show file (q to quit less)
nano file.txt                               # edit (Ctrl+O save, Ctrl+X exit)
unzip file.zip                              # extract

# Packages
sudo apt update && sudo apt upgrade -y      # update packages
sudo apt install -y htop unzip git          # install tools

# Services
systemctl status ollama                     # service status (q to quit)
sudo systemctl restart ollama               # restart service
journalctl -u ollama -f                     # live logs (Ctrl+C to stop)
```

## 8. Ollama (Inside VM)

> - **What:** Installing Ollama and managing models.
> - **How:** Install script sets up a service on port 11434; `ollama pull / run / ps` manage models.
> - **When to use:** Setting up the LLM server and choosing a model that fits the VM.

```bash
curl -fsSL https://ollama.com/install.sh | sh   # install
curl http://localhost:11434                     # "Ollama is running"

ollama pull qwen3:4b                            # chat model
ollama pull bge-m3                              # embedding model
ollama list                                     # models on disk
ollama ps                                       # loaded models, CPU/GPU
ollama run qwen3:4b                             # chat (/bye to exit, /set nothink)
ollama run qwen3:4b --verbose "Hallo"           # speed (eval rate)
ollama rm mistral                               # delete model
```

Model fit: 2 vCPU / 8 GB, use 3B to 4B. T4 GPU (16 GB), up to about 14B.

## 9. GPU Driver (GPU VMs Only)

> - **What:** NVIDIA drivers for GPU VMs.
> - **How:** `ubuntu-drivers install` picks the right driver; reboot, then check with `nvidia-smi`.
> - **When to use:** Only on GPU VM sizes, before Ollama can use the GPU.

```bash
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers install
sudo reboot
nvidia-smi                                      # check after reboot
```

## 10. SSH Tunnel (Laptop to VM Ollama)

> - **What:** Secure access to the VM's Ollama from your laptop.
> - **How:** SSH port forwarding: laptop port 11435 -> VM localhost:11434 through the encrypted SSH connection.
> - **When to use:** Using the remote model without opening port 11434 to the internet.

```powershell
# Terminal 1: keep open (blank = working)
ssh -i $KEY -N -L 11435:localhost:11434 "$USER@$IP"

# Terminal 2: test
curl.exe http://localhost:11435/api/tags
```

## 11. Local App Using VM Ollama

> - **What:** Pointing a local Python app at the VM's Ollama.
> - **How:** Set `OLLAMA_HOST` to the tunnel address; the Ollama client uses it.
> - **When to use:** Developing locally while the heavy model runs on the VM.

`.env`

```text
OLLAMA_HOST=http://localhost:11435
LLM_MODEL=qwen3:4b
EMBED_MODEL=bge-m3
```

`app.py`

```python
import os
import ollama
from dotenv import load_dotenv

load_dotenv()
client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))

client.embed(model=os.getenv("EMBED_MODEL"), input=["text"], keep_alive="30m")
client.chat(model=os.getenv("LLM_MODEL"), messages=[{"role": "user", "content": "Hi"}],
            think=False, keep_alive="30m")
```

Run (see [10 - Python Virtual Environment](10_python-virtual-environment.md)):

```powershell
python -m venv .venv
.venv\Scripts\activate                      # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload                    # http://localhost:8000
```

## 12. Verify Requests Hit the VM

> - **What:** Proving the app really uses the VM.
> - **How:** Watch the VM's Ollama logs while the app runs; close the tunnel and the app should fail.
> - **When to use:** After setup, or when you suspect the app uses a local Ollama instead.

```bash
journalctl -u ollama -f                     # VM: see POST /api/embed and /api/chat
ollama ps                                   # VM: model loaded
```

Close the tunnel: the app must fail.

## 13. Laptop (PowerShell)

> - **What:** Checking your laptop's side: services, ports, env vars, IP.
> - **How:** PowerShell cmdlets (see [02 - Terminal and PowerShell](02_terminal-powershell.md)).
> - **When to use:** Something on the laptop blocks the tunnel port, or `OLLAMA_HOST` is not set.

```powershell
Get-Service | Where-Object Status -eq Running                                   # services
Get-Process *ollama*                                                            # local Ollama
Get-NetTCPConnection -State Listen | Select LocalAddress, LocalPort, OwningProcess  # ports
echo $env:OLLAMA_HOST                                                           # env var
Invoke-RestMethod https://api.ipify.org                                         # my IPv4
```

## 14. Troubleshooting

| Error | Fix |
|---|---|
| Resource provider not registered | `az provider register -n Microsoft.Compute` (also Network, Storage, Quota) |
| `NotAvailableForSubscription` | Pick another size or region |
| Region not accepting new customers | Use Sweden Central, North Europe, France Central |
| `lscpu` not recognized | You're on Windows, SSH into the VM first |
| SSH `Connection timed out` | No NSG rule for your IP, add/update rule |
| SSH `Permission denied (publickey)` | Wrong key or username |
| `SecurityRuleInvalidAddressPrefix` | IPv6 or typo, use `api.ipify.org` |
| `Failed to connect to Ollama` | Tunnel closed or `OLLAMA_HOST` not loaded |
| Slow answers | `think=False`, fewer chunks, `keep_alive`, GPU VM |

## 15. End of Session

> - **What:** Shutting everything down so you are not billed.
> - **How:** Stop the app and tunnel, then deallocate the VM and confirm its state.
> - **When to use:** Always, at the end of every working session.

```powershell
# Ctrl+C app and tunnel, exit VM, then:
az vm deallocate -g $RG -n $VM
az vm list -d -o table                      # expect "VM deallocated"
```

Deallocated VMs still bill for disk and static IP. Delete the resource group when done.
