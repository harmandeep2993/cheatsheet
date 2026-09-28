# 48 - Azure

<!-- nav:start -->
**Previous:** [47 - Terraform](47_terraform.md) | **Index:** [All guides](../README.md) | **Next:** [49 - Azure VM + Linux + Ollama](49_azure-vm-ollama.md)
<!-- nav:end -->

Quick reference for Microsoft Azure with the Azure CLI: core concepts, the most used services, security, cost and infrastructure as code.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Azure?

Microsoft Azure is a **cloud platform**: instead of buying and running your own servers, you rent computing power, storage, databases, networking and AI services from Microsoft's data centres around the world and pay only for what you use. You create and manage everything through the **Azure Portal** (website, portal.azure.com), the **Azure CLI** (`az` commands in a terminal), SDKs (Python libraries) or infrastructure-as-code files (Bicep / Terraform).

Every thing you create (a VM, a storage account, a database) is a **resource**. Resources live in **resource groups** (folders), which belong to a **subscription** (the billing account), inside a **tenant** (your organisation's identity directory, Microsoft Entra ID).

```text
Tenant (Microsoft Entra ID: users, groups, apps)
 +-- Subscription (billing + limits)            e.g. "Pay-As-You-Go"
      +-- Resource group (folder, one lifecycle) e.g. "rg-sales-api-dev"
           +-- Resources                         VM, storage account, container app, key vault ...
                (each in a region)               e.g. swedencentral, westeurope
```

### Service models

| Model | You manage | Azure manages | Examples |
|---|---|---|---|
| **IaaS** (Infrastructure) | OS, runtime, app, data | Hardware, network, virtualisation | Virtual Machines |
| **PaaS** (Platform) | App and data | OS, patching, scaling, runtime | App Service, Container Apps, Azure SQL |
| **Serverless** | Only code / container | Everything, scales to zero | Azure Functions, Container Apps (min 0) |
| **SaaS / AI services** | Just use it | Everything | Azure OpenAI, AI Search, Microsoft 365 |

### Why use it?

- **No hardware**: create a server, database or GPU machine in minutes; delete it when done.
- **Pay as you go**: pay per second / hour / request; stop resources to stop most costs.
- **Scale**: from one small container to thousands of instances, in regions worldwide.
- **Managed services**: Azure handles backups, patching, high availability and security updates.
- **Security and compliance**: identity (Entra ID), role-based access, Key Vault, EU data regions.
- **Microsoft ecosystem**: integrates with Microsoft 365, GitHub, VS Code and Azure OpenAI.

### Key terms

| Term | Meaning |
|---|---|
| Tenant | Your organisation's directory (Microsoft Entra ID) |
| Subscription | Billing unit with its own limits and permissions |
| Resource group (RG) | Container for related resources; delete the RG = delete everything in it |
| Resource | One service instance: VM, storage account, web app ... |
| Region | Physical data-centre location (swedencentral, westeurope, northeurope) |
| SKU / tier | Size and price level of a resource (Basic, Standard, B1, S0) |
| Resource provider | Azure service namespace that must be registered (`Microsoft.App`) |
| RBAC | Role-based access control: who can do what, on which scope |
| Managed identity | An identity Azure gives your app so it can access other resources without passwords |
| Service principal | An identity for automation / CI pipelines |

**Where it fits:** deploy containers from [43 - Docker](43_docker.md) and APIs from [40 - FastAPI](40_fastapi.md); a full VM + LLM walkthrough is in [49 - Azure VM + Linux + Ollama](49_azure-vm-ollama.md). Automate it with [47 - Terraform](47_terraform.md) and [44 - GitHub Actions](44_github-actions.md); run Kubernetes on AKS with [46](46_kubernetes.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Azure documentation | https://learn.microsoft.com/en-us/azure/ |
| Azure CLI | https://learn.microsoft.com/en-us/cli/azure/ |
| Azure CLI command reference | https://learn.microsoft.com/en-us/cli/azure/reference-index |
| Azure Container Apps | https://learn.microsoft.com/en-us/azure/container-apps/ |
| Azure AI Foundry (incl. Azure OpenAI) | https://learn.microsoft.com/en-us/azure/ai-foundry/ |
| Bicep | https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/ |
| Pricing calculator | https://azure.microsoft.com/en-us/pricing/calculator/ |
| Resource naming abbreviations | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-abbreviations |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install, Log In, Cloud Shell](#1-install-log-in-cloud-shell)
2. [Subscriptions and Account](#2-subscriptions-and-account)
3. [Resource Groups](#3-resource-groups)
4. [Regions, Providers and Quotas](#4-regions-providers-and-quotas)
5. [Output Formats and --query](#5-output-formats-and---query)
6. [Virtual Machines](#6-virtual-machines)
7. [Storage Accounts and Blobs](#7-storage-accounts-and-blobs)
8. [Container Registry (ACR)](#8-container-registry-acr)
9. [Container Apps](#9-container-apps)
10. [App Service (Web Apps)](#10-app-service-web-apps)
11. [Azure Functions](#11-azure-functions)
12. [Key Vault (Secrets)](#12-key-vault-secrets)
13. [Databases](#13-databases)
14. [Networking](#14-networking)
15. [Identity and Access (RBAC)](#15-identity-and-access-rbac)
16. [Managed Identity and Service Principals](#16-managed-identity-and-service-principals)
17. [Azure SDK for Python](#17-azure-sdk-for-python)
18. [Azure OpenAI](#18-azure-openai)
19. [Monitoring and Logs](#19-monitoring-and-logs)
20. [Cost Management](#20-cost-management)
21. [Tags, Locks and Cleanup](#21-tags-locks-and-cleanup)
22. [Infrastructure as Code (Bicep)](#22-infrastructure-as-code-bicep)
23. [End to End: Deploy a FastAPI Container](#23-end-to-end-deploy-a-fastapi-container)
24. [Which Service to Use](#24-which-service-to-use)
25. [Naming Conventions](#25-naming-conventions)
26. [Troubleshooting](#26-troubleshooting)
27. [Try It](#27-try-it)

---

## 0. Flags and Parameters

> How `az` commands are built and what the common flags mean. `az <group> [<sub-group>] <action> --flags`; most flags work the same across all services.
>
> Use this when you see `az containerapp create -g rg -n api --image ... --ingress external` and want to know what each part does.

```text
az  storage  blob  upload  --account-name stsales  -c data  -n sales.csv  -f ./sales.csv  --auth-mode login
|   |        |     |       |                       |        |             |               |
|   |        |     |       |                       |        |             |               +-- use your Entra login, not keys
|   |        |     |       |                       |        |             +------------------ local file to upload
|   |        |     |       |                       |        +-------------------------------- blob name in Azure
|   |        |     |       |                       +----------------------------------------- container (folder)
|   |        |     |       +------------------------------------------------------------------ storage account
|   |        |     +-------------------------------------------------------------------------- action
|   |        +-------------------------------------------------------------------------------- sub-group: blobs
|   +----------------------------------------------------------------------------------------- group: storage
+--------------------------------------------------------------------------------------------- Azure CLI
```

Help anywhere: `az storage blob upload --help`, `az find "container app"` (examples from docs).

### Global flags (work on every command)

| Flag | Long form | Meaning | Example |
|---|---|---|---|
| `-g` | `--resource-group` | Resource group | `-g rg-demo` |
| `-n` | `--name` | Resource name | `-n myvm` |
| `-l` | `--location` | Region | `-l swedencentral` |
| `-o` | `--output` | `json`, `jsonc`, `table`, `tsv`, `yaml`, `none` | `-o table` |
| `--query` | | JMESPath filter on the JSON result | `--query "[].name"` |
| `--subscription` | | Run against another subscription | `--subscription <id>` |
| `--ids` | | Target resources by full ID instead of `-g` / `-n` | `--ids $(az vm list --query "[].id" -o tsv)` |
| `--yes` / `-y` | | Do not ask for confirmation | `az group delete -n rg --yes` |
| `--no-wait` | | Start the operation and return immediately | `--no-wait` |
| `--tags` | | Key=value labels | `--tags env=dev owner=harman` |
| `--verbose` / `--debug` | | More output / full HTTP details for troubleshooting | `--debug` |
| `--only-show-errors` | | Hide warnings | |

### Common service flags

| Flag | Used in | Meaning |
|---|---|---|
| `--sku` | most create commands | Size / pricing tier (`Basic`, `Standard_LRS`, `B1`, `S0`) |
| `--image` | vm, containerapp, webapp | OS image (VM) or container image |
| `--size` | vm | VM size (`Standard_B2s`) |
| `--admin-username` | vm | Login user name |
| `--generate-ssh-keys` | vm | Create / reuse `~/.ssh/id_rsa` keys |
| `--auth-mode login` | storage | Use your Entra identity + RBAC instead of account keys |
| `--target-port` | containerapp | Port your container listens on |
| `--ingress` | containerapp | `external` (internet) or `internal` (only inside the environment) |
| `--min-replicas` / `--max-replicas` | containerapp | Scaling limits; `0` = scale to zero (no cost when idle) |
| `--registry-server` | containerapp | Registry to pull the image from |
| `--runtime` | webapp, functionapp | Language runtime (`PYTHON:3.12`) |
| `--settings` | webapp config | App settings = environment variables |
| `--assignee` / `--role` / `--scope` | role assignment | Who / which role / on which resource |

---

## 1. Install, Log In, Cloud Shell

> Getting the Azure CLI and signing in. Install `az`, then `az login` opens the browser; Cloud Shell in the Portal has `az` pre-installed.
>
> Use it as the first step on any machine; Cloud Shell when you cannot install anything locally.

```powershell
winget install -e --id Microsoft.AzureCLI       # Windows
brew install azure-cli                          # Mac
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash   # Ubuntu

az --version
az upgrade                                      # update the CLI
az login                                        # browser login
az login --use-device-code                      # login from a machine without browser (VM, SSH)
az logout
```

**Cloud Shell**: click the `>_` icon in the Portal; Bash or PowerShell with `az`, `git`, `docker` CLI and a small persistent disk.

## 2. Subscriptions and Account

> Choosing which subscription your commands act on. `az account` lists and switches subscriptions; the selected one is used by every later command.
>
> Use this when you have several subscriptions (work, personal, trial) or resources "disappear" (wrong subscription).

```bash
az account show -o table                        # current subscription
az account list -o table                        # all subscriptions you can access
az account set --subscription "<name-or-id>"    # switch
az account show --query id -o tsv               # current subscription ID
az ad signed-in-user show --query "{name:displayName, id:id}" -o table   # who am I
```

## 3. Resource Groups

> Folders for resources that share a lifecycle. Create one per project / environment; everything inside can be listed, tagged and deleted together. Always create a resource group first; delete it to clean up a whole project.

```bash
az group create -n rg-sales-dev -l swedencentral
az group list -o table
az group show -n rg-sales-dev
az resource list -g rg-sales-dev -o table       # everything inside
az group delete -n rg-sales-dev --yes --no-wait # delete group AND all resources (permanent)
az group exists -n rg-sales-dev                 # true / false
```

Tip: one RG per app per environment (`rg-sales-dev`, `rg-sales-prod`).

## 4. Regions, Providers and Quotas

> Where resources run, which services are enabled, and how much you are allowed to create. Regions are chosen per resource; providers must be registered once per subscription; quotas limit vCPUs etc.
>
> Use it to answer questions like "Not available in region", "provider not registered" or "quota exceeded" errors.

```bash
az account list-locations --query "[].name" -o tsv        # all regions
az vm list-sizes -l swedencentral -o table                 # VM sizes in a region
az vm list-usage -l swedencentral -o table                 # vCPU quota used / limit

az provider list --query "[?registrationState=='Registered'].namespace" -o table
az provider register -n Microsoft.App                      # Container Apps
az provider register -n Microsoft.ContainerRegistry
az provider show -n Microsoft.App --query registrationState -o tsv
```

Choose a region close to your users; EU data: `swedencentral`, `westeurope`, `northeurope`, `germanywestcentral`, `francecentral`.

## 5. Output Formats and --query

> Controlling how results look and picking only the fields you need. `-o` changes the format; `--query` uses JMESPath to filter and reshape the JSON.
>
> Use it for readable tables for humans (`-o table`), single values for scripts (`-o tsv`).

| `-o` | Result |
|---|---|
| `json` | Full JSON (default) |
| `table` | Readable table |
| `tsv` | Plain values, tab separated (store in variables) |
| `yaml` | YAML |
| `none` | Nothing (only errors) |

| `--query` | Returns |
|---|---|
| `"name"` | One field |
| `"[].name"` | Field from every item in a list |
| `"[0]"` | First item |
| `"[?location=='swedencentral'].name"` | Filter, then pick a field |
| `"[?contains(name, 'api')]"` | Items whose name contains "api" |
| `"[].{Name:name, RG:resourceGroup}"` | New object with renamed fields (good with `-o table`) |
| `"length([])"` | Count |

```powershell
$IP = az vm show -d -g rg-demo -n myvm --query publicIps -o tsv
az vm list -d --query "[].{Name:name, State:powerState, IP:publicIps}" -o table
```

## 6. Virtual Machines

> Full computers in the cloud where you control the OS (IaaS). Pick an image, size and login method; Azure creates disk, network card, public IP and NSG with it.
>
> Use it for custom software, GPU workloads, LLM hosting, anything needing full OS control. Full walkthrough: [49 - Azure VM + Linux + Ollama](49_azure-vm-ollama.md).

```bash
az vm create -g rg-demo -n myvm \
  --image Ubuntu2404 --size Standard_B2s \
  --admin-username azureuser --generate-ssh-keys \
  --public-ip-sku Standard

az vm list -d -o table                          # status and IPs
az vm start -g rg-demo -n myvm
az vm deallocate -g rg-demo -n myvm             # stop and release compute (billing stops)
az vm restart -g rg-demo -n myvm
az vm resize -g rg-demo -n myvm --size Standard_D4s_v5
az vm auto-shutdown -g rg-demo -n myvm --time 1900      # daily shutdown at 19:00 UTC
az vm run-command invoke -g rg-demo -n myvm --command-id RunShellScript --scripts "uptime"
az vm delete -g rg-demo -n myvm --yes           # disk / IP / NIC may remain: delete the RG to be sure
```

`stop` keeps billing for compute; `deallocate` stops compute billing (disk still billed).

## 7. Storage Accounts and Blobs

> Cheap, durable storage for files (blobs), plus queues, tables and file shares. A storage account holds containers; containers hold blobs (files). Access with Entra login + RBAC or keys / SAS.
>
> Use it for data files for analysis, model files, backups, images, static websites.

```bash
az storage account create -n stsalesdev123 -g rg-demo -l swedencentral --sku Standard_LRS
# Give yourself data access (needed for --auth-mode login)
az role assignment create --assignee $(az ad signed-in-user show --query id -o tsv) \
  --role "Storage Blob Data Contributor" \
  --scope $(az storage account show -n stsalesdev123 -g rg-demo --query id -o tsv)

az storage container create --account-name stsalesdev123 -n data --auth-mode login
az storage blob upload --account-name stsalesdev123 -c data -n sales.csv -f ./sales.csv --auth-mode login
az storage blob upload-batch --account-name stsalesdev123 -d data -s ./folder --auth-mode login
az storage blob list --account-name stsalesdev123 -c data --auth-mode login -o table
az storage blob download --account-name stsalesdev123 -c data -n sales.csv -f ./copy.csv --auth-mode login
```

| SKU | Redundancy |
|---|---|
| `Standard_LRS` | 3 copies in one data centre (cheapest) |
| `Standard_ZRS` | Copies across availability zones |
| `Standard_GRS` | Copies to a second region |

Storage account names: 3 to 24 lowercase letters and digits, globally unique. Role assignments can take a few minutes to apply.

## 8. Container Registry (ACR)

> Private Docker image storage in Azure. Push images with Docker, or let ACR build them in the cloud with `az acr build`.
>
> Use it for storing images for Container Apps, App Service or VMs. Docker basics: [43 - Docker](43_docker.md).

```bash
az acr create -g rg-demo -n acrsalesdev --sku Basic
az acr login -n acrsalesdev                     # docker login for this registry

docker tag myapi:1.0 acrsalesdev.azurecr.io/myapi:1.0
docker push acrsalesdev.azurecr.io/myapi:1.0

az acr build -r acrsalesdev -t myapi:1.0 .      # build in Azure, no local Docker needed
az acr repository list -n acrsalesdev -o table
az acr repository show-tags -n acrsalesdev --repository myapi -o table
```

## 9. Container Apps

> Serverless containers: run any Docker image with HTTPS, autoscaling and scale-to-zero, without managing servers or Kubernetes. Apps run in an environment; set image, port and ingress; Azure provides a public HTTPS URL.
>
> Use it for APIs (FastAPI), web apps, background workers. Usually the easiest way to run a container in Azure.

```bash
az extension add --name containerapp --upgrade
az provider register -n Microsoft.App
az provider register -n Microsoft.OperationalInsights

# One command: build from source (Dockerfile), create ACR + environment + app
az containerapp up -n sales-api -g rg-demo -l swedencentral \
  --source . --ingress external --target-port 8000

# Or step by step with an existing image
az containerapp env create -n cae-demo -g rg-demo -l swedencentral
az containerapp create -n sales-api -g rg-demo --environment cae-demo \
  --image acrsalesdev.azurecr.io/myapi:1.0 --registry-server acrsalesdev.azurecr.io \
  --target-port 8000 --ingress external --min-replicas 0 --max-replicas 3 \
  --env-vars APP_ENV=prod

az containerapp show -n sales-api -g rg-demo --query properties.configuration.ingress.fqdn -o tsv   # URL
az containerapp logs show -n sales-api -g rg-demo --follow
az containerapp update -n sales-api -g rg-demo --image acrsalesdev.azurecr.io/myapi:1.1   # deploy new version
az containerapp revision list -n sales-api -g rg-demo -o table

# Secrets -> environment variables
az containerapp secret set -n sales-api -g rg-demo --secrets api-key=<value>
az containerapp update -n sales-api -g rg-demo --set-env-vars API_KEY=secretref:api-key
```

## 10. App Service (Web Apps)

> Managed hosting for web apps from code or containers (PaaS). An App Service plan (the server size) hosts one or more web apps; deploy code, Azure runs it.
>
> Use it for classic web apps / APIs where you deploy code without a Dockerfile, with deployment slots, custom domains and always-on.

```bash
# Quickest: from the project folder
az webapp up -n sales-web -g rg-demo --runtime "PYTHON:3.12" --sku B1

# Step by step
az appservice plan create -n plan-demo -g rg-demo --is-linux --sku B1
az webapp create -n sales-web -g rg-demo -p plan-demo --runtime "PYTHON:3.12"
az webapp config appsettings set -n sales-web -g rg-demo --settings APP_ENV=prod API_KEY=@Microsoft.KeyVault(SecretUri=<uri>)
az webapp config set -n sales-web -g rg-demo \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app"   # FastAPI
az webapp deploy -n sales-web -g rg-demo --src-path app.zip --type zip
az webapp log tail -n sales-web -g rg-demo
az webapp browse -n sales-web -g rg-demo
```

App settings become environment variables inside the app. `F1` free tier exists but sleeps and has limits.

## 11. Azure Functions

> Serverless functions triggered by HTTP, timers, queues or blob uploads; pay per execution. Write small functions locally with Core Tools, then publish to a Function App.
>
> Use it for scheduled jobs (nightly data pull), reacting to file uploads, small webhooks.

```bash
npm install -g azure-functions-core-tools@4     # or: winget install Microsoft.Azure.FunctionsCoreTools
func init myfunc --python
cd myfunc
func new --name hello --template "HTTP trigger"
func start                                      # run locally

az functionapp create -n fn-sales-dev -g rg-demo --storage-account stsalesdev123 \
  --consumption-plan-location swedencentral --runtime python --runtime-version 3.11 \
  --functions-version 4 --os-type linux
func azure functionapp publish fn-sales-dev
```

## 12. Key Vault (Secrets)

> Secure storage for secrets (API keys, passwords), keys and certificates. Store secrets once; apps read them at runtime with their managed identity; access controlled by RBAC and logged.
>
> Use it in every secret in production, instead of `.env` files or hard-coded values.

```bash
az keyvault create -n kv-sales-dev -g rg-demo -l swedencentral     # RBAC authorization is the default
az role assignment create --assignee $(az ad signed-in-user show --query id -o tsv) \
  --role "Key Vault Secrets Officer" \
  --scope $(az keyvault show -n kv-sales-dev --query id -o tsv)

az keyvault secret set --vault-name kv-sales-dev -n openai-key --value "<secret>"
az keyvault secret show --vault-name kv-sales-dev -n openai-key --query value -o tsv
az keyvault secret list --vault-name kv-sales-dev -o table
az keyvault secret delete --vault-name kv-sales-dev -n openai-key   # soft-deleted, recoverable
```

Key Vault names are globally unique (3 to 24 characters). Soft delete keeps deleted vaults / secrets for a retention period; `purge` removes them for good.

## 13. Databases

> Managed databases: PostgreSQL, MySQL, Azure SQL, Cosmos DB. Azure runs the server (backups, patching, HA); you connect with normal tools (psql, SQLAlchemy).
>
> Use it for app data that must persist. SQL basics: [20 - SQL](20_sql.md).

```bash
# PostgreSQL Flexible Server (password from an environment variable, not typed in the command)
az postgres flexible-server create -n pg-sales-dev -g rg-demo -l swedencentral \
  --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 16 \
  --admin-user pgadmin --admin-password "$PG_PASSWORD" \
  --public-access $(curl -s https://api.ipify.org)

az postgres flexible-server firewall-rule create -n pg-sales-dev -g rg-demo \
  --rule-name my-ip --start-ip-address <ip> --end-ip-address <ip>
az postgres flexible-server db create -s pg-sales-dev -g rg-demo -d salesdb
az postgres flexible-server stop -n pg-sales-dev -g rg-demo      # save cost when not used

psql "host=pg-sales-dev.postgres.database.azure.com port=5432 dbname=salesdb user=pgadmin sslmode=require"
```

| Service | Use for |
|---|---|
| Azure Database for PostgreSQL / MySQL | Open-source relational databases |
| Azure SQL Database | Microsoft SQL Server, serverless option |
| Cosmos DB | Global NoSQL (JSON documents), also vector search |

## 14. Networking

> Virtual networks, subnets, firewalls and IP addresses. A VNet is your private network; NSGs filter traffic; resources get private and optionally public IPs.
>
> Use it for securing VMs and databases, connecting services privately, opening ports.

```bash
az network vnet create -g rg-demo -n vnet-demo --address-prefix 10.0.0.0/16 \
  --subnet-name default --subnet-prefix 10.0.0.0/24
az network vnet list -o table
az network nsg list -o table
az network nsg rule list -g rg-demo --nsg-name myvmNSG -o table
az network public-ip list -o table
az vm open-port -g rg-demo -n myvm --port 80 --priority 900   # opens to the internet: web servers only
```

Never open SSH (22), RDP (3389) or database ports to `*`. Limit to your IP (see [49 - Azure VM](49_azure-vm-ollama.md)) or use Azure Bastion / private endpoints.

## 15. Identity and Access (RBAC)

> Controlling who can do what on which resources. A role assignment = **who** (user, group, identity) + **role** (set of permissions) + **scope** (subscription, RG or resource).
>
> Use it for giving a teammate access, letting an app read storage, fixing "AuthorizationFailed".

| Role | Can |
|---|---|
| Owner | Everything, including granting access |
| Contributor | Create / change / delete resources, not grant access |
| Reader | View only |
| Storage Blob Data Contributor / Reader | Read / write blob data |
| Key Vault Secrets User / Officer | Read / manage secrets |
| AcrPull / AcrPush | Pull / push container images |

```bash
az role assignment create --assignee user@example.com --role Reader \
  --scope /subscriptions/<sub-id>/resourceGroups/rg-demo
az role assignment list --assignee user@example.com --all -o table
az role assignment delete --assignee user@example.com --role Reader -g rg-demo
az role definition list --query "[?contains(roleName, 'Storage')].roleName" -o tsv
```

Give the smallest role on the smallest scope that works (least privilege).

## 16. Managed Identity and Service Principals

> Identities for apps and automation instead of personal accounts or stored passwords. Managed identity: Azure creates and rotates credentials for a resource. Service principal: an app identity with a secret or certificate, for outside Azure (CI).
>
> Use it for an app in Azure accessing storage / Key Vault (managed identity); GitHub Actions deploying to Azure (service principal / federated credential).

```bash
# Managed identity for a container app, then allow it to read secrets
az containerapp identity assign -n sales-api -g rg-demo --system-assigned
PRINCIPAL=$(az containerapp show -n sales-api -g rg-demo --query identity.principalId -o tsv)
az role assignment create --assignee $PRINCIPAL --role "Key Vault Secrets User" \
  --scope $(az keyvault show -n kv-sales-dev --query id -o tsv)

# Service principal for CI (prints a secret once: store it in GitHub secrets, never in code)
az ad sp create-for-rbac --name sp-sales-ci --role Contributor \
  --scopes /subscriptions/<sub-id>/resourceGroups/rg-demo
```

## 17. Azure SDK for Python

> Python libraries to use Azure services from code. `DefaultAzureCredential` tries your `az login` locally and the managed identity in Azure, so the same code works in both.
>
> Use it for reading blobs, secrets or databases from a Python app or notebook.

```powershell
pip install azure-identity azure-storage-blob azure-keyvault-secrets
```

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient

credential = DefaultAzureCredential()      # az login locally, managed identity in Azure

secrets = SecretClient("https://kv-sales-dev.vault.azure.net", credential)
api_key = secrets.get_secret("openai-key").value

blobs = BlobServiceClient("https://stsalesdev123.blob.core.windows.net", credential)
data = blobs.get_blob_client("data", "sales.csv").download_blob().readall()
```

## 18. Azure OpenAI

> OpenAI models (GPT family, embeddings) hosted in Azure, with Azure security and regions. Create an Azure OpenAI resource, deploy a model under a deployment name, call it with the `openai` Python package.
>
> Use it for LLM features where data must stay in Azure / EU, or enterprise requirements. For self-hosted open models, see [49 - Azure VM + Ollama](49_azure-vm-ollama.md).

```bash
az cognitiveservices account create -n aoai-sales -g rg-demo -l swedencentral --kind OpenAI --sku S0
az cognitiveservices account list-models -n aoai-sales -g rg-demo -o table     # what you can deploy
az cognitiveservices account deployment create -n aoai-sales -g rg-demo \
  --deployment-name chat --model-name <model> --model-version <version> \
  --model-format OpenAI --sku-name GlobalStandard --sku-capacity 10
az cognitiveservices account show -n aoai-sales -g rg-demo --query properties.endpoint -o tsv
```

```python
import os

from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-10-21",
)
resp = client.chat.completions.create(
    model="chat",                                # the DEPLOYMENT name, not the model name
    messages=[{"role": "user", "content": "Summarise Azure in one sentence."}],
)
print(resp.choices[0].message.content)
```

Model names, versions and API versions change often: check `list-models` and the Azure docs. Azure AI Foundry (portal) offers more models from other providers.

## 19. Monitoring and Logs

> Seeing what happened (activity log), how resources perform (metrics) and what apps log. Activity log records management actions; Azure Monitor collects metrics; Application Insights / Log Analytics store app logs and traces.
>
> Use it to answer questions like "Who deleted this?", "why is the app slow?", debugging production errors.

```bash
az monitor activity-log list -g rg-demo --offset 1d -o table           # who did what, last day
az monitor metrics list --resource $(az vm show -g rg-demo -n myvm --query id -o tsv) \
  --metric "Percentage CPU" --interval PT5M -o table
az containerapp logs show -n sales-api -g rg-demo --follow             # app logs
az webapp log tail -n sales-web -g rg-demo
```

Python app telemetry to Application Insights:

```python
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()       # reads APPLICATIONINSIGHTS_CONNECTION_STRING from the environment
```

## 20. Cost Management

> Tracking and limiting what you spend. Cost Management in the Portal shows spend per resource / RG; budgets send alerts; stop or delete idle resources.
>
> Use it for from day one; cloud bills grow quietly.

- Portal -> **Cost Management** -> Cost analysis (group by resource group) and **Budgets** (alert at 50%, 80%, 100%).
- Use the **Pricing calculator** (azure.microsoft.com/pricing/calculator) before creating big resources.

```bash
az consumption budget create --budget-name monthly-50 --amount 50 --category Cost \
  --time-grain Monthly --start-date 2026-10-01 --end-date 2027-09-30
az vm deallocate -g rg-demo -n myvm             # stop VM compute billing
az vm auto-shutdown -g rg-demo -n myvm --time 1900
az postgres flexible-server stop -n pg-sales-dev -g rg-demo
az containerapp update -n sales-api -g rg-demo --min-replicas 0    # scale to zero when idle
az group delete -n rg-demo --yes                # the only way to be sure nothing is left
```

| Cost trap | Fix |
|---|---|
| VM "stopped" but still billed | `deallocate`, not `stop` |
| Disks, public IPs, snapshots left after deleting a VM | Delete the resource group |
| Premium SKUs chosen by default | Pick Basic / Burstable for dev |
| Log Analytics ingesting too much | Lower log level, set daily cap |

## 21. Tags, Locks and Cleanup

> Labels for organising / billing, and locks that prevent accidental deletion. Tags are key=value pairs on resources; locks block delete (or all changes) until removed.
>
> Use it for tags on everything (owner, env, project); locks on production resources.

```bash
az group update -n rg-demo --tags env=dev owner=harman project=sales
az resource list --tag env=dev -o table
az resource tag --tags env=dev --ids <resource-id>

az lock create -n no-delete --lock-type CanNotDelete -g rg-prod
az lock list -g rg-prod -o table
az lock delete -n no-delete -g rg-prod

az group list --query "[?tags.env=='dev'].name" -o tsv     # find dev groups to clean up
```

## 22. Infrastructure as Code (Bicep)

> Describing Azure resources in files instead of clicking or running many commands. Bicep files declare resources; `az deployment group create` makes Azure match the file (repeatable, reviewable in Git).
>
> Use it for anything you will create more than once (dev / test / prod), or want to review in pull requests.

```bicep
// main.bicep
param location string = resourceGroup().location
param storageName string

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: { minimumTlsVersion: 'TLS1_2' }
}

output blobEndpoint string = storage.properties.primaryEndpoints.blob
```

```bash
az bicep install
az deployment group what-if -g rg-demo --template-file main.bicep --parameters storageName=stdemo123   # preview
az deployment group create  -g rg-demo --template-file main.bicep --parameters storageName=stdemo123
az deployment group list -g rg-demo -o table
```

Terraform is a popular multi-cloud alternative; the Azure Developer CLI (`azd up`) deploys full app templates.

## 23. End to End: Deploy a FastAPI Container

> The full path from local FastAPI project to a public HTTPS API. Resource group -> registry build -> container app -> test URL -> clean up.
>
> Use it for shipping an API from [40 - FastAPI](40_fastapi.md) with the Dockerfile from [43 - Docker](43_docker.md).

```bash
RG=rg-sales-api; LOC=swedencentral; ACR=acrsalesapi$RANDOM; APP=sales-api

az group create -n $RG -l $LOC
az acr create -g $RG -n $ACR --sku Basic --admin-enabled true
az acr build -r $ACR -t $APP:1.0 .                          # build image in Azure

az containerapp env create -n cae-$APP -g $RG -l $LOC
az containerapp create -n $APP -g $RG --environment cae-$APP \
  --image $ACR.azurecr.io/$APP:1.0 --registry-server $ACR.azurecr.io \
  --target-port 8000 --ingress external --min-replicas 0 --max-replicas 2

URL=$(az containerapp show -n $APP -g $RG --query properties.configuration.ingress.fqdn -o tsv)
curl https://$URL/                                          # test
echo "Docs: https://$URL/docs"

# New version
az acr build -r $ACR -t $APP:1.1 .
az containerapp update -n $APP -g $RG --image $ACR.azurecr.io/$APP:1.1

az group delete -n $RG --yes --no-wait                      # clean up everything
```

For production, prefer a managed identity with the `AcrPull` role over registry admin credentials.

## 24. Which Service to Use

> A quick mapping from need to Azure service. Start with the most managed option; go lower (VMs) only when you need the control.
>
> Use it for planning where to run a project.

| Need | Service |
|---|---|
| Run a container / API with HTTPS and autoscale | Container Apps |
| Host a web app from code (no Dockerfile) | App Service |
| Scheduled or event-triggered small jobs | Azure Functions (or Container Apps jobs) |
| Full OS control, GPU, custom software | Virtual Machines |
| Many containers, complex orchestration | AKS (Kubernetes) |
| Files, datasets, model files | Blob Storage |
| Relational database | PostgreSQL Flexible Server / Azure SQL |
| NoSQL / global JSON data | Cosmos DB |
| Secrets and keys | Key Vault |
| Container images | Container Registry |
| LLM APIs (GPT) | Azure OpenAI / AI Foundry |
| Search / RAG index | Azure AI Search |
| Big data / notebooks | Databricks, Microsoft Fabric |
| ML training and model registry | Azure Machine Learning |

## 25. Naming Conventions

> A consistent pattern for resource names. `<type prefix>-<app>-<env>[-<region>]`; some types forbid dashes.
>
> Use it in every resource; makes costs, logs and cleanup easy to follow.

| Resource | Prefix | Example |
|---|---|---|
| Resource group | `rg-` | `rg-sales-dev` |
| Virtual machine | `vm-` | `vm-ollama-dev` |
| Storage account | `st` (no dashes, lowercase) | `stsalesdev001` |
| Container registry | `acr` (no dashes) | `acrsalesdev` |
| Container app / environment | `ca-` / `cae-` | `ca-sales-api`, `cae-sales-dev` |
| App Service plan / web app | `asp-` / `app-` | `asp-sales-dev`, `app-sales-dev` |
| Key Vault | `kv-` | `kv-sales-dev` |
| PostgreSQL | `psql-` | `psql-sales-dev` |
| Virtual network / NSG | `vnet-` / `nsg-` | `vnet-sales-dev`, `nsg-vm-ollama` |

## 26. Troubleshooting

| Error / problem | Fix |
|---|---|
| `Please run 'az login' to setup account` | `az login` (or `--use-device-code` on a VM) |
| Resources not found / wrong list | Wrong subscription: `az account show`, then `az account set` |
| `The subscription is not registered to use namespace 'Microsoft.X'` | `az provider register -n Microsoft.X` |
| `QuotaExceeded` / `OperationNotAllowed` for VM size | `az vm list-usage -l <region>`; pick another size / region or request a quota increase |
| `SkuNotAvailable` / region not accepting customers | Try another region (swedencentral, northeurope, francecentral) |
| `AuthorizationFailed` | Missing role on that scope; ask an Owner for a role assignment |
| Storage / Key Vault `403` with `--auth-mode login` | Assign the data role (Storage Blob Data Contributor, Key Vault Secrets User); wait a few minutes |
| `The storage account name is already taken` | Names are global; add digits / initials |
| Container app shows default page or 404 | Wrong `--target-port`, or the app listens on 127.0.0.1 instead of 0.0.0.0 |
| Container app cannot pull image | Pass `--registry-server` (+ identity with AcrPull, or admin credentials) |
| `az containerapp` not recognized | `az extension add --name containerapp --upgrade` |
| Unexpected bill | Cost analysis by resource group; deallocate VMs, delete unused RGs, set a budget |
| Command hangs or unclear error | Re-run with `--debug`; check the Activity log in the Portal |

## 27. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Inventory

List all resources of a resource group as a table with only name and type.

<details markdown="1">
<summary>Solution</summary>

```bash
az resource list -g rg-demo --query "[].{Name:name, Type:type}" -o table
```

</details>

### Exercise 2: Secret round trip

Store a secret in Key Vault and read only its value.

<details markdown="1">
<summary>Solution</summary>

```bash
az keyvault secret set --vault-name kv-demo -n api-key --value "s3cret"
az keyvault secret show --vault-name kv-demo -n api-key --query value -o tsv
```

</details>

### Exercise 3: Deploy the capstone

Deploy the chatbot container to Azure Container Apps and delete everything afterwards.

<details markdown="1">
<summary>Solution</summary>

Follow [97 - Capstone Project](97_capstone-project.md) section 13, then `az group delete -n rg-docs-chatbot --yes --no-wait`.

</details>

---

<!-- nav:start -->
**Previous:** [47 - Terraform](47_terraform.md) | **Index:** [All guides](../README.md) | **Next:** [49 - Azure VM + Linux + Ollama](49_azure-vm-ollama.md)
<!-- nav:end -->
