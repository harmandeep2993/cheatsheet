# 14 - Azure VM + Linux + Ollama

Quick reference for running Ollama on an Azure Ubuntu VM and using it from a local app via SSH tunnel.

## Contents

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

## 1. Variables (PowerShell)

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

```powershell
az group list -o table                      # resource groups
az resource list -o table                   # all resources
az resource list -g $RG -o table            # resources in group
az group delete -n $RG                      # delete group + everything (permanent)
az provider register -n Microsoft.Compute   # register provider
az provider list --query "[?registrationState=='Registered'].namespace" -o table
```

## 5. NSG (Security Rules)

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

```bash
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers install
sudo reboot
nvidia-smi                                      # check after reboot
```

## 10. SSH Tunnel (Laptop to VM Ollama)

```powershell
# Terminal 1: keep open (blank = working)
ssh -i $KEY -N -L 11435:localhost:11434 "$USER@$IP"

# Terminal 2: test
curl.exe http://localhost:11435/api/tags
```

## 11. Local App Using VM Ollama

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

Run (see [06 - Python Virtual Environment](06_python-virtual-environment.md)):

```powershell
python -m venv .venv
.venv\Scripts\activate                      # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload                    # http://localhost:8000
```

## 12. Verify Requests Hit the VM

```bash
journalctl -u ollama -f                     # VM: see POST /api/embed and /api/chat
ollama ps                                   # VM: model loaded
```

Close the tunnel: the app must fail.

## 13. Laptop (PowerShell)

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

```powershell
# Ctrl+C app and tunnel, exit VM, then:
az vm deallocate -g $RG -n $VM
az vm list -d -o table                      # expect "VM deallocated"
```

Deallocated VMs still bill for disk and static IP. Delete the resource group when done.
