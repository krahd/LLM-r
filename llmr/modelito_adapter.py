from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Iterator
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
    try:
        models = ModelitoClient(provider=provider, model=model).list_models()
    except Exception as exc:
        logging.warning(
            "Model listing failed for provider '%s' (%s). Falling back to configured model.",
            provider,
            exc,
        )
        return [model] if model else []
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
        raise RuntimeError(
            "modelito is not installed. Install modelito to manage local runtimes."
        ) from exc
    return modelito


def _ollama_payload(ok: bool, message: str, **extra: Any) -> dict[str, Any]:
    payload = {"ok": ok, "message": message, "models": []}
    payload.update(extra)
    payload.setdefault("models", [])
    return payload


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
    method = _first_callable(modelito, ("list_local_models",))
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="ollama",
            operation="list-local-models",
            candidates=("list_local_models",),
        )
    try:
        models = _clean_model_names(list(method()))
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
    method = _first_callable(modelito, ("list_remote_models",))
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="ollama",
            operation="list-remote-models",
            candidates=("list_remote_models",),
        )
    try:
        models = _clean_model_names(list(method()))
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
    method = _first_callable(modelito, ("start_ollama",))
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="ollama",
            operation="start",
            candidates=("start_ollama",),
        )
    try:
        ok = bool(method())
    except Exception as exc:
        return _ollama_payload(False, f"Unable to start Ollama: {exc}")
    return _ollama_payload(ok, "Ollama started." if ok else "Ollama did not start.")


def ollama_stop() -> dict[str, Any]:
    modelito = _modelito_module()
    method = _first_callable(modelito, ("stop_ollama",))
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="ollama",
            operation="stop",
            candidates=("stop_ollama",),
        )
    try:
        ok = bool(method(force=True))
    except Exception as exc:
        return _ollama_payload(False, f"Unable to stop Ollama: {exc}")
    return _ollama_payload(ok, "Ollama stopped." if ok else "Ollama did not stop.")


def ollama_install() -> dict[str, Any]:
    modelito = _modelito_module()
    method = _first_callable(modelito, ("install_ollama",))
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="ollama",
            operation="install",
            candidates=("install_ollama",),
        )
    try:
        ok = bool(method(allow_install=True))
    except Exception as exc:
        return _ollama_payload(False, f"Unable to install Ollama: {exc}")
    return _ollama_payload(ok, "Ollama is installed." if ok else "Ollama install did not complete.")


def ollama_download(model: str) -> dict[str, Any]:
    modelito = _modelito_module()
    name = model.strip()
    if not name:
        return _ollama_payload(False, "Choose a model to download.")
    method = _first_callable(modelito, ("download_model",))
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="ollama",
            operation="download",
            candidates=("download_model",),
        )
    try:
        ok = bool(method(name))
    except Exception as exc:
        return _ollama_payload(False, f"Unable to download {name}: {exc}", model=name)
    return _ollama_payload(ok, f"Downloaded {name}." if ok else f"Download failed for {name}.", model=name)


def ollama_delete(model: str) -> dict[str, Any]:
    modelito = _modelito_module()
    name = model.strip()
    if not name:
        return _ollama_payload(False, "Choose a local model to delete.")
    method = _first_callable(modelito, ("delete_model",))
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="ollama",
            operation="delete",
            candidates=("delete_model",),
        )
    try:
        ok = bool(method(name))
    except Exception as exc:
        return _ollama_payload(False, f"Unable to delete {name}: {exc}", model=name)
    return _ollama_payload(ok, f"Deleted {name}." if ok else f"Delete failed for {name}.", model=name)


def ollama_serve(model: str) -> dict[str, Any]:
    modelito = _modelito_module()
    name = model.strip()
    if not name:
        return _ollama_payload(False, "Choose a local model to serve.")
    method = _first_callable(modelito, ("serve_model",))
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="ollama",
            operation="serve",
            candidates=("serve_model",),
        )
    try:
        ok = bool(method(name))
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


def _omlx_payload(ok: bool, message: str, **extra: Any) -> dict[str, Any]:
    """Standard response payload for oMLX operations."""
    payload = {"ok": ok, "message": message, "models": []}
    payload.update(extra)
    payload.setdefault("models", [])
    return payload


def _first_callable(module: Any, candidates: tuple[str, ...]) -> Callable[..., Any] | None:
    for name in candidates:
        method = getattr(module, name, None)
        if callable(method):
            return method
    return None


def _missing_modelito_capability_payload(
    runtime: str,
    operation: str,
    candidates: tuple[str, ...],
) -> dict[str, Any]:
    tried = ", ".join(candidates)
    return {
        "ok": False,
        "message": (
            f"Missing Modelito capability for {runtime} {operation}. "
            f"LLM-r tried: {tried}. "
            "Your installed Modelito version may not support this capability. "
            "Update Modelito or switch to a version that includes this runtime helper."
        ),
        "runtime": runtime,
        "operation": operation,
        "candidates": list(candidates),
        "models": [],
    }


def omlx_status() -> dict[str, Any]:
    """Inspect oMLX service state and availability."""
    modelito = _modelito_module()
    service = getattr(modelito, "omlx_service", None)
    try:
        state = service.inspect_service_state() if service else {}
    except Exception as exc:
        return _omlx_payload(False, f"Unable to inspect oMLX: {exc}")

    installed = bool(state.get("installed"))
    running = bool(state.get("running"))
    message = "oMLX is running." if running else (
        "oMLX is installed but not running." if installed else "oMLX is not installed."
    )
    return _omlx_payload(True, message, **state)


def omlx_local_models() -> dict[str, Any]:
    """List models available locally in oMLX."""
    modelito = _modelito_module()
    method = _first_callable(
        modelito,
        ("list_local_omlx_models", "list_local_models_omlx", "list_omlx_models"),
    )
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="omlx",
            operation="list-local-models",
            candidates=("list_local_omlx_models", "list_local_models_omlx", "list_omlx_models"),
        )
    try:
        models = _clean_model_names(list(method()))
    except Exception as exc:
        return _omlx_payload(False, f"Unable to list local oMLX models: {exc}", models=[])
    return _omlx_payload(True, f"Loaded {len(models)} local oMLX model(s).", models=models)


def omlx_running_models() -> dict[str, Any]:
    """Return models currently loaded by oMLX."""
    modelito = _modelito_module()
    candidates = ("list_running_omlx_models", "list_loaded_omlx_models", "running_omlx_models")
    method = _first_callable(modelito, candidates)
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="omlx",
            operation="list-running-models",
            candidates=candidates,
        )
    try:
        models = _clean_model_names(list(method()))
    except Exception as exc:
        return _omlx_payload(False, f"Unable to determine running oMLX models: {exc}", models=[])

    return _omlx_payload(
        True,
        f"{len(models)} oMLX model(s) currently served.",
        models=models,
    )


def omlx_remote_models() -> dict[str, Any]:
    """List available models from oMLX registry or library."""
    modelito = _modelito_module()
    method = _first_callable(
        modelito,
        ("list_remote_omlx_models", "list_omlx_remote_models", "list_available_omlx_models"),
    )
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="omlx",
            operation="list-remote-models",
            candidates=(
                "list_remote_omlx_models",
                "list_omlx_remote_models",
                "list_available_omlx_models",
            ),
        )
    try:
        models = _clean_model_names(list(method()))
    except Exception as exc:
        return _omlx_payload(False, f"Unable to list available oMLX models: {exc}", models=[])
    return _omlx_payload(True, f"Loaded {len(models)} available oMLX model(s).", models=models)


def omlx_start() -> dict[str, Any]:
    """Start the oMLX service."""
    modelito = _modelito_module()
    candidates = ("start_omlx", "start_omlx_service")
    method = _first_callable(modelito, candidates)
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="omlx",
            operation="start",
            candidates=candidates,
        )
    try:
        ok = bool(method())
    except Exception as exc:
        return _omlx_payload(False, f"Unable to start oMLX: {exc}")
    return _omlx_payload(ok, "oMLX started." if ok else "oMLX did not start.")


def omlx_stop() -> dict[str, Any]:
    """Stop the oMLX service."""
    modelito = _modelito_module()
    candidates = ("stop_omlx", "stop_omlx_service")
    method = _first_callable(modelito, candidates)
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="omlx",
            operation="stop",
            candidates=candidates,
        )
    try:
        try:
            ok = bool(method(force=True))
        except TypeError:
            ok = bool(method())
    except Exception as exc:
        return _omlx_payload(False, f"Unable to stop oMLX: {exc}")
    return _omlx_payload(ok, "oMLX stopped." if ok else "oMLX did not stop.")


def omlx_install() -> dict[str, Any]:
    """Install oMLX runtime."""
    modelito = _modelito_module()
    candidates = ("install_omlx", "install_omlx_runtime")
    method = _first_callable(modelito, candidates)
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="omlx",
            operation="install",
            candidates=candidates,
        )
    try:
        try:
            ok = bool(method(allow_install=True))
        except TypeError:
            ok = bool(method())
    except Exception as exc:
        return _omlx_payload(False, f"Unable to install oMLX: {exc}")
    return _omlx_payload(ok, "oMLX is installed." if ok else "oMLX install did not complete.")


def omlx_download(model: str) -> dict[str, Any]:
    """Download an oMLX model."""
    modelito = _modelito_module()
    name = model.strip()
    if not name:
        return _omlx_payload(False, "Choose a model to download.")
    candidates = ("download_omlx_model", "download_model_omlx")
    method = _first_callable(modelito, candidates)
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="omlx",
            operation="download",
            candidates=candidates,
        )
    try:
        ok = bool(method(name))
    except Exception as exc:
        return _omlx_payload(False, f"Unable to download {name}: {exc}", model=name)
    return _omlx_payload(ok, f"Downloaded {name}." if ok else f"Download failed for {name}.", model=name)


def omlx_delete(model: str) -> dict[str, Any]:
    """Delete a local oMLX model."""
    modelito = _modelito_module()
    name = model.strip()
    if not name:
        return _omlx_payload(False, "Choose a local model to delete.")
    candidates = ("delete_omlx_model", "delete_model_omlx")
    method = _first_callable(modelito, candidates)
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="omlx",
            operation="delete",
            candidates=candidates,
        )
    try:
        ok = bool(method(name))
    except Exception as exc:
        return _omlx_payload(False, f"Unable to delete {name}: {exc}", model=name)
    return _omlx_payload(ok, f"Deleted {name}." if ok else f"Delete failed for {name}.", model=name)


def omlx_serve(model: str) -> dict[str, Any]:
    """Serve (load) an oMLX model."""
    modelito = _modelito_module()
    name = model.strip()
    if not name:
        return _omlx_payload(False, "Choose a local model to serve.")
    candidates = ("serve_omlx_model", "serve_model_omlx")
    method = _first_callable(modelito, candidates)
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="omlx",
            operation="serve",
            candidates=candidates,
        )
    try:
        ok = bool(method(name))
    except Exception as exc:
        return _omlx_payload(False, f"Unable to serve {name}: {exc}", model=name)
    return _omlx_payload(ok, f"Serving {name}." if ok else f"Could not serve {name}.", model=name)


def omlx_stop_serving(model: str) -> dict[str, Any]:
    """Stop serving (unload) an oMLX model."""
    name = model.strip()
    if not name:
        return _omlx_payload(False, "Choose a served model to stop.", model=name)

    modelito = _modelito_module()
    candidates = ("stop_omlx_model", "stop_serving_omlx_model", "unserve_omlx_model")
    method = _first_callable(modelito, candidates)
    if method is None:
        return _missing_modelito_capability_payload(
            runtime="omlx",
            operation="stop-serving",
            candidates=candidates,
        )
    try:
        ok = bool(method(name))
    except Exception as exc:
        return _omlx_payload(False, f"Could not stop serving {name}: {exc}", model=name)

    return _omlx_payload(
        ok,
        f"Stopped serving {name}." if ok else f"Could not stop serving {name}.",
        model=name,
    )
