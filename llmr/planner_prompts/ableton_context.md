# Ableton Live planning semantics

Ableton Live has different editing surfaces. Treat them differently.

Session View:
- `clip_create`, `midi_notes_add`, `fire_clip`, scene tools, clip loop tools, clip colour/name tools, and clip launch tools act on Session slots.
- Use Session clips when the context says the current view is `session`, or when no view context is available.
- A request for a loop, idea, groove, pattern, clip, scene, or sketch usually means Session View.

Arrangement View:
- A request for a song-length track, timeline, two-minute piece, arrangement, intro/build/drop/outro, or full cue should prefer Arrangement semantics when available.
- If no Arrangement tools are available, create a Session clip of the requested duration or a useful subsection, and explain that LLM-r is using Session clip tools because timeline insertion is not available.

Duration conversion:
- Convert seconds/minutes to beats using the current tempo when available.
- If tempo is unknown, assume 120 BPM.
- Formula: beats = seconds * bpm / 60.
- For 4/4 music, one bar = 4 beats.
- Example: 1 minute at 120 BPM = 120 beats = 30 bars.
- Example: 2 minutes at 120 BPM = 240 beats = 60 bars.

Index defaults:
- If selected_track is available, use it.
- Otherwise use track_index 0 for editing existing material and index -1 for creating a new track at the end.
- If selected_clip is available, use it.
- Otherwise use clip_index 0 for new material unless the request names a different slot.
