# Azure VM + Linux + Ollama Cheat Sheet

Quick reference for running Ollama on an Azure Ubuntu VM and using it from a local app via SSH tunnel.

## Variables (PowerShell)

Set once per session, then copy commands as they are.

```powershell
$RG   = "my-resource-group"
$VM   = "my-vm"
$NSG  = "my-vm-nsg"
$KEY  = "$HOME\.ssh\my-vm_key.pem"
$USER = "azureuser"
$IP   = az vm show -d -g $RG -n $VM --query publicIps -o tsv
```

---

## Azure CLI

```powershell
winget install -e --id Microsoft.AzureCLI   # install (Windows)
brew install azure-cli                      # install (Mac)
az login                                    # log in
az --version                                # check install
az account show -o table                    # current subscription
```

## VM

```powershell
az vm list -d -o table                      # status + IP
az vm start      -g $RG -n $VM              # start
az vm deallocate -g $RG -n $VM              # stop, no compute cost
az vm stop       -g $RG -n $VM              # OS off, STILL billed
az vm show -g $RG -n $VM --query hardwareProfile.vmSize -o tsv   # size
az vm list-sizes -l swedencentral -o table  # sizes in a region
```

## Resources and cleanup

```powershell
az group list -o table                      # resource groups
az resource list -o table                   # all resources
az resource list -g $RG -o table            # resources in group
az group delete -n $RG                      # delete group + everything (permanent)
az provider register -n Microsoft.Compute   # register provider
az provider list --query "[?registrationState=='Registered'].namespace" -o table
```

## NSG (security rules)

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

## SSH

```powershell
ssh -i $KEY "$USER@$IP"                     # connect
exit                                        # back to laptop

# Fix "UNPROTECTED PRIVATE KEY FILE" (Windows)
icacls $KEY /inheritance:r
icacls $KEY /grant:r "$($env:USERNAME):(R)"

# Copy files
scp -i $KEY .\file.zip "$USER@${IP}:~"     # laptop to VM
scp -i $KEY "$USER@${IP}:~/file.txt" .     # VM to laptop
```

Linux (Mac) key permissions: `chmod 400 key.pem`

## Linux (inside VM)

```bash
whoami; hostname; uptime                    # who, where, load
lscpu | grep "Model name"; nproc            # CPU, vCPUs
free -h                                     # RAM
df -h /                                     # disk
htop                                        # live monitor (q to quit)
nvidia-smi                                  # GPU (GPU VMs only)

sudo apt update && sudo apt upgrade -y      # update packages
sudo apt install -y htop unzip git          # install tools

systemctl status ollama                     # service status (q to quit)
sudo systemctl restart ollama               # restart service
journalctl -u ollama -f                     # live logs (Ctrl+C to stop)
```

## Ollama (inside VM)

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

## GPU driver (GPU VMs only)

```bash
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers install
sudo reboot
nvidia-smi                                      # check after reboot
```

## SSH tunnel (laptop to VM Ollama)

```powershell
# Terminal 1: keep open (blank = working)
ssh -i $KEY -N -L 11435:localhost:11434 "$USER@$IP"

# Terminal 2: test
curl.exe http://localhost:11435/api/tags
```

## Local app using VM Ollama

`.env`
```
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

Run
```powershell
python -m venv .venv
.venv\Scripts\activate                      # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload                    # http://localhost:8000
```

## Verify requests hit the VM

```bash
journalctl -u ollama -f                     # VM: see POST /api/embed and /api/chat
ollama ps                                   # VM: model loaded
```
Close the tunnel: the app must fail.

## Laptop (PowerShell)

```powershell
Get-Service | Where-Object Status -eq Running                                   # services
Get-Process *ollama*                                                            # local Ollama
Get-NetTCPConnection -State Listen | Select LocalAddress, LocalPort, OwningProcess  # ports
echo $env:OLLAMA_HOST                                                           # env var
Invoke-RestMethod https://api.ipify.org                                         # my IPv4
```

## Troubleshooting

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

## End of session

```powershell
# Ctrl+C app and tunnel, exit VM, then:
az vm deallocate -g $RG -n $VM
az vm list -d -o table                      # expect "VM deallocated"
```

Deallocated VMs still bill for disk and static IP. Delete the resource group when done.
