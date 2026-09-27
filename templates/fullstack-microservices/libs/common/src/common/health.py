"""Health endpoint used by Docker healthchecks, Kubernetes probes and the proxy."""

from fastapi import APIRouter


def health_router(service_name: str) -> APIRouter:
    """Router with GET /health returning the service name and status."""
    router = APIRouter(tags=["health"])

    @router.get("/health")
    def health() -> dict[str, str]:
        """Liveness / readiness check."""
        return {"status": "ok", "service": service_name}

    return router
