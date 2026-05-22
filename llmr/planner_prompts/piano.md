# Piano and harmony planning guidance

For piano, keys, chords, and ballad requests:
- Create a MIDI track if the request implies generated MIDI and no suitable selected track is provided.
- Prefer loading a piano/keys instrument with `device_load` when Device Bridge is available.
- Use `clip_create` followed by `midi_notes_add`.
- For jazz ballads, use slow-to-medium tempo unless the user specifies tempo. If changing tempo is not explicitly requested, do not change it unless necessary for the musical result.
- Use extended chords when appropriate: maj7, min7, dominant 7, 9ths, 13ths, altered dominants.
- Use sparse voicings and sustained durations for ballads.
- Include a simple structure: opening chord phrase, response, variation, cadence.
- Avoid generating enormous raw note arrays. A compact voicing progression is preferable to invalid exhaustive material.

Typical jazz-ballad materials:
- ii-V-I progressions.
- Rootless left-hand voicings and right-hand colour tones.
- Gentle syncopation and occasional anticipations.
- Velocities around 45-85 unless the user asks for aggressive playing.
