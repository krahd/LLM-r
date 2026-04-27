from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterator


@dataclass
class LLMResult:
    raw_text: str


class ModelitoClient:
    """Wrapper for modelito.Client abstraction (provider-agnostic)."""

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
        """Complete a prompt using the configured model via summarize()."""
        messages = [self._Message(role="user", content=prompt)]
        try:
            output = self._client.summarize(messages)
            return LLMResult(raw_text=str(output))
        except Exception as exc:
            logging.error("Modelito completion failed: %s", exc)
            raise RuntimeError(f"Modelito completion failed: {exc}") from exc

    def stream(self, prompt: str) -> Iterator[str]:
        """Stream completion chunks. Falls back to summarize() when stream is unavailable."""
        messages = [self._Message(role="user", content=prompt)]
        if not hasattr(self._client, "stream"):
            yield self.complete(prompt).raw_text
            return

        try:
            for chunk in self._client.stream(messages):
                if chunk is None:
                    continue
                yield str(chunk)
        except Exception as exc:
            logging.error("Modelito stream failed: %s", exc)
            raise RuntimeError(f"Modelito stream failed: {exc}") from exc

    def list_models(self) -> list[dict[str, Any]]:
        """Return available models as normalized dictionaries."""
        if not hasattr(self._client, "list_models"):
            return [{"id": self.model, "provider": self.provider, "default": True}]

        try:
            raw = self._client.list_models()
        except Exception as exc:
            logging.error("Modelito list_models failed: %s", exc)
            raise RuntimeError(f"Modelito list_models failed: {exc}") from exc

        models: list[dict[str, Any]] = []
        for item in raw or []:
            if isinstance(item, dict):
                mid = str(item.get("id") or item.get("model") or "")
                payload = {"id": mid or self.model, **item}
            else:
                payload = {"id": str(item)}
            payload.setdefault("provider", self.provider)
            models.append(payload)
        return models

    def model_metadata(self, model: str | None = None) -> dict[str, Any]:
        """Return metadata for a model when supported by provider."""
        model_id = model or self.model
        method = getattr(self._client, "model_metadata", None) or getattr(self._client, "get_model_metadata", None)
        if not method:
            return {"model": model_id, "provider": self.provider, "available": False, "metadata": {}}

        try:
            metadata = method(model_id)
        except Exception as exc:
            logging.error("Modelito model metadata lookup failed: %s", exc)
            raise RuntimeError(f"Modelito model metadata lookup failed: {exc}") from exc

        return {
            "model": model_id,
            "provider": self.provider,
            "available": True,
            "metadata": metadata if isinstance(metadata, dict) else {"value": metadata},
        }
