# Live State Model (v1)

`/api/live/*` endpoints expose the internal snapshot model used by LLM-r:

- `song`
  - `tempo`, `is_playing`, `session_record`, `metronome`
  - `time_signature` (`numerator`, `denominator`)
  - `global_quantization`, `count_in`
- `tracks[]`
  - `track_index`, `name`, `volume`, `pan`, `mute`, `solo`, `arm`
  - `sends{send_index: level}`
  - `clips[]` (`clip_index`, `length_beats`)
  - `devices[]` (`device_index`, `name`, `parameters{parameter_index: value}`)
- `scenes[]`
  - `scene_index`, `name`

This is currently an optimistic state cache updated from executed actions.
