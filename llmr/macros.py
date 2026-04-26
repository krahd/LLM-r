from __future__ import annotations

from llmr.schemas import PlannedToolCall, ToolName



# Static macros (can be extended to support runtime editing)
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

# Placeholder for runtime-editable macros (future feature)
_RUNTIME_MACROS: dict[str, list[PlannedToolCall]] = {}


def list_macros() -> list[str]:
    """List all available macro names (static + runtime)."""
    return sorted(set(_STATIC_MACROS) | set(_RUNTIME_MACROS))


def get_macro(name: str) -> list[PlannedToolCall] | None:
    """Get a macro by name, searching both static and runtime macros."""
    return _RUNTIME_MACROS.get(name) or _STATIC_MACROS.get(name)
