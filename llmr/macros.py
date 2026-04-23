from __future__ import annotations

from llmr.schemas import PlannedToolCall, ToolName


_MACROS: dict[str, list[PlannedToolCall]] = {
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


def list_macros() -> list[str]:
    return sorted(_MACROS)


def get_macro(name: str) -> list[PlannedToolCall] | None:
    return _MACROS.get(name)
