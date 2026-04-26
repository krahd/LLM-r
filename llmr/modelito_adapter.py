from __future__ import annotations
import logging

from dataclasses import dataclass


@dataclass
class LLMResult:
    raw_text: str



class ModelitoClient:
    """
    Adapter for modelito with compatibility fallbacks.

    This class encapsulates all LLM/model logic. It supports local and cloud models (OpenAI, Anthropic, Google, Ollama, etc.)
    via the Modelito library. Provider and model are selected via environment variables or config.

    Example providers: 'openai', 'anthropic', 'google', 'ollama', etc.
    Example models: 'gpt-4.1-mini', 'claude-3-sonnet', 'gemini-pro', 'llama3', etc.

    Users must install and configure Modelito separately. API keys and credentials are handled by Modelito, not LLM-r.
    """

    def __init__(self, provider: str, model: str) -> None:
        self.provider = provider
        self.model = model

        logging.info(f"[ModelitoClient] Initializing with provider='{provider}', model='{model}'")

        try:
            import modelito  # type: ignore
        except Exception as exc:  # pragma: no cover
            logging.error(
                "Modelito is not installed. Please install the modelito package and re-run.")
            raise RuntimeError(
                "modelito is not installed. Install your modelito package and re-run.") from exc

        try:
            self._client = modelito.Client(provider=provider, model=model)
        except Exception as exc:
            logging.error(
                f"Failed to initialize Modelito client for provider='{provider}', model='{model}': {exc}")
            raise RuntimeError(f"Failed to initialize Modelito client: {exc}") from exc

    def complete(self, prompt: str) -> LLMResult:
        """
        Complete a prompt using the configured model. Tries both 'complete' and 'chat' methods for compatibility.
        """
        try:
            if hasattr(self._client, "complete"):
                output = self._client.complete(prompt)
                return LLMResult(raw_text=str(output))

            if hasattr(self._client, "chat"):
                output = self._client.chat([{"role": "user", "content": prompt}])
                return LLMResult(raw_text=str(output))

            logging.error("Modelito client does not expose complete() or chat() methods.")
            raise RuntimeError("modelito client does not expose complete() or chat()")
        except Exception as exc:
            logging.error(f"Modelito completion failed: {exc}")
            raise
