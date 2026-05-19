# Modelito Integration Guide

LLM-r uses [Modelito](https://github.com/krahd/modelito) to connect to LLMs. Local and cloud providers are mediated through Modelito rather than provider-specific client code inside LLM-r.

Set these environment variables:

- `LLMR_PROVIDER` (e.g., `openai`, `anthropic`, `google`, `ollama`, `omlx`)
- `LLMR_MODEL` (e.g., `gpt-4.1-mini`, `claude-3-sonnet`, `gemini-pro`, `llama3`)

## Examples

### Ollama

```bash
export LLMR_PROVIDER=ollama
export LLMR_MODEL=llama3
python backend/main.py
```

### oMLX

```bash
export LLMR_PROVIDER=omlx
export LLMR_MODEL=llama3:latest
python backend/main.py
```

### OpenAI

```bash
export LLMR_PROVIDER=openai
export LLMR_MODEL=gpt-4.1-mini
python backend/main.py
```

API keys and credentials are handled by Modelito. See [Modelito documentation](https://github.com/krahd/modelito) for details on configuring providers and models.

## Local Runtime Management API

LLM-r exposes local runtime management endpoints for both Ollama and oMLX through the FastAPI surface.

### oMLX endpoints

- `GET /api/omlx/status`
- `GET /api/omlx/local_models`
- `GET /api/omlx/remote_models`
- `GET /api/omlx/running_models`
- `POST /api/omlx/start`
- `POST /api/omlx/stop`
- `POST /api/omlx/install`
- `POST /api/omlx/download` with `{"model": "..."}`
- `POST /api/omlx/delete` with `{"model": "..."}`
- `POST /api/omlx/serve` with `{"model": "..."}`
- `POST /api/omlx/stop_serving` with `{"model": "..."}`

Example requests:

```bash
curl -s http://127.0.0.1:8787/api/omlx/status
curl -s http://127.0.0.1:8787/api/omlx/local_models
curl -s http://127.0.0.1:8787/api/omlx/remote_models
curl -s -X POST http://127.0.0.1:8787/api/omlx/download -H 'Content-Type: application/json' -d '{"model":"some-model"}'
curl -s -X POST http://127.0.0.1:8787/api/omlx/serve -H 'Content-Type: application/json' -d '{"model":"some-model"}'
```

The PyQt Advanced Settings dialog includes local runtime controls for both Ollama and oMLX (status, install/start/stop, local/remote/running lists, download/delete/serve/stop-serving, and set-active-model workflow).

## Runtime and Model ID Notes

- oMLX support in LLM-r is mediated by Modelito and the Modelito oMLX runtime helpers.
- Do not assume that models pulled in Ollama are automatically available to oMLX.
- A model ID is only usable in oMLX if the Modelito/oMLX layer exposes that same ID.
- In the GUI, oMLX model choices should normally come from runtime-discovered local and remote model lists.

## Troubleshooting
- If you see errors about Modelito not being installed, reinstall LLM-r's project
  dependencies with `pip install -e .`. The current dependency is pinned in
  `pyproject.toml`.
- If you see errors about provider/model, check your environment variables and Modelito documentation.
- If `LLMR_PROVIDER=omlx` is set but no models appear, check `GET /api/omlx/status` and `GET /api/omlx/local_models` first.
