# LLM-r

**LLM-r** bridges [Ableton Live](https://www.ableton.com/) and large language models to automate music-production workflows. Describe what you want in plain language — LLM-r translates it into OSC actions and sends them to Ableton Live via [AbletonOSC](https://github.com/sigabrt/AbletonOSC). LLM connectivity is provided by [Modelito](https://github.com/krahd/modelito), a lightweight adapter that supports OpenAI, Anthropic, Google, Ollama, and other providers.

```text
Natural language prompt
        │
        ▼
   LLM-r planner  ──── Modelito ────►  LLM (OpenAI / Anthropic / Ollama / …)
        │
        ▼
   Action plan  (dry-run or execute)
        │
        ▼
   AbletonOSC  ────────────────────►  Ableton Live
```

---

## Features

- **Natural-language planner** — `POST /api/plan` converts a free-text prompt into a typed, validated action plan
- **Safe execution** — dry-run mode, destructive-action approval step, and a strict capability registry
- **Macro system** — named sequences of actions (`idea_sketch`, `performance_prep`, …) with full CRUD via the API
- **Live state introspection** — query song settings, tracks, devices, clips, and parameters at runtime
- **Session history** — plans, executions, and sessions are persisted to disk and survive restarts
- **SSE streaming** — `POST /api/stream` for streaming LLM completions
- **Desktop GUI** — PyQt6 app that auto-starts the server, includes a settings dialog, and requires no env-var setup
- **Multi-provider LLM support** — swap between cloud and local models with two environment variables

---

## Requirements

| Requirement | Version |
| --- | --- |
| Python | 3.11 or newer |
| [AbletonOSC](https://github.com/sigabrt/AbletonOSC) | installed and running in Ableton Live |
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

Install and enable the [AbletonOSC](https://github.com/sigabrt/AbletonOSC) MIDI Remote Script in Ableton Live. By default it listens on `127.0.0.1:11000`.

### 2. Launch

#### Option A — Desktop GUI (recommended)

```bash
python gui/pyqt_app.py
```

The GUI starts the server automatically, and a built-in Settings dialog lets you configure the LLM provider, model, and Ableton connection without touching environment variables.

#### Option B — Server only (headless / API)

```bash
python backend/main.py
```

Configure via environment variables (see [Configuration](#configuration)) before launching. The web UI is available at `http://127.0.0.1:8787`.

### 3. Send a prompt

```bash
curl -s -X POST http://127.0.0.1:8787/api/plan \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Set the tempo to 120 BPM and create a MIDI track"}'
```

The response contains a `plan_id`. Execute it (`"dry_run": true` previews without sending OSC):

```bash
curl -s -X POST http://127.0.0.1:8787/api/execute \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "<PLAN_ID>", "dry_run": false}'
```

---

## Configuration

Settings are read from environment variables, then from `.llmr/settings.json` (written by the GUI or `PATCH /api/settings`), with environment variables taking precedence. The GUI settings dialog covers the most common options without requiring manual env-var setup.

| Variable | Default | Description |
| --- | --- | --- |
| `LLMR_PROVIDER` | `openai` | Modelito LLM provider |
| `LLMR_MODEL` | `gpt-4.1-mini` | Model name for the selected provider |
| `LLMR_HOST` | `0.0.0.0` | Interface the API server binds to |
| `LLMR_PORT` | `8787` | Port the API server listens on |
| `LLMR_ABLETON_HOST` | `127.0.0.1` | AbletonOSC host |
| `LLMR_ABLETON_PORT` | `11000` | AbletonOSC port |
| `LLMR_PLAN_STORE_PATH` | `.llmr/plans.json` | Persistent plan storage |
| `LLMR_MACRO_STORE_PATH` | `.llmr/macros.json` | Persistent macro storage |
| `LLMR_SESSION_STORE_PATH` | `.llmr/sessions.json` | Persistent session storage |
| `LLMR_SETTINGS_PATH` | `.llmr/settings.json` | Runtime settings file |
| `LLMR_API_TOKEN` | *(unset)* | Bearer token to protect write endpoints |

> **Security:** `LLMR_HOST=0.0.0.0` exposes the API on all network interfaces. Set `LLMR_HOST=127.0.0.1` when running locally. See [docs/SECURITY.md](docs/SECURITY.md).

---

## API Reference

### Core

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/api/capabilities` | Runtime capability registry (tools, argument schemas, destructive flags) |
| `GET` | `/api/settings` | Current runtime settings |
| `PATCH` | `/api/settings` | Update runtime settings and persist to disk |
| `GET` | `/api/models` | Available models from Modelito |
| `GET` | `/api/model_metadata` | Metadata for the active model |

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
| `GET` | `/api/v2/capabilities` | Capabilities with domain/safety/destructive filtering |

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

LLM-r exposes a declarative OSC capability registry. The runtime source of truth is always `GET /api/capabilities`. Capabilities are organised into domains:

| Domain | Actions |
| --- | --- |
| `song` | Transport, tempo, time signature, quantization, count-in |
| `tracks` | Create, delete, rename, mixer controls, sends |
| `session` | Scene and clip operations |
| `devices` | Device and parameter inspection |
| `parameters` | Parameter writes |

Capabilities marked `destructive: true` require `"approved": true` in `POST /api/execute` (unless `dry_run` is enabled). Full catalog: [docs/CAPABILITIES.md](docs/CAPABILITIES.md).

---

## Macros

Macros are named sequences of Ableton actions. LLM-r ships with built-in static macros (`idea_sketch`, `performance_prep`) and supports runtime macros persisted to disk.

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
- **Destructive approval** — actions flagged `destructive: true` (track/scene/clip deletion, stop-all) require `"approved": true`
- **Capability registry** — the planner is grounded in a strict schema; it cannot generate actions outside the declared capability surface
- **TTL pruning** — plans expire after 60 minutes; the store is bounded to 256 entries
- **No double execution** — a plan can only be executed once

---

## Desktop GUI

The GUI is a single-app experience: it starts the server as a subprocess on launch and shuts it down on close. No separate server process is needed.

```bash
pip install PyQt6
python gui/pyqt_app.py
```

A **Settings** dialog (accessible from the toolbar) lets you configure everything at runtime:

- LLM provider and model
- Ableton OSC host and port
- Server URL and API token

Settings are persisted to `~/.llmr/gui.json` (connection settings) and pushed to the server via `PATCH /api/settings`. Server output is logged to `~/.llmr/server.log`.

If a server is already running when the GUI opens, it attaches to it instead of starting a new one.

---

## Development

```bash
# Run tests
pytest -q

# Lint
ruff .

# Run server with auto-reload
uvicorn llmr.app:app --host 127.0.0.1 --port 8787 --reload
```

### Release builds

A CI workflow builds release artifacts on tag pushes: [.github/workflows/release.yml](.github/workflows/release.yml).

To build locally (sdist, wheel, and PyInstaller standalone binary):

```bash
./scripts/build_release.sh
```

PyInstaller binaries are platform-specific and placed in `release/`. See [docs/RELEASE.md](docs/RELEASE.md).

---

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md).

---

## Documentation

| Document | Description |
| --- | --- |
| [docs/CAPABILITIES.md](docs/CAPABILITIES.md) | Full capability catalog |
| [docs/MACROS.md](docs/MACROS.md) | Macro authoring guide |
| [docs/SECURITY.md](docs/SECURITY.md) | Security model and deployment advice |
| [docs/MODELITO.md](docs/MODELITO.md) | Modelito integration details |
| [docs/RELEASE.md](docs/RELEASE.md) | Release and build instructions |

---

## Contributing

Contributions are welcome. Open an issue to discuss a change, then submit a pull request. Follow the existing code style and add tests for new behaviour.

---

## License

No license file is present in this repository. Contact the maintainer or open an issue to clarify the distribution terms.
