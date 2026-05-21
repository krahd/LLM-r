# LLM-r Plug-in GUI — Primary Surface

The VST3 plug-in is the **primary and recommended interface** for LLM-r.
Load it in Ableton Live like any instrument or effect and control your session
entirely from within the host for the core plan/review/execute workflow, without
opening a separate terminal or companion window.

## Features

- **Command surface** — type requests in natural language and review the result
  as a Plan Board instead of raw model output.
- **Result / Details tabs** — use Result for the interpreted action board and
  Details for the exact provider response/debug payload.
- **Fixed main window** — the plug-in editor uses a stable fixed size for host compatibility.
- **Modal Settings window** — click Settings to open a single-screen modal
  window with provider/model, optional Custom model, Server/API base URL, API
  key, Preview mode, destructive approval, AbletonOSC, Device Bridge setup,
  Ollama controls, oMLX note, Test readiness, Save, and Cancel.
- **Normal selector behaviour** — provider, model, installed-model, and
  downloadable-model controls are non-editable selectors that open when clicked
  anywhere on the visible field.
- **First-use guidance** — Help opens an in-plug-in text guide for a safe
  first Preview path. Screenshots are not bundled yet.
- **System Prompts window** — edit, save, load, and reset planner prompt presets without editing code.
- **Explicit settings commit** — Save applies changes; Cancel discards edits.
- **Persistent settings** — API keys, ports, model names, and checkboxes are
  saved to macOS `NSUserDefaults` and restored across sessions.
- **One-click Run** — Run plans first, then automatically executes the validated
  action list in Preview or live mode depending on Settings.
- **Preview by default** — every plan is previewed before live execution; toggle
  off when you're confident.
- **Destructive-action guard** — track/scene/clip deletes and `stop_all_clips`
  require "Allow destructive actions" to be enabled in Settings.

## Command workflow

1. Load **LLM-r** as a VST3 instrument in any Ableton Live track.
2. Open Settings, choose Provider and Model, keep Preview only on, and click Test readiness.
3. For cloud providers, add the API key in Settings.
4. For `device_load`, use Settings -> Device Bridge -> Recheck.
5. Type a request — e.g. *"Create a 4-bar bass line at 90 BPM on a new MIDI
   track"* — and press **Run**.
6. LLM-r calls the configured LLM, returns a Plan Board, then runs Preview or live execution based on Settings.
7. Review Result and Details; turn Preview only off only when you want live execution.

## Settings panel

Open with the ⚙ Settings button. Use Save to apply changes, or Cancel to leave
the current runtime settings unchanged.
The VST3 Settings window is one modal screen; it does not use a Basic/Advanced
split or a scrolling settings view.

### LLM Provider

| Field | Description |
| --- | --- |
| Provider | openai / anthropic / google / ollama / custom |
| Model | Non-editable provider-specific selector; Ollama uses installed local models |
| Custom model | Explicit text field for unlisted model IDs or custom provider use |
| Server | Leave blank/provider default, or set an API base URL |
| API Key | Securely stored; used for cloud providers |
| LLM-r guidance prompt | Adds extra planning context (recommended on) |

### AbletonOSC

| Field | Description |
| --- | --- |
| Host | Default `127.0.0.1` |
| Port | Default `11000` |
| Preview only | Run without mutating Live |
| Allow destructive actions | Permit destructive live actions when Preview only is off |

### Device Bridge

Settings includes a **Recheck** control that verifies the local
LLMRDeviceBridge Remote Script on `127.0.0.1:8788` before executing plans that
include `device_load`. Live execution also asks the bridge to resolve
each selected device, preset, or browser path before any OSC mutation is sent.

Bridge install is now user-library-selected, not hard-coded. In Device Bridge:

- click **Choose Ableton User Library...** and select the folder shown by Live
  Browser -> right-click User Library -> Show in Finder
- click **Install / Reinstall Bridge**
- restart Live
- set Control Surface to `LLMR_Bridge` in Settings -> Link, Tempo & MIDI
- click **Recheck**

The VST3 shows:

- selected Ableton User Library path
- bridge install target (`<User Library>/Remote Scripts/LLMR_Bridge`)
- bridge status on disk vs runtime reachability

Recovery actions include **Reveal Installed Bridge**, **Copy Install Path**,
**Install / Reinstall Bridge**, **Open Bridge Setup Help**, and **Recheck**.
External SSD User Libraries are supported when the drive is mounted before Live starts.
If `LLMR_Bridge` does not appear in Live, check Live `Log.txt` for `LLMR`,
`Bridge`, `RemoteScriptError`, `Traceback`, or `ImportError`.

### Ollama (local models)

Ollama management operations are available from Settings. Opening Settings
refreshes local Ollama status automatically:

| Action | Description |
| --- | --- |
| Start Ollama | Launches `ollama serve` in the background |
| Stop Ollama | Kills the running Ollama process |
| Install Ollama | Opens the Ollama download page in your browser |
| Refresh Status | Reads the local Ollama API and shows service/model status |
| Installed models combo | Shows locally installed models from `/api/tags` |
| Serve | Loads the selected installed model and sets it as the active planner model |
| Stop Serving | Unloads the selected model without stopping the Ollama service |
| Test | Sends a tiny prompt to the selected local model |
| Refresh Online | Loads the downloadable-model pull-down from the Ollama online library |
| Download model | Pulls the selected downloadable model through the local Ollama API |

## Other approaches

The plug-in GUI covers the full workflow for most users.
For advanced or headless setups, LLM-r also provides:

### Desktop GUI (`gui/pyqt_app.py`)

A PyQt6 standalone window with the same plan/review/execute workflow.

- **Embedded mode** — runs the LLM planner in-process without a server.
- **HTTP mode** — attaches to a running `llmr serve` server for multi-client
  or remote setups.
- Start/stop the server from within the GUI.
- **Plan Board tabs** — Plan shows action cards, Action Table shows parsed tool
  calls, Run Log shows execution reports, and Details shows the complete payload
  including parsed `llm_raw` when available.
- **Simple Settings** — choose provider/model and execution defaults. When the
  provider is `ollama`, the model field is a pull-down backed by local Ollama
  models and safe fallback choices.
- **Advanced Settings** — provider API keys, planner guidance, AbletonOSC,
  Device Bridge, server connection, and Ollama service/model management live
  outside the main settings screen.

```bash
pip install PyQt6
python gui/pyqt_app.py
```

Desktop Advanced Settings includes both an Ollama screen and an oMLX screen
for status refresh, install/start/stop, local model selection, serving and
stopping served models, deleting local models, and downloading from a
downloadable-model pull-down. The toolbar Open Help button opens the user
manual on GitHub.

### HTTP API (headless / scripting)

```bash
# Start the server
llmr serve

# Plan
curl -X POST http://127.0.0.1:8787/api/plan \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Set tempo to 120"}'

# Execute
curl -X POST http://127.0.0.1:8787/api/execute \
     -H "Content-Type: application/json" \
     -d '{"plan_id": "<ID>", "dry_run": false}'
```

### Web UI

A minimal browser interface served at `http://127.0.0.1:8787/` when the server
is running. Useful for quick testing without installing PyQt6.

## Building the plug-in

```bash
bash scripts/build_vst3.sh          # builds to build/vst3/LLM-r.vst3
bash scripts/install_vst3.sh        # copies to ~/Library/Audio/Plug-Ins/VST3/
```

Requires macOS and Xcode Command Line Tools (`clang++`).
