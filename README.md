# LLM-r 1.1.0

LLM-r bridges **Ableton Live** and an LLM using AbletonOSC + modelito.

## What's improved in 1.1.0

- Added `GET /api/plan/{plan_id}` for plan audit/retrieval after creation.
- Added `dry_run` option to `POST /api/execute` so users can validate execution payloads without sending OSC.
- Added stricter prompt validation (`min_length`, `max_length`) and prompt trimming.
- Kept lifecycle safety: TTL plan pruning, bounded store, destructive approval, and no double execution.

## API

- `GET /health`
- `GET /api/capabilities`
- `POST /api/plan` with `{ "prompt": "..." }`
- `GET /api/plan/{plan_id}`
- `POST /api/execute` with `{ "plan_id": "...", "approved": true|false, "dry_run": true|false }`

## Run

```bash
python backend/main.py
```

Open `http://localhost:8787`.
