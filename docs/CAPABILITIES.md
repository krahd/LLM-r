# Capabilities

The authoritative source at runtime is always `GET /api/capabilities`. The
table below is derived from `llmr/ableton_osc.py` and kept in sync manually.

## Domains

| Domain | Covers |
| --- | --- |
| `song` | Transport, tempo, time signature, quantization, count-in |
| `tracks` | Track create / delete / duplicate / rename / mixer / send |
| `session` | Scene and clip-slot lifecycle, clip/scene launch |
| `clips` | Clip duplication, names, colors, launch behavior, loop/marker properties |
| `midi` | MIDI note read requests, note insertion, note removal |
| `audio` | Audio clip gain, pitch, warp mode, RAM mode, warping toggle |
| `devices` | Device and parameter inspection, device deletion |
| `parameters` | Device parameter writes |
| `utility` | Undo / redo |

## Tool Catalog

| Tool | Domain | Destructive | Args |
| --- | --- | --- | --- |
| `create_midi_track` | tracks | - | `index: int` (optional, -1 appends) |
| `create_audio_track` | tracks | - | `index: int` (optional, -1 appends) |
| `set_tempo` | song | - | `bpm: float > 0` |
| `fire_clip` | session | - | `track_index: int`, `clip_index: int` |
| `stop_all_clips` | session | **yes** | - |
| `set_track_volume` | tracks | - | `track_index: int`, `volume: 0..1` |
| `set_track_mute` | tracks | - | `track_index: int`, `mute: bool` |
| `set_track_solo` | tracks | - | `track_index: int`, `solo: bool` |
| `arm_track` | tracks | - | `track_index: int`, `arm: bool` |
| `fire_scene` | session | - | `scene_index: int` |
| `song_play` | song | - | - |
| `song_stop` | song | - | - |
| `song_continue` | song | - | - |
| `song_record` | song | - | `record: bool` |
| `song_metronome` | song | - | `enabled: bool` |
| `song_set_time_signature` | song | - | `numerator: int > 0`, `denominator: int > 0` |
| `song_set_global_quantization` | song | - | `quantization: int >= 0` |
| `song_set_count_in` | song | - | `count_in: int >= 0` |
| `track_rename` | tracks | - | `track_index: int`, `name: non-empty string` |
| `track_delete` | tracks | **yes** | `track_index: int` |
| `track_duplicate` | tracks | - | `track_index: int` |
| `track_set_pan` | tracks | - | `track_index: int`, `pan: -1..1` |
| `track_set_send` | tracks | - | `track_index: int`, `send_index: int`, `level: 0..1` |
| `scene_create` | session | - | `scene_index: int` (optional, -1 appends) |
| `scene_delete` | session | **yes** | `scene_index: int` |
| `scene_rename` | session | - | `scene_index: int`, `name: non-empty string` |
| `clip_create` | session | - | `track_index: int`, `clip_index: int`, `length_beats: float > 0` |
| `clip_delete` | session | **yes** | `track_index: int`, `clip_index: int` |
| `clip_duplicate_loop` | clips | - | `track_index: int`, `clip_index: int` |
| `clip_duplicate_to` | clips | - | `track_index: int`, `clip_index: int`, `target_track_index: int`, `target_clip_index: int` |
| `clip_rename` | clips | - | `track_index: int`, `clip_index: int`, `name: non-empty string` |
| `clip_set_color` | clips | - | `track_index: int`, `clip_index: int`, `color: 0..16777215` |
| `clip_set_color_index` | clips | - | `track_index: int`, `clip_index: int`, `color_index: 0..69` |
| `clip_set_start_marker` | clips | - | `track_index: int`, `clip_index: int`, `start_marker: float >= 0` |
| `clip_set_end_marker` | clips | - | `track_index: int`, `clip_index: int`, `end_marker: float >= 0` |
| `clip_set_loop_start` | clips | - | `track_index: int`, `clip_index: int`, `loop_start: float >= 0` |
| `clip_set_loop_end` | clips | - | `track_index: int`, `clip_index: int`, `loop_end: float >= 0` |
| `clip_set_looping` | clips | - | `track_index: int`, `clip_index: int`, `looping: bool` |
| `clip_set_position` | clips | - | `track_index: int`, `clip_index: int`, `position: float >= 0` |
| `clip_set_muted` | clips | - | `track_index: int`, `clip_index: int`, `muted: bool` |
| `clip_set_launch_mode` | clips | - | `track_index: int`, `clip_index: int`, `launch_mode: 0..3` |
| `clip_set_launch_quantization` | clips | - | `track_index: int`, `clip_index: int`, `launch_quantization: 0..14` |
| `clip_set_velocity_amount` | clips | - | `track_index: int`, `clip_index: int`, `velocity_amount: 0..1` |
| `midi_notes_get` | midi | - | `track_index: int`, `clip_index: int`, optional `start_pitch`, `pitch_span`, `start_time`, `time_span` |
| `midi_notes_add` | midi | - | `track_index: int`, `clip_index: int`, `notes: [{pitch,start_time,duration,velocity,mute?}]` |
| `midi_notes_remove` | midi | **yes** | `track_index: int`, `clip_index: int`, optional pitch/time range |
| `midi_notes_clear` | midi | **yes** | `track_index: int`, `clip_index: int` |
| `clip_set_gain` | audio | - | `track_index: int`, `clip_index: int`, `gain: 0..1` |
| `clip_set_pitch_coarse` | audio | - | `track_index: int`, `clip_index: int`, `semitones: -48..48` |
| `clip_set_pitch_fine` | audio | - | `track_index: int`, `clip_index: int`, `cents: -50..49` |
| `clip_set_warping` | audio | - | `track_index: int`, `clip_index: int`, `warping: bool` |
| `clip_set_warp_mode` | audio | - | `track_index: int`, `clip_index: int`, `warp_mode: 0..6` |
| `clip_set_ram_mode` | audio | - | `track_index: int`, `clip_index: int`, `ram_mode: bool` |
| `device_get_parameters` | devices | - | `track_index: int`, `device_index: int` |
| `device_get_parameter` | devices | - | `track_index: int`, `device_index: int`, `parameter_index: int` |
| `device_get_parameter_name` | devices | - | `track_index: int`, `device_index: int`, `parameter_index: int` |
| `device_get_parameter_value_string` | devices | - | `track_index: int`, `device_index: int`, `parameter_index: int` |
| `device_get_parameter_names` | devices | - | `track_index: int`, `device_index: int` |
| `device_get_parameter_min_values` | devices | - | `track_index: int`, `device_index: int` |
| `device_get_parameter_max_values` | devices | - | `track_index: int`, `device_index: int` |
| `device_set_parameters` | parameters | - | `track_index: int`, `device_index: int`, `values: non-empty float list` |
| `device_set_parameter` | parameters | - | `track_index: int`, `device_index: int`, `parameter_index: int`, `value: float` |
| `device_delete` | devices | **yes** | `track_index: int`, `device_index: int` |
| `utility_undo` | utility | - | - |
| `utility_redo` | utility | - | - |

Tools marked **destructive** require `"approved": true` in `POST /api/execute`,
unless `dry_run` is enabled.

## Notes On Coverage

- MIDI note add/get/remove are backed by AbletonOSC's current Clip API. Editing
  note timing or velocity is represented as remove-and-add operations over a
  known pitch/time range.
- Audio clip operations are non-destructive clip-property edits: gain, pitch,
  start/end markers, loop settings, warping, warp mode, RAM mode, and clip
  launch behavior.
- Upstream AbletonOSC does not currently expose browser search/load, plugin
  loading, preset loading, destructive sample-file editing, arrangement clip
  insertion, or warp marker CRUD. Those need an AbletonOSC/Remote Script
  extension before they can be executable LLM-r tools.

## Filtering

`GET /api/v2/capabilities` accepts query parameters to filter the list:

| Parameter | Type | Description |
| --- | --- | --- |
| `domain` | string | Return only tools in this domain |
| `safety` | string | Return only tools with this safety level (`safe`, `confirm`) |
| `include_destructive` | bool | Set to `false` to exclude destructive tools |
