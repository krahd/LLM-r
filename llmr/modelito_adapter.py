from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Iterator
from urllib.request import urlopen


@dataclass
class _LocalMessage:
    role: str
    content: str


class _LocalMockClient:
    def __init__(self, provider: str, model: str) -> None:
        self.provider = provider
        self.model = model

    def summarize(self, messages: list[_LocalMessage]) -> str:
        prompt = messages[-1].content if messages else ""
        return f"[MOCK] {prompt}"

    def stream(self, messages: list[_LocalMessage]) -> Iterator[str]:
        yield self.summarize(messages)

    def list_models(self) -> list[dict[str, str]]:
        return [{"id": self.model, "provider": self.provider}]


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
            if provider == "mock":
                logging.warning(
                    "Modelito is not installed. Using built-in local mock provider for tests."
                )
                self._client = _LocalMockClient(provider=provider, model=model)
                self._Message = _LocalMessage
                self._normalize_models = None
                self._normalize_metadata = None
                return
            logging.error(
                "Modelito is not installed. Please install the modelito package and re-run.")
            raise RuntimeError(
                "modelito is not installed. Install your modelito package and re-run.") from exc
        try:
            self._client = modelito.Client(provider=provider, model=model)
            self._Message = modelito.Message
            self._normalize_models = getattr(modelito, "normalize_models", None)
            self._normalize_metadata = getattr(modelito, "normalize_metadata", None)
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
        stream_method = getattr(self._client, "stream", None)
        provider_stream_method = getattr(getattr(self._client, "provider", None), "stream", None)

        try:
            if callable(stream_method):
                yielded = False
                for chunk in stream_method(messages):
                    if chunk is None:
                        continue
                    yielded = True
                    yield str(chunk)
                if yielded:
                    return

            if callable(provider_stream_method):
                yielded = False
                for chunk in provider_stream_method(messages):
                    if chunk is None:
                        continue
                    yielded = True
                    yield str(chunk)
                if yielded:
                    return

            yield self.complete(prompt).raw_text
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

        normalizer = self._normalize_models
        if callable(normalizer):
            models = list(normalizer(raw))
        else:
            models = []
            for item in raw or []:
                if isinstance(item, dict):
                    mid = str(item.get("id") or item.get("model") or "")
                    payload = {"id": mid or self.model, **item}
                else:
                    payload = {"id": str(item)}
                models.append(payload)

        for payload in models:
            payload.setdefault("provider", self.provider)
        return models

    def model_metadata(self, model: str | None = None) -> dict[str, Any]:
        """Return metadata for a model when supported by provider."""
        model_id = model or self.model
        method = getattr(self._client, "model_metadata", None) or getattr(
            self._client, "get_model_metadata", None)
        if not method:
            return {"model": model_id, "provider": self.provider, "available": False, "metadata": {}}

        try:
            metadata = method(model_id)
        except Exception as exc:
            logging.error("Modelito model metadata lookup failed: %s", exc)
            raise RuntimeError(f"Modelito model metadata lookup failed: {exc}") from exc

        normalizer = self._normalize_metadata
        normalized_metadata = normalizer(metadata) if callable(normalizer) else metadata

        return {
            "model": model_id,
            "provider": self.provider,
            "available": bool(normalized_metadata),
            "metadata": (
                normalized_metadata
                if isinstance(normalized_metadata, dict)
                else {"value": normalized_metadata}
            ),
        }


def modelito_models(provider: str, model: str) -> list[str]:
    """Return normalized model ids for a provider."""
    models = ModelitoClient(provider=provider, model=model).list_models()
    ids: list[str] = []
    for item in models:
        if isinstance(item, dict):
            model_id = str(item.get("id") or item.get("model") or "").strip()
        else:
            model_id = str(item).strip()
        if model_id and model_id not in ids:
            ids.append(model_id)
    if model and model not in ids:
        ids.insert(0, model)
    return ids


def _modelito_module():
    try:
        import modelito  # type: ignore
    except Exception as exc:
        raise RuntimeError("modelito is not installed. Install modelito to manage Ollama.") from exc
    return modelito


def _ollama_payload(ok: bool, message: str, **extra: Any) -> dict[str, Any]:
    return {"ok": ok, "message": message, **extra}


_MODEL_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*(?::[A-Za-z0-9._/-]+)?$")
_OLLAMA_LIBRARY_CARD_RE = re.compile(
    r'<a href="/library/([^"/:?#]+)"\s+class="group w-full space-y-5">',
    re.S,
)


def _clean_model_names(values: list[Any]) -> list[str]:
    models: list[str] = []
    for value in values:
        raw = str(value).strip()
        if not raw:
            continue
        lowered = raw.lower()
        if any(token in lowered for token in (
            "warning:", "traceback", "exception", "backtrace", "sigabrt",
            "corefoundation", "libc++abi", "libobjc", "dylib",
        )):
            continue
        name = raw.split()[0]
        if not name or not _MODEL_NAME_RE.match(name):
            continue
        if name.isdigit() or name.lower() in {
            "name", "model", "models", "warning", "error", "traceback", "see",
        }:
            continue
        if name not in models:
            models.append(name)
    return models


def _ollama_library_models() -> list[str]:
    with urlopen("https://ollama.com/library", timeout=12) as response:
        html = response.read().decode("utf-8", errors="replace")
    return _clean_model_names(_OLLAMA_LIBRARY_CARD_RE.findall(html))


def ollama_status() -> dict[str, Any]:
    modelito = _modelito_module()
    service = getattr(modelito, "ollama_service", None)
    try:
        state = service.inspect_service_state() if service else {}
    except Exception as exc:
        return _ollama_payload(False, f"Unable to inspect Ollama: {exc}")

    installed = bool(state.get("installed"))
    running = bool(state.get("running"))
    message = "Ollama is running." if running else (
        "Ollama is installed but not running." if installed else "Ollama is not installed."
    )
    return _ollama_payload(True, message, **state)


def ollama_local_models() -> dict[str, Any]:
    modelito = _modelito_module()
    try:
        models = _clean_model_names(list(getattr(modelito, "list_local_models")()))
    except Exception as exc:
        return _ollama_payload(False, f"Unable to list local Ollama models: {exc}", models=[])
    return _ollama_payload(True, f"Loaded {len(models)} local model(s).", models=models)


def ollama_running_models() -> dict[str, Any]:
    """Return models currently loaded by Ollama.

    Modelito has changed helper names across versions, so use it when available
    and fall back to the stable Ollama CLI command.
    """
    models: list[str] = []
    try:
        modelito = _modelito_module()
    except RuntimeError:
        modelito = None

    for method_name in ("list_running_models", "list_loaded_models", "running_models"):
        method = getattr(modelito, method_name, None) if modelito else None
        if callable(method):
            try:
                models = _clean_model_names(list(method()))
                return _ollama_payload(
                    True,
                    f"{len(models)} Ollama model(s) currently served.",
                    models=models,
                )
            except Exception:
                break

    try:
        proc = subprocess.run(
            ["ollama", "ps"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except FileNotFoundError:
        return _ollama_payload(False, "Ollama CLI is not installed.", models=[])
    except Exception as exc:
        return _ollama_payload(False, f"Unable to inspect served Ollama models: {exc}", models=[])

    if proc.returncode != 0:
        message = (proc.stderr or proc.stdout or "ollama ps failed").strip()
        return _ollama_payload(False, message, models=[])

    rows = proc.stdout.splitlines()[1:]
    models = _clean_model_names(rows)
    return _ollama_payload(True, f"{len(models)} Ollama model(s) currently served.", models=models)


def ollama_remote_models() -> dict[str, Any]:
    modelito = _modelito_module()
    try:
        models = _clean_model_names(list(getattr(modelito, "list_remote_models")()))
        if not models:
            models = _ollama_library_models()
    except Exception as exc:
        try:
            models = _ollama_library_models()
        except Exception:
            return _ollama_payload(False, f"Unable to list online Ollama models: {exc}", models=[])
    return _ollama_payload(True, f"Loaded {len(models)} online model(s).", models=models)


def ollama_start() -> dict[str, Any]:
    modelito = _modelito_module()
    try:
        ok = bool(getattr(modelito, "start_ollama")())
    except Exception as exc:
        return _ollama_payload(False, f"Unable to start Ollama: {exc}")
    return _ollama_payload(ok, "Ollama started." if ok else "Ollama did not start.")


def ollama_stop() -> dict[str, Any]:
    modelito = _modelito_module()
    try:
        ok = bool(getattr(modelito, "stop_ollama")(force=True))
    except Exception as exc:
        return _ollama_payload(False, f"Unable to stop Ollama: {exc}")
    return _ollama_payload(ok, "Ollama stopped." if ok else "Ollama did not stop.")


def ollama_install() -> dict[str, Any]:
    modelito = _modelito_module()
    try:
        ok = bool(getattr(modelito, "install_ollama")(allow_install=True))
    except Exception as exc:
        return _ollama_payload(False, f"Unable to install Ollama: {exc}")
    return _ollama_payload(ok, "Ollama is installed." if ok else "Ollama install did not complete.")


def ollama_download(model: str) -> dict[str, Any]:
    modelito = _modelito_module()
    name = model.strip()
    if not name:
        return _ollama_payload(False, "Choose a model to download.")
    try:
        ok = bool(getattr(modelito, "download_model")(name))
    except Exception as exc:
        return _ollama_payload(False, f"Unable to download {name}: {exc}", model=name)
    return _ollama_payload(ok, f"Downloaded {name}." if ok else f"Download failed for {name}.", model=name)


def ollama_delete(model: str) -> dict[str, Any]:
    modelito = _modelito_module()
    name = model.strip()
    if not name:
        return _ollama_payload(False, "Choose a local model to delete.")
    try:
        ok = bool(getattr(modelito, "delete_model")(name))
    except Exception as exc:
        return _ollama_payload(False, f"Unable to delete {name}: {exc}", model=name)
    return _ollama_payload(ok, f"Deleted {name}." if ok else f"Delete failed for {name}.", model=name)


def ollama_serve(model: str) -> dict[str, Any]:
    modelito = _modelito_module()
    name = model.strip()
    if not name:
        return _ollama_payload(False, "Choose a local model to serve.")
    try:
        ok = bool(getattr(modelito, "serve_model")(name))
    except Exception as exc:
        return _ollama_payload(False, f"Unable to serve {name}: {exc}", model=name)
    return _ollama_payload(ok, f"Serving {name}." if ok else f"Could not serve {name}.", model=name)


def ollama_stop_serving(model: str) -> dict[str, Any]:
    name = model.strip()
    if not name:
        return _ollama_payload(False, "Choose a served model to stop.", model=name)

    try:
        modelito = _modelito_module()
    except RuntimeError:
        modelito = None

    for method_name in ("stop_model", "stop_serving_model", "unserve_model"):
        method = getattr(modelito, method_name, None) if modelito else None
        if callable(method):
            try:
                ok = bool(method(name))
                return _ollama_payload(
                    ok,
                    f"Stopped serving {name}." if ok else f"Could not stop serving {name}.",
                    model=name,
                )
            except Exception:
                break

    try:
        proc = subprocess.run(
            ["ollama", "stop", name],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        return _ollama_payload(False, "Ollama CLI is not installed.", model=name)
    except Exception as exc:
        return _ollama_payload(False, f"Unable to stop serving {name}: {exc}", model=name)

    if proc.returncode != 0:
        message = (proc.stderr or proc.stdout or f"Could not stop serving {name}.").strip()
        return _ollama_payload(False, message, model=name)
    return _ollama_payload(True, f"Stopped serving {name}.", model=name)
