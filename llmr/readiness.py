"""Unified readiness model for LLM-r.

Computes a structured readiness report describing whether the system is
configured and available for planning, dry-run preview, and live execution.

The function is a pure helper; the only side-effect is an optional HTTP probe
of the Device Bridge endpoint.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from llmr.config import Settings
    from llmr.osc_replies import OscReplyListener


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
    model_ok = bool(provider and model)
    model_info: dict[str, Any] = {
        "ok": model_ok,
        "provider": provider,
        "model": model,
        "message": (
            f"{provider} / {model}"
            if model_ok
            else "No provider or model is configured."
        ),
        "next_step": (
            ""
            if model_ok
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
    ready_to_plan: bool = model_ok
    ready_to_dry_run: bool = model_ok  # preview does not require Ableton
    ready_to_execute: bool = model_ok and osc_configured

    # ── Warnings and errors ───────────────────────────────────────────────────
    warnings: list[str] = []
    errors: list[str] = []

    if not model_ok:
        errors.append(
            "No model configured. Planning and execution will fail. "
            "Open Settings and choose a provider and model."
        )
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
