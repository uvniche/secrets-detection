from fastapi.testclient import TestClient

from secure_api.config import Settings, get_settings
from secure_api.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_protected_without_server_key_returns_503() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(api_key="")
    try:
        r = client.get("/protected", headers={"X-API-Key": "any"})
        assert r.status_code == 503
    finally:
        app.dependency_overrides.clear()


def test_protected_invalid_key_returns_401() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(api_key="real-key")
    try:
        r = client.get("/protected", headers={"X-API-Key": "wrong"})
        assert r.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_protected_with_valid_key() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(api_key="test-secret")
    try:
        r = client.get("/protected", headers={"X-API-Key": "test-secret"})
        assert r.status_code == 200
        assert r.json()["message"] == "authorized"
    finally:
        app.dependency_overrides.clear()
