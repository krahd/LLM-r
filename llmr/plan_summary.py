from __future__ import annotations

from typing import Any

_TARGET_KEYS: tuple[tuple[str, str], ...] = (
    ("track_index", "Track {value}"),
    ("track", "Track {value}"),
    ("track_name", "Track: {value}"),
    ("scene_index", "Scene {value}"),
    ("scene", "Scene {value}"),
    ("scene_name", "Scene: {value}"),
    ("clip_index", "Clip {value}"),
    ("clip", "Clip {value}"),
    ("clip_name", "Clip: {value}"),
    ("device_name", "Device: {value}"),
    ("device", "Device: {value}"),
    ("parameter_name", "Parameter: {value}"),
)


def _clean_value(value: Any) -> str:
    text = str(value).strip()
    return text


def infer_transport(action: dict[str, Any]) -> str:
    explicit = str(action.get("transport") or "").strip().lower()
    if explicit:
        return explicit
    tool = str(action.get("tool") or "").strip().lower()
    if tool == "device_load":
        return "device_bridge"
    if action.get("address"):
        return "osc"
    return "osc"


def infer_target_labels(args: Any) -> list[str]:
    if not isinstance(args, dict):
        return []
    labels: list[str] = []
    for key, template in _TARGET_KEYS:
        if key not in args:
            continue
        value = _clean_value(args.get(key, ""))
        if not value:
            continue
        labels.append(template.format(value=value))
    return labels


def infer_target_label(args: Any) -> str:
    labels = infer_target_labels(args)
    if not labels:
        return "General"
    return " · ".join(labels)


def summarise_actions(actions: list[dict[str, Any]]) -> dict[str, Any]:
    safe_count = 0
    destructive_count = 0
    transport_counts = {"osc": 0, "device_bridge": 0, "other": 0}
    destructive_tools: list[str] = []

    for action in actions:
        is_destructive = bool(action.get("destructive", False))
        if is_destructive:
            destructive_count += 1
            destructive_tools.append(str(action.get("tool") or "action"))
        else:
            safe_count += 1

        transport = infer_transport(action)
        if transport == "osc":
            transport_counts["osc"] += 1
        elif transport == "device_bridge":
            transport_counts["device_bridge"] += 1
        else:
            transport_counts["other"] += 1

    return {
        "count": len(actions),
        "safe_count": safe_count,
        "destructive_count": destructive_count,
        "transport_counts": transport_counts,
        "destructive_tools": destructive_tools,
    }
