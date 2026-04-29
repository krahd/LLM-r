# Scenarios

These recipes describe workflows the current capability set can execute. They do
not imply audio rendering, plugin loading, browser search, warp marker editing,
or semantic mix/master processing.

## Sketch Starter

1. Set tempo and time signature.
2. Create and rename MIDI/audio tracks.
3. Create and rename a scene.
4. Create empty clips.
5. Add MIDI notes when the user gives or requests concrete notes/rhythms.
6. Arm tracks and enable metronome/count-in when recording is implied.
7. Fire the scene or clip only when the user asks to start playback.

## MIDI Clip Editing

1. Use `midi_notes_get` when a client is listening for AbletonOSC replies or
   when inspecting an already known LLM-r state cache.
2. Add notes with explicit pitch, start time, duration, velocity, and optional
   mute state.
3. Edit timing, pitch, or velocity by removing notes in a known pitch/time range
   and adding replacement notes.
4. Use destructive approval for remove or clear operations.

## Audio Clip Prep

1. Adjust non-destructive audio clip properties: gain, transpose/detune, warping,
   warp mode, RAM mode, clip start/end markers, and loop settings.
2. Keep destructive sample-file editing, resampling, exporting, and rendering out
   of executable plans until a dedicated audio processing pipeline exists.

## Performance Prep

1. Set tempo, time signature, global quantization, and count-in.
2. Create or rename scenes.
3. Arm requested tracks.
4. Clear unintended mute/solo states when explicitly requested.
5. Start, continue, stop, or record only when requested.

## Mix Prep

1. Adjust track volume, pan, mute, solo, and sends.
2. Set known device parameters by track/device/parameter index.
3. Avoid mastering claims unless future capabilities add export/render, loudness,
   EQ, compression, and limiting operations.

## Unsupported Today

- Fully automatic humanize, quantize, transpose, or velocity shaping of unknown
  existing MIDI clips without note readback.
- Load instruments, effects, samples, presets, or plugin chains.
- Edit warp markers, arrangement clips, or automation lanes.
- Export, render, resample, or loudness-analyze a Live set.
