LLM-r MIDI Remote Script scaffold
================================

This folder contains a scaffold and instructions for creating a MIDI Remote Script that receives JSON messages from LLM-r and calls into the Live Object Model.

Files:
- `install.md` — installation instructions for different OSes and Live versions.
- `bridge_example.py` — annotated example code suitable to adapt inside a ControlSurface implementation.

Important: Remote scripts run in Ableton's embedded Python environment — third-party packages may not be available. Use the standard library (`socket`, `json`) and Live's API.
