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
    clip_duplicate_loop = "clip_duplicate_loop"
    clip_duplicate_to = "clip_duplicate_to"
    clip_rename = "clip_rename"
    clip_set_color = "clip_set_color"
    clip_set_color_index = "clip_set_color_index"
    clip_set_gain = "clip_set_gain"
    clip_set_pitch_coarse = "clip_set_pitch_coarse"
    clip_set_pitch_fine = "clip_set_pitch_fine"
    clip_set_start_marker = "clip_set_start_marker"
    clip_set_end_marker = "clip_set_end_marker"
    clip_set_loop_start = "clip_set_loop_start"
    clip_set_loop_end = "clip_set_loop_end"
    clip_set_looping = "clip_set_looping"
    clip_set_position = "clip_set_position"
    clip_set_warping = "clip_set_warping"
    clip_set_warp_mode = "clip_set_warp_mode"
    clip_set_ram_mode = "clip_set_ram_mode"
    clip_set_muted = "clip_set_muted"
    clip_set_launch_mode = "clip_set_launch_mode"
    clip_set_launch_quantization = "clip_set_launch_quantization"
    clip_set_velocity_amount = "clip_set_velocity_amount"
    midi_notes_get = "midi_notes_get"
    midi_notes_add = "midi_notes_add"
    midi_notes_remove = "midi_notes_remove"
    midi_notes_clear = "midi_notes_clear"
    device_get_parameters = "device_get_parameters"
    device_get_parameter = "device_get_parameter"
    device_get_parameter_name = "device_get_parameter_name"
    device_get_parameter_value_string = "device_get_parameter_value_string"
    device_get_parameter_names = "device_get_parameter_names"
    device_get_parameter_min_values = "device_get_parameter_min_values"
    device_get_parameter_max_values = "device_get_parameter_max_values"
    device_set_parameters = "device_set_parameters"
    device_set_parameter = "device_set_parameter"
    device_delete = "device_delete"
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
