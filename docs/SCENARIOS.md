# Scenarios

These recipes describe workflows the current capability set can execute. They do
not imply MIDI note generation, audio rendering, plugin loading, or semantic
mix/master processing.

## Sketch Starter

1. Set tempo and time signature.
2. Create and rename MIDI/audio tracks.
3. Create and rename a scene.
4. Create empty clips.
5. Arm tracks and enable metronome/count-in when recording is implied.
6. Fire the scene or clip only when the user asks to start playback.

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

- Humanize, quantize, transpose, velocity edit, or compose MIDI notes.
- Load instruments, effects, samples, presets, or plugin chains.
- Edit audio clips, warp markers, arrangement clips, or automation lanes.
- Export, render, resample, or loudness-analyze a Live set.
