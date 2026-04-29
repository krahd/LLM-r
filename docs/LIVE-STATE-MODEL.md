# Live State Model

`/api/live/*` endpoints expose the internal snapshot model used by LLM-r:

- `song`
  - `tempo`, `is_playing`, `session_record`, `metronome`
  - `time_signature` (`numerator`, `denominator`)
  - `global_quantization`, `count_in`
- `tracks[]`
  - `track_index`, `name`, `volume`, `pan`, `mute`, `solo`, `arm`
  - `sends{send_index: level}`
  - `clips[]`
    - `clip_index`, `name`, `length_beats`
    - `notes[]` (`pitch`, `start_time`, `duration`, `velocity`, `mute`)
    - clip properties updated by LLM-r actions: `color`, `color_index`, `gain`,
      `pitch_coarse`, `pitch_fine`, `start_marker`, `end_marker`,
      `loop_start`, `loop_end`, `looping`, `position`, `warping`,
      `warp_mode`, `ram_mode`, `muted`, `launch_mode`,
      `launch_quantization`, `velocity_amount`
  - `devices[]` (`device_index`, `name`, `parameters{parameter_index: value}`)
- `scenes[]`
  - `scene_index`, `name`

This is currently an optimistic state cache updated from executed actions.
