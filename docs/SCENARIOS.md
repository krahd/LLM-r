# Scenarios

These are tested or expected workflows for the current release. They are aimed
at practical set setup and safe execution, not full production automation.

Each scenario includes a suggested prompt, expected plan shape, safety notes,
required dependencies, and dry-run behaviour.

## 1. Tempo and transport setup

- User prompt: "Set tempo to 124 BPM, set 4/4, turn metronome on, and continue playback."
- Expected plan shape:
   - `set_tempo`
   - `song_set_time_signature`
   - `song_metronome`
   - `song_continue` or `song_play`
- Safety notes: non-destructive, but changes global song state.
- Required dependencies: AbletonOSC only.
- Dry-run without mutation: yes.

## 2. Create MIDI and audio tracks

- User prompt: "Create one MIDI track called Drums and one audio track called Vox In."
- Expected plan shape:
   - `create_midi_track`
   - `track_rename`
   - `create_audio_track`
   - `track_rename`
- Safety notes: non-destructive; appends tracks unless prompt targets an index.
- Required dependencies: AbletonOSC only.
- Dry-run without mutation: yes.

## 3. Load a device with Device Bridge

- User prompt: "Load Drum Rack on track 2."
- Expected plan shape:
   - optional `track_rename` or context setup step
   - `device_load` with `query="Drum Rack"` and a suitable `device_type`
- Safety notes: loading can change track device chain; ambiguous matches should
   stay unresolved until user confirms a specific candidate/path.
- Required dependencies: AbletonOSC + Device Bridge.
- Dry-run without mutation: yes.

## 4. Create a simple drum sketch

- User prompt: "Create a 4-bar drum sketch at 122 BPM with a kick on beats 1 and 3."
- Expected plan shape:
   - `set_tempo`
   - `create_midi_track`
   - `track_rename`
   - `clip_create`
   - `midi_notes_add`
- Safety notes: non-destructive if writing into a new or empty clip slot.
- Required dependencies: AbletonOSC only.
- Dry-run without mutation: yes.

## 5. Duplicate and launch clips

- User prompt: "Duplicate clip 0 on track 1 to clip 1 and launch the new clip."
- Expected plan shape:
   - `clip_duplicate_to`
   - `fire_clip`
- Safety notes: duplicate is usually reversible with undo; launch affects
   playback state.
- Required dependencies: AbletonOSC only.
- Dry-run without mutation: yes.

## 6. Dry-run a destructive operation

- User prompt: "Dry-run deleting clip 2 on track 0 so I can inspect the plan first."
- Expected plan shape:
   - `clip_delete` (destructive=true)
- Safety notes: destructive tool; execute path requires explicit destructive
   approval and dry-run off.
- Required dependencies: AbletonOSC only.
- Dry-run without mutation: yes.

## 7. Macro usage

- User prompt: "Run the performance_prep macro."
- Expected plan shape:
   - via `POST /api/plan_macro` -> expanded calls from macro definition
   - built-in examples: `idea_sketch`, `performance_prep`
- Safety notes: macro safety depends on contained calls; review plan before run.
- Required dependencies: AbletonOSC only for current built-ins.
- Dry-run without mutation: yes.

## Not covered by these scenarios

- Rich audio editing and warp marker editing.
- Full arrangement composition across many tracks/scenes.
- Automatic plug-in chain construction and mastering/loudness/export workflows.
