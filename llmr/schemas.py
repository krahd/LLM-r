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
    song_play = "song_play"
    song_stop = "song_stop"
    song_continue = "song_continue"
    song_record = "song_record"
    song_metronome = "song_metronome"
    song_set_time_signature = "song_set_time_signature"
    song_set_global_quantization = "song_set_global_quantization"
    song_set_count_in = "song_set_count_in"
    track_rename = "track_rename"
    track_delete = "track_delete"
    track_duplicate = "track_duplicate"
    track_set_pan = "track_set_pan"
    track_set_send = "track_set_send"
    scene_create = "scene_create"
    scene_delete = "scene_delete"
    scene_rename = "scene_rename"
    clip_create = "clip_create"
    clip_delete = "clip_delete"
    device_get_parameters = "device_get_parameters"
    device_set_parameter = "device_set_parameter"
    utility_undo = "utility_undo"
    utility_redo = "utility_redo"


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
    domain: str = "utility"
    safety: str = "safe"


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
