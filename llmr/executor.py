from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from llmr.ableton_osc import AbletonOSCClient


def execute_actions(
    actions: list,
    *,
    ableton_host: str,
    ableton_port: int,
    approved: bool,
    dry_run: bool,
) -> tuple[list[dict[str, Any]], str | None]:
    """Send a list of AbletonActions over OSC, returning (report, executed_at).

    Raises:
        PermissionError: any action is destructive and approved is False.
        RuntimeError: an OSC send fails.
    """
    if any(a.destructive for a in actions) and not approved:
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
            }
            try:
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
                "status": "dry_run",
            })

    return report, executed_at
