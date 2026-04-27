# GUI Plugin / Desktop Client

LLM-r now includes a minimal **PyQt6 desktop scaffold** at `gui/pyqt_app.py`.

## What it does
- Connects to the LLM-r API (default `http://127.0.0.1:8787`)
- Sends prompts to `POST /api/plan`
- Displays plan JSON
- Executes the latest plan via `POST /api/execute`
- Supports dry-run toggle
- Supports bearer auth via `LLMR_GUI_API_TOKEN`

## Run

```bash
pip install PyQt6
python gui/pyqt_app.py
```

Optional environment variables:
- `LLMR_GUI_API_URL` (default `http://127.0.0.1:8787`)
- `LLMR_GUI_API_TOKEN` (if `LLMR_API_TOKEN` is enabled server-side)

## Notes
- This is a starting scaffold, not a production UX.
- Next steps: macro browser, capability explorer, streaming output panel, and better execution review UI.
