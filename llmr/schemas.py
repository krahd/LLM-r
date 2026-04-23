from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ToolName(str, Enum):
    create_midi_track = "create_midi_track"
    create_audio_track = "create_audio_track"
    set_tempo = "set_tempo"
    fire_clip = "fire_clip"
    stop_all_clips = "stop_all_clips"
    set_track_volume = "set_track_volume"
    set_track_mute = "set_track_mute"
    set_track_solo = "set_track_solo"
    arm_track = "arm_track"
    fire_scene = "fire_scene"


@dataclass
class PlannedToolCall:
    tool: ToolName
    args: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanEnvelope:
    explanation: str
    confidence: float = 0.5
    calls: list[PlannedToolCall] = field(default_factory=list)


@dataclass
class Capability:
    tool: ToolName
    description: str
    args_schema: dict[str, str]
    destructive: bool = False


def parse_plan_envelope(data: dict[str, Any]) -> PlanEnvelope:
    calls = []
    for c in data.get("calls", []):
        tool_raw = c.get("tool")
        try:
            tool = ToolName(tool_raw)
        except Exception:
            continue
        calls.append(PlannedToolCall(tool=tool, args=c.get("args", {})))

    conf = float(data.get("confidence", 0.0))
    conf = max(0.0, min(1.0, conf))
    return PlanEnvelope(explanation=str(data.get("explanation", "")), confidence=conf, calls=calls)
