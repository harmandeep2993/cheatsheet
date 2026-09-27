"""Tests for the shared library: request IDs and the health router."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from common import REQUEST_ID_HEADER, RequestIdMiddleware, current_request_id, health_router


def make_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health_router("demo-service"))

    @app.get("/whoami")
    def whoami() -> dict:
        return {"request_id": current_request_id()}

    return app


def test_health_reports_service_name():
    assert TestClient(make_app()).get("/health").json() == {"status": "ok", "service": "demo-service"}


def test_request_id_is_reused_from_caller():
    response = TestClient(make_app()).get("/whoami", headers={REQUEST_ID_HEADER: "abc123"})
    assert response.json() == {"request_id": "abc123"}
    assert response.headers[REQUEST_ID_HEADER] == "abc123"


def test_request_id_is_generated_when_missing():
    response = TestClient(make_app()).get("/whoami")
    assert response.headers[REQUEST_ID_HEADER] == response.json()["request_id"]
    assert current_request_id() is None
