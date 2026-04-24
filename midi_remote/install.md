Installing the LLM-r MIDI Remote Script
=======================================

This document shows how to install the `LLMRRemote` package into Ableton Live's
`MIDI Remote Scripts` folder so Live can load the bridge that accepts JSON
messages sent by the `RemoteScriptClient`.

1) Choose install path

- macOS (example):
  - Live 11 (App Store): /Applications/Ableton Live 11 Suite.app/Contents/App-Resources/MIDI Remote Scripts/
  - Live installed from installer: /Applications/Ableton Live 11 Suite.app/Contents/App-Resources/MIDI Remote Scripts/

- Windows (example):
  - C:\ProgramData\Ableton\Live x.x.x\Resources\MIDI Remote Scripts\

2) Copy the package

Use the provided `install.sh` (macOS/Linux) or copy manually. If you prefer a
PowerShell copy on Windows, follow the examples below.

macOS / Linux (example):

```bash
# customize LIVE_REMOTE_PATH if your Live installation is different
LIVE_REMOTE_PATH="/Applications/Ableton Live 11 Suite.app/Contents/App-Resources/MIDI Remote Scripts"
./install.sh --target "$LIVE_REMOTE_PATH"
```

Windows (PowerShell example):

```powershell
# $env:LIVE_REMOTE_PATH = 'C:\ProgramData\Ableton\Live x.x.x\Resources\MIDI Remote Scripts'
# Copy-Item -Path .\LLMRRemote -Destination $env:LIVE_REMOTE_PATH -Recurse -Force
```

3) Restart Ableton Live

Live scans the `MIDI Remote Scripts` directory at startup. Restart Live and
open the `MIDI` preferences to enable the new remote script for a control
surface if required by your Live version.

4) Configuration

- On the server side, make sure `LLMR_USE_REMOTE_SCRIPT=1` and the host/port
  match the values used in the remote script (defaults: host `127.0.0.1`,
  port `20000`). See `docs/midi_remote.md` for more details.

Notes
- Remote scripts run inside Live's embedded Python; avoid non-standard
  libraries. Use only the Python standard library and the Live API inside the
  remote script.
- The scaffold provided is a starting point — adapt `LLMRRemote/LLMRRemote.py`
  to match your Live version's ControlSurface API and naming conventions.
