from types import SimpleNamespace

import pytest

from llmr import modelito_adapter
from llmr.modelito_adapter import ModelitoClient, _clean_model_names


def test_modelito_adapter_uses_real_mock_provider():
    client = ModelitoClient(provider="mock", model="mock-model")

    result = client.complete("hello")
    assert result.raw_text == "[MOCK] hello"

    models = client.list_models()
    assert models == [{"id": "mock-model", "provider": "mock"}]

    metadata = client.model_metadata()
    assert metadata == {
        "model": "mock-model",
        "provider": "mock",
        "available": False,
        "metadata": {},
    }


def test_modelito_adapter_streams_real_mock_provider():
    client = ModelitoClient(provider="mock", model="mock-model")

    assert "".join(client.stream("hello")) == "[MOCK] hello"


def test_clean_model_names_ignores_ollama_diagnostics():
    assert _clean_model_names([
        "NAME ID SIZE",
        "llama3:latest 365c0bd3c000 4.7 GB",
        "WARNING: Using native backtrace.",
        "0   ollama 0x00000001033e9700 ggml_print_backtrace + 276",
        "libc++abi.dylib crash line",
    ]) == ["llama3:latest"]


def test_omlx_local_models_has_consistent_shape(monkeypatch):
    fake_modelito = SimpleNamespace(
        list_local_omlx_models=lambda: ["mlx-community/Qwen2.5-7B"]
    )
    monkeypatch.setattr(modelito_adapter, "_modelito_module", lambda: fake_modelito)

    payload = modelito_adapter.omlx_local_models()
    assert set(payload.keys()) >= {"ok", "message", "models"}
    assert payload["ok"] is True
    assert payload["models"] == ["mlx-community/Qwen2.5-7B"]


def test_omlx_missing_method_returns_clear_error(monkeypatch):
    fake_modelito = SimpleNamespace()
    monkeypatch.setattr(modelito_adapter, "_modelito_module", lambda: fake_modelito)

    payload = modelito_adapter.omlx_local_models()
    assert payload["ok"] is False
    assert payload["runtime"] == "omlx"
    assert payload["operation"] == "list-local-models"
    assert "LLM-r tried:" in payload["message"]
    assert "Modelito version" in payload["message"]
    assert payload["models"] == []


@pytest.mark.parametrize(
    ("operation", "candidates", "call"),
    [
        (
            "list-local-models",
            ["list_local_omlx_models", "list_local_models_omlx", "list_omlx_models"],
            lambda: modelito_adapter.omlx_local_models(),
        ),
        (
            "list-remote-models",
            ["list_remote_omlx_models", "list_omlx_remote_models", "list_available_omlx_models"],
            lambda: modelito_adapter.omlx_remote_models(),
        ),
        (
            "start",
            ["start_omlx", "start_omlx_service"],
            lambda: modelito_adapter.omlx_start(),
        ),
        (
            "stop",
            ["stop_omlx", "stop_omlx_service"],
            lambda: modelito_adapter.omlx_stop(),
        ),
        (
            "install",
            ["install_omlx", "install_omlx_runtime"],
            lambda: modelito_adapter.omlx_install(),
        ),
        (
            "download",
            ["download_omlx_model", "download_model_omlx"],
            lambda: modelito_adapter.omlx_download("mlx-community/Qwen2.5-7B"),
        ),
        (
            "delete",
            ["delete_omlx_model", "delete_model_omlx"],
            lambda: modelito_adapter.omlx_delete("mlx-community/Qwen2.5-7B"),
        ),
        (
            "serve",
            ["serve_omlx_model", "serve_model_omlx"],
            lambda: modelito_adapter.omlx_serve("mlx-community/Qwen2.5-7B"),
        ),
        (
            "stop-serving",
            ["stop_omlx_model", "stop_serving_omlx_model", "unserve_omlx_model"],
            lambda: modelito_adapter.omlx_stop_serving("mlx-community/Qwen2.5-7B"),
        ),
    ],
)
def test_omlx_missing_capability_payload(monkeypatch, operation, candidates, call):
    fake_modelito = SimpleNamespace()
    monkeypatch.setattr(modelito_adapter, "_modelito_module", lambda: fake_modelito)

    payload = call()

    assert payload["ok"] is False
    assert payload["runtime"] == "omlx"
    assert payload["operation"] == operation
    assert payload["candidates"] == candidates
    assert "LLM-r tried:" in payload["message"]
    assert payload["models"] == []


def test_ollama_missing_capability_payload(monkeypatch):
    fake_modelito = SimpleNamespace()
    monkeypatch.setattr(modelito_adapter, "_modelito_module", lambda: fake_modelito)

    payload = modelito_adapter.ollama_serve("llama3:latest")

    assert payload["ok"] is False
    assert payload["runtime"] == "ollama"
    assert payload["operation"] == "serve"
    assert payload["candidates"] == ["serve_model"]
    assert "LLM-r tried:" in payload["message"]
    assert payload["models"] == []


def test_ollama_status_has_consistent_shape(monkeypatch):
    fake_service = SimpleNamespace(
        inspect_service_state=lambda: {"installed": True, "running": False}
    )
    fake_modelito = SimpleNamespace(ollama_service=fake_service)
    monkeypatch.setattr(modelito_adapter, "_modelito_module", lambda: fake_modelito)

    payload = modelito_adapter.ollama_status()
    assert set(payload.keys()) >= {"ok", "message", "models"}
    assert payload["ok"] is True
    assert payload["models"] == []


def test_modelito_models_falls_back_to_configured_model(monkeypatch):
    class BrokenClient:
        def __init__(self, provider: str, model: str):
            self.provider = provider
            self.model = model

        def list_models(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(modelito_adapter, "ModelitoClient", BrokenClient)
    assert modelito_adapter.modelito_models("omlx", "fallback-model") == ["fallback-model"]
