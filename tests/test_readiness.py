"""Tests for the GET /api/readiness endpoint and compute_readiness helper."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from llmr import app as app_module
from llmr.app import app
from llmr.macros import init_macro_store
from llmr.planner import PlanStore
from llmr.sessions import SessionStore

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_app_state(tmp_path):
    app_module.store = PlanStore(persist_path=str(tmp_path / "plans.json"))
    app_module.session_store = SessionStore(
        persist_path=str(tmp_path / "sessions.json")
    )
    app_module._plan_session_index.clear()
    init_macro_store(str(tmp_path / "macros.json"))
    app_module._osc_reply_listener = None
    yield


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def default_settings():
    """Return a fake settings object that satisfies all readiness checks."""
    s = MagicMock()
    s.modelito_provider = "openai"
    s.modelito_model = "gpt-4.1-mini"
    s.ableton_host = "127.0.0.1"
    s.ableton_port = 11000
    s.device_bridge_enabled = True
    s.device_bridge_host = "127.0.0.1"
    s.device_bridge_port = 8788
    s.osc_reply_enabled = False
    s.osc_reply_host = "127.0.0.1"
    s.osc_reply_port = 9000
    return s


# ── Unit tests for compute_readiness ─────────────────────────────────────────


class TestComputeReadiness:
    def test_all_ok(self, default_settings):
        from llmr.readiness import compute_readiness

        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            r = compute_readiness(default_settings)

        assert r["ready_to_plan"] is True
        assert r["ready_to_dry_run"] is True
        assert r["ready_to_execute"] is True
        assert r["model"]["ok"] is True
        assert r["ableton_osc"]["ok"] is True
        assert r["errors"] == []

    def test_missing_model_provider(self, default_settings):
        from llmr.readiness import compute_readiness

        default_settings.modelito_provider = ""
        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            r = compute_readiness(default_settings)

        assert r["ready_to_plan"] is False
        assert r["ready_to_dry_run"] is False
        assert r["ready_to_execute"] is False
        assert r["model"]["ok"] is False
        assert r["model"]["next_step"] != ""
        assert len(r["errors"]) >= 1

    def test_missing_model_name(self, default_settings):
        from llmr.readiness import compute_readiness

        default_settings.modelito_model = ""
        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            r = compute_readiness(default_settings)

        assert r["ready_to_plan"] is False
        assert r["model"]["ok"] is False

    def test_dry_run_ready_without_osc(self, default_settings):
        """Dry-run planning works even when AbletonOSC host is not set."""
        from llmr.readiness import compute_readiness

        default_settings.ableton_host = ""
        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            r = compute_readiness(default_settings)

        assert r["ready_to_dry_run"] is True, "Dry-run must work without OSC"
        assert r["ready_to_execute"] is False
        assert r["ableton_osc"]["ok"] is False

    def test_device_bridge_disabled(self, default_settings):
        """Disabled Device Bridge is not an error for readiness."""
        from llmr.readiness import compute_readiness

        default_settings.device_bridge_enabled = False
        r = compute_readiness(default_settings)

        assert r["device_bridge"]["ok"] is None
        assert r["device_bridge"]["enabled"] is False
        # disabled bridge should not block planning or execution
        assert r["ready_to_plan"] is True
        assert r["ready_to_execute"] is True

    def test_device_bridge_unreachable_warning(self, default_settings):
        """Enabled but unreachable Device Bridge appears as a warning, not an error."""
        from llmr.readiness import compute_readiness

        with patch(
            "llmr.device_bridge.health",
            return_value={"ok": False, "error": "Connection refused"},
        ):
            r = compute_readiness(default_settings)

        assert r["device_bridge"]["ok"] is False
        assert any("Device Bridge" in w for w in r["warnings"])
        # Still ready to plan and execute (device_load would fail, but OSC actions work)
        assert r["ready_to_plan"] is True

    def test_osc_reply_listener_running(self, default_settings):
        from llmr.readiness import compute_readiness

        default_settings.osc_reply_enabled = True
        listener = MagicMock()
        listener.status.return_value = {
            "enabled": True,
            "listening": True,
            "host": "127.0.0.1",
            "port": 9000,
            "started_at": "2026-01-01T00:00:00",
            "error": None,
        }
        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            r = compute_readiness(default_settings, osc_reply_listener=listener)

        assert r["osc_replies"]["ok"] is True
        assert r["osc_replies"]["listening"] is True

    def test_osc_reply_listener_not_running(self, default_settings):
        from llmr.readiness import compute_readiness

        default_settings.osc_reply_enabled = True
        # No listener passed
        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            r = compute_readiness(default_settings, osc_reply_listener=None)

        assert r["osc_replies"]["ok"] is False
        assert any("OSC reply" in w for w in r["warnings"])

    def test_osc_reply_disabled_is_ok(self, default_settings):
        from llmr.readiness import compute_readiness

        default_settings.osc_reply_enabled = False
        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            r = compute_readiness(default_settings, osc_reply_listener=None)

        assert r["osc_replies"]["ok"] is True, "Disabled listener should not be an error"

    def test_response_schema_keys(self, default_settings):
        """All expected top-level keys are present."""
        from llmr.readiness import compute_readiness

        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            r = compute_readiness(default_settings)

        required = {
            "ready_to_plan",
            "ready_to_dry_run",
            "ready_to_execute",
            "model",
            "ableton_osc",
            "device_bridge",
            "osc_replies",
            "server",
            "warnings",
            "errors",
        }
        assert required <= set(r.keys())

    def test_model_subkeys(self, default_settings):
        from llmr.readiness import compute_readiness

        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            r = compute_readiness(default_settings)

        for key in ("ok", "provider", "model", "message", "next_step"):
            assert key in r["model"]

    def test_device_bridge_subkeys(self, default_settings):
        from llmr.readiness import compute_readiness

        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            r = compute_readiness(default_settings)

        for key in ("ok", "enabled", "host", "port", "message", "next_step"):
            assert key in r["device_bridge"]


# ── Integration tests via API endpoint ───────────────────────────────────────


class TestReadinessEndpoint:
    def test_readiness_endpoint_returns_200(self, client, monkeypatch):
        monkeypatch.setattr(app_module, "_osc_reply_listener", None)
        with patch("llmr.device_bridge.health", return_value={"ok": False}):
            r = client.get("/api/readiness")
        assert r.status_code == 200

    def test_readiness_endpoint_shape(self, client, monkeypatch):
        monkeypatch.setattr(app_module, "_osc_reply_listener", None)
        with patch("llmr.device_bridge.health", return_value={"ok": False}):
            data = client.get("/api/readiness").json()

        for key in (
            "ready_to_plan",
            "ready_to_dry_run",
            "ready_to_execute",
            "model",
            "ableton_osc",
            "device_bridge",
            "osc_replies",
            "server",
            "warnings",
            "errors",
        ):
            assert key in data, f"Missing key: {key}"

    def test_readiness_endpoint_with_listener(self, client, monkeypatch):
        listener = MagicMock()
        listener.status.return_value = {
            "enabled": True,
            "listening": True,
            "host": "127.0.0.1",
            "port": 9000,
            "started_at": None,
            "error": None,
        }
        monkeypatch.setattr(app_module, "_osc_reply_listener", listener)
        with patch("llmr.device_bridge.health", return_value={"ok": True}):
            data = client.get("/api/readiness").json()
        assert data["osc_replies"]["listening"] is True

    def test_readiness_reflects_settings(self, client, monkeypatch):
        """Endpoint uses live settings, not stale cached values."""
        monkeypatch.setattr(app_module.settings, "modelito_provider", "")
        monkeypatch.setattr(app_module.settings, "modelito_model", "")
        monkeypatch.setattr(app_module, "_osc_reply_listener", None)
        with patch("llmr.device_bridge.health", return_value={"ok": False}):
            data = client.get("/api/readiness").json()
        assert data["ready_to_plan"] is False
        assert data["model"]["ok"] is False
