# Modelito Integration Guide

LLM-r uses [Modelito](https://github.com/krahd/modelito) to connect to LLMs.
That means LLM-r does not implement a separate planner client for every cloud or
local runtime. Instead:

```text
LLM-r -> Modelito -> provider/runtime
```

## Which provider should I use?

- Use OpenAI, Anthropic, or Gemini if you want the simplest cloud setup.
- Use Ollama if you already use Ollama and want to keep using its local model store.
- Use oMLX if you want an Apple Silicon local MLX-style runtime and its own local model store.

## Provider and model settings

Set these environment variables:

- `LLMR_PROVIDER` for the provider/runtime name such as `openai`, `anthropic`, `google`, `ollama`, or `omlx`
- `LLMR_MODEL` for the model ID that makes sense for that provider/runtime

Examples:

### OpenAI

```bash
export LLMR_PROVIDER=openai
export LLMR_MODEL=gpt-4.1-mini
python backend/main.py
```

### Ollama

```bash
export LLMR_PROVIDER=ollama
export LLMR_MODEL=llama3.2:latest
python backend/main.py
```

### oMLX

```bash
export LLMR_PROVIDER=omlx
export LLMR_MODEL=<omlx-model-id>
python backend/main.py
```

API keys and credentials are handled by Modelito. See [Modelito documentation](https://github.com/krahd/modelito) for details on configuring providers and models.

## Model stores and model IDs

Cloud and local runtimes do not use one universal model namespace.

- Cloud providers use provider-specific model IDs such as `gpt-4.1-mini`.
- Ollama uses Ollama model tags such as `llama3.2:latest`.
- oMLX uses the IDs exposed by the oMLX runtime and surfaced through LLM-r's `/api/omlx/*` endpoints or the PyQt oMLX tab.

Important consequences:

- Ollama and oMLX keep separate model stores.
- `ollama pull ...` does not make that model available to oMLX.
- A model ID that works in Ollama may not be a valid oMLX model ID.
- For oMLX, prefer runtime-discovered model IDs over copying an Ollama-style tag by guesswork.

If you are unsure which ID to use, fetch the runtime's model list from the companion UI or the API instead of typing one blindly.

## Local Runtime Management API

LLM-r exposes local runtime management endpoints for both Ollama and oMLX through the FastAPI surface.

These endpoints are most useful from the PyQt GUI, the web/API companion surfaces, or your own automation. The shipped VST3 currently exposes Ollama controls, but not a full oMLX management UI.

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
- See [USER_MANUAL.md](USER_MANUAL.md) for the first-run flow and [../README.md](../README.md) for the product-surface overview.

## Troubleshooting
- If you see errors about Modelito not being installed, reinstall LLM-r's project
  dependencies with `pip install -e .`. The current dependency is pinned in
  `pyproject.toml`.
- If you see errors about provider/model, check your environment variables and Modelito documentation.
- If `LLMR_PROVIDER=omlx` is set but no models appear, check `GET /api/omlx/status` and `GET /api/omlx/local_models` first.
