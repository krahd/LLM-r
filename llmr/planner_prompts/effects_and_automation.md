# Effects, devices, and automation guidance

Effects and instruments:
- Use `device_load` for instruments, audio effects, MIDI effects, plug-ins, drums, and Ableton browser devices.
- Use `device_type` carefully: `instrument`, `audio_effect`, `midi_effect`, `plugin`, `drum`, or `all`.
- Use `device_set_parameter` or `device_set_parameters` after loading or selecting a device when the user asks for compression, reverb amount, delay feedback, filter cutoff, wet/dry, gain, or similar settings.
- If a device parameter name is known semantically, prefer `parameter_name` with `device_name`; otherwise use `parameter_index` only when context provides it.
- If the request is ambiguous, load the most general useful device and explain the assumption concisely.

Automation:
- Treat automation as a first-class musical request.
- If an automation-envelope tool is available, use it for parameter changes over time.
- In the current tool set, if no automation-envelope tool is available, do not pretend to draw automation. Use static parameter changes only where useful, and explain: "Automation envelopes are not yet exposed; I set the static parameter value instead."
- For volume/pan/send changes over time, use automation tools only if available. Otherwise, avoid fake automation.

Examples of correct fallbacks:
- "add reverb to this piano" -> `device_load` with audio_effect/reverb, then optionally `device_set_parameter` for wet/dry if parameter context is available.
- "automate filter cutoff opening over 8 bars" -> use automation tool if listed; otherwise no-op or static parameter with explanation.
- "add compression and reverb to drums" -> load compressor and reverb on the drum track; set conservative static values if possible.
