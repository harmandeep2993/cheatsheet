# Deploy

This folder holds deployment files, kept apart from application code. It starts empty on purpose: pick one target and add only its files.

## Typical layout

```text
deploy/
  azure/            Container Apps: one app per service, infrastructure as code (Bicep or Terraform)
    main.bicep
  k8s/              Kubernetes: one folder per service
    documents-service/
      deployment.yaml
      service.yaml
    chat-service/
      deployment.yaml
      service.yaml
    frontend/
    ingress.yaml    replaces proxy/nginx.conf: routes /api/documents, /api/chat and /
```

## Rules that stay the same on every platform

- Build one image per service from the repository root, for example `docker build -f services/chat-service/Dockerfile -t chat-service:<git-sha> .`, and push it to a registry.
- Tag images with the Git commit SHA, never only `latest`, so every deployment is traceable and can be rolled back.
- Configuration comes from environment variables; secrets come from the platform's secret store (Key Vault, Kubernetes Secrets), never from files in the image.
- Each service keeps its own database. In the cloud use a managed database (Azure Database for PostgreSQL) instead of a database container.
- The health endpoint `/health` of each service is used for readiness and liveness probes.

See guides 43 (Docker), 44 (GitHub Actions), 46 (Kubernetes), 47 (Terraform) and 48 (Azure) in the pocket guide.
