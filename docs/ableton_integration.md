LLM-r Ableton Integration
=========================

This document outlines the Ableton integration via OSC and the components included in the repository.

Key pieces
- `llmr/ableton_osc.py` — maps `ToolName` to OSC addresses and exposes `capabilities()` for discovery.
- `llmr/osc_server.py` — a small OSC server and `StateManager` which accepts `/llmr/state` JSON snapshots.
- `llmr/simulator.py` — lightweight local simulator for development (listens on port 11000 by default).

Workflow
- The LLM produces a `PlanEnvelope` describing `calls` using `ToolName` and `args`.
- The server converts each planned call to an OSC address (via `AbletonOSCClient.to_action`) and can `dry_run` to show exact OSC messages.
- For execution, the server attempts to build undo snapshots from the latest `StateManager` values (if available), executes OSC messages, and stores undo actions.

Security and safety
- Only run the OSC bridge on a trusted network. Do not expose to the public internet.
- Destructive actions are flagged in `capabilities()` and require approval to execute.

Max-for-Live bridge
- See `docs/m4l/device_template.md` for instructions to create a Max for Live device that forwards Live state to `/llmr/state` and accepts the `/live/*` addresses implemented in `ableton_osc.py`.
