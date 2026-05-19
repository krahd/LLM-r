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
