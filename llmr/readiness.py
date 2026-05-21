"""Unified readiness model for LLM-r.

Computes a structured readiness report describing whether the system is
configured and available for planning, dry-run preview, and live execution.

The function is a pure helper; the only side-effect is an optional HTTP probe
of the Device Bridge endpoint.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from llmr.modelito_adapter import (
    ollama_local_models,
    ollama_status,
    omlx_local_models,
    omlx_status,
)

if TYPE_CHECKING:
    from llmr.config import Settings
    from llmr.osc_replies import OscReplyListener


def _model_names_from_payload(payload: dict[str, Any]) -> list[str]:
    """Extract normalized model names from a local-runtime payload."""
    values = payload.get("models", []) or []
    names: list[str] = []

    for item in values:
        if isinstance(item, str):
            name = item.strip()
            if name and name not in names:
                names.append(name)
            continue

        if isinstance(item, dict):
            for key in ("id", "model", "name"):
                raw = str(item.get(key, "")).strip()
                if raw and raw not in names:
                    names.append(raw)
            for raw_value in item.values():
                raw = str(raw_value).strip()
                if raw and raw not in names:
                    names.append(raw)
            continue

        raw = str(item).strip()
        if raw and raw not in names:
            names.append(raw)

    return names


def _contains_model(payload: dict[str, Any], configured_model: str) -> bool:
    """Check whether a configured model exists in a local-runtime payload."""
    target = configured_model.strip()
    if not target:
        return False

    names = _model_names_from_payload(payload)
    if target in names:
        return True

    target_folded = target.casefold()
    return any(name.casefold() == target_folded for name in names)


def compute_readiness(
    settings: "Settings",
    osc_reply_listener: "OscReplyListener | None" = None,
) -> dict[str, Any]:
    """Return a structured readiness report.

    Parameters
    ----------
    settings:
        The live ``Settings`` singleton.
    osc_reply_listener:
        The running ``OscReplyListener`` instance, if one has been started by
        the API server, or ``None`` when called from an embedded context.

    Returns
    -------
    dict with the following keys:

    - ``ready_to_plan``     bool  — model provider/model are configured.
    - ``ready_to_dry_run``  bool  — same as ``ready_to_plan``.
    - ``ready_to_execute``  bool  — model is configured and AbletonOSC is set.
    - ``model``             dict  — provider/model status.
    - ``ableton_osc``       dict  — AbletonOSC config status (UDP; unverifiable).
    - ``device_bridge``     dict  — Device Bridge HTTP probe result.
    - ``osc_replies``       dict  — OSC reply listener status.
    - ``server``            dict  — server mode note.
    - ``warnings``          list  — non-blocking issues.
    - ``errors``            list  — blocking issues.
    """
    # ── Model ─────────────────────────────────────────────────────────────────
    provider = (settings.modelito_provider or "").strip()
    model = (settings.modelito_model or "").strip()
    has_provider_and_model = bool(provider and model)
    model_info: dict[str, Any] = {
        "ok": has_provider_and_model,
        "provider": provider,
        "model": model,
        "message": (
            f"{provider} / {model}"
            if has_provider_and_model
            else "No provider or model is configured."
        ),
        "next_step": (
            ""
            if has_provider_and_model
            else "Open Settings and choose a provider and model."
        ),
    }

    # ── AbletonOSC ────────────────────────────────────────────────────────────
    osc_host = (settings.ableton_host or "").strip()
    osc_port = int(settings.ableton_port) if settings.ableton_port else 0
    osc_configured = bool(osc_host and osc_port)
    ableton_osc_info: dict[str, Any] = {
        "ok": osc_configured,
        "host": osc_host,
        "port": osc_port,
        "message": (
            f"Configured at {osc_host}:{osc_port}. "
            "Ableton Live with AbletonOSC must be running for live execution."
            if osc_configured
            else "AbletonOSC host or port is not set."
        ),
        "next_step": (
            ""
            if osc_configured
            else (
                "Set a valid AbletonOSC host and port in "
                "Advanced Settings \u2192 Runtime."
            )
        ),
    }

    # ── Device Bridge ─────────────────────────────────────────────────────────
    db_enabled = bool(settings.device_bridge_enabled)
    db_host = (settings.device_bridge_host or "").strip()
    db_port = int(settings.device_bridge_port) if settings.device_bridge_port else 0

    if db_enabled:
        from llmr.device_bridge import health as _db_health

        _probe = _db_health(host=db_host, port=db_port, timeout=1.5)
        db_ok: bool | None = bool(_probe.get("ok", False))
        db_message = (
            f"Reachable at {db_host}:{db_port}."
            if db_ok
            else _probe.get(
                "error",
                f"Unreachable at {db_host}:{db_port}.",
            )
        )
        db_next_step = (
            ""
            if db_ok
            else (
                "Install the LLMRDeviceBridge Remote Script in Ableton Live "
                "and ensure Ableton Live is open."
            )
        )
    else:
        db_ok = None  # disabled; not required for OSC-only plans
        db_message = (
            "Device Bridge is disabled. "
            "Plans using device_load will not be available."
        )
        db_next_step = (
            "Enable Device Bridge in Advanced Settings \u2192 Runtime "
            "if you need device loading."
        )

    device_bridge_info: dict[str, Any] = {
        "ok": db_ok,
        "enabled": db_enabled,
        "host": db_host,
        "port": db_port,
        "message": db_message,
        "next_step": db_next_step,
    }

    # ── OSC reply listener ────────────────────────────────────────────────────
    reply_enabled = bool(settings.osc_reply_enabled)

    if osc_reply_listener is not None:
        reply_status = osc_reply_listener.status()
        reply_listening = bool(reply_status.get("listening", False))
        reply_error: str | None = reply_status.get("error")
    else:
        reply_listening = False
        reply_error = None if not reply_enabled else "Listener not started."

    osc_reply_ok = reply_listening if reply_enabled else True
    osc_replies_info: dict[str, Any] = {
        "ok": osc_reply_ok,
        "listening": reply_listening,
        "message": (
            f"Listening on {settings.osc_reply_host}:{settings.osc_reply_port}."
            if reply_listening
            else (
                "OSC reply listening is disabled."
                if not reply_enabled
                else (
                    "Not listening."
                    + (f" Error: {reply_error}" if reply_error else "")
                )
            )
        ),
        "next_step": (
            ""
            if osc_reply_ok
            else (
                "Enable OSC reply listening in Advanced Settings "
                "or start the LLM-r API server."
            )
        ),
    }

    # ── Server ────────────────────────────────────────────────────────────────
    server_info: dict[str, Any] = {
        "ok": True,
        "mode": "http",
        "message": "LLM-r API server is running.",
    }

    # ── Readiness flags ───────────────────────────────────────────────────────
    model_error: str | None = None
    model_next_step = ""
    final_model_ok = True

    provider_api_env = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "cohere": "COHERE_API_KEY",
        "mistral": "MISTRAL_API_KEY",
    }
    if not provider:
        final_model_ok = False
        model_error = "No model provider is configured."
        model_next_step = "Open Settings and choose a provider and model."
    elif not model:
        final_model_ok = False
        model_error = "No model is configured for the selected provider."
        model_next_step = "Open Settings and choose a provider and model."
    elif provider in provider_api_env:
        key_name = provider_api_env[provider]
        if not (os.getenv(key_name) or "").strip():
            final_model_ok = False
            model_error = (
                f"Missing API key for {provider}. Set the {key_name} environment variable,"
                " or use PyQt Advanced Settings to save and apply it."
            )
            model_next_step = (
                "Set the environment variable, or open PyQt Advanced Settings → API Keys and save."
            )
    elif provider == "ollama":
        status_payload = ollama_status()
        if not bool(status_payload.get("ok", False)):
            final_model_ok = False
            model_error = (
                f"Ollama runtime check failed: {status_payload.get('message', 'unknown error')}"
            )
            model_next_step = "Fix Ollama runtime status in Advanced Settings \u2192 Ollama."
        elif not bool(status_payload.get("running", False)):
            final_model_ok = False
            model_error = "Start Ollama service. Open Advanced Settings \u2192 Ollama."
            model_next_step = "Start Ollama, then refresh readiness."
        else:
            local_payload = ollama_local_models()
            if not bool(local_payload.get("ok", False)):
                final_model_ok = False
                model_error = (
                    "Ollama local model listing failed: "
                    f"{local_payload.get('message', 'unknown error')}"
                )
                model_next_step = "Fix local model listing in Advanced Settings \u2192 Ollama."
            else:
                local_names = _model_names_from_payload(local_payload)
                if not local_names:
                    final_model_ok = False
                    model_error = (
                        "Download or select an Ollama model. "
                        "Open Advanced Settings \u2192 Ollama."
                    )
                    model_next_step = "Download a local Ollama model or choose one already installed."
                elif not _contains_model(local_payload, model):
                    final_model_ok = False
                    model_error = (
                        f"Selected Ollama model is not installed: {model}. "
                        "Download it or choose an installed model in Advanced Settings \u2192 Ollama."
                    )
                    model_next_step = "Choose an installed Ollama model or download the selected one."
    elif provider == "omlx":
        status_payload = omlx_status()
        if not bool(status_payload.get("ok", False)):
            final_model_ok = False
            model_error = (
                f"oMLX runtime check failed: {status_payload.get('message', 'unknown error')}"
            )
            model_next_step = "Fix oMLX runtime status in Advanced Settings \u2192 oMLX."
        elif not bool(status_payload.get("running", False)):
            final_model_ok = False
            model_error = "Start oMLX service. Open Advanced Settings \u2192 oMLX."
            model_next_step = "Start oMLX, then refresh readiness."
        else:
            local_payload = omlx_local_models()
            if not bool(local_payload.get("ok", False)):
                final_model_ok = False
                model_error = (
                    "oMLX local model listing failed: "
                    f"{local_payload.get('message', 'unknown error')}"
                )
                model_next_step = "Fix local model listing in Advanced Settings \u2192 oMLX."
            else:
                local_names = _model_names_from_payload(local_payload)
                if not local_names:
                    final_model_ok = False
                    model_error = (
                        "Download or select an oMLX model. "
                        "Open Advanced Settings \u2192 oMLX."
                    )
                    model_next_step = "Download a local oMLX model or choose one already installed."
                elif not _contains_model(local_payload, model):
                    final_model_ok = False
                    model_error = (
                        f"Selected oMLX model is not installed: {model}. "
                        "Download it or choose an installed model in Advanced Settings \u2192 oMLX."
                    )
                    model_next_step = "Choose an installed oMLX model or download the selected one."

    if final_model_ok:
        model_info["message"] = f"{provider} / {model} is ready for planning."
        model_info["next_step"] = ""
    else:
        model_info["message"] = model_error or "Provider/model is not ready for planning."
        model_info["next_step"] = model_next_step or "Resolve model readiness and retry."
    model_info["ok"] = final_model_ok

    ready_to_plan: bool = final_model_ok
    ready_to_dry_run: bool = final_model_ok
    ready_to_execute: bool = final_model_ok and osc_configured

    # ── Warnings and errors ───────────────────────────────────────────────────
    warnings: list[str] = []
    errors: list[str] = []

    if not final_model_ok:
        errors.append(model_info["message"])
    if not osc_configured:
        warnings.append(
            "AbletonOSC host/port is not configured. Live execution will fail."
        )
    if db_enabled and db_ok is False:
        warnings.append(
            "Device Bridge is enabled but unreachable. "
            "Plans that include device_load will fail."
        )
    if reply_enabled and not reply_listening:
        warnings.append(
            "OSC reply listener is enabled but not running. "
            "Action feedback will not be received."
        )

    return {
        "ready_to_plan": ready_to_plan,
        "ready_to_dry_run": ready_to_dry_run,
        "ready_to_execute": ready_to_execute,
        "model": model_info,
        "ableton_osc": ableton_osc_info,
        "device_bridge": device_bridge_info,
        "osc_replies": osc_replies_info,
        "server": server_info,
        "warnings": warnings,
        "errors": errors,
    }
