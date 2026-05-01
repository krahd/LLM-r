# LLM-r Plug-in GUI — Primary Surface

The VST3 plug-in is the **primary and recommended interface** for LLM-r.
Load it in Ableton Live like any instrument or effect and control your session
entirely from within the host — no terminal, no server, no extra windows required.

## Features

- **Chat interface** — type requests in natural language and get responses in a
  scrollable chat history, just like a standard LLM chat app.
- **Response tabs** — use Chat for the interpreted plan and Raw JSON for the
  exact provider response/debug payload.
- **Resizable window** — drag the plug-in editor to the size you want.
- **Separate Settings panel** — click ⚙ Settings to open a dedicated screen.
  Basic provider/model choices stay on the first settings screen. API keys,
  endpoint, AbletonOSC, and Ollama service/model controls are in Advanced
  Settings so the normal workflow stays clean.
- **Explicit settings commit** — Save applies changes; Cancel discards edits.
- **Persistent settings** — API keys, ports, model names, and checkboxes are
  saved to macOS `NSUserDefaults` and restored across sessions.
- **Dry-run by default** — every plan is previewed before execution; toggle
  off when you're confident.
- **Destructive-action guard** — track/scene/clip deletes and `stop_all_clips`
  require "Allow destructive actions" to be enabled in Settings.

## Chat workflow

1. Load **LLM-r** as a VST3 instrument in any Ableton Live track.
2. Open ⚙ Settings and configure your LLM provider (API key, model, endpoint).
3. Type a request — e.g. *"Create a 4-bar bass line at 90 BPM on a new MIDI
   track"* — and press **Send**.
4. LLM-r calls the configured LLM and returns a plan in the chat.
5. Review the plan, then click **▶ Execute** (or enable Dry run to preview).

## Settings panel

Open with the ⚙ Settings button. Use Save to apply changes, or Cancel to leave
the current runtime settings unchanged.
Use Advanced for provider keys, endpoint, AbletonOSC, and Ollama management.

### LLM Provider

| Field | Description |
| --- | --- |
| Provider | openai / anthropic / google / ollama / custom |
| Model | Provider-specific pull-down; Ollama uses installed local models |
| Endpoint | Leave blank for provider default |
| API Key | Securely stored; used for cloud providers |
| LLM-r guidance prompt | Adds extra planning context (recommended on) |
| Allow destructive actions | Enables execution of destructive OSC tools |

### AbletonOSC

| Field | Description |
| --- | --- |
| Host | Default `127.0.0.1` |
| Port | Default `11000` |
| Dry run default | Pre-check to preview plans without sending OSC |

### Advanced Ollama (local models)

Ollama management operations are available from Advanced Settings:

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
- **Processed response tabs** — Chat shows the interpreted plan/result, Actions
  shows parsed tool calls, Execution shows run reports, and Raw `.json` shows
  the complete payload including parsed `llm_raw` when available.
- **Simple Settings** — choose provider/model and execution defaults. When the
  provider is `ollama`, the model field is a pull-down backed by local Ollama
  models and safe fallback choices.
- **Advanced Settings** — provider API keys, planner guidance, AbletonOSC,
  server connection, and Ollama service/model management live outside the main
  settings screen.

```bash
pip install PyQt6
python gui/pyqt_app.py
```

Desktop Advanced Settings includes an Ollama screen for status refresh,
install/start/stop, local model selection, serving a model, stopping a served
model, deleting a local model, and downloading from a downloadable-model
pull-down. The toolbar Open Help button opens the user manual on GitHub.

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
