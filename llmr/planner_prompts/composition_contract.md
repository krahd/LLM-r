# Musical composition contract

LLM-r must produce executable musical plans, not generic descriptions.

For musical requests:
- Create or select an appropriate MIDI track when the user asks for generated MIDI material.
- Create a clip with `length_beats` matching the requested duration when feasible.
- Add MIDI notes with `midi_notes_add` only after creating the clip.
- Keep raw note lists bounded. Prefer 16 to 64 musically meaningful notes per call. Avoid thousands of notes in one response.
- For longer requests, create a representative pattern across the full clip length using repeated motifs, fills, accents, and sparse variations rather than exhaustive dense sequencing.
- Use velocities between 1 and 127.
- Use `start_time` and `duration` in beats.
- Do not use negative start times or zero/negative durations.
- For humanisation, vary velocity and timing slightly inside the generated notes. If exact timing perturbation is too complex, vary velocity and include an explanation.
- For `extend`, `humanise`, or `add variation` requests, use existing selected clip context if available. If not available, create a new longer clip and explain the assumption.

Completeness expectations:
- "Complete" means structured, not necessarily dense.
- For a one-minute idea, include at least an A section and a variation/fill near the end.
- For two minutes, include repeated sections with at least some changes every 8 or 16 bars.
- If the current tool set cannot manipulate Arrangement View, state this limitation while still making the best executable Session clip plan.
