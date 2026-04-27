## Macro Usage

LLM-r supports macros—named sequences of actions for Ableton Live. Macros can be used for common workflows (e.g., 'idea_sketch', 'performance_prep').

- List available macros: `GET /api/macros`
- Plan a macro: `POST /api/plan_macro` with `{ "name": "macro_name" }`

**Example:**

```json
{
	"name": "idea_sketch"
}
```

Macros are currently static, but the system is designed for future runtime editing.

To propose a new macro, open an issue or contribute to `llmr/macros.py`.

## Roadmap

- **Editable macros:** Allow users to create and edit macros at runtime.
- **GUI plugin:** Develop a desktop or Ableton-integrated GUI for easier interaction.
- **More LLM providers:** Expand Modelito support for local and cloud models.
- **Security:** Optional authentication for API endpoints.
## Security

**LLM-r is intended to run on your local machine by default.**

- By default, the API binds to `0.0.0.0` (all interfaces). For maximum safety, set `LLMR_HOST=127.0.0.1` to restrict access to your machine only.
- **Never expose LLM-r to the public internet without authentication or a reverse proxy.**
- API keys and credentials are handled by Modelito and are never logged or exposed by LLM-r.
- If you see a warning about running on a public interface, review your deployment settings.

# LLM-r 1.5.1

## GitHub About Box

For maintainers: copy-ready GitHub About metadata is documented in:

- `docs/GITHUB-ABOUT-BOX.md` (full guidance + checklist)
- `.github/ABOUT_BOX.md` (quick copy version)

Recommended short description:

`LLM-r bridges Ableton Live and LLM agents via AbletonOSC + Modelito.`

LLM-r bridges **Ableton Live** and an LLM using AbletonOSC + Modelito.

## Release Binaries

This repository now includes a CI workflow and local helper to produce release artifacts (source distributions, wheels, and standalone binaries built by PyInstaller).

- CI workflow: [.github/workflows/release.yml](.github/workflows/release.yml)
- Local build helper: [scripts/build_release.sh](scripts/build_release.sh)
- Release instructions: [docs/RELEASE.md](docs/RELEASE.md)

PyInstaller binaries are platform-specific and are placed in the `release/` directory when built locally. Use the CI (tag push) to build per-platform artifacts and attach them to a GitHub Release.

## What's improved in 1.3.0

- Added declarative OSC capability registry with stricter argument validation and reduced planner/tool drift.
- Added transport controls (`song_play`, `song_stop`, `song_continue`, `song_record`, `song_metronome`).
- Expanded capability surface with song/time controls, track lifecycle/mixer controls, scene+clip lifecycle, and device parameter actions.
- Added utility actions (`utility_undo`, `utility_redo`) and batch execution endpoint for direct action lists.
- Added per-action execution reporting in `POST /api/execute` responses.
- Added introspection endpoints for live state snapshots: `/api/live/song`, `/api/live/tracks`, `/api/live/tracks/{id}/devices`, `/api/live/tracks/{id}/clips`.
- Added **persistent plan storage** to disk (`LLMR_PLAN_STORE_PATH`, default `.llmr/plans.json`).
- Plans now survive process restarts and still respect TTL pruning behavior.
- Added `GET /api/plan/{plan_id}` for plan audit/retrieval after creation.
- Added `dry_run` option to `POST /api/execute` so users can validate execution payloads without sending OSC.
- Added stricter prompt validation (`min_length`, `max_length`) and prompt trimming.
- Kept lifecycle safety: TTL plan pruning, bounded store, destructive approval, and no double execution.
- Kept macro workflow (`/api/macros`, `/api/plan_macro`) plus dry-run and approval controls.

## API

- `GET /health`
- `GET /api/capabilities`
- `GET /api/macros`
- `GET /api/macros/{name}`
- `POST /api/macros` (auth if enabled)
- `PUT /api/macros/{name}` (auth if enabled)
- `DELETE /api/macros/{name}` (auth if enabled)
- `POST /api/plan`
- `POST /api/plan_macro`
- `POST /api/stream` (SSE streaming completions)
- `GET /api/models`
- `GET /api/model_metadata`
- `GET /api/plan/{plan_id}`
- `POST /api/execute`
- `POST /api/execute_batch`
- `GET /api/live/song`
- `GET /api/live/tracks`
- `GET /api/live/tracks/{track_id}/devices`
- `GET /api/live/tracks/{track_id}/clips`
- `GET /api/live/tracks/{track_id}/parameters`
- `GET /api/v2/capabilities` (domain/safety/destructive filtering)
- `GET /api/sessions`
- `GET /api/sessions/{session_id}`
- `GET /api/history`


## Modelito Configuration

LLM-r uses [Modelito](https://github.com/krahd/modelito) to connect to LLMs. You can use local or cloud models (OpenAI, Anthropic, Google, Ollama, etc.) by setting the following environment variables:

- `LLMR_PROVIDER` (e.g., `openai`, `anthropic`, `google`, `ollama`)
- `LLMR_MODEL` (e.g., `gpt-4.1-mini`, `claude-3-sonnet`, `gemini-pro`, `llama3`)
- `LLMR_PLAN_STORE_PATH` (default `.llmr/plans.json`)
- `LLMR_MACRO_STORE_PATH` (default `.llmr/macros.json`)
- `LLMR_SESSION_STORE_PATH` (default `.llmr/sessions.json`)
- `LLMR_API_TOKEN` (optional bearer token for protected endpoints)
- `LLMR_ABLETON_HOST`, `LLMR_ABLETON_PORT`

# LLM-r

LLM-r bridges Ableton Live and large language models (LLMs) to automate music-production workflows. It uses AbletonOSC for control messages and Modelito as a lightweight LLM adapter. The project exposes a local FastAPI server with a planner, macro system, and safety features (dry-run, approval) plus a small PyQt GUI scaffold.

Key capabilities:

- Plan generation from natural-language prompts (LLM → actionable plan)
- Execute safe OSC actions against Ableton Live (with dry-run and approval)
- Persistent plan, macro, and session storage
- Introspectable capability registry (`GET /api/capabilities`)
- Optional PyQt desktop scaffold for quick interactions

This README highlights how to get started, run the server and GUI, and build release artifacts.

## Requirements

- Python 3.11 or newer
- (Optional GUI) PyQt6

## Quick start

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install (editable) dependencies:

```bash
pip install -e .
# or with GUI dependencies:
pip install -e .[gui]
```

3. Configure environment variables (optional — sensible defaults are provided by `llmr/config.py`):

```bash
export LLMR_PROVIDER=ollama
export LLMR_MODEL=llama3
export LLMR_HOST=127.0.0.1
export LLMR_PORT=8787
export LLMR_ABLETON_HOST=127.0.0.1
export LLMR_ABLETON_PORT=11000
# Optional API token to protect endpoints
export LLMR_API_TOKEN=your-secret-token
```

4. Run the server:

```bash
python backend/main.py
```

Open the web UI: http://127.0.0.1:8787

## Minimal GUI (desktop scaffold)

The repository includes a small PyQt6-based scaffold at `gui/pyqt_app.py` that talks to the local API.

```bash
pip install PyQt6
python gui/pyqt_app.py
```

Environment variables for the GUI:

- `LLMR_GUI_API_URL` (default `http://127.0.0.1:8787`)
- `LLMR_GUI_API_TOKEN` (if server-side API token is enabled)

## API overview

Common endpoints (see source for full behaviour and validation):

- `GET /health` — basic health check
- `POST /api/plan` — create a plan from a prompt
- `POST /api/plan_macro` — create plan from a named macro
- `POST /api/execute` — execute a stored plan (requires approval for destructive actions when enabled)
- `POST /api/execute_batch` — execute a list of tool calls
- `GET /api/capabilities` — runtime capability registry (tools, args schema, destructive flag)
- `GET /api/models` and `GET /api/model_metadata` — Modelito integration
- `GET /api/macros`, `GET /api/macros/{name}`, `POST/PUT/DELETE /api/macros` — macro CRUD (write endpoints require auth if `LLMR_API_TOKEN` is set)

Examples

Create a plan:

```bash
curl -s -X POST -H "Content-Type: application/json" \
	-d '{"prompt":"Set the tempo to 120 BPM and create a MIDI track"}' \
	http://127.0.0.1:8787/api/plan
```

Execute a plan (dry-run):

```bash
curl -s -X POST -H "Content-Type: application/json" \
	-d '{"plan_id":"<PLAN_ID>","dry_run":true}' \
	http://127.0.0.1:8787/api/execute
```

If `LLMR_API_TOKEN` is set on the server, include `-H "Authorization: Bearer $LLMR_API_TOKEN"` on write requests.

## Safety model

LLM-r marks potentially destructive tools (track/scene/clip deletion, stop-all) and enforces an approval step for plans that require destructive actions. Use `dry_run` to preview execution without sending OSC messages.

Inspect capabilities at runtime with `GET /api/capabilities` to see the authoritative source of tool definitions and argument schemas (derived from `llmr/ableton_osc.py`).

## Development

- Run tests:

```bash
pytest -q
```

- Linting: `ruff .` (project uses `ruff` in `pyproject.toml`)

- Run the API with auto-reload (development):

```bash
uvicorn llmr.app:app --host 127.0.0.1 --port 8787 --reload
```

## Release builds

This repository includes a CI workflow that builds release assets on tag pushes: `.github/workflows/release.yml`.

Locally you can create artifacts with the helper script:

```bash
./scripts/build_release.sh
```

The script attempts to build sdist/wheel and to create PyInstaller standalone binaries for the GUI and server; PyInstaller binaries are platform-specific and are placed in `release/`.

See [docs/RELEASE.md](docs/RELEASE.md) for details.

## Docs & references

- Capability catalog: [docs/CAPABILITIES.md](docs/CAPABILITIES.md)
- GUI notes: [docs/GUI-PLUGIN.md](docs/GUI-PLUGIN.md)
- Release instructions: [docs/RELEASE.md](docs/RELEASE.md)
- GitHub About copy: [docs/GITHUB-ABOUT-BOX.md](docs/GITHUB-ABOUT-BOX.md)

## Contribution

Contributions welcome — open an issue or submit a pull request. Follow repository coding style and add tests for new behaviour.

## License

No license file is present in this repository. Add a `LICENSE` file to clarify the terms under which this project is distributed.
