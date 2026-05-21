# LLM-r

**LLM-r** bridges [Ableton Live](https://www.ableton.com/) and large language models to automate music-production workflows. The **VST3 plug-in is the primary product surface**: describe what you want in plain language inside Ableton Live, review the generated plan, then dry-run or execute it.

The other surfaces are companions for the same workflow:

- **PyQt GUI**: control, setup, debugging, and local-runtime management companion
- **Web UI**: lightweight browser companion for planning, review, and readiness checks
- **FastAPI**: automation and headless surface for scripts, agents, and HTTP clients

```text
Natural language prompt in the VST3
        │
        ▼
  LLM-r planner  ────────────────►  Modelito-backed LLM runtime
                           (OpenAI / Anthropic / Google /
                            Ollama / oMLX / custom)
        │
        ▼
   Action plan  (dry-run or execute)
        │
        ▼
   AbletonOSC / Device Bridge ─────►  Ableton Live
```

---

## Features

- **Self-contained VST3 plug-in** — configure the LLM, write prompts, review plans, dry-run, and execute from inside Ableton Live
- **Clear surface split** — VST3 for primary in-Live use, PyQt for setup/debug/control, web UI for lightweight browser access, and FastAPI for automation/headless workflows
- **Natural-language planner** — the plug-in and `POST /api/plan` convert a free-text prompt into a typed, validated action plan
- **Safe execution** — dry-run mode, destructive-action approval step, and a strict capability registry
- **Macro system** — named sequences of actions (`idea_sketch`, `performance_prep`, …) with full CRUD via the API
- **Live state introspection** — query song settings, tracks, devices, clips, and parameters at runtime
- **Device loading** — load Live browser devices or plug-ins by name through the bundled LLMRDeviceBridge Remote Script
- **MIDI and clip editing** — add/remove MIDI notes, set note velocity through note payloads, rename/duplicate clips, and adjust clip loop/marker settings
- **Audio clip controls** — set clip gain, transpose/detune, warping, warp mode, and RAM mode for existing audio clips
- **Session history** — plans, executions, and sessions are persisted to disk and survive restarts
- **SSE streaming** — `POST /api/stream` for streaming LLM completions
- **Desktop GUI** — optional PyQt6 companion app with embedded mode, onboarding, server attach/start controls, readiness display, and local-runtime management tabs
- **Web UI** — optional browser companion with readiness chips, Active Model display, a compact basic provider/model editor, Plan Board, run log, and details view
- **Multi-provider LLM support** — use cloud or local models from the appropriate surface; local runtimes (Ollama and oMLX) are mediated by [Modelito](docs/MODELITO.md)

---

## Requirements

| Requirement | Version |
| --- | --- |
| Python | 3.11 or newer |
| [AbletonOSC](https://github.com/ideoforms/AbletonOSC) | installed and running in Ableton Live |
| LLMRDeviceBridge *(device loading only)* | installed and enabled in Ableton Live |
| PyQt6 *(optional GUI)* | 6.7 or newer |

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/krahd/LLM-r.git
cd LLM-r

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -e .

# Optional: include the desktop GUI
pip install -e .[gui]
```

---

## Quick Start

### 1. Start AbletonOSC

Install and enable the [AbletonOSC](https://github.com/ideoforms/AbletonOSC) MIDI Remote Script in Ableton Live. By default it listens on `127.0.0.1:11000`.

For instrument/effect/plug-in loading, also install and enable the bundled
`LLMRDeviceBridge` Remote Script. The VST3 can install it into Ableton's User
Library Remote Scripts folder and will prompt you on first use.

### 2. Launch

#### Option A — VST3 plug-in (primary)

Build/install the local VST3 bundle, then open the Ableton test set:

```bash
bash scripts/test_install_vst3_and_open.sh "$HOME/Library/Audio/Plug-Ins/VST3"
```

Open the `LLM-r` plug-in window in Ableton Live. The plug-in GUI is the main
user-facing workflow: provider/model settings, prompt entry, plan review,
dry-run, Auto-approve, destructive-action approval, Plan/Details tabs, and
Advanced Settings for cloud API keys, Device Bridge checks, and Ollama runtime
controls.

The shipped VST3 does **not** currently expose the PyQt/web readiness strip or
an oMLX runtime-management UI. Use the companion surfaces for those tasks.

#### Option B — Desktop GUI (optional)

```bash
python gui/pyqt_app.py
```

The GUI can run in embedded mode, attach to a running server, or start a local
server from the toolbar. Its main Settings dialog keeps the normal workflow
short: choose the provider, choose the model, set execution defaults, and save.
It also includes the most complete first-run/setup surface today: onboarding,
readiness display, and local runtime controls for both Ollama and oMLX
(service management, model download, serve, stop serving, delete). See
[docs/MODELITO.md](docs/MODELITO.md) for provider setup details. Use Open Help
in the toolbar to open the GitHub manual.

#### Option C — Server only (headless / API)

```bash
python backend/main.py
```

Configure via environment variables (see [Configuration](#configuration)) before launching. The web UI is available at `http://127.0.0.1:8787`.

#### Web UI (lightweight browser companion)

When the FastAPI server is running, open `http://127.0.0.1:8787` for a compact
browser companion. It is useful for remote/local browser access, readiness
checks, prompt testing, plan review, manual execution outside Ableton's
plug-in window, and basic provider/model changes for ordinary local setup.

The web UI intentionally stays narrow in scope: it can edit the active
provider/model pair, and displays read-only local runtime status (Ollama and oMLX
installation/running state, local model count, and currently served model count);
PyQt remains the full setup surface for API keys, Ollama/oMLX service management,
model download/serve/delete, and AbletonOSC configuration.

### First run

Use this sequence on a new install:

1. Choose a provider and model.
2. Keep **Dry run** enabled.
3. Check readiness before trusting live execution.

Readiness checks:
In PyQt or web UI, read the readiness status directly.
In headless mode, call `GET /api/readiness`.
In the VST3, confirm your provider/API key settings and run a dry run first; the plug-in does not yet show the same readiness strip as the companion surfaces.

1. Try a safe prompt such as `Set the tempo to 120 BPM` or `Create one MIDI track named Ideas`.
2. Review the plan before executing.
3. Execute only after the plan looks correct and any destructive steps are intentional.

### Try these first

Safe first prompts for novice users:

- `Set tempo to 120 BPM and turn metronome on.`
- `Create one MIDI track named Drums.`
- `Create an audio track named Vox In and arm it.`
- `Create a 4-bar clip on track 0 and rename it Beat Sketch.`
- `Dry-run deleting clip 0 on track 0.`

More advanced prompts for professional users:

- `Set tempo to 126 BPM, set global quantization to 1 bar, and continue playback.`
- `Create a drums sketch: make a MIDI track, create a 4-bar clip, and add a basic kick/snare pattern.`
- `Duplicate clip 0 to clip 1 on track 1 and launch clip 1.`
- `Load Drum Rack on track 2.` *(requires Device Bridge)*
- `Load EQ Eight on track 1 and set a conservative gain staging level.` *(requires Device Bridge for loading)*

For live performance, keep Dry run on until the set is saved and tested. Avoid
Auto-approve with Dry run off during performance.

### Local models

LLM-r does not talk to Ollama or oMLX directly from planner code. **Modelito
mediates provider access** and normalises the planner-facing interface.

Ollama and oMLX are still separate local runtimes:

- Ollama has its own service, model store, and model IDs.
- oMLX has its own service, model store, and model IDs.
- A model pulled with `ollama pull` does **not** automatically become an oMLX model.
- If you want the same family in both runtimes, download it separately in each runtime and use the ID exposed by that runtime.

See [docs/MODELITO.md](docs/MODELITO.md) for the ordinary-user provider guide,
runtime differences, and model-ID notes.

Real Ollama/oMLX runtime validation is manual by default in this repository
unless you add dedicated integration tests for your target machine/runtime.

### 3. Send a prompt

```bash
curl -s -X POST http://127.0.0.1:8787/api/plan \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Set the tempo to 120 BPM and create a MIDI track"}'
```

The response contains a `plan_id`. Execute it (`"dry_run": true` previews without sending actions):

```bash
curl -s -X POST http://127.0.0.1:8787/api/execute \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "<PLAN_ID>", "dry_run": false}'
```

You can also execute explicit note edits without an LLM plan:

```bash
curl -s -X POST http://127.0.0.1:8787/api/execute_batch \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false, "calls": [
    {"tool": "clip_create", "args": {"track_index": 0, "clip_index": 0, "length_beats": 4}},
    {"tool": "midi_notes_add", "args": {"track_index": 0, "clip_index": 0, "notes": [
      {"pitch": 60, "start_time": 0, "duration": 1, "velocity": 100},
      {"pitch": 64, "start_time": 1, "duration": 1, "velocity": 92},
      {"pitch": 67, "start_time": 2, "duration": 1, "velocity": 96}
    ]}}
  ]}'
```

### Optional LLM assistant context

If you are wiring LLM-r into a custom assistant, agent, or chat UI, you can give
the model the optional prompt in [docs/LLM_ASSISTANT_PROMPT.md](docs/LLM_ASSISTANT_PROMPT.md).
It explains the current Ableton Live control surface, the required JSON plan
format, safe execution behavior, and how to translate broad requests like
"compose a piano ballad", "mix the live set", or "add a sax solo" into actions
LLM-r can actually execute.

LLM-r appends this context to the planner prompt by default. You can disable it
in the GUI Settings dialog, via `PATCH /api/settings`, or when launching the
server:

```bash
LLMR_PLANNER_EXTRA_PROMPT_ENABLED=false python backend/main.py
```

---

## Configuration

Settings are read from environment variables, then from `.llmr/settings.json` (written by the GUI or `PATCH /api/settings`), with environment variables taking precedence. The GUI settings dialog covers the most common options without requiring manual env-var setup.

| Variable | Default | Description |
| --- | --- | --- |
| `LLMR_PROVIDER` | `openai` | Modelito LLM provider |
| `LLMR_MODEL` | `gpt-4.1-mini` | Model name for the selected provider |
| `LLMR_PLANNER_EXTRA_PROMPT_ENABLED` | `true` | Whether to append the optional LLM assistant prompt to the planner prompt |
| `LLMR_PLANNER_EXTRA_PROMPT_PATH` | `docs/LLM_ASSISTANT_PROMPT.md` | Optional file appended to the LLM-r planner prompt |
| `LLMR_HOST` | `127.0.0.1` | Interface the API server binds to |
| `LLMR_PORT` | `8787` | Port the API server listens on |
| `LLMR_ABLETON_HOST` | `127.0.0.1` | AbletonOSC host |
| `LLMR_ABLETON_PORT` | `11000` | AbletonOSC port |
| `LLMR_DEVICE_BRIDGE_ENABLED` | `true` | Whether `device_load` calls are allowed |
| `LLMR_DEVICE_BRIDGE_HOST` | `127.0.0.1` | LLMRDeviceBridge host |
| `LLMR_DEVICE_BRIDGE_PORT` | `8788` | LLMRDeviceBridge port |
| `LLMR_OSC_REPLY_ENABLED` | `true` | Start the AbletonOSC reply listener for live-state reconciliation |
| `LLMR_OSC_REPLY_HOST` | `127.0.0.1` | OSC reply listener bind host |
| `LLMR_OSC_REPLY_PORT` | `11001` | OSC reply listener port |
| `LLMR_PLAN_STORE_PATH` | `.llmr/plans.json` | Persistent plan storage |
| `LLMR_MACRO_STORE_PATH` | `.llmr/macros.json` | Persistent macro storage |
| `LLMR_SESSION_STORE_PATH` | `.llmr/sessions.json` | Persistent session storage |
| `LLMR_SETTINGS_PATH` | `.llmr/settings.json` | Runtime settings file |
| `LLMR_API_TOKEN` | *(unset)* | Bearer token to protect write endpoints |

> **Security:** Keep `LLMR_HOST=127.0.0.1` for local use. Setting `LLMR_HOST=0.0.0.0` exposes the API on all network interfaces. See [docs/SECURITY.md](docs/SECURITY.md).

---

## API Reference

### Core

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/api/capabilities` | Runtime capability registry with domain/safety/destructive filtering |
| `GET` | `/api/settings` | Current runtime settings |
| `PATCH` | `/api/settings` | Update runtime settings and persist to disk |
| `GET` | `/api/models` | Available models from Modelito |
| `GET` | `/api/model_metadata` | Metadata for the active model |
| `GET` | `/api/device-bridge/status` | LLMRDeviceBridge reachability |
| `GET` | `/api/device-bridge/devices` | Browse Device Bridge candidates by `query` and `device_type` |
| `POST` | `/api/device-bridge/resolve` | Validate the exact `device_load` candidate, preset, or confirmed browser path without mutating Live |
| `GET` | `/api/device-parameters/maps` | Safe semantic device parameter mappings |
| `GET` | `/api/osc-replies/status` | OSC reply listener status |
| `GET` | `/api/osc-replies/recent` | Recent OSC replies applied to live state |
| `POST` | `/api/live/refresh` | Request AbletonOSC readback; recognized replies update live state |

### Planning & Execution

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/plan` | Create a plan from a natural-language prompt |
| `GET` | `/api/plan/{plan_id}` | Retrieve a stored plan |
| `POST` | `/api/execute` | Execute a plan by ID (supports `dry_run` and `approved`) |
| `POST` | `/api/execute_batch` | Execute an explicit list of tool calls |
| `POST` | `/api/stream` | Streaming LLM completions (SSE) |

### Macro Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/macros` | List all macros |
| `GET` | `/api/macros/{name}` | Fetch a macro by name |
| `POST` | `/api/macros` | Create a runtime macro *(auth required if token set)* |
| `PUT` | `/api/macros/{name}` | Update a runtime macro *(auth required if token set)* |
| `DELETE` | `/api/macros/{name}` | Delete a runtime macro *(auth required if token set)* |
| `POST` | `/api/plan_macro` | Create a plan from a named macro |

### Live State

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/live/song` | Current song settings (tempo, time signature, …) |
| `GET` | `/api/live/tracks` | All tracks |
| `GET` | `/api/live/tracks/{id}/devices` | Devices on a track |
| `GET` | `/api/live/tracks/{id}/clips` | Clips on a track |
| `GET` | `/api/live/tracks/{id}/parameters` | Parameters on a track |

### History

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/sessions` | All sessions |
| `GET` | `/api/sessions/{session_id}` | A specific session |
| `GET` | `/api/history` | Execution history |

When `LLMR_API_TOKEN` is set, include the token on write requests:

```bash
-H "Authorization: Bearer $LLMR_API_TOKEN"
```

---

## Capabilities

LLM-r exposes a declarative capability registry. The runtime source of truth is always `GET /api/capabilities`. It accepts optional query parameters: `domain`, `safety`, and `include_destructive=false`. Each capability includes a `transport` field (`osc` or `device_bridge`). Capabilities are organised into domains:

| Domain | Actions |
| --- | --- |
| `song` | Transport, tempo, time signature, quantization, count-in |
| `tracks` | Create, delete, rename, mixer controls, sends |
| `session` | Scene and clip operations |
| `clips` | Clip duplication, naming, color, launch, loop, and marker properties |
| `midi` | MIDI note get/add/remove/clear |
| `audio` | Existing audio clip gain, pitch, warping, warp mode, and RAM mode |
| `devices` | Device loading, parameter inspection, device deletion |
| `parameters` | Parameter writes |

Capabilities marked `destructive: true` require `"approved": true` in `POST /api/execute` (unless `dry_run` is enabled). Full catalog: [docs/CAPABILITIES.md](docs/CAPABILITIES.md).

Browser search/load for one named device or plug-in is handled by
LLMRDeviceBridge. Plugin-chain loading, warp marker CRUD, destructive
sample-file edits, render/export, and loudness analysis remain outside the
current runtime contract.

---

## Macros

Macros are named sequences of Ableton actions. LLM-r ships with built-in static macros (`idea_sketch`, `performance_prep`) and supports runtime macros persisted to disk.

When to use macros:

- reuse a setup pattern you trust
- get a quick starter plan before refining with normal prompts
- standardize repetitive prep steps across sessions

Built-in macro names in this release:

- `idea_sketch`
- `performance_prep`

Macro discoverability in shipped surfaces:

- Web UI: built-in and runtime macro names can be listed and planned from the Macros panel.
- API/headless: use `/api/macros` and `/api/plan_macro`.

**List macros:**

```bash
curl http://127.0.0.1:8787/api/macros
```

**Run a macro:**

```bash
curl -s -X POST http://127.0.0.1:8787/api/plan_macro \
  -H "Content-Type: application/json" \
  -d '{"name": "idea_sketch"}'
```

**Create a runtime macro via the API:**

```bash
curl -s -X POST http://127.0.0.1:8787/api/macros \
  -H "Content-Type: application/json" \
  -d '{"name": "my_macro", "calls": [{"tool": "set_tempo", "args": {"bpm": 110}}, {"tool": "song_play", "args": {}}]}'
```

Runtime macros are persisted to `LLMR_MACRO_STORE_PATH` and survive restarts. To contribute a built-in macro, add an entry to `_STATIC_MACROS` in `llmr/macros.py` — see [docs/MACROS.md](docs/MACROS.md).

---

## Safety Model

LLM-r is designed to avoid unintended changes to a live session:

- **Dry-run** — pass `"dry_run": true` to `POST /api/execute` to validate a plan without sending any OSC messages
- **Destructive approval** — actions flagged `destructive: true` (track/scene/clip/device deletion, MIDI note removal/clear, stop-all) require `"approved": true`
- **Capability registry** — the planner is grounded in a strict schema; it cannot generate actions outside the declared capability surface
- **TTL pruning** — plans expire after 60 minutes; the store is bounded to 256 entries
- **No double execution** — a plan can only be executed once

---

## VST3 Plug-in

The VST3 plug-in is the primary self-contained control surface. It does not
require the desktop GUI or FastAPI server for normal use. The plug-in stores its
own runtime settings in macOS user defaults and can:

- choose provider/model/endpoint and API key
- provider picker includes `openai`, `anthropic`, `google`, `ollama`, `omlx`, and `custom`
- switch between Plan and Details response tabs
- copy/select text from the response panel
- keep provider/model on the basic settings screen while API keys, AbletonOSC,
  Device Bridge checks, and Ollama controls live under Advanced Settings
- show transport/device status checks and Ollama model/runtime state
- load the downloadable-model pull-down from the Ollama online model library
- save or cancel settings changes explicitly
- send the built-in LLM-r tool catalog and optional guidance to the LLM
- parse the returned JSON plan
- dry-run or execute the resulting AbletonOSC and Device Bridge actions
- auto-approve plans after planning while respecting the dry-run default
- block destructive actions unless explicitly allowed

The shipped VST3 currently does **not** provide:

- the PyQt/web readiness strip backed by `GET /api/readiness`
- an oMLX runtime-management tab
- the PyQt onboarding wizard

For full readiness checks and local runtime management (including oMLX), use the
PyQt GUI companion.

## Desktop GUI

The GUI is an optional companion. It can run LLM-r in embedded mode without a
separate server process, attach to a running server, or start/stop a local server
from the toolbar.

```bash
pip install PyQt6
python gui/pyqt_app.py
```

A **Settings** dialog (accessible from the toolbar) lets you configure everything at runtime:

- Main Settings: LLM provider, model, dry-run default, Auto-approve, and destructive-execution default
- Advanced Settings: provider API keys, assistant prompt guidance, Ableton OSC host/port, server URL, and API token
- Advanced Settings → Ollama: status, start/stop service, installed model picker, served model stop, downloadable-model picker, download, serve, and delete
- Advanced Settings → oMLX: status, start/stop service, local model picker, download, serve, stop serving, and delete; see [docs/MODELITO.md](docs/MODELITO.md)
- Readiness bar: ready-to-plan, ready-to-dry-run, and ready-to-execute state with hints
- Response tabs: Plan for action cards, Action Table for parsed tool calls, Run Log for execution reports, and Details for the complete payload plus parsed `llm_raw` when available
- Open Help opens the GitHub user manual from the toolbar

PyQt also includes a first-run onboarding wizard focused on safe initial setup:

- choose cloud or local provider/runtime (or configure later)
- for local runtimes, run real Install / Start Service / Refresh actions in-wizard
- pick a discovered local model or type an exact model ID manually
- keep safe defaults (Dry run on, Auto-approve off, destructive execution off)

Advanced Settings remains the full local-runtime management surface.

## Web UI

The web UI is a lightweight browser companion rather than the primary product
surface. It is useful when you want a quick plan/review/execute panel outside
Ableton Live without opening the PyQt app.

It currently provides:

- provider/model summary pulled from runtime settings
- readiness chips backed by `GET /api/readiness`
- plain-language prompt workflow: Create a plan -> preview only -> run in Ableton
- quick-start prompt templates grouped for novice, production, sound design, and safety tasks
- macro launcher using `/api/macros` and `/api/plan_macro` when available
- read-only capabilities browser using `/api/capabilities`
- Plan Board, Run Log, and Details tabs with copy-plan-json/copy-summary actions
- stronger live/destructive safety messaging and readiness-driven control disable states

GUI connection settings are persisted to `~/.llmr/gui.json`. Runtime settings are
pushed to the server via `PATCH /api/settings` when connected to HTTP mode, or
saved directly by the embedded backend.

If a server is already running when the GUI opens, it attaches to it instead of starting a new one.

---

## Development

```bash
# Run tests
python -m pytest -q

# Lint
ruff check .

# Run server with auto-reload
uvicorn llmr.app:app --host 127.0.0.1 --port 8787 --reload
```

### Release builds

A CI workflow builds release artifacts on tag pushes: [.github/workflows/release.yml](.github/workflows/release.yml).

To build locally (sdist, wheel, and PyInstaller standalone binary):

```bash
./scripts/build_release.sh
```

PyInstaller binaries are platform-specific and placed in the git-ignored
`release/` directory. See [docs/RELEASE.md](docs/RELEASE.md).
Local install helpers for generated vendor packages and VST3 bundles live under
`scripts/`.

---

## Development Plan

See [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md).

---

## Documentation

| Document | Description |
| --- | --- |
| [docs/CAPABILITIES.md](docs/CAPABILITIES.md) | Full capability catalog |
| [docs/ABLETON_SMOKE_TEST.md](docs/ABLETON_SMOKE_TEST.md) | Real AbletonOSC + Device Bridge smoke-test checklist |
| [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md) | Current AbletonOSC runtime contract notes |
| [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md) | Current pre-release audit and roadmap |
| [docs/USER_MANUAL.md](docs/USER_MANUAL.md) | User-facing guide for the VST3 workflow |
| [docs/GUI-PLUGIN.md](docs/GUI-PLUGIN.md) | Technical GUI behavior and settings |
| [docs/LLM_ASSISTANT_PROMPT.md](docs/LLM_ASSISTANT_PROMPT.md) | Default planner guidance prompt |
| [docs/MACROS.md](docs/MACROS.md) | Macro authoring guide |
| [docs/MODELITO.md](docs/MODELITO.md) | Modelito integration details |
| [docs/RELEASE.md](docs/RELEASE.md) | Release and build instructions |
| [docs/SCENARIOS.md](docs/SCENARIOS.md) | Current executable workflow recipes |
| [docs/SECURITY.md](docs/SECURITY.md) | Security model and deployment advice |

---

## Current Limitations

- Real Ableton Live validation (transport, OSC, device loading) is required for release confidence and is not automated.
- Native VST3 build, install, and load should be verified on macOS before each release.
- The shipped VST3 plug-in does not yet expose the same readiness strip or oMLX management controls that the PyQt and web companion surfaces expose.
- Real oMLX runtime validation is manual; automated tests cover the FastAPI routes with monkeypatched adapters only.
- Some advanced workflows (device loading, ambiguous browser resolution) require both AbletonOSC and the LLMRDeviceBridge Remote Script.
- Local model access via Ollama and oMLX is mediated by Modelito. Models pulled through Ollama are not automatically available to oMLX unless both runtimes expose the same model identifier.

---

## Contributing

Contributions are welcome. Open an issue to discuss a change, then submit a pull request. Follow the existing code style and add tests for new behaviour.

---

## License

See [LICENSE](LICENSE).
