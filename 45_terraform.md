# 45 - Terraform

Quick reference for Terraform: infrastructure as code for Azure and other clouds. Providers, resources, variables, state, modules, the plan / apply workflow and CI/CD.

## Introduction

### What is Terraform?

**Terraform** (by HashiCorp; **OpenTofu** is the open-source fork with the same language) lets you describe cloud infrastructure (resource groups, storage, databases, container apps, Kubernetes clusters, DNS ...) in **text files** written in **HCL** (HashiCorp Configuration Language). Terraform compares those files with what currently exists and makes the changes needed to match. This is called **Infrastructure as Code (IaC)**: your infrastructure is versioned in Git, reviewed in pull requests and reproducible for dev / test / prod.

### Mental model: desired state + a memory of what exists

```text
   *.tf files                 terraform plan                          cloud (Azure)
 (DESIRED state)  ------>  compare desired  vs  state + real cloud  ------>  "3 to add, 1 to change, 0 to destroy"
                                   |
 terraform.tfstate                 |  terraform apply
 (what Terraform created   <-------+-------------------------------->  creates / updates / deletes resources
  last time: IDs, attributes)                                         then updates the state file
```

- **Declarative**: you say *what* you want, not the steps to get there.
- **Plan before apply**: always see exactly what will change before it happens.
- **State** is Terraform's memory; it must be stored safely (remote backend) and never edited by hand.

Compared with the Azure CLI ([46](46_azure.md)): CLI commands are **imperative** ("create this now"); running them twice may fail or duplicate. Terraform is **idempotent**: applying the same files again changes nothing.

### Why use it?

- **Reproducible environments**: create dev, test and prod from the same code.
- **Reviewable changes**: infrastructure changes go through pull requests and `plan` output.
- **Documentation**: the code *is* the inventory of what exists.
- **Multi-cloud / multi-service**: one tool for Azure, AWS, GCP, GitHub, Cloudflare, Kubernetes, Datadog ...
- **Safe teardown**: `terraform destroy` removes exactly what was created.

Terraform vs Bicep: Bicep is Azure-only and native to Azure ([46](46_azure.md) section 22); Terraform works across many providers and is common in multi-cloud teams.

### Key terms

| Term | Meaning |
|---|---|
| HCL | The configuration language of Terraform |
| Provider | Plugin that talks to a platform's API (`azurerm`, `aws`, `kubernetes`) |
| Resource | One infrastructure object to manage (`azurerm_storage_account`) |
| Data source | Read-only lookup of something that already exists |
| Variable / output | Input parameter / value exported after apply |
| Local | Named expression to avoid repetition |
| State | File recording managed resources and their IDs |
| Backend | Where state is stored (local file, Azure Storage, Terraform Cloud) |
| Module | Reusable group of resources (like a function) |
| Plan / apply / destroy | Preview / execute / remove changes |
| Drift | Real infrastructure changed outside Terraform |

**Where it fits:** creates the Azure resources from [46 - Azure](46_azure.md) and clusters for [44 - Kubernetes](44_kubernetes.md); runs in [42 - GitHub Actions](42_github-actions.md); code in [04 - Git](04_git.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Terraform documentation | https://developer.hashicorp.com/terraform/docs |
| Terraform Registry (providers, modules) | https://registry.terraform.io/ |
| AzureRM provider | https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs |
| OpenTofu | https://opentofu.org/docs/ |
| Azure Verified Modules | https://azure.github.io/Azure-Verified-Modules/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install and Authenticate](#1-install-and-authenticate)
2. [Project Structure](#2-project-structure)
3. [HCL Basics](#3-hcl-basics)
4. [Providers](#4-providers)
5. [Resources and References](#5-resources-and-references)
6. [Variables and tfvars](#6-variables-and-tfvars)
7. [Outputs and Locals](#7-outputs-and-locals)
8. [Data Sources](#8-data-sources)
9. [The Workflow: init, plan, apply, destroy](#9-the-workflow-init-plan-apply-destroy)
10. [State and Remote Backends](#10-state-and-remote-backends)
11. [Loops and Conditionals](#11-loops-and-conditionals)
12. [Modules](#12-modules)
13. [Environments (dev / prod)](#13-environments-dev--prod)
14. [Example: AI App Infrastructure on Azure](#14-example-ai-app-infrastructure-on-azure)
15. [Import Existing Resources](#15-import-existing-resources)
16. [Terraform in CI/CD](#16-terraform-in-cicd)
17. [Best Practices](#17-best-practices)
18. [Troubleshooting](#18-troubleshooting)

---

## 0. Flags and Parameters

> - **What:** The Terraform commands and flags you use daily.
> - **How:** `terraform <command> [flags]` in the folder with your `.tf` files.
> - **When to use:** You see `terraform plan -var-file=prod.tfvars -out=tfplan` and want to know what each part does.

```text
terraform  plan  -var-file=prod.tfvars  -out=tfplan
|          |     |                      |
|          |     |                      +-- save the exact plan to a file (apply it later unchanged)
|          |     +------------------------- load variable values from this file
|          +------------------------------- preview changes (no changes made)
+------------------------------------------ CLI
```

| Command / flag | Meaning |
|---|---|
| `terraform init` | Download providers / modules, set up the backend (run first and after changes) |
| `terraform init -upgrade` | Upgrade providers within version constraints |
| `terraform fmt -recursive` | Format all files |
| `terraform validate` | Check syntax and internal consistency |
| `terraform plan` | Show what would change |
| `-var="name=value"` / `-var-file=x.tfvars` | Set variables |
| `-out=tfplan` | Save the plan; then `terraform apply tfplan` |
| `terraform apply` / `-auto-approve` | Apply changes / without the confirmation prompt (CI only) |
| `terraform destroy` | Delete everything in this configuration |
| `-target=resource.name` | Limit to one resource (emergencies only) |
| `terraform output [-raw name]` | Show outputs |
| `terraform state list` / `state show <addr>` | Inspect state |
| `terraform import` / `import` block | Bring existing resources under management |
| `terraform workspace list / new / select` | Multiple states for one config |

---

## 1. Install and Authenticate

> - **What:** Installing Terraform and letting it access Azure.
> - **How:** Install the CLI; for local work, log in with the Azure CLI and Terraform uses that login.
> - **When to use:** Once per machine; CI uses OIDC (section 16).

```powershell
winget install -e --id Hashicorp.Terraform        # or OpenTofu: winget install -e --id OpenTofu.Tofu
terraform -version
az login
az account set --subscription "<subscription-id>"
```

## 2. Project Structure

> - **What:** How to organise Terraform files.
> - **How:** Terraform loads all `*.tf` files in a folder; split them by purpose.
> - **When to use:** Every project.

```text
infra/
  versions.tf        terraform + provider versions, backend
  providers.tf       provider configuration
  variables.tf       input variables
  main.tf            resources
  outputs.tf         outputs
  dev.tfvars         values for dev
  prod.tfvars        values for prod
  modules/
    container_app/   reusable module
```

Add to `.gitignore`: `.terraform/`, `*.tfstate`, `*.tfstate.*`, `*.tfplan`, `crash.log`. Commit `.terraform.lock.hcl` (provider versions).

## 3. HCL Basics

> - **What:** The syntax of Terraform files.
> - **How:** Blocks with a type, labels and a body of `argument = value` pairs.
> - **When to use:** Reading and writing any `.tf` file.

```hcl
# block_type "label1" "label2" { arguments }
resource "azurerm_resource_group" "main" {
  name     = "rg-sales-dev"             # string
  location = "swedencentral"
  tags = {                              # map
    env   = "dev"
    owner = "harman"
  }
}

# Types: string, number, bool, list(...), map(...), object({...})
# Interpolation: "rg-${var.app}-${var.env}"
# Comments: # or //, block comments /* ... */
```

## 4. Providers

> - **What:** Plugins that know how to manage a platform's resources.
> - **How:** Declare required providers with version constraints; configure them.
> - **When to use:** Top of every configuration.

```hcl
# versions.tf
terraform {
  required_version = ">= 1.6"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"                # any 4.x
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

# providers.tf
provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}
```

## 5. Resources and References

> - **What:** Declaring infrastructure objects and connecting them.
> - **How:** `resource "<type>" "<local name>"`; refer to attributes with `<type>.<name>.<attribute>`; references create dependencies automatically.
> - **When to use:** The core of every configuration.

```hcl
resource "random_string" "suffix" {
  length  = 5
  upper   = false
  special = false
}

resource "azurerm_storage_account" "data" {
  name                     = "stsales${random_string.suffix.result}"   # globally unique
  resource_group_name      = azurerm_resource_group.main.name          # reference -> dependency
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
}

resource "azurerm_storage_container" "docs" {
  name                  = "docs"
  storage_account_id    = azurerm_storage_account.data.id
  container_access_type = "private"
}
```

Resource arguments are documented on the Terraform Registry (registry.terraform.io -> provider -> resource); check the docs for the provider version you use.

## 6. Variables and tfvars

> - **What:** Inputs that make configurations reusable.
> - **How:** Declare in `variables.tf` with type, description, default and validation; set values in `.tfvars` files, `-var` flags or `TF_VAR_name` env vars.
> - **When to use:** Anything that differs between environments (names, sizes, regions).

```hcl
# variables.tf
variable "env" {
  type        = string
  description = "Environment name"
  validation {
    condition     = contains(["dev", "prod"], var.env)
    error_message = "env must be dev or prod."
  }
}

variable "location" {
  type    = string
  default = "swedencentral"
}

variable "subscription_id" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true                     # hidden in plan output
}
```

```hcl
# dev.tfvars
env      = "dev"
location = "swedencentral"
```

```powershell
$env:TF_VAR_db_password = "..."        # secrets via env vars, not files in Git
terraform plan -var-file=dev.tfvars
```

## 7. Outputs and Locals

> - **What:** Values exported after apply, and named helper expressions.
> - **How:** `output` blocks print / expose values; `locals` compute reusable values.
> - **When to use:** URLs and names needed by apps or CI; consistent naming and tags.

```hcl
locals {
  prefix = "sales-${var.env}"
  tags = {
    env     = var.env
    project = "sales"
    managed = "terraform"
  }
}

output "storage_account_name" {
  value = azurerm_storage_account.data.name
}

output "app_url" {
  value = "https://${azurerm_container_app.api.ingress[0].fqdn}"
}
```

```powershell
terraform output -raw app_url
```

## 8. Data Sources

> - **What:** Reading information about existing resources or the environment.
> - **How:** `data "<type>" "<name>" { ... }` then reference `data.<type>.<name>.<attr>`.
> - **When to use:** Referencing things Terraform does not manage (shared networks, current user, existing Key Vault).

```hcl
data "azurerm_client_config" "current" {}          # tenant / object id of whoever runs Terraform

data "azurerm_key_vault" "shared" {
  name                = "kv-shared-prod"
  resource_group_name = "rg-shared"
}
```

## 9. The Workflow: init, plan, apply, destroy

> - **What:** The core loop of using Terraform.
> - **How:** Initialise once, then edit -> format -> validate -> plan -> review -> apply.
> - **When to use:** Every change.

```powershell
terraform init                                # once, and after adding providers / modules / backend
terraform fmt -recursive
terraform validate
terraform plan -var-file=dev.tfvars -out=tfplan
terraform apply tfplan                        # applies exactly what you reviewed
terraform destroy -var-file=dev.tfvars        # tear down (asks for confirmation)
```

Plan symbols: `+` create, `~` update in place, `-` destroy, `-/+` destroy and recreate (read these carefully!).

## 10. State and Remote Backends

> - **What:** Where Terraform keeps its record of managed resources.
> - **How:** By default a local `terraform.tfstate` file; teams store it remotely (e.g. an Azure Storage container) with locking so two people cannot apply at once.
> - **When to use:** As soon as more than one person / CI runs Terraform (or immediately, to be safe).

```hcl
# versions.tf
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "sttfstate12345"
    container_name       = "tfstate"
    key                  = "sales/dev.tfstate"
    use_azuread_auth     = true
  }
}
```

- State can contain secrets: protect the storage account (private, RBAC, versioning).
- Never edit state files by hand; use `terraform state mv / rm` if you must restructure.

## 11. Loops and Conditionals

> - **What:** Creating several similar resources or optional ones.
> - **How:** `count` for N copies or on / off, `for_each` over a map / set, conditional expressions `cond ? a : b`.
> - **When to use:** Several containers, one resource per environment, optional features.

```hcl
variable "containers" {
  type    = set(string)
  default = ["raw", "processed", "models"]
}

resource "azurerm_storage_container" "c" {
  for_each           = var.containers
  name               = each.value
  storage_account_id = azurerm_storage_account.data.id
}

resource "azurerm_log_analytics_workspace" "logs" {
  count               = var.env == "prod" ? 1 : 0          # only in prod
  name                = "log-${local.prefix}"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
}
```

## 12. Modules

> - **What:** Reusable packages of Terraform code.
> - **How:** A folder with its own variables / resources / outputs; call it with a `module` block; public modules from the Registry (e.g. Azure Verified Modules).
> - **When to use:** Repeating the same group of resources (e.g. "container app + identity + role assignments") across apps / environments.

```hcl
module "api_app" {
  source          = "./modules/container_app"
  name            = "ca-${local.prefix}-api"
  environment_id  = azurerm_container_app_environment.main.id
  image           = var.api_image
  target_port     = 8000
  tags            = local.tags
}

output "api_url" {
  value = module.api_app.url
}
```

## 13. Environments (dev / prod)

> - **What:** Running the same configuration for several environments.
> - **How:** Separate state per environment (different backend `key` or folders) plus different `.tfvars` files.
> - **When to use:** Any project with more than one environment.

| Approach | How | Notes |
|---|---|---|
| tfvars + separate state keys | `-var-file=prod.tfvars`, backend `key = sales/prod.tfstate` | Simple and common |
| Folder per environment | `envs/dev`, `envs/prod` calling shared modules | Clear separation, some duplication |
| Workspaces | `terraform workspace select prod` | Easy, but easy to apply to the wrong one |

## 14. Example: AI App Infrastructure on Azure

> - **What:** A realistic small stack: resource group, container registry, Log Analytics, Container Apps environment and an API container app.
> - **How:** Resources referencing each other; image and model name as variables.
> - **When to use:** Template for deploying a FastAPI / LLM app ([39](39_fastapi.md), [46](46_azure.md)).

```hcl
resource "azurerm_resource_group" "main" {
  name     = "rg-${local.prefix}"
  location = var.location
  tags     = local.tags
}

resource "azurerm_container_registry" "acr" {
  name                = "acr${replace(local.prefix, "-", "")}"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  sku                 = "Basic"
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${local.prefix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${local.prefix}"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = var.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
}

resource "azurerm_container_app" "api" {
  name                         = "ca-${local.prefix}-api"
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode                = "Single"

  template {
    min_replicas = 0
    max_replicas = 3
    container {
      name   = "api"
      image  = var.api_image
      cpu    = 0.5
      memory = "1Gi"
      env {
        name  = "LLM_MODEL"
        value = var.llm_model
      }
      env {
        name        = "ANTHROPIC_API_KEY"
        secret_name = "anthropic-key"
      }
    }
  }

  secret {
    name  = "anthropic-key"
    value = var.anthropic_api_key          # sensitive variable from env / Key Vault
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}
```

Registry credentials / managed identity for image pulls and Key Vault references are omitted for brevity; see the provider docs for `registry` and `identity` blocks.

## 15. Import Existing Resources

> - **What:** Bringing resources created by hand (Portal / CLI) under Terraform management.
> - **How:** Write the resource block, declare an `import` block with the Azure resource ID, run plan / apply; adjust the code until plan shows no changes.
> - **When to use:** Adopting Terraform for existing infrastructure.

```hcl
import {
  to = azurerm_resource_group.main
  id = "/subscriptions/<sub-id>/resourceGroups/rg-sales-dev"
}
```

```powershell
terraform plan -generate-config-out=generated.tf     # let Terraform draft the resource code
```

## 16. Terraform in CI/CD

> - **What:** Planning on pull requests and applying on merge.
> - **How:** GitHub Actions with OIDC login to Azure; plan output posted for review; apply on `main` with environment approval.
> - **When to use:** Team projects ([42 - GitHub Actions](42_github-actions.md)).

```yaml
name: Terraform

on:
  pull_request:
    paths: ["infra/**"]
  push:
    branches: [main]
    paths: ["infra/**"]

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  terraform:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infra
    env:
      ARM_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      ARM_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
      ARM_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      ARM_USE_OIDC: "true"
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: terraform fmt -check -recursive
      - run: terraform validate
      - run: terraform plan -var-file=prod.tfvars -out=tfplan
      - name: Apply (main only)
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve tfplan
```

Protect the apply step with a GitHub environment that requires approval for production.

## 17. Best Practices

> - **What:** Habits that keep Terraform safe and maintainable.
> - **How:** Small, reviewed changes; remote state; pinned versions; no secrets in code.
> - **When to use:** Always.

- Always read the **plan** before apply; watch for `-/+` (replace) on stateful resources.
- **Remote state** with locking; separate state per environment.
- **Pin** provider versions; commit `.terraform.lock.hcl`.
- **No secrets in `.tf` / `.tfvars` in Git**: use env vars, Key Vault data sources, CI secrets.
- **Tag** everything (`managed = "terraform"`, env, owner).
- Use `prevent_destroy` lifecycle on critical resources (databases).
- Do not change Terraform-managed resources in the Portal (causes drift); if you must, import / update the code.
- `terraform fmt` and `validate` in CI; consider `tflint` / `checkov` for linting and security scanning.

## 18. Troubleshooting

| Problem | Fix |
|---|---|
| `Error: Inconsistent dependency lock file` / provider not installed | `terraform init` (or `init -upgrade`) |
| `Error acquiring the state lock` | Someone / a crashed run holds the lock; wait, or `terraform force-unlock <id>` if you are sure |
| `A resource with the ID ... already exists` | Resource exists outside Terraform: import it or change the name |
| Plan wants to recreate a resource | A "force new" argument changed (name, location, SKU); check if intended |
| Plan shows changes you did not make (drift) | Someone changed it manually; decide: update code or let Terraform revert |
| `AuthorizationFailed` | Identity lacks role on the subscription / RG; check `az account show` / CI identity roles |
| Storage account name invalid | 3 to 24 lowercase letters / digits, globally unique |
| Secrets visible in state | Expected: state stores values; secure the backend; prefer Key Vault references |
| Different results on each machine | Different provider versions; commit the lock file |
