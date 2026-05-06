from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from llmr.ableton_osc import AbletonOSCClient
from llmr.device_bridge import DeviceBridgeError, health as device_bridge_health, load_device, resolve_device
from llmr.schemas import ToolName


def _truthy(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"1", "true", "yes", "on"}


def _device_load_args(action: Any) -> dict[str, Any]:
    if len(action.args) < 3:
        raise RuntimeError("device_load action is missing normalized arguments")
    options = action.args[3] if len(action.args) > 3 and isinstance(action.args[3], dict) else {}
    return {
        "track_index": int(action.args[0]),
        "query": str(action.args[1]),
        "device_type": str(action.args[2]),
        "preset_query": options.get("preset_query"),
        "browser_path": options.get("browser_path"),
        "allow_ambiguous": _truthy(options.get("allow_ambiguous", False)),
    }


def _preflight_device_loads(
    actions: list,
    *,
    device_bridge_enabled: bool,
    device_bridge_host: str,
    device_bridge_port: int,
) -> None:
    loads = [action for action in actions if action.tool == ToolName.device_load]
    if not loads:
        return
    if not device_bridge_enabled:
        raise RuntimeError("Device Bridge is disabled")

    status = device_bridge_health(host=device_bridge_host, port=device_bridge_port)
    if not status.get("ok"):
        detail = status.get("error") or status.get("status") or "unknown error"
        raise RuntimeError(f"Device Bridge unavailable before executing plan: {detail}")

    for action in loads:
        payload = _device_load_args(action)
        try:
            resolve_device(
                host=device_bridge_host,
                port=device_bridge_port,
                **payload,
            )
        except DeviceBridgeError as exc:
            raise RuntimeError(f"Device Bridge resolve failed: {exc}") from exc


def execute_actions(
    actions: list,
    *,
    ableton_host: str,
    ableton_port: int,
    approved: bool,
    dry_run: bool,
    device_bridge_enabled: bool = True,
    device_bridge_host: str = "127.0.0.1",
    device_bridge_port: int = 8788,
) -> tuple[list[dict[str, Any]], str | None]:
    """Execute a list of AbletonActions, returning (report, executed_at).

    Raises:
        PermissionError: any non-dry-run action is destructive and approved is False.
        RuntimeError: an action transport fails.
    """
    if not dry_run and any(a.destructive for a in actions) and not approved:
        raise PermissionError("Plan includes destructive actions and requires approval")

    report: list[dict[str, Any]] = []
    executed_at: str | None = None

    if not dry_run:
        _preflight_device_loads(
            actions,
            device_bridge_enabled=device_bridge_enabled,
            device_bridge_host=device_bridge_host,
            device_bridge_port=device_bridge_port,
        )
        client = AbletonOSCClient(ableton_host, ableton_port)
        for index, action in enumerate(actions):
            entry: dict[str, Any] = {
                "index": index,
                "tool": action.tool.value,
                "address": action.address,
                "args": action.args,
                "transport": getattr(action, "transport", "osc"),
            }
            try:
                if action.tool == ToolName.device_load:
                    if not device_bridge_enabled:
                        raise RuntimeError("Device Bridge is disabled")
                    entry["response"] = load_device(
                        host=device_bridge_host,
                        port=device_bridge_port,
                        **_device_load_args(action),
                    )
                else:
                    client.send(action)
                entry["status"] = "sent"
            except Exception as exc:
                entry["status"] = "failed"
                entry["error"] = str(exc)
                report.append(entry)
                raise RuntimeError("Failed executing one or more actions") from exc
            report.append(entry)
        executed_at = datetime.now(timezone.utc).isoformat()
    else:
        for index, action in enumerate(actions):
            report.append({
                "index": index,
                "tool": action.tool.value,
                "address": action.address,
                "args": action.args,
                "transport": getattr(action, "transport", "osc"),
                "status": "dry_run",
            })

    return report, executed_at
