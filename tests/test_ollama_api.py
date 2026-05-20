"""Explicit tests for /api/ollama/* routes via FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient

from llmr import app as app_module
from llmr.macros import init_macro_store
from llmr.sessions import SessionStore


@pytest.fixture(autouse=True)
def _reset_app_state(tmp_path, monkeypatch):
    """Minimal app-state isolation: reset stores and disable auth token."""
    app_module.store = app_module.PlanStore(persist_path=str(tmp_path / "plans.json"))
    app_module.session_store = SessionStore(persist_path=str(tmp_path / "sessions.json"))
    app_module._plan_session_index.clear()
    init_macro_store(str(tmp_path / "macros.json"))
    monkeypatch.setattr(app_module.settings, "api_token", "")


# ---------------------------------------------------------------------------
# GET routes
# ---------------------------------------------------------------------------


def test_ollama_status_get(monkeypatch):
    expected = {"ok": True, "running": False, "version": "1.0.0"}
    monkeypatch.setattr(app_module, "ollama_status", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.get("/api/ollama/status")
    assert resp.status_code == 200
    assert resp.json() == expected


def test_ollama_local_models_get(monkeypatch):
    expected = {"ok": True, "models": ["llama3.2:latest"]}
    monkeypatch.setattr(app_module, "ollama_local_models", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.get("/api/ollama/local_models")
    assert resp.status_code == 200
    assert resp.json() == expected


def test_ollama_remote_models_get(monkeypatch):
    expected = {"ok": True, "models": ["qwen3:latest"]}
    monkeypatch.setattr(app_module, "ollama_remote_models", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.get("/api/ollama/remote_models")
    assert resp.status_code == 200
    assert resp.json() == expected


def test_ollama_running_models_get(monkeypatch):
    expected = {"ok": True, "models": []}
    monkeypatch.setattr(app_module, "ollama_running_models", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.get("/api/ollama/running_models")
    assert resp.status_code == 200
    assert resp.json() == expected


# ---------------------------------------------------------------------------
# POST service routes (no body required)
# ---------------------------------------------------------------------------


def test_ollama_start_post(monkeypatch):
    expected = {"ok": True, "message": "ollama started"}
    monkeypatch.setattr(app_module, "ollama_start", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/ollama/start")
    assert resp.status_code == 200
    assert resp.json() == expected


def test_ollama_stop_post(monkeypatch):
    expected = {"ok": True, "message": "ollama stopped"}
    monkeypatch.setattr(app_module, "ollama_stop", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/ollama/stop")
    assert resp.status_code == 200
    assert resp.json() == expected


def test_ollama_install_post(monkeypatch):
    expected = {"ok": True, "message": "ollama install opened"}
    monkeypatch.setattr(app_module, "ollama_install", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/ollama/install")
    assert resp.status_code == 200
    assert resp.json() == expected


# ---------------------------------------------------------------------------
# POST model routes — verify model arg forwarding
# ---------------------------------------------------------------------------


def test_ollama_download_post(monkeypatch):
    received: list[str] = []
    expected = {"ok": True, "message": "download started"}

    def fake_download(model: str) -> dict:
        received.append(model)
        return expected

    monkeypatch.setattr(app_module, "ollama_download", fake_download)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/ollama/download", json={"model": "test-model"})
    assert resp.status_code == 200
    assert resp.json() == expected
    assert received == ["test-model"]


def test_ollama_delete_post(monkeypatch):
    received: list[str] = []
    expected = {"ok": True, "message": "deleted"}

    def fake_delete(model: str) -> dict:
        received.append(model)
        return expected

    monkeypatch.setattr(app_module, "ollama_delete", fake_delete)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/ollama/delete", json={"model": "test-model"})
    assert resp.status_code == 200
    assert resp.json() == expected
    assert received == ["test-model"]


def test_ollama_serve_post(monkeypatch):
    received: list[str] = []
    expected = {"ok": True, "message": "serving"}

    def fake_serve(model: str) -> dict:
        received.append(model)
        return expected

    monkeypatch.setattr(app_module, "ollama_serve", fake_serve)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/ollama/serve", json={"model": "test-model"})
    assert resp.status_code == 200
    assert resp.json() == expected
    assert received == ["test-model"]


def test_ollama_stop_serving_post(monkeypatch):
    received: list[str] = []
    expected = {"ok": True, "message": "stopped serving"}

    def fake_stop_serving(model: str) -> dict:
        received.append(model)
        return expected

    monkeypatch.setattr(app_module, "ollama_stop_serving", fake_stop_serving)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/ollama/stop_serving", json={"model": "test-model"})
    assert resp.status_code == 200
    assert resp.json() == expected
    assert received == ["test-model"]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_ollama_download_empty_model_returns_422(monkeypatch):
    monkeypatch.setattr(app_module, "ollama_download", lambda model: {"ok": True})
    with TestClient(app_module.app) as client:
        resp = client.post("/api/ollama/download", json={"model": ""})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Settings persistence — ollama provider and model
# ---------------------------------------------------------------------------


def test_settings_patch_persists_ollama_provider_and_model(monkeypatch):
    monkeypatch.setattr(type(app_module.settings), "save", lambda self: None)

    with TestClient(app_module.app) as client:
        resp = client.patch(
            "/api/settings",
            json={"modelito_provider": "ollama", "modelito_model": "llama3.2:latest"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["modelito_provider"] == "ollama"
    assert data["modelito_model"] == "llama3.2:latest"
