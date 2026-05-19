"""Explicit tests for /api/omlx/* routes via FastAPI TestClient."""

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


def test_omlx_status_get(monkeypatch):
    expected = {"ok": True, "running": False, "version": "1.0.0"}
    monkeypatch.setattr(app_module, "omlx_status", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.get("/api/omlx/status")
    assert resp.status_code == 200
    assert resp.json() == expected


def test_omlx_local_models_get(monkeypatch):
    expected = {"ok": True, "models": ["mlx-community/Llama-3.2-3B"]}
    monkeypatch.setattr(app_module, "omlx_local_models", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.get("/api/omlx/local_models")
    assert resp.status_code == 200
    assert resp.json() == expected


def test_omlx_remote_models_get(monkeypatch):
    expected = {"ok": True, "models": ["mlx-community/Mistral-7B"]}
    monkeypatch.setattr(app_module, "omlx_remote_models", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.get("/api/omlx/remote_models")
    assert resp.status_code == 200
    assert resp.json() == expected


def test_omlx_running_models_get(monkeypatch):
    expected = {"ok": True, "models": []}
    monkeypatch.setattr(app_module, "omlx_running_models", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.get("/api/omlx/running_models")
    assert resp.status_code == 200
    assert resp.json() == expected


# ---------------------------------------------------------------------------
# POST service routes (no body required)
# ---------------------------------------------------------------------------


def test_omlx_start_post(monkeypatch):
    expected = {"ok": True, "message": "omlx started"}
    monkeypatch.setattr(app_module, "omlx_start", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/omlx/start")
    assert resp.status_code == 200
    assert resp.json() == expected


def test_omlx_stop_post(monkeypatch):
    expected = {"ok": True, "message": "omlx stopped"}
    monkeypatch.setattr(app_module, "omlx_stop", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/omlx/stop")
    assert resp.status_code == 200
    assert resp.json() == expected


def test_omlx_install_post(monkeypatch):
    expected = {"ok": True, "message": "omlx installed"}
    monkeypatch.setattr(app_module, "omlx_install", lambda: expected)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/omlx/install")
    assert resp.status_code == 200
    assert resp.json() == expected


# ---------------------------------------------------------------------------
# POST model routes — verify model arg forwarding
# ---------------------------------------------------------------------------


def test_omlx_download_post(monkeypatch):
    received: list[str] = []
    expected = {"ok": True, "message": "download started"}

    def fake_download(model: str) -> dict:
        received.append(model)
        return expected

    monkeypatch.setattr(app_module, "omlx_download", fake_download)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/omlx/download", json={"model": "test-model"})
    assert resp.status_code == 200
    assert resp.json() == expected
    assert received == ["test-model"]


def test_omlx_delete_post(monkeypatch):
    received: list[str] = []
    expected = {"ok": True, "message": "deleted"}

    def fake_delete(model: str) -> dict:
        received.append(model)
        return expected

    monkeypatch.setattr(app_module, "omlx_delete", fake_delete)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/omlx/delete", json={"model": "test-model"})
    assert resp.status_code == 200
    assert resp.json() == expected
    assert received == ["test-model"]


def test_omlx_serve_post(monkeypatch):
    received: list[str] = []
    expected = {"ok": True, "message": "serving"}

    def fake_serve(model: str) -> dict:
        received.append(model)
        return expected

    monkeypatch.setattr(app_module, "omlx_serve", fake_serve)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/omlx/serve", json={"model": "test-model"})
    assert resp.status_code == 200
    assert resp.json() == expected
    assert received == ["test-model"]


def test_omlx_stop_serving_post(monkeypatch):
    received: list[str] = []
    expected = {"ok": True, "message": "stopped serving"}

    def fake_stop_serving(model: str) -> dict:
        received.append(model)
        return expected

    monkeypatch.setattr(app_module, "omlx_stop_serving", fake_stop_serving)
    with TestClient(app_module.app) as client:
        resp = client.post("/api/omlx/stop_serving", json={"model": "test-model"})
    assert resp.status_code == 200
    assert resp.json() == expected
    assert received == ["test-model"]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_omlx_download_empty_model_returns_422(monkeypatch):
    monkeypatch.setattr(app_module, "omlx_download", lambda model: {"ok": True})
    with TestClient(app_module.app) as client:
        resp = client.post("/api/omlx/download", json={"model": ""})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Settings persistence — omlx provider and model
# ---------------------------------------------------------------------------


def test_settings_patch_persists_omlx_provider_and_model(monkeypatch):
    monkeypatch.setattr(type(app_module.settings), "save", lambda self: None)

    with TestClient(app_module.app) as client:
        resp = client.patch(
            "/api/settings",
            json={"modelito_provider": "omlx", "modelito_model": "test-omlx-model"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["modelito_provider"] == "omlx"
    assert data["modelito_model"] == "test-omlx-model"
