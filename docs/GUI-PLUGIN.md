# Desktop GUI

LLM-r includes a PyQt6 desktop client at `gui/pyqt_app.py`.

## What it does
- Runs in embedded mode when no server is reachable.
- Connects to a running LLM-r API server (default `http://127.0.0.1:8787`) when available.
- Starts and stops a local server from the Server controls.
- Sends prompts to `POST /api/plan`
- Displays plan JSON
- Executes the latest plan via `POST /api/execute`
- Supports dry-run toggle
- Supports bearer auth via settings or `LLMR_GUI_API_TOKEN`
- Edits runtime settings for provider, model, assistant prompt guidance, AbletonOSC, server URL, and API token.

## Run

```bash
pip install PyQt6
python gui/pyqt_app.py
```

Optional environment variables:
- `LLMR_GUI_API_URL` (default `http://127.0.0.1:8787`)
- `LLMR_GUI_API_TOKEN` (if `LLMR_API_TOKEN` is enabled server-side)

## Settings

Connection settings are stored in `~/.llmr/gui.json`. Runtime settings are pushed
to the server through `PATCH /api/settings` in HTTP mode or saved directly in
embedded mode.
