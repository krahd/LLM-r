# LLM-r

**LLM-r** bridges [Ableton Live](https://www.ableton.com/) and large language models to automate music-production workflows. 

LLM-r translates LLMs' output into OSC actions and sends them to Ableton Live via [AbletonOSC](https://github.com/sigabrt/AbletonOSC). LLM connectivity is provided by [Modelito](https://github.com/krahd/modelito), a lightweight adapter that supports OpenAI, Anthropic, Google, Ollama, and other providers.

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
- **Optional desktop GUI** — lightweight PyQt6 scaffold that talks to the local API
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

### 2. Configure LLM-r

Set environment variables for your LLM provider. The defaults use OpenAI:

```bash
# LLM provider (openai · anthropic · google · ollama · …)
export LLMR_PROVIDER=openai
export LLMR_MODEL=gpt-4.1-mini

# Or use a local model with Ollama
export LLMR_PROVIDER=ollama
export LLMR_MODEL=llama3

# Restrict the API to localhost only (recommended)
export LLMR_HOST=127.0.0.1
```

See [Configuration](#configuration) for all available variables.

### 3. Run the server

```bash
python backend/main.py
```

The server starts at `http://127.0.0.1:8787` by default. Open that URL in a browser for the web UI.

### 4. Send your first prompt

```bash
curl -s -X POST http://127.0.0.1:8787/api/plan \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Set the tempo to 120 BPM and create a MIDI track"}'
```

The response contains a `plan_id`. Execute it (add `"dry_run": true` to preview without sending OSC):

```bash
curl -s -X POST http://127.0.0.1:8787/api/execute \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "<PLAN_ID>", "dry_run": false}'
```

---

## Configuration

All settings are controlled via environment variables. Sensible defaults are provided for local development.

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
| `LLMR_API_TOKEN` | *(unset)* | Bearer token to protect write endpoints |

> **Security note:** `LLMR_HOST=0.0.0.0` exposes the API on all network interfaces. Set `LLMR_HOST=127.0.0.1` when running locally. Never expose LLM-r to the public internet without a reverse proxy and authentication. See [docs/SECURITY.md](docs/SECURITY.md).

---

## API Reference

### Core

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/api/capabilities` | Runtime capability registry (tools, argument schemas, destructive flags) |
| `GET` | `/api/models` | Available models from Modelito |
| `GET` | `/api/model_metadata` | Metadata for the active model |

### Planning & Execution

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/plan` | Create a plan from a natural-language prompt |
| `GET` | `/api/plan/{plan_id}` | Retrieve a stored plan |
| `POST` | `/api/execute` | Execute a plan by ID (supports `dry_run`) |
| `POST` | `/api/execute_batch` | Execute an explicit list of tool calls |
| `POST` | `/api/stream` | Streaming LLM completions (SSE) |

### Macros

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

If `LLMR_API_TOKEN` is set, include `-H "Authorization: Bearer $LLMR_API_TOKEN"` on all write requests.

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

Capabilities marked `destructive: true` require explicit approval before execution (unless `dry_run` is enabled). Full details: [docs/CAPABILITIES.md](docs/CAPABILITIES.md).

---

## Macros

Macros are named sequences of Ableton actions. LLM-r ships with built-in static macros (e.g. `idea_sketch`, `performance_prep`) and supports runtime macros that are persisted to disk.

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

**Add a static macro** — edit `llmr/macros.py` and add an entry to `_STATIC_MACROS`. See [docs/MACROS.md](docs/MACROS.md) for the full contribution flow.

---

## Safety Model

LLM-r is designed to avoid unintended changes to a live session:

- **Dry-run** — pass `"dry_run": true` to `POST /api/execute` to validate a plan without sending any OSC messages
- **Destructive approval** — actions flagged `destructive: true` (track/scene/clip deletion, stop-all) require explicit confirmation before execution
- **Capability registry** — the planner is grounded in a strict schema; it cannot generate actions outside the declared capability surface
- **TTL pruning** — plans expire automatically; a bounded store prevents unbounded growth
- **No double execution** — a plan can only be executed once

---

## Desktop GUI (Optional)

A lightweight PyQt6 scaffold is included at `gui/pyqt_app.py`.

```bash
pip install PyQt6
python gui/pyqt_app.py
```

| Variable | Default | Description |
| --- | --- | --- |
| `LLMR_GUI_API_URL` | `http://127.0.0.1:8787` | LLM-r server URL |
| `LLMR_GUI_API_TOKEN` | *(unset)* | Bearer token (if server auth is enabled) |

A full Ableton-integrated plugin is on the [roadmap](#roadmap).

---

## Development

```bash
# Run tests
pytest -q

# Lint
ruff .

# Run with auto-reload
uvicorn llmr.app:app --host 127.0.0.1 --port 8787 --reload
```

### Release builds

A CI workflow builds release artifacts on tag pushes: [.github/workflows/release.yml](.github/workflows/release.yml).

To build locally (sdist, wheel, and PyInstaller standalone binary):

```bash
./scripts/build_release.sh
```

PyInstaller binaries are platform-specific and are placed in `release/`. See [docs/RELEASE.md](docs/RELEASE.md) for full instructions.

---

## Roadmap

- **Editable macros** — create and edit macros at runtime via the API
- **GUI plugin** — full Ableton device or standalone desktop application
- **More LLM providers** — expand Modelito coverage for additional local and cloud models
- **API authentication** — optional token-based auth for all endpoints
- **Advanced workflows** — composition assistance, session recall, community macro sharing

See [docs/ROADMAP.md](docs/ROADMAP.md) for details.

---

## Documentation

| Document | Description |
| --- | --- |
| [docs/CAPABILITIES.md](docs/CAPABILITIES.md) | Full capability catalog |
| [docs/MACROS.md](docs/MACROS.md) | Macro authoring guide |
| [docs/SECURITY.md](docs/SECURITY.md) | Security model and deployment advice |
| [docs/GUI-PLUGIN.md](docs/GUI-PLUGIN.md) | GUI plugin notes |
| [docs/MODELITO.md](docs/MODELITO.md) | Modelito integration details |
| [docs/RELEASE.md](docs/RELEASE.md) | Release and build instructions |

---

## Contributing

Contributions are welcome. Open an issue to discuss a change, then submit a pull request. Please follow the existing code style and add tests for new behaviour.

---

## License

No license file is present in this repository. Contact the maintainer or open an issue to clarify the distribution terms.
