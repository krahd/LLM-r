from llmr.modelito_adapter import ModelitoClient


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
        "available": True,
        "metadata": {},
    }


def test_modelito_adapter_streams_real_mock_provider():
    client = ModelitoClient(provider="mock", model="mock-model")

    assert "".join(client.stream("hello")) == "[MOCK] hello"
