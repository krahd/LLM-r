# LLM-r Plug-in GUI — Primary Surface

The VST3 plug-in is the **primary and recommended interface** for LLM-r.
Load it in Ableton Live like any instrument or effect and control your session
entirely from within the host — no terminal, no server, no extra windows required.

## Features

- **Chat interface** — type requests in natural language and get responses in a
  scrollable chat history, just like a standard LLM chat app.
- **Resizable window** — drag the plug-in editor to the size you want.
- **Separate Settings panel** — click ⚙ Settings to open a dedicated screen.
  All LLM provider, AbletonOSC, and Ollama settings live there so the main
  view stays clean.
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

Open with the ⚙ Settings button; close with ✓ Done (saves automatically).

### LLM Provider

| Field | Description |
| --- | --- |
| Provider | openai / anthropic / ollama / custom |
| Model | e.g. `gpt-4.1-mini`, `claude-3-sonnet`, `llama3` |
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

### Ollama (local models)

All Ollama management operations are available directly in the Settings panel:

| Action | Description |
| --- | --- |
| Start Ollama | Launches `ollama serve` in the background |
| Stop Ollama | Kills the running Ollama process |
| Install Ollama | Opens [ollama.ai](https://ollama.ai) in your browser |
| ↺ Refresh List | Runs `ollama list` and populates the installed-models picker |
| Installed models combo | Shows all locally installed models; select to use |
| Download model | Enter a model name (e.g. `llama3`, `mistral`) and click ⬇ Download |

## Other approaches

The plug-in GUI covers the full workflow for most users.
For advanced or headless setups, LLM-r also provides:

### Desktop GUI (`gui/pyqt_app.py`)

A PyQt6 standalone window with the same chat/plan/execute workflow.

- **Embedded mode** — runs the LLM planner in-process without a server.
- **HTTP mode** — attaches to a running `llmr serve` server for multi-client
  or remote setups.
- Start/stop the server from within the GUI.

```bash
pip install PyQt6
python gui/pyqt_app.py
```

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
