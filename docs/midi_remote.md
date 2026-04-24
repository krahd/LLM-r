MIDI Remote Script Bridge (LLM-r)
================================

This document explains the MIDI Remote Script bridge option for LLM-r. Remote scripts run inside Ableton Live and have direct access to the Live Object Model (LOM), avoiding the need for Max for Live.

Overview
- LLM-r will send small JSON messages over UDP to the remote script. The remote script listens on a configurable port and applies those requests to the LOM.
- The JSON payload format used by the server is: `{ "address": "/live/..", "args": [...], "tool": "tool_name" }`.

Server-side
- Configure the server to enable remote script mode:

```bash
export LLMR_USE_REMOTE_SCRIPT=1
export LLMR_REMOTE_HOST=127.0.0.1
export LLMR_REMOTE_PORT=20000
```

- When enabled, the server will prefer sending JSON messages to the remote script; if disabled, the server continues to use OSC.

Remote script (inside Live)
- Create a remote script package (folder) inside Live's `MIDI Remote Scripts` folder. The package should start a small UDP listener (plain `socket`) on the configured port and parse incoming JSON messages.
- Example responsibilities of the remote script:
  - Call `song().view.select_track(...)`, `song().tracks[i].clip_slots[j].fire()`, `song().tempo`, device parameter set/get, etc.
  - Emit acknowledgements and optionally snapshot state back to the HTTP server at `/llmr/state` (use the server's OSC state endpoint or send JSON back if you implement that channel).

Safety
- Handle messages on the main thread or schedule calls on Live's main thread as required by the remote script API.
- Validate arguments carefully and never execute destructive commands without explicit acknowledgement or approval logic.

See `midi_remote/` for a scaffold and install instructions.
