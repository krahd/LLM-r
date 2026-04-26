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

# LLM-r 1.3.0

LLM-r bridges **Ableton Live** and an LLM using AbletonOSC + modelito.

## What's improved in 1.3.0

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
- `POST /api/plan`
- `POST /api/plan_macro`
- `GET /api/plan/{plan_id}`
- `POST /api/execute`


## Modelito Configuration

LLM-r uses [Modelito](https://github.com/krahd/modelito) to connect to LLMs. You can use local or cloud models (OpenAI, Anthropic, Google, Ollama, etc.) by setting the following environment variables:

- `LLMR_PROVIDER` (e.g., `openai`, `anthropic`, `google`, `ollama`)
- `LLMR_MODEL` (e.g., `gpt-4.1-mini`, `claude-3-sonnet`, `gemini-pro`, `llama3`)
- `LLMR_PLAN_STORE_PATH` (default `.llmr/plans.json`)
- `LLMR_ABLETON_HOST`, `LLMR_ABLETON_PORT`

**API keys and credentials are handled by Modelito.**

**Troubleshooting:**
- If you see errors about Modelito not being installed, run `pip install modelito`.
- If you see errors about provider/model, check your environment variables and Modelito documentation.

**Example:**

```bash
export LLMR_PROVIDER=ollama
export LLMR_MODEL=llama3
python backend/main.py
```

See [Modelito documentation](https://github.com/krahd/modelito) for more details.

## Run

```bash
python backend/main.py
```

Open `http://localhost:8787`.

## Screenshots

![Web UI](docs/screenshots/ui-screenshot.svg)
