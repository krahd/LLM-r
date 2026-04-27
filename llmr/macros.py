from __future__ import annotations

import json
from pathlib import Path

from llmr.schemas import PlannedToolCall, ToolName


_STATIC_MACROS: dict[str, list[PlannedToolCall]] = {
    "idea_sketch": [
        PlannedToolCall(tool=ToolName.create_midi_track, args={}),
        PlannedToolCall(tool=ToolName.set_tempo, args={"bpm": 122}),
        PlannedToolCall(tool=ToolName.arm_track, args={"track_index": 0, "arm": True}),
    ],
    "performance_prep": [
        PlannedToolCall(tool=ToolName.set_tempo, args={"bpm": 128}),
        PlannedToolCall(tool=ToolName.set_track_volume, args={"track_index": 0, "volume": 0.85}),
        PlannedToolCall(tool=ToolName.set_track_solo, args={"track_index": 0, "solo": False}),
    ],
}


class MacroStore:
    def __init__(self, persist_path: str | None = None) -> None:
        self._persist_path = Path(persist_path) if persist_path else None
        self._runtime_macros: dict[str, list[PlannedToolCall]] = {}
        self._load()

    @property
    def runtime_macros(self) -> dict[str, list[PlannedToolCall]]:
        return self._runtime_macros

    def list_names(self) -> list[str]:
        return sorted(set(_STATIC_MACROS) | set(self._runtime_macros))

    def get(self, name: str) -> list[PlannedToolCall] | None:
        return self._runtime_macros.get(name) or _STATIC_MACROS.get(name)

    def is_static(self, name: str) -> bool:
        return name in _STATIC_MACROS

    def put_runtime(self, name: str, calls: list[PlannedToolCall]) -> None:
        if name in _STATIC_MACROS:
            raise ValueError("Cannot overwrite static macro")
        self._runtime_macros[name] = calls
        self._save()

    def delete_runtime(self, name: str) -> bool:
        if name in _STATIC_MACROS:
            raise ValueError("Cannot delete static macro")
        existed = self._runtime_macros.pop(name, None) is not None
        if existed:
            self._save()
        return existed

    def _save(self) -> None:
        if not self._persist_path:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            name: [{"tool": call.tool.value, "args": call.args} for call in calls]
            for name, calls in self._runtime_macros.items()
        }
        self._persist_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._persist_path or not self._persist_path.exists():
            return
        try:
            raw = json.loads(self._persist_path.read_text(encoding="utf-8"))
        except Exception:
            return

        loaded: dict[str, list[PlannedToolCall]] = {}
        for name, calls in (raw or {}).items():
            if not isinstance(name, str) or not isinstance(calls, list):
                continue
            parsed_calls: list[PlannedToolCall] = []
            for item in calls:
                if not isinstance(item, dict):
                    continue
                try:
                    tool = ToolName(str(item.get("tool")))
                except Exception:
                    continue
                args = item.get("args", {})
                if not isinstance(args, dict):
                    args = {}
                parsed_calls.append(PlannedToolCall(tool=tool, args=args))
            if parsed_calls:
                loaded[name] = parsed_calls
        self._runtime_macros = loaded


_DEFAULT_STORE = MacroStore()


def init_macro_store(persist_path: str | None) -> MacroStore:
    global _DEFAULT_STORE
    _DEFAULT_STORE = MacroStore(persist_path=persist_path)
    return _DEFAULT_STORE


def list_macros() -> list[str]:
    return _DEFAULT_STORE.list_names()


def get_macro(name: str) -> list[PlannedToolCall] | None:
    return _DEFAULT_STORE.get(name)


def upsert_runtime_macro(name: str, calls: list[PlannedToolCall]) -> None:
    _DEFAULT_STORE.put_runtime(name, calls)


def delete_runtime_macro(name: str) -> bool:
    return _DEFAULT_STORE.delete_runtime(name)


def serialize_macro(name: str) -> dict | None:
    calls = _DEFAULT_STORE.get(name)
    if calls is None:
        return None
    source = "static" if _DEFAULT_STORE.is_static(name) else "runtime"
    return {
        "name": name,
        "source": source,
        "calls": [{"tool": call.tool.value, "args": call.args} for call in calls],
    }
