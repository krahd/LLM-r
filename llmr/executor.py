from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from llmr.ableton_osc import AbletonOSCClient
from llmr.device_bridge import load_device
from llmr.schemas import ToolName


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
    """Send a list of AbletonActions over OSC, returning (report, executed_at).

    Raises:
        PermissionError: any non-dry-run action is destructive and approved is False.
        RuntimeError: an OSC send fails.
    """
    if not dry_run and any(a.destructive for a in actions) and not approved:
        raise PermissionError("Plan includes destructive actions and requires approval")

    report: list[dict[str, Any]] = []
    executed_at: str | None = None

    if not dry_run:
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
                    if len(action.args) < 3:
                        raise RuntimeError("device_load action is missing normalized arguments")
                    entry["response"] = load_device(
                        host=device_bridge_host,
                        port=device_bridge_port,
                        track_index=int(action.args[0]),
                        query=str(action.args[1]),
                        device_type=str(action.args[2]),
                    )
                else:
                    client.send(action)
                entry["status"] = "sent"
            except Exception as exc:
                entry["status"] = "failed"
                entry["error"] = str(exc)
                report.append(entry)
                raise RuntimeError("Failed sending one or more OSC actions") from exc
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
