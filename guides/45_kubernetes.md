# 45 - Kubernetes

<!-- nav:start -->
**Previous:** [44 - Nginx, Reverse Proxy and HTTPS](44_nginx-https.md) | **Index:** [All guides](../README.md) | **Next:** [46 - Terraform](46_terraform.md)
<!-- nav:end -->

Quick reference for Kubernetes (K8s): core concepts, kubectl, Pods, Deployments, Services, Ingress, ConfigMaps / Secrets, scaling, GPUs, Helm, local clusters and Azure Kubernetes Service.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Kubernetes?

Kubernetes is a system that **runs and manages containers across many machines**. With Docker you start containers yourself on one computer; with Kubernetes you **declare what you want** ("run 3 copies of my API image, reachable at this address, restart them if they crash, add more when CPU is high") and Kubernetes continuously works to make reality match that description, across a **cluster** of machines (**nodes**).

### Mental model: desired state and a control loop

```text
YOU write YAML (desired state)          KUBERNETES CONTROL PLANE             WORKER NODES
------------------------------          -------------------------            ------------
Deployment: api                         API server stores the YAML           node 1: [pod api-1] [pod redis]
  image: myacr/api:1.2        kubectl   scheduler picks nodes for pods       node 2: [pod api-2]
  replicas: 3              ----------->  controllers keep checking:          node 3: [pod api-3]
Service: api (port 80 -> 8000)           "3 wanted, 2 running? start one!"
Ingress: api.example.com -> api                                          a pod crashes -> replaced
                                                                         a node dies   -> pods moved
```

```text
How traffic reaches your code:

internet -> Ingress (HTTPS, host / path routing) -> Service (stable name + load balancing)
         -> Pods (your containers, created and replaced by a Deployment)
```

Key idea: you never "start a container" directly. You describe objects; controllers create and heal them.

### Why use it (and when not)?

| Good fit | Probably overkill |
|---|---|
| Many services / microservices, several teams | One small app or API |
| Need auto-scaling, rolling updates, self-healing | A demo or internal tool |
| Mixed workloads: APIs, workers, GPU model servers | You have no one to operate a cluster |
| Portability across clouds / on-prem | A managed PaaS (Container Apps, App Service) is enough |

For a single FastAPI app, start with [47 - Azure](47_azure.md) Container Apps (which runs on Kubernetes under the hood, without you managing it).

### Key terms

| Term | Meaning |
|---|---|
| Cluster | Control plane + worker nodes |
| Node | A machine (VM) that runs pods |
| Pod | Smallest unit: one (or a few tightly coupled) containers with shared network |
| Deployment | Keeps N identical pods running; handles rolling updates |
| ReplicaSet | Created by a Deployment to maintain the pod count |
| Service | Stable network name / IP that load-balances to pods |
| Ingress | HTTP(S) routing from outside to Services |
| Namespace | Folder-like isolation for objects |
| ConfigMap / Secret | Configuration / sensitive values injected into pods |
| Volume / PVC | Storage mounted into pods / a request for persistent storage |
| Label / selector | Key-value tags / how objects find each other |
| Probe | Health check (liveness, readiness, startup) |
| HPA | Horizontal Pod Autoscaler: scales replicas on metrics |
| Helm | Package manager for Kubernetes apps (charts) |
| kubectl | The command-line tool to talk to the cluster |

**Where it fits:** runs images from [42 - Docker](42_docker.md); YAML from [07](07_yaml-json.md); deployed by [43 - GitHub Actions](43_github-actions.md); managed clusters on [47 - Azure](47_azure.md) (AKS); infrastructure created with [46 - Terraform](46_terraform.md); serves apps like [39 - FastAPI](39_fastapi.md) and model servers from [35 - Local LLMs](35_local-llms.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Kubernetes documentation | https://kubernetes.io/docs/home/ |
| kubectl reference | https://kubernetes.io/docs/reference/kubectl/ |
| Helm | https://helm.sh/docs/ |
| kind (local clusters) | https://kind.sigs.k8s.io/ |
| Azure Kubernetes Service (AKS) | https://learn.microsoft.com/en-us/azure/aks/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Local Cluster Setup](#1-local-cluster-setup)
2. [kubectl Basics](#2-kubectl-basics)
3. [Pods](#3-pods)
4. [Deployments](#4-deployments)
5. [Services](#5-services)
6. [Ingress (HTTP Routing and HTTPS)](#6-ingress-http-routing-and-https)
7. [ConfigMaps and Secrets](#7-configmaps-and-secrets)
8. [Health Probes](#8-health-probes)
9. [Resources: Requests and Limits](#9-resources-requests-and-limits)
10. [Scaling (Manual and Autoscaling)](#10-scaling-manual-and-autoscaling)
11. [Rolling Updates and Rollbacks](#11-rolling-updates-and-rollbacks)
12. [Storage (Volumes and PVCs)](#12-storage-volumes-and-pvcs)
13. [Jobs and CronJobs](#13-jobs-and-cronjobs)
14. [Namespaces and Contexts](#14-namespaces-and-contexts)
15. [GPUs and Model Serving](#15-gpus-and-model-serving)
16. [Helm](#16-helm)
17. [Azure Kubernetes Service (AKS)](#17-azure-kubernetes-service-aks)
18. [Complete Example: FastAPI on Kubernetes](#18-complete-example-fastapi-on-kubernetes)
19. [Troubleshooting](#19-troubleshooting)
20. [Try It](#20-try-it)

---

## 0. Flags and Parameters

> How kubectl commands are built and the most used flags. `kubectl <verb> <resource> [name] [flags]`.
>
> Use this when you see `kubectl logs -f deploy/api -n prod --tail 100` and want to know what each part does.

```text
kubectl  logs  -f  deploy/api  -n prod  --tail 100
|        |     |   |           |        |
|        |     |   |           |        +-- only the last 100 lines
|        |     |   |           +----------- -n: namespace
|        |     |   +----------------------- resource/name (a pod of this deployment)
|        |     +--------------------------- -f: follow (stream new lines)
|        +--------------------------------- verb: show container logs
+------------------------------------------ Kubernetes CLI
```

| Flag | Meaning |
|---|---|
| `-n <ns>` / `-A` | Namespace / all namespaces |
| `-f <file or folder>` | Use YAML file(s) (with `apply`, `delete`) |
| `-o wide` / `-o yaml` / `-o json` | More columns / full object as YAML / JSON |
| `-l app=api` | Filter by label |
| `-w` | Watch for changes |
| `--dry-run=client -o yaml` | Generate YAML without creating anything |
| `-it` | Interactive terminal (`exec`) |
| `-c <container>` | Pick a container in a multi-container pod |
| `--context <name>` | Target another cluster |
| `-f` (logs) / `--previous` | Follow logs / logs of the crashed previous container |

---

## 1. Local Cluster Setup

> Running a small Kubernetes cluster on your laptop for learning and testing. Docker Desktop's built-in Kubernetes, kind (Kubernetes in Docker) or minikube.
>
> Use it for learning, testing manifests before deploying to a real cluster.

```powershell
winget install -e --id Kubernetes.kubectl
winget install -e --id Kubernetes.kind             # or: enable Kubernetes in Docker Desktop settings
kind create cluster --name dev
kubectl cluster-info
kubectl get nodes
kind load docker-image sales-api:1.0 --name dev     # make a local image available to the cluster
kind delete cluster --name dev
```

## 2. kubectl Basics

> The everyday commands. Get / describe to inspect, apply to create / update from YAML, logs / exec to debug.
>
> Use it for all the time.

```bash
kubectl get pods                          # also: deploy, svc, ingress, nodes, all
kubectl get pods -o wide -A               # all namespaces, with node and IP
kubectl describe pod <name>               # details + EVENTS (first place to look when broken)
kubectl apply -f k8s/                     # create / update everything in a folder
kubectl delete -f k8s/deployment.yaml
kubectl logs <pod> -f                     # follow logs
kubectl logs deploy/api --tail 50
kubectl exec -it <pod> -- sh              # shell inside a container
kubectl port-forward svc/api 8000:80      # localhost:8000 -> service port 80
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl explain deployment.spec           # built-in docs for any field
kubectl top pods                          # CPU / memory (needs metrics-server)
```

Tip: `kubectl create deployment api --image=nginx --dry-run=client -o yaml > deployment.yaml` generates a starting YAML.

## 3. Pods

> The smallest deployable unit: one or more containers sharing network and storage. Usually created by Deployments / Jobs, not directly; each pod gets its own IP and is replaceable (cattle, not pets).
>
> Use it for understanding what runs; direct pods only for quick tests.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello
  labels:
    app: hello
spec:
  containers:
    - name: web
      image: nginx:1.27
      ports:
        - containerPort: 80
```

```bash
kubectl run tmp --rm -it --image=python:3.12-slim -- bash     # throwaway debug pod
```

## 4. Deployments

> Keeps a desired number of identical pods running and updates them safely. A pod template + `replicas`; changing the image triggers a rolling update.
>
> Use it in every stateless app (APIs, UIs, workers).

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api                     # manages pods with this label
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: acrsalesdev.azurecr.io/sales-api:1.2
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: api-config
            - secretRef:
                name: api-secrets
```

## 5. Services

> A stable address that load-balances traffic to the pods matching a label. Pods come and go (new IPs); the Service keeps one DNS name (`api` / `api.<namespace>.svc.cluster.local`).
>
> Use it in every app that other pods or the Ingress must reach.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api                       # send traffic to pods with this label
  ports:
    - port: 80                     # service port
      targetPort: 8000             # container port
  type: ClusterIP                  # internal only (default)
```

| Type | Reachable from |
|---|---|
| `ClusterIP` | Inside the cluster only (default; use with Ingress) |
| `NodePort` | Each node's IP on a high port (testing) |
| `LoadBalancer` | A cloud load balancer with a public / private IP |

Other pods call it as `http://api` (same namespace) or `http://api.prod.svc.cluster.local`.

## 6. Ingress (HTTP Routing and HTTPS)

> Routing external HTTP(S) traffic to Services by host name and path. An Ingress resource + an **ingress controller** (e.g. ingress-nginx, Application Gateway for Containers); TLS certificates often via cert-manager.
>
> Use it for exposing web apps / APIs with domains and HTTPS.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt        # if cert-manager is installed
spec:
  ingressClassName: nginx
  tls:
    - hosts: [api.example.com]
      secretName: api-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
```

The newer **Gateway API** (Gateway + HTTPRoute resources) is the successor to Ingress for advanced routing.

## 7. ConfigMaps and Secrets

> Configuration and sensitive values kept outside the image. Create them from literals / files; inject as environment variables or mounted files.
>
> Use it for model names, URLs, feature flags (ConfigMap); API keys, DB passwords (Secret).

```bash
kubectl create configmap api-config --from-literal=LLM_MODEL=claude-opus-5 --from-literal=LOG_LEVEL=info
kubectl create secret generic api-secrets --from-literal=ANTHROPIC_API_KEY=sk-ant-...
kubectl create secret generic api-secrets --from-env-file=.env          # from a .env file
kubectl get secret api-secrets -o yaml                                   # values are base64, NOT encrypted
```

Kubernetes Secrets are only base64-encoded: restrict access with RBAC, enable encryption at rest, and prefer a secret store integration (Azure Key Vault CSI driver / External Secrets Operator) in production. Never commit secret YAML with real values.

## 8. Health Probes

> Checks Kubernetes uses to know whether a container is alive and ready for traffic. HTTP / TCP / command probes; failing liveness -> restart; failing readiness -> removed from the Service until ready.
>
> Use it in every production container (especially slow-starting ones that load models).

```yaml
          readinessProbe:
            httpGet: {path: /health, port: 8000}
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet: {path: /health, port: 8000}
            periodSeconds: 20
            failureThreshold: 3
          startupProbe:                      # give slow model loading time before liveness starts
            httpGet: {path: /health, port: 8000}
            failureThreshold: 30
            periodSeconds: 10
```

## 9. Resources: Requests and Limits

> CPU / memory each container reserves and may use at most. `requests` are used for scheduling (guaranteed); `limits` cap usage (exceeding memory limit = killed, "OOMKilled").
>
> Use it always; required for autoscaling and stable clusters.

```yaml
          resources:
            requests:
              cpu: "250m"            # 0.25 CPU core
              memory: "512Mi"
            limits:
              memory: "1Gi"
```

## 10. Scaling (Manual and Autoscaling)

> Changing the number of pod replicas. `kubectl scale` manually; a HorizontalPodAutoscaler adjusts replicas based on CPU / memory / custom metrics; KEDA scales on events (queue length).
>
> Use it for variable traffic; background workers driven by queue depth ([41](41_redis-queues.md)).

```bash
kubectl scale deploy/api --replicas=5
kubectl autoscale deploy/api --min=2 --max=10 --cpu-percent=70
kubectl get hpa
```

Nodes can also autoscale (cluster autoscaler / AKS node autoscaling) so new pods have room.

## 11. Rolling Updates and Rollbacks

> Deploying a new version without downtime, and undoing it. Changing the pod template (e.g. image tag) replaces pods gradually; readiness probes gate traffic; history allows rollback.
>
> Use it in every release.

```bash
kubectl set image deploy/api api=acrsalesdev.azurecr.io/sales-api:1.3
kubectl rollout status deploy/api
kubectl rollout history deploy/api
kubectl rollout undo deploy/api                    # back to the previous version
kubectl rollout restart deploy/api                 # restart pods (e.g. to pick up new secrets)
```

Use immutable tags (commit SHA) instead of `latest` so you always know what runs.

## 12. Storage (Volumes and PVCs)

> Data that must survive pod restarts. A PersistentVolumeClaim requests storage from a StorageClass (cloud disk / file share); pods mount it.
>
> Use it for databases, model caches, uploaded files. (Prefer managed databases / blob storage for app data when possible.).

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-cache
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 50Gi
---
# in the pod spec:
#   volumes:
#     - name: models
#       persistentVolumeClaim: {claimName: model-cache}
#   containers[].volumeMounts:
#     - name: models
#       mountPath: /root/.ollama
```

Stateful services with stable identities (databases) use **StatefulSets**.

## 13. Jobs and CronJobs

> Run-to-completion work and scheduled work. A Job runs pods until they succeed; a CronJob creates Jobs on a cron schedule.
>
> Use it for batch processing, nightly RAG re-indexing, eval runs, database migrations.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: reindex-docs
spec:
  schedule: "0 2 * * *"                  # 02:00 every day
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: reindex
              image: acrsalesdev.azurecr.io/indexer:1.0
              args: ["python", "-m", "indexer.run"]
```

## 14. Namespaces and Contexts

> Separating environments / teams inside a cluster, and switching between clusters. Namespaces group objects; kubeconfig contexts point kubectl at different clusters.
>
> Use it for dev / staging / prod separation, multiple clusters.

```bash
kubectl create namespace prod
kubectl apply -f k8s/ -n prod
kubectl config get-contexts
kubectl config use-context aks-prod
kubectl config set-context --current --namespace=prod    # default namespace
```

## 15. GPUs and Model Serving

> Running GPU workloads like vLLM or Ollama on Kubernetes. GPU node pools with the NVIDIA device plugin; pods request `nvidia.com/gpu`; taints / tolerations keep other pods off expensive GPU nodes.
>
> Use it for self-hosted LLMs serving many users ([35](35_local-llms.md)).

```yaml
      containers:
        - name: vllm
          image: vllm/vllm-openai:latest
          args: ["--model", "Qwen/Qwen2.5-7B-Instruct", "--max-model-len", "8192"]
          resources:
            limits:
              nvidia.com/gpu: 1
      tolerations:
        - key: "sku"
          operator: "Equal"
          value: "gpu"
          effect: "NoSchedule"
```

Scale GPU node pools to zero when idle to save money; model downloads are large, so cache them on a PVC.

## 16. Helm

> The package manager for Kubernetes: installs whole apps (many YAML files) as one "chart" with configurable values. Add a repo, install a chart with your values, upgrade / roll back as a release.
>
> Use it for installing third-party software (ingress-nginx, cert-manager, Redis, Qdrant, monitoring), packaging your own app.

```bash
winget install -e --id Helm.Helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress ingress-nginx/ingress-nginx -n ingress --create-namespace
helm list -A
helm upgrade ingress ingress-nginx/ingress-nginx -n ingress -f values.yaml
helm rollback ingress 1 -n ingress
helm uninstall ingress -n ingress
helm create my-app                        # scaffold your own chart
```

## 17. Azure Kubernetes Service (AKS)

> Managed Kubernetes on Azure: Microsoft runs the control plane; you manage node pools and workloads. Create a cluster with `az aks`, get credentials for kubectl, attach your container registry.
>
> Use it for production Kubernetes on Azure. Details on the rest of Azure: [47](47_azure.md).

```bash
az aks create -g rg-demo -n aks-demo --node-count 2 --node-vm-size Standard_D4s_v5 \
  --generate-ssh-keys --attach-acr acrsalesdev --enable-managed-identity
az aks get-credentials -g rg-demo -n aks-demo                 # configures kubectl
kubectl get nodes
az aks nodepool add -g rg-demo --cluster-name aks-demo -n gpupool \
  --node-vm-size Standard_NC4as_T4_v3 --node-count 0 --enable-cluster-autoscaler --min-count 0 --max-count 2 \
  --node-taints sku=gpu:NoSchedule
az aks stop -g rg-demo -n aks-demo                             # stop the cluster to save cost (dev)
az aks start -g rg-demo -n aks-demo
```

AKS Automatic simplifies operations further; Azure Container Apps is simpler still if you do not need full Kubernetes.

## 18. Complete Example: FastAPI on Kubernetes

> All objects for a small API: config, secret, deployment, service, ingress. One folder of YAML files applied with `kubectl apply -f k8s/`.
>
> Use it as a template for your first real deployment.

```yaml
# k8s/app.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
data:
  LLM_MODEL: claude-opus-5
  LOG_LEVEL: info
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 2
  selector:
    matchLabels: {app: api}
  template:
    metadata:
      labels: {app: api}
    spec:
      containers:
        - name: api
          image: acrsalesdev.azurecr.io/sales-api:3f9c2ab     # commit SHA tag
          ports: [{containerPort: 8000}]
          envFrom:
            - configMapRef: {name: api-config}
            - secretRef: {name: api-secrets}                  # created with kubectl, not in Git
          resources:
            requests: {cpu: "250m", memory: "512Mi"}
            limits: {memory: "1Gi"}
          readinessProbe:
            httpGet: {path: /health, port: 8000}
          livenessProbe:
            httpGet: {path: /health, port: 8000}
            periodSeconds: 20
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector: {app: api}
  ports: [{port: 80, targetPort: 8000}]
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
spec:
  ingressClassName: nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: {name: api, port: {number: 80}}
```

```bash
kubectl create secret generic api-secrets --from-literal=ANTHROPIC_API_KEY=... -n prod
kubectl apply -f k8s/ -n prod
kubectl get pods,svc,ingress -n prod
```

## 19. Troubleshooting

| Status / problem | Meaning | Fix |
|---|---|---|
| `ImagePullBackOff` / `ErrImagePull` | Cannot download the image | Check image name / tag; registry access (`--attach-acr`, imagePullSecrets) |
| `CrashLoopBackOff` | Container starts and crashes repeatedly | `kubectl logs <pod> --previous`; missing env vars / secrets; wrong command |
| `Pending` | No node can fit the pod | `kubectl describe pod` events: insufficient CPU / memory / GPU; add nodes / lower requests |
| `OOMKilled` | Exceeded memory limit | Raise memory limit; fix memory use |
| Pod running but no traffic | Readiness failing or Service selector mismatch | Check labels match; `kubectl get endpoints api`; probe path / port |
| Ingress returns 404 / 503 | Wrong host / path / service name or no controller | Check `ingressClassName`, controller pods, service port |
| Changes not applied | Same image tag reused | Use a new tag (commit SHA) or `rollout restart` |
| `kubectl` talks to wrong cluster | Wrong context | `kubectl config current-context`; `use-context` |
| `Forbidden` errors | RBAC permissions | Ask for a role binding; check namespace |

## 20. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Deploy and expose

Run 2 replicas of nginx, expose them as a Service and open it locally.

<details markdown="1">
<summary>Solution</summary>

```bash
kubectl create deployment web --image=nginx:1.27 --replicas=2
kubectl expose deployment web --port=80
kubectl port-forward svc/web 8080:80       # open http://localhost:8080
```

</details>

### Exercise 2: Update and roll back

Scale to 5 replicas, change the image, then undo the change.

<details markdown="1">
<summary>Solution</summary>

```bash
kubectl scale deploy/web --replicas=5
kubectl set image deploy/web nginx=nginx:1.28
kubectl rollout status deploy/web
kubectl rollout undo deploy/web
```

</details>

### Exercise 3: CrashLoopBackOff

A pod keeps restarting. Which commands show why?

<details markdown="1">
<summary>Solution</summary>

```bash
kubectl describe pod <pod>              # Events at the bottom
kubectl logs <pod> --previous           # logs of the crashed container
```

Common causes: missing env var / secret, wrong command, app crashes on start, failing liveness probe.

</details>

---

<!-- nav:start -->
**Previous:** [44 - Nginx, Reverse Proxy and HTTPS](44_nginx-https.md) | **Index:** [All guides](../README.md) | **Next:** [46 - Terraform](46_terraform.md)
<!-- nav:end -->
