# Capabilities

The authoritative source at runtime is always `GET /api/capabilities`. The table below is derived from `llmr/ableton_osc.py` and kept in sync manually.

## Domains

| Domain | Covers |
| --- | --- |
| `song` | Transport, tempo, time signature, quantization, count-in |
| `tracks` | Track create / delete / duplicate / rename / mixer / send |
| `session` | Scene and clip lifecycle, clip launch |
| `devices` | Device parameter inspection |
| `parameters` | Device parameter writes |
| `utility` | Undo / redo |

## Tool catalog

| Tool | Domain | Destructive | Args |
| --- | --- | --- | --- |
| `create_midi_track` | tracks | — | `index: int` (optional, -1 appends) |
| `create_audio_track` | tracks | — | `index: int` (optional, -1 appends) |
| `set_tempo` | song | — | `bpm: float > 0` |
| `fire_clip` | session | — | `track_index: int`, `clip_index: int` |
| `stop_all_clips` | session | **yes** | — |
| `set_track_volume` | tracks | — | `track_index: int`, `volume: 0..1` |
| `set_track_mute` | tracks | — | `track_index: int`, `mute: bool` |
| `set_track_solo` | tracks | — | `track_index: int`, `solo: bool` |
| `arm_track` | tracks | — | `track_index: int`, `arm: bool` |
| `fire_scene` | session | — | `scene_index: int` |
| `song_play` | song | — | — |
| `song_stop` | song | — | — |
| `song_continue` | song | — | — |
| `song_record` | song | — | `record: bool` |
| `song_metronome` | song | — | `enabled: bool` |
| `song_set_time_signature` | song | — | `numerator: int > 0`, `denominator: int > 0` |
| `song_set_global_quantization` | song | — | `quantization: int >= 0` |
| `song_set_count_in` | song | — | `count_in: int >= 0` |
| `track_rename` | tracks | — | `track_index: int`, `name: non-empty string` |
| `track_delete` | tracks | **yes** | `track_index: int` |
| `track_duplicate` | tracks | — | `track_index: int` |
| `track_set_pan` | tracks | — | `track_index: int`, `pan: -1..1` |
| `track_set_send` | tracks | — | `track_index: int`, `send_index: int`, `level: 0..1` |
| `scene_create` | session | — | `scene_index: int` (optional, -1 appends) |
| `scene_delete` | session | **yes** | `scene_index: int` |
| `scene_rename` | session | — | `scene_index: int`, `name: non-empty string` |
| `clip_create` | session | — | `track_index: int`, `clip_index: int`, `length_beats: float > 0` |
| `clip_delete` | session | **yes** | `track_index: int`, `clip_index: int` |
| `device_get_parameters` | devices | — | `track_index: int`, `device_index: int` |
| `device_set_parameter` | parameters | — | `track_index: int`, `device_index: int`, `parameter_index: int`, `value: float` |
| `utility_undo` | utility | — | — |
| `utility_redo` | utility | — | — |

Tools marked **destructive** require `"approved": true` in `POST /api/execute`, unless `dry_run` is enabled.

## Filtering

`GET /api/v2/capabilities` accepts query parameters to filter the list:

| Parameter | Type | Description |
| --- | --- | --- |
| `domain` | string | Return only tools in this domain |
| `safety` | string | Return only tools with this safety level (`safe`, `confirm`) |
| `include_destructive` | bool | Set to `false` to exclude destructive tools |
