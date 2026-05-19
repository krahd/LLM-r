Max for Live Device Template (LLM-r)
===================================

This folder contains a minimal scaffold and instructions to create a Max-for-Live device that bridges Ableton Live's Live Object Model (LOM) to OSC messages accepted by LLM-r.

Overview
- The device should listen on a UDP port (default 11000) for incoming OSC messages produced by LLM-r (e.g., `/live/device/set/parameter`).
- It should also emit state snapshots as JSON strings to `/llmr/state` so the server can keep an up-to-date model of the Live set.

Quick steps to build the device in Max:
1. Create a new Max for Live Audio or MIDI Effect device in Live.
2. Add a `udpreceive` object and set the port (e.g., `udpreceive 11000`).
3. Add a `udpsend` (or `udpsend` inside Max) to emit state snapshots to the LLM-r server (if needed).
4. Add `js` or `jsui` object to parse incoming messages (addresses + args) and map them to `live.object` / `live.path` calls.
5. When a command alters state, optionally send an `/ack` back to the origin and emit a `/llmr/state` JSON snapshot.

Example helper (for `js` object)
See `example_js.js` for a simple JS snippet that parses a JSON payload and forwards an OSC-style command to `post()` (use inside Max to inspect messages).

Saving as `.amxd`
- After building and testing, save the device as an `.amxd` instrument and place it in your Live set's track to enable the bridge.

Testing without Live
- Use `llmr/simulator.py` as a local OSC sink while developing the device. The simulator accepts `/llmr/state` snapshots and `/live/*` addresses.
