from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMResult:
    raw_text: str


class ModelitoClient:
    """Adapter for modelito with compatibility fallbacks."""

    def __init__(self, provider: str, model: str) -> None:
        self.provider = provider
        self.model = model

        try:
            import modelito  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("modelito is not installed. Install your modelito package and re-run.") from exc

        self._client = modelito.Client(provider=provider, model=model)

    def complete(self, prompt: str) -> LLMResult:
        if hasattr(self._client, "complete"):
            output = self._client.complete(prompt)
            return LLMResult(raw_text=str(output))

        if hasattr(self._client, "chat"):
            output = self._client.chat([{"role": "user", "content": prompt}])
            return LLMResult(raw_text=str(output))

        raise RuntimeError("modelito client does not expose complete() or chat()")
