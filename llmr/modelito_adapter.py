from __future__ import annotations
import logging

import logging

from dataclasses import dataclass

@dataclass
class LLMResult:
    raw_text: str

class ModelitoClient:
    """
    Wrapper for the new modelito.Client abstraction (provider-agnostic).
    """
    def __init__(self, provider: str, model: str) -> None:
        self.provider = provider
        self.model = model
        logging.info(f"[ModelitoClient] Initializing with provider='{provider}', model='{model}'")
        try:
            import modelito  # type: ignore
        except Exception as exc:
            logging.error("Modelito is not installed. Please install the modelito package and re-run.")
            raise RuntimeError("modelito is not installed. Install your modelito package and re-run.") from exc
        try:
            self._client = modelito.Client(provider=provider, model=model)
            self._Message = modelito.Message
        except Exception as exc:
            logging.error(f"Failed to initialize Modelito client for provider='{provider}', model='{model}': {exc}")
            raise RuntimeError(f"Failed to initialize Modelito client: {exc}") from exc

    def complete(self, prompt: str) -> LLMResult:
        """
        Complete a prompt using the configured model. Uses the provider-agnostic summarize() method.
        """
        try:
            messages = [self._Message(role="user", content=prompt)]
            output = self._client.summarize(messages)
            return LLMResult(raw_text=str(output))
        except Exception as exc:
            logging.error(f"Modelito completion failed: {exc}")
            raise
