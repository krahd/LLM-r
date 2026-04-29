from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from llmr.schemas import Capability, ToolName

try:
    from pythonosc.udp_client import SimpleUDPClient  # type: ignore
except ImportError:  # pragma: no cover
    class SimpleUDPClient:  # type: ignore[override]
        def __init__(self, host: str, port: int) -> None:
            self.host = host
            self.port = port

        def send_message(self, address: str, args: list[Any]) -> None:
            raise RuntimeError(
                "python-osc is required. Install it with: pip install python-osc"
            )


@dataclass
class AbletonAction:
    tool: ToolName
    address: str
    args: list[Any]
    description: str
    destructive: bool = False


@dataclass
class ToolSpec:
    tool: ToolName
    address: str
    description: str
    args_schema: dict[str, str]
    args_builder: Callable[[dict[str, Any]], list[Any]]
    destructive: bool = False
    domain: str = "utility"
    safety: str = "safe"


def _int_arg(args: dict[str, Any], key: str, default: int) -> int:
    return int(args.get(key, default))


def _float_arg(args: dict[str, Any], key: str, default: float) -> float:
    return float(args.get(key, default))


def _bool_int_arg(args: dict[str, Any], key: str, default: bool) -> int:
    return int(bool(args.get(key, default)))


def _string_arg(args: dict[str, Any], key: str) -> str:
    value = str(args.get(key, "")).strip()
    if not value:
        raise ValueError(f"'{key}' is required")
    return value


def _bounded_int(value: Any, name: str, minimum: int, maximum: int) -> int:
    normalized = int(value)
    if not minimum <= normalized <= maximum:
        raise ValueError(f"'{name}' must be between {minimum} and {maximum}")
    return normalized


def _bounded_float(value: Any, name: str, minimum: float, maximum: float) -> float:
    normalized = float(value)
    if not minimum <= normalized <= maximum:
        raise ValueError(f"'{name}' must be between {minimum:g} and {maximum:g}")
    return normalized


def _build_create_midi_track(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "index", -1)]


def _build_create_audio_track(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "index", -1)]


def _build_set_tempo(args: dict[str, Any]) -> list[Any]:
    bpm = _float_arg(args, "bpm", 120.0)
    if bpm <= 0:
        raise ValueError("'bpm' must be > 0")
    return [bpm]


def _build_fire_clip(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "track_index", 0), _int_arg(args, "clip_index", 0)]


def _build_set_track_volume(args: dict[str, Any]) -> list[Any]:
    track_index = _int_arg(args, "track_index", 0)
    volume = _float_arg(args, "volume", 0.8)
    if not 0 <= volume <= 1:
        raise ValueError("'volume' must be between 0 and 1")
    return [track_index, volume]


def _build_set_track_toggle(args: dict[str, Any], field: str, default: bool) -> list[Any]:
    return [_int_arg(args, "track_index", 0), _bool_int_arg(args, field, default)]


def _build_fire_scene(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "scene_index", 0)]


def _build_song_noargs(_args: dict[str, Any]) -> list[Any]:
    return []


def _build_song_record(args: dict[str, Any]) -> list[Any]:
    return [_bool_int_arg(args, "record", True)]


def _build_song_metronome(args: dict[str, Any]) -> list[Any]:
    return [_bool_int_arg(args, "enabled", True)]


def _build_song_time_signature(args: dict[str, Any]) -> list[Any]:
    numerator = _int_arg(args, "numerator", 4)
    denominator = _int_arg(args, "denominator", 4)
    if numerator <= 0 or denominator <= 0:
        raise ValueError("'numerator' and 'denominator' must be > 0")
    return [numerator, denominator]


def _build_song_global_quantization(args: dict[str, Any]) -> list[Any]:
    quantization = _int_arg(args, "quantization", 4)
    if quantization < 0:
        raise ValueError("'quantization' must be >= 0")
    return [quantization]


def _build_song_count_in(args: dict[str, Any]) -> list[Any]:
    count_in = _int_arg(args, "count_in", 1)
    if count_in < 0:
        raise ValueError("'count_in' must be >= 0")
    return [count_in]


def _build_track_rename(args: dict[str, Any]) -> list[Any]:
    track_index = _int_arg(args, "track_index", 0)
    name = str(args.get("name", "")).strip()
    if not name:
        raise ValueError("'name' is required")
    return [track_index, name]


def _build_track_delete(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "track_index", 0)]


def _build_track_duplicate(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "track_index", 0)]


def _build_track_pan(args: dict[str, Any]) -> list[Any]:
    track_index = _int_arg(args, "track_index", 0)
    pan = _float_arg(args, "pan", 0.0)
    if not -1.0 <= pan <= 1.0:
        raise ValueError("'pan' must be between -1 and 1")
    return [track_index, pan]


def _build_track_send(args: dict[str, Any]) -> list[Any]:
    track_index = _int_arg(args, "track_index", 0)
    send_index = _int_arg(args, "send_index", 0)
    level = _float_arg(args, "level", 0.0)
    if not 0.0 <= level <= 1.0:
        raise ValueError("'level' must be between 0 and 1")
    return [track_index, send_index, level]


def _build_scene_create(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "scene_index", -1)]


def _build_scene_delete(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "scene_index", 0)]


def _build_scene_rename(args: dict[str, Any]) -> list[Any]:
    scene_index = _int_arg(args, "scene_index", 0)
    name = str(args.get("name", "")).strip()
    if not name:
        raise ValueError("'name' is required")
    return [scene_index, name]


def _build_clip_create(args: dict[str, Any]) -> list[Any]:
    track_index = _int_arg(args, "track_index", 0)
    clip_index = _int_arg(args, "clip_index", 0)
    length_beats = _float_arg(args, "length_beats", 4.0)
    if length_beats <= 0:
        raise ValueError("'length_beats' must be > 0")
    return [track_index, clip_index, length_beats]


def _build_clip_delete(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "track_index", 0), _int_arg(args, "clip_index", 0)]


def _build_clip_noargs(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "track_index", 0), _int_arg(args, "clip_index", 0)]


def _build_clip_duplicate_to(args: dict[str, Any]) -> list[Any]:
    return [
        _int_arg(args, "track_index", 0),
        _int_arg(args, "clip_index", 0),
        _int_arg(args, "target_track_index", 0),
        _int_arg(args, "target_clip_index", 0),
    ]


def _build_clip_rename(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "track_index", 0), _int_arg(args, "clip_index", 0), _string_arg(args, "name")]


def _build_clip_int_property(args: dict[str, Any], field: str, minimum: int, maximum: int) -> list[Any]:
    return [
        _int_arg(args, "track_index", 0),
        _int_arg(args, "clip_index", 0),
        _bounded_int(args.get(field, minimum), field, minimum, maximum),
    ]


def _build_clip_float_property(args: dict[str, Any], field: str, minimum: float, maximum: float) -> list[Any]:
    return [
        _int_arg(args, "track_index", 0),
        _int_arg(args, "clip_index", 0),
        _bounded_float(args.get(field, minimum), field, minimum, maximum),
    ]


def _build_clip_bool_property(args: dict[str, Any], field: str, default: bool) -> list[Any]:
    return [_int_arg(args, "track_index", 0), _int_arg(args, "clip_index", 0), _bool_int_arg(args, field, default)]


def _build_clip_beat_property(args: dict[str, Any], field: str) -> list[Any]:
    value = _float_arg(args, field, 0.0)
    if value < 0:
        raise ValueError(f"'{field}' must be >= 0")
    return [_int_arg(args, "track_index", 0), _int_arg(args, "clip_index", 0), value]


def _build_midi_note_range(args: dict[str, Any], *, allow_empty: bool) -> list[Any]:
    payload = [_int_arg(args, "track_index", 0), _int_arg(args, "clip_index", 0)]
    fields = ("start_pitch", "pitch_span", "start_time", "time_span")
    provided = [field in args for field in fields]
    if not any(provided):
        if allow_empty:
            return payload
        return payload + [0, 128, 0.0, 16384.0]
    if not all(provided):
        raise ValueError("'start_pitch', 'pitch_span', 'start_time', and 'time_span' must be provided together")
    start_pitch = _bounded_int(args["start_pitch"], "start_pitch", 0, 127)
    pitch_span = int(args["pitch_span"])
    start_time = float(args["start_time"])
    time_span = float(args["time_span"])
    if pitch_span <= 0 or start_pitch + pitch_span > 128:
        raise ValueError("'pitch_span' must be > 0 and stay within MIDI pitch range")
    if time_span <= 0:
        raise ValueError("'time_span' must be > 0")
    return payload + [start_pitch, pitch_span, start_time, time_span]


def _build_midi_notes_get(args: dict[str, Any]) -> list[Any]:
    return _build_midi_note_range(args, allow_empty=True)


def _build_midi_notes_remove(args: dict[str, Any]) -> list[Any]:
    return _build_midi_note_range(args, allow_empty=True)


def _build_midi_notes_clear(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "track_index", 0), _int_arg(args, "clip_index", 0)]


def _normalize_note(note: Any, index: int) -> list[Any]:
    if not isinstance(note, dict):
        raise ValueError(f"'notes[{index}]' must be an object")
    pitch = _bounded_int(note.get("pitch", 60), "pitch", 0, 127)
    start_time = float(note.get("start_time", 0.0))
    duration = float(note.get("duration", 0.25))
    velocity = _bounded_float(note.get("velocity", 100.0), "velocity", 0.0, 127.0)
    mute = int(bool(note.get("mute", False)))
    if start_time < 0:
        raise ValueError("'start_time' must be >= 0")
    if duration <= 0:
        raise ValueError("'duration' must be > 0")
    return [pitch, start_time, duration, velocity, mute]


def _build_midi_notes_add(args: dict[str, Any]) -> list[Any]:
    notes = args.get("notes")
    if not isinstance(notes, list) or not notes:
        raise ValueError("'notes' must be a non-empty list")
    payload: list[Any] = [_int_arg(args, "track_index", 0), _int_arg(args, "clip_index", 0)]
    for index, note in enumerate(notes):
        payload.extend(_normalize_note(note, index))
    return payload


def _build_device_get_parameters(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "track_index", 0), _int_arg(args, "device_index", 0)]


def _build_device_get_parameter(args: dict[str, Any]) -> list[Any]:
    return [
        _int_arg(args, "track_index", 0),
        _int_arg(args, "device_index", 0),
        _int_arg(args, "parameter_index", 0),
    ]


def _build_device_set_parameters(args: dict[str, Any]) -> list[Any]:
    values = args.get("values")
    if not isinstance(values, list) or not values:
        raise ValueError("'values' must be a non-empty list")
    return [_int_arg(args, "track_index", 0), _int_arg(args, "device_index", 0), *[float(v) for v in values]]


def _build_device_set_parameter(args: dict[str, Any]) -> list[Any]:
    track_index = _int_arg(args, "track_index", 0)
    device_index = _int_arg(args, "device_index", 0)
    parameter_index = _int_arg(args, "parameter_index", 0)
    value = _float_arg(args, "value", 0.0)
    return [track_index, device_index, parameter_index, value]


def _build_device_delete(args: dict[str, Any]) -> list[Any]:
    return [_int_arg(args, "track_index", 0), _int_arg(args, "device_index", 0)]


_TOOL_SPECS: dict[ToolName, ToolSpec] = {
    ToolName.create_midi_track: ToolSpec(
        tool=ToolName.create_midi_track,
        address="/live/song/create_midi_track",
        description="Create MIDI track",
        args_schema={"index": "int (optional)"},
        args_builder=_build_create_midi_track,
        domain="tracks",
    ),
    ToolName.create_audio_track: ToolSpec(
        tool=ToolName.create_audio_track,
        address="/live/song/create_audio_track",
        description="Create audio track",
        args_schema={"index": "int (optional)"},
        args_builder=_build_create_audio_track,
        domain="tracks",
    ),
    ToolName.set_tempo: ToolSpec(
        tool=ToolName.set_tempo,
        address="/live/song/set/tempo",
        description="Set global tempo",
        args_schema={"bpm": "float > 0"},
        args_builder=_build_set_tempo,
        domain="song",
    ),
    ToolName.fire_clip: ToolSpec(
        tool=ToolName.fire_clip,
        address="/live/clip/fire",
        description="Launch clip slot",
        args_schema={"track_index": "int", "clip_index": "int"},
        args_builder=_build_fire_clip,
        domain="session",
    ),
    ToolName.stop_all_clips: ToolSpec(
        tool=ToolName.stop_all_clips,
        address="/live/song/stop_all_clips",
        description="Stop all running clips",
        args_schema={},
        args_builder=_build_song_noargs,
        destructive=True,
        domain="session",
        safety="confirm",
    ),
    ToolName.set_track_volume: ToolSpec(
        tool=ToolName.set_track_volume,
        address="/live/track/set/volume",
        description="Set track volume",
        args_schema={"track_index": "int", "volume": "0..1"},
        args_builder=_build_set_track_volume,
        domain="tracks",
    ),
    ToolName.set_track_mute: ToolSpec(
        tool=ToolName.set_track_mute,
        address="/live/track/set/mute",
        description="Toggle mute",
        args_schema={"track_index": "int", "mute": "bool"},
        args_builder=lambda args: _build_set_track_toggle(args, "mute", True),
        domain="tracks",
    ),
    ToolName.set_track_solo: ToolSpec(
        tool=ToolName.set_track_solo,
        address="/live/track/set/solo",
        description="Toggle solo",
        args_schema={"track_index": "int", "solo": "bool"},
        args_builder=lambda args: _build_set_track_toggle(args, "solo", True),
        domain="tracks",
    ),
    ToolName.arm_track: ToolSpec(
        tool=ToolName.arm_track,
        address="/live/track/set/arm",
        description="Arm/disarm recording",
        args_schema={"track_index": "int", "arm": "bool"},
        args_builder=lambda args: _build_set_track_toggle(args, "arm", True),
        domain="tracks",
    ),
    ToolName.fire_scene: ToolSpec(
        tool=ToolName.fire_scene,
        address="/live/scene/fire",
        description="Launch scene",
        args_schema={"scene_index": "int"},
        args_builder=_build_fire_scene,
        domain="session",
    ),
    ToolName.song_play: ToolSpec(
        tool=ToolName.song_play,
        address="/live/song/start_playing",
        description="Start transport playback",
        args_schema={},
        args_builder=_build_song_noargs,
        domain="song",
    ),
    ToolName.song_stop: ToolSpec(
        tool=ToolName.song_stop,
        address="/live/song/stop_playing",
        description="Stop transport playback",
        args_schema={},
        args_builder=_build_song_noargs,
        domain="song",
    ),
    ToolName.song_continue: ToolSpec(
        tool=ToolName.song_continue,
        address="/live/song/continue_playing",
        description="Continue playback from current timeline position",
        args_schema={},
        args_builder=_build_song_noargs,
        domain="song",
    ),
    ToolName.song_record: ToolSpec(
        tool=ToolName.song_record,
        address="/live/song/set/session_record",
        description="Toggle session record",
        args_schema={"record": "bool"},
        args_builder=_build_song_record,
        domain="song",
    ),
    ToolName.song_metronome: ToolSpec(
        tool=ToolName.song_metronome,
        address="/live/song/set/metronome",
        description="Toggle metronome",
        args_schema={"enabled": "bool"},
        args_builder=_build_song_metronome,
        domain="song",
    ),
    ToolName.song_set_time_signature: ToolSpec(
        tool=ToolName.song_set_time_signature,
        address="/live/song/set/signature_numerator",
        description="Set time signature numerator and denominator",
        args_schema={"numerator": "int > 0", "denominator": "int > 0"},
        args_builder=_build_song_time_signature,
        domain="song",
    ),
    ToolName.song_set_global_quantization: ToolSpec(
        tool=ToolName.song_set_global_quantization,
        address="/live/song/set/clip_trigger_quantization",
        description="Set global clip launch quantization",
        args_schema={"quantization": "int >= 0"},
        args_builder=_build_song_global_quantization,
        domain="song",
    ),
    ToolName.song_set_count_in: ToolSpec(
        tool=ToolName.song_set_count_in,
        address="/live/song/set/count_in_duration",
        description="Set count-in duration",
        args_schema={"count_in": "int >= 0"},
        args_builder=_build_song_count_in,
        domain="song",
    ),
    ToolName.track_rename: ToolSpec(
        tool=ToolName.track_rename,
        address="/live/track/set/name",
        description="Rename track",
        args_schema={"track_index": "int", "name": "non-empty string"},
        args_builder=_build_track_rename,
        domain="tracks",
    ),
    ToolName.track_delete: ToolSpec(
        tool=ToolName.track_delete,
        address="/live/song/delete_track",
        description="Delete track",
        args_schema={"track_index": "int"},
        args_builder=_build_track_delete,
        destructive=True,
        domain="tracks",
        safety="confirm",
    ),
    ToolName.track_duplicate: ToolSpec(
        tool=ToolName.track_duplicate,
        address="/live/song/duplicate_track",
        description="Duplicate track",
        args_schema={"track_index": "int"},
        args_builder=_build_track_duplicate,
        domain="tracks",
    ),
    ToolName.track_set_pan: ToolSpec(
        tool=ToolName.track_set_pan,
        address="/live/track/set/panning",
        description="Set track pan",
        args_schema={"track_index": "int", "pan": "-1..1"},
        args_builder=_build_track_pan,
        domain="tracks",
    ),
    ToolName.track_set_send: ToolSpec(
        tool=ToolName.track_set_send,
        address="/live/track/set/send",
        description="Set track send level",
        args_schema={"track_index": "int", "send_index": "int", "level": "0..1"},
        args_builder=_build_track_send,
        domain="tracks",
    ),
    ToolName.scene_create: ToolSpec(
        tool=ToolName.scene_create,
        address="/live/song/create_scene",
        description="Create a scene",
        args_schema={"scene_index": "int (optional, -1 append)"},
        args_builder=_build_scene_create,
        domain="session",
    ),
    ToolName.scene_delete: ToolSpec(
        tool=ToolName.scene_delete,
        address="/live/song/delete_scene",
        description="Delete a scene",
        args_schema={"scene_index": "int"},
        args_builder=_build_scene_delete,
        destructive=True,
        domain="session",
        safety="confirm",
    ),
    ToolName.scene_rename: ToolSpec(
        tool=ToolName.scene_rename,
        address="/live/scene/set/name",
        description="Rename a scene",
        args_schema={"scene_index": "int", "name": "non-empty string"},
        args_builder=_build_scene_rename,
        domain="session",
    ),
    ToolName.clip_create: ToolSpec(
        tool=ToolName.clip_create,
        address="/live/clip_slot/create_clip",
        description="Create a clip in clip slot",
        args_schema={"track_index": "int", "clip_index": "int", "length_beats": "float > 0"},
        args_builder=_build_clip_create,
        domain="session",
    ),
    ToolName.clip_delete: ToolSpec(
        tool=ToolName.clip_delete,
        address="/live/clip_slot/delete_clip",
        description="Delete a clip from clip slot",
        args_schema={"track_index": "int", "clip_index": "int"},
        args_builder=_build_clip_delete,
        destructive=True,
        domain="session",
        safety="confirm",
    ),
    ToolName.clip_duplicate_loop: ToolSpec(
        tool=ToolName.clip_duplicate_loop,
        address="/live/clip/duplicate_loop",
        description="Duplicate a MIDI clip loop in place",
        args_schema={"track_index": "int", "clip_index": "int"},
        args_builder=_build_clip_noargs,
        domain="clips",
    ),
    ToolName.clip_duplicate_to: ToolSpec(
        tool=ToolName.clip_duplicate_to,
        address="/live/clip_slot/duplicate_clip_to",
        description="Duplicate a clip to an empty clip slot",
        args_schema={
            "track_index": "int",
            "clip_index": "int",
            "target_track_index": "int",
            "target_clip_index": "int",
        },
        args_builder=_build_clip_duplicate_to,
        domain="clips",
    ),
    ToolName.clip_rename: ToolSpec(
        tool=ToolName.clip_rename,
        address="/live/clip/set/name",
        description="Rename a clip",
        args_schema={"track_index": "int", "clip_index": "int", "name": "non-empty string"},
        args_builder=_build_clip_rename,
        domain="clips",
    ),
    ToolName.clip_set_color: ToolSpec(
        tool=ToolName.clip_set_color,
        address="/live/clip/set/color",
        description="Set clip RGB color",
        args_schema={"track_index": "int", "clip_index": "int", "color": "0..16777215"},
        args_builder=lambda args: _build_clip_int_property(args, "color", 0, 16777215),
        domain="clips",
    ),
    ToolName.clip_set_color_index: ToolSpec(
        tool=ToolName.clip_set_color_index,
        address="/live/clip/set/color_index",
        description="Set clip color index",
        args_schema={"track_index": "int", "clip_index": "int", "color_index": "0..69"},
        args_builder=lambda args: _build_clip_int_property(args, "color_index", 0, 69),
        domain="clips",
    ),
    ToolName.clip_set_gain: ToolSpec(
        tool=ToolName.clip_set_gain,
        address="/live/clip/set/gain",
        description="Set audio clip gain",
        args_schema={"track_index": "int", "clip_index": "int", "gain": "0..1"},
        args_builder=lambda args: _build_clip_float_property(args, "gain", 0.0, 1.0),
        domain="audio",
    ),
    ToolName.clip_set_pitch_coarse: ToolSpec(
        tool=ToolName.clip_set_pitch_coarse,
        address="/live/clip/set/pitch_coarse",
        description="Set audio clip coarse pitch in semitones",
        args_schema={"track_index": "int", "clip_index": "int", "semitones": "-48..48"},
        args_builder=lambda args: _build_clip_int_property(args, "semitones", -48, 48),
        domain="audio",
    ),
    ToolName.clip_set_pitch_fine: ToolSpec(
        tool=ToolName.clip_set_pitch_fine,
        address="/live/clip/set/pitch_fine",
        description="Set audio clip fine pitch in cents",
        args_schema={"track_index": "int", "clip_index": "int", "cents": "-50..49"},
        args_builder=lambda args: _build_clip_float_property(args, "cents", -50.0, 49.0),
        domain="audio",
    ),
    ToolName.clip_set_start_marker: ToolSpec(
        tool=ToolName.clip_set_start_marker,
        address="/live/clip/set/start_marker",
        description="Set clip start marker in beats",
        args_schema={"track_index": "int", "clip_index": "int", "start_marker": "float >= 0"},
        args_builder=lambda args: _build_clip_beat_property(args, "start_marker"),
        domain="clips",
    ),
    ToolName.clip_set_end_marker: ToolSpec(
        tool=ToolName.clip_set_end_marker,
        address="/live/clip/set/end_marker",
        description="Set clip end marker in beats",
        args_schema={"track_index": "int", "clip_index": "int", "end_marker": "float >= 0"},
        args_builder=lambda args: _build_clip_beat_property(args, "end_marker"),
        domain="clips",
    ),
    ToolName.clip_set_loop_start: ToolSpec(
        tool=ToolName.clip_set_loop_start,
        address="/live/clip/set/loop_start",
        description="Set clip loop start in beats",
        args_schema={"track_index": "int", "clip_index": "int", "loop_start": "float >= 0"},
        args_builder=lambda args: _build_clip_beat_property(args, "loop_start"),
        domain="clips",
    ),
    ToolName.clip_set_loop_end: ToolSpec(
        tool=ToolName.clip_set_loop_end,
        address="/live/clip/set/loop_end",
        description="Set clip loop end in beats",
        args_schema={"track_index": "int", "clip_index": "int", "loop_end": "float >= 0"},
        args_builder=lambda args: _build_clip_beat_property(args, "loop_end"),
        domain="clips",
    ),
    ToolName.clip_set_looping: ToolSpec(
        tool=ToolName.clip_set_looping,
        address="/live/clip/set/looping",
        description="Toggle clip looping",
        args_schema={"track_index": "int", "clip_index": "int", "looping": "bool"},
        args_builder=lambda args: _build_clip_bool_property(args, "looping", True),
        domain="clips",
    ),
    ToolName.clip_set_position: ToolSpec(
        tool=ToolName.clip_set_position,
        address="/live/clip/set/position",
        description="Set clip loop position while preserving loop length",
        args_schema={"track_index": "int", "clip_index": "int", "position": "float >= 0"},
        args_builder=lambda args: _build_clip_beat_property(args, "position"),
        domain="clips",
    ),
    ToolName.clip_set_warping: ToolSpec(
        tool=ToolName.clip_set_warping,
        address="/live/clip/set/warping",
        description="Toggle audio clip warping",
        args_schema={"track_index": "int", "clip_index": "int", "warping": "bool"},
        args_builder=lambda args: _build_clip_bool_property(args, "warping", True),
        domain="audio",
    ),
    ToolName.clip_set_warp_mode: ToolSpec(
        tool=ToolName.clip_set_warp_mode,
        address="/live/clip/set/warp_mode",
        description="Set audio clip warp mode",
        args_schema={"track_index": "int", "clip_index": "int", "warp_mode": "0..6"},
        args_builder=lambda args: _build_clip_int_property(args, "warp_mode", 0, 6),
        domain="audio",
    ),
    ToolName.clip_set_ram_mode: ToolSpec(
        tool=ToolName.clip_set_ram_mode,
        address="/live/clip/set/ram_mode",
        description="Toggle audio clip RAM mode",
        args_schema={"track_index": "int", "clip_index": "int", "ram_mode": "bool"},
        args_builder=lambda args: _build_clip_bool_property(args, "ram_mode", True),
        domain="audio",
    ),
    ToolName.clip_set_muted: ToolSpec(
        tool=ToolName.clip_set_muted,
        address="/live/clip/set/muted",
        description="Mute or unmute a clip",
        args_schema={"track_index": "int", "clip_index": "int", "muted": "bool"},
        args_builder=lambda args: _build_clip_bool_property(args, "muted", True),
        domain="clips",
    ),
    ToolName.clip_set_launch_mode: ToolSpec(
        tool=ToolName.clip_set_launch_mode,
        address="/live/clip/set/launch_mode",
        description="Set clip launch mode",
        args_schema={"track_index": "int", "clip_index": "int", "launch_mode": "0..3"},
        args_builder=lambda args: _build_clip_int_property(args, "launch_mode", 0, 3),
        domain="clips",
    ),
    ToolName.clip_set_launch_quantization: ToolSpec(
        tool=ToolName.clip_set_launch_quantization,
        address="/live/clip/set/launch_quantization",
        description="Set clip launch quantization",
        args_schema={"track_index": "int", "clip_index": "int", "launch_quantization": "0..14"},
        args_builder=lambda args: _build_clip_int_property(args, "launch_quantization", 0, 14),
        domain="clips",
    ),
    ToolName.clip_set_velocity_amount: ToolSpec(
        tool=ToolName.clip_set_velocity_amount,
        address="/live/clip/set/velocity_amount",
        description="Set clip launch velocity sensitivity",
        args_schema={"track_index": "int", "clip_index": "int", "velocity_amount": "0..1"},
        args_builder=lambda args: _build_clip_float_property(args, "velocity_amount", 0.0, 1.0),
        domain="clips",
    ),
    ToolName.midi_notes_get: ToolSpec(
        tool=ToolName.midi_notes_get,
        address="/live/clip/get/notes",
        description="Request MIDI notes from a clip, optionally by pitch/time range",
        args_schema={
            "track_index": "int",
            "clip_index": "int",
            "start_pitch": "int 0..127 optional",
            "pitch_span": "int > 0 optional",
            "start_time": "float optional",
            "time_span": "float > 0 optional",
        },
        args_builder=_build_midi_notes_get,
        domain="midi",
    ),
    ToolName.midi_notes_add: ToolSpec(
        tool=ToolName.midi_notes_add,
        address="/live/clip/add/notes",
        description="Add MIDI notes to a clip",
        args_schema={
            "track_index": "int",
            "clip_index": "int",
            "notes": "list of {pitch:0..127,start_time>=0,duration>0,velocity:0..127,mute?:bool}",
        },
        args_builder=_build_midi_notes_add,
        domain="midi",
    ),
    ToolName.midi_notes_remove: ToolSpec(
        tool=ToolName.midi_notes_remove,
        address="/live/clip/remove/notes",
        description="Remove MIDI notes in a pitch/time range, or all notes when no range is provided",
        args_schema={
            "track_index": "int",
            "clip_index": "int",
            "start_pitch": "int 0..127 optional",
            "pitch_span": "int > 0 optional",
            "start_time": "float optional",
            "time_span": "float > 0 optional",
        },
        args_builder=_build_midi_notes_remove,
        destructive=True,
        domain="midi",
        safety="confirm",
    ),
    ToolName.midi_notes_clear: ToolSpec(
        tool=ToolName.midi_notes_clear,
        address="/live/clip/remove/notes",
        description="Remove all MIDI notes from a clip",
        args_schema={"track_index": "int", "clip_index": "int"},
        args_builder=_build_midi_notes_clear,
        destructive=True,
        domain="midi",
        safety="confirm",
    ),
    ToolName.device_get_parameters: ToolSpec(
        tool=ToolName.device_get_parameters,
        address="/live/device/get/parameters/value",
        description="Request all parameter values for a device",
        args_schema={"track_index": "int", "device_index": "int"},
        args_builder=_build_device_get_parameters,
        domain="devices",
    ),
    ToolName.device_get_parameter: ToolSpec(
        tool=ToolName.device_get_parameter,
        address="/live/device/get/parameter/value",
        description="Request a single device parameter value",
        args_schema={"track_index": "int", "device_index": "int", "parameter_index": "int"},
        args_builder=_build_device_get_parameter,
        domain="devices",
    ),
    ToolName.device_get_parameter_name: ToolSpec(
        tool=ToolName.device_get_parameter_name,
        address="/live/device/get/parameter/name",
        description="Request a single device parameter name",
        args_schema={"track_index": "int", "device_index": "int", "parameter_index": "int"},
        args_builder=_build_device_get_parameter,
        domain="devices",
    ),
    ToolName.device_get_parameter_value_string: ToolSpec(
        tool=ToolName.device_get_parameter_value_string,
        address="/live/device/get/parameter/value_string",
        description="Request a human-readable device parameter value",
        args_schema={"track_index": "int", "device_index": "int", "parameter_index": "int"},
        args_builder=_build_device_get_parameter,
        domain="devices",
    ),
    ToolName.device_get_parameter_names: ToolSpec(
        tool=ToolName.device_get_parameter_names,
        address="/live/device/get/parameters/name",
        description="Request all parameter names for a device",
        args_schema={"track_index": "int", "device_index": "int"},
        args_builder=_build_device_get_parameters,
        domain="devices",
    ),
    ToolName.device_get_parameter_min_values: ToolSpec(
        tool=ToolName.device_get_parameter_min_values,
        address="/live/device/get/parameters/min",
        description="Request device parameter minimum values",
        args_schema={"track_index": "int", "device_index": "int"},
        args_builder=_build_device_get_parameters,
        domain="devices",
    ),
    ToolName.device_get_parameter_max_values: ToolSpec(
        tool=ToolName.device_get_parameter_max_values,
        address="/live/device/get/parameters/max",
        description="Request device parameter maximum values",
        args_schema={"track_index": "int", "device_index": "int"},
        args_builder=_build_device_get_parameters,
        domain="devices",
    ),
    ToolName.device_set_parameters: ToolSpec(
        tool=ToolName.device_set_parameters,
        address="/live/device/set/parameters/value",
        description="Set multiple device parameter values by index order",
        args_schema={"track_index": "int", "device_index": "int", "values": "non-empty float list"},
        args_builder=_build_device_set_parameters,
        domain="parameters",
    ),
    ToolName.device_set_parameter: ToolSpec(
        tool=ToolName.device_set_parameter,
        address="/live/device/set/parameter/value",
        description="Set a device parameter value",
        args_schema={
            "track_index": "int",
            "device_index": "int",
            "parameter_index": "int",
            "value": "float",
        },
        args_builder=_build_device_set_parameter,
        domain="parameters",
    ),
    ToolName.device_delete: ToolSpec(
        tool=ToolName.device_delete,
        address="/live/track/delete_device",
        description="Delete a device from a track",
        args_schema={"track_index": "int", "device_index": "int"},
        args_builder=_build_device_delete,
        destructive=True,
        domain="devices",
        safety="confirm",
    ),
    ToolName.utility_undo: ToolSpec(
        tool=ToolName.utility_undo,
        address="/live/song/undo",
        description="Undo last operation",
        args_schema={},
        args_builder=_build_song_noargs,
        domain="utility",
    ),
    ToolName.utility_redo: ToolSpec(
        tool=ToolName.utility_redo,
        address="/live/song/redo",
        description="Redo last undone operation",
        args_schema={},
        args_builder=_build_song_noargs,
        domain="utility",
    ),
}


class AbletonOSCClient:
    def __init__(self, host: str, port: int) -> None:
        self._udp = SimpleUDPClient(host, port)

    def send(self, action: AbletonAction) -> None:
        self._udp.send_message(action.address, action.args)

    def to_action(self, tool: ToolName, args: dict[str, Any]) -> AbletonAction:
        spec = _TOOL_SPECS.get(tool)
        if spec is None:
            raise ValueError(f"Unsupported tool: {tool}")
        try:
            normalized_args = spec.args_builder(args)
        except Exception as exc:
            raise ValueError(f"Invalid args for '{tool.value}': {exc}") from exc
        return AbletonAction(
            tool=tool,
            address=spec.address,
            args=normalized_args,
            description=spec.description,
            destructive=spec.destructive,
        )


def capabilities() -> list[Capability]:
    return [
        Capability(
            tool=spec.tool,
            description=spec.description,
            args_schema=spec.args_schema,
            destructive=spec.destructive,
            domain=spec.domain,
            safety=spec.safety,
        )
        for spec in _TOOL_SPECS.values()
    ]
