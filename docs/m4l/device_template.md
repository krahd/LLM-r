Max for Live (M4L) Device Template
=================================

This file describes a minimal Max for Live device that bridges Live's LOM to OSC for use with LLM-r.

Design
- Listen for incoming OSC commands on a configured UDP port (default 11000).
- Supported addresses should match the mapping in `llmr/ableton_osc.py` (e.g., `/live/device/set/parameter`).
- Emit state snapshots as a JSON string to `/llmr/state` whenever important state changes occur (selection changes, transport, device parameter changes, track create/delete, clips changes).

Implementation notes
- Use `udpreceive` and `udpsend` objects in Max to receive/send UDP packets.
- Use `live.path`, `live.object`, and `live.observer` objects to read/set values in the Live Object Model.
- When setting a parameter, send an `/ack` or `/error` OSC response back to the origin with details.

Security
- Only allow connections from trusted hosts — Max patches can filter by sender IP/port.

Testing
- Use `llmr/simulator.py` to validate message formats before running inside Live.
