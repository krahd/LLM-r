from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterator


@dataclass
class LLMResult:
    raw_text: str


class ModelitoClient:
    """Thin wrapper around modelito.Client with no LLM-r-side fallbacks."""

    def __init__(self, provider: str, model: str) -> None:
        self.provider = provider
        self.model = model
        logging.info("[ModelitoClient] Initializing with provider='%s', model='%s'", provider, model)
        try:
            import modelito  # type: ignore
        except Exception as exc:
            logging.error("Modelito is not installed. Please install the modelito package and re-run.")
            raise RuntimeError("modelito is not installed. Install your modelito package and re-run.") from exc
        try:
            self._client = modelito.Client(provider=provider, model=model)
            self._Message = modelito.Message
        except Exception as exc:
            logging.error("Failed to initialize Modelito client: %s", exc)
            raise RuntimeError(f"Failed to initialize Modelito client: {exc}") from exc

    def complete(self, prompt: str) -> LLMResult:
        messages = [self._Message(role="user", content=prompt)]
        try:
            output = self._client.summarize(messages)
            return LLMResult(raw_text=str(output))
        except Exception as exc:
            logging.error("Modelito completion failed: %s", exc)
            raise RuntimeError(f"Modelito completion failed: {exc}") from exc

    def stream(self, prompt: str) -> Iterator[str]:
        messages = [self._Message(role="user", content=prompt)]
        try:
            for chunk in self._client.stream(messages):
                if chunk is None:
                    continue
                yield str(chunk)
        except Exception as exc:
            logging.error("Modelito stream failed: %s", exc)
            raise RuntimeError(f"Modelito stream failed: {exc}") from exc

    def list_models(self) -> list[dict[str, Any]]:
        try:
            raw = self._client.list_models()
        except Exception as exc:
            logging.error("Modelito list_models failed: %s", exc)
            raise RuntimeError(f"Modelito list_models failed: {exc}") from exc
        if not isinstance(raw, list):
            raise RuntimeError("Modelito list_models returned a non-list payload")
        return raw

    def model_metadata(self, model: str | None = None) -> dict[str, Any]:
        model_id = model or self.model
        method = getattr(self._client, "model_metadata", None) or getattr(self._client, "get_model_metadata", None)
        if method is None:
            raise RuntimeError("Modelito client does not expose model metadata API")

        try:
            metadata = method(model_id)
        except Exception as exc:
            logging.error("Modelito model metadata lookup failed: %s", exc)
            raise RuntimeError(f"Modelito model metadata lookup failed: {exc}") from exc

        if not isinstance(metadata, dict):
            raise RuntimeError("Modelito model metadata API returned a non-dict payload")
        return metadata
