# Modelito Integration Guide

LLM-r uses [Modelito](https://github.com/krahd/modelito) to connect to LLMs. You can use local or cloud models (OpenAI, Anthropic, Google, Ollama, oMLX, etc.) by setting the following environment variables:

- `LLMR_PROVIDER` (e.g., `openai`, `anthropic`, `google`, `ollama`, `omlx`)
- `LLMR_MODEL` (e.g., `gpt-4.1-mini`, `claude-3-sonnet`, `gemini-pro`, `llama3`, `llama3:latest`)

## Examples

### Using Ollama (local)

```bash
export LLMR_PROVIDER=ollama
export LLMR_MODEL=llama3:latest
python backend/main.py
```

### Using oMLX (local)

```bash
export LLMR_PROVIDER=omlx
export LLMR_MODEL=llama3:latest
python backend/main.py
```

### Using OpenAI (cloud)

```bash
export LLMR_PROVIDER=openai
export LLMR_MODEL=gpt-4-turbo
export OPENAI_API_KEY=sk-...
python backend/main.py
```

## Local Runtime Management

### Ollama Management

LLM-r provides REST endpoints to manage Ollama services and models:

- **GET `/api/ollama/status`** — Check if Ollama is installed and running
- **GET `/api/ollama/local_models`** — List locally downloaded Ollama models
- **GET `/api/ollama/remote_models`** — List available Ollama models from the registry
- **GET `/api/ollama/running_models`** — List currently served models
- **POST `/api/ollama/install`** — Install Ollama (requires authentication)
- **POST `/api/ollama/start`** — Start the Ollama service (requires authentication)
- **POST `/api/ollama/stop`** — Stop the Ollama service (requires authentication)
- **POST `/api/ollama/download`** — Download a model (requires authentication, payload: `{"model": "name"}`)
- **POST `/api/ollama/delete`** — Delete a local model (requires authentication, payload: `{"model": "name"}`)
- **POST `/api/ollama/serve`** — Serve/load a model (requires authentication, payload: `{"model": "name"}`)
- **POST `/api/ollama/stop_serving`** — Stop serving a model (requires authentication, payload: `{"model": "name"}`)

### oMLX Management

oMLX support is implemented through Modelito. LLM-r exposes the following oMLX endpoints:

- **GET `/api/omlx/status`** — Check if oMLX is installed and running
- **GET `/api/omlx/local_models`** — List locally available oMLX models
- **GET `/api/omlx/remote_models`** — List available oMLX models from the registry
- **GET `/api/omlx/running_models`** — List currently loaded models
- **POST `/api/omlx/install`** — Install oMLX (requires authentication)
- **POST `/api/omlx/start`** — Start the oMLX service (requires authentication)
- **POST `/api/omlx/stop`** — Stop the oMLX service (requires authentication)
- **POST `/api/omlx/download`** — Download a model (requires authentication, payload: `{"model": "name"}`)
- **POST `/api/omlx/delete`** — Delete a local model (requires authentication, payload: `{"model": "name"}`)
- **POST `/api/omlx/serve`** — Serve/load a model (requires authentication, payload: `{"model": "name"}`)
- **POST `/api/omlx/stop_serving`** — Stop serving a model (requires authentication, payload: `{"model": "name"}`)

## Important Notes on Local Runtimes

- **Model compatibility**: oMLX and Ollama maintain separate model stores. Models pulled into Ollama are not automatically available to oMLX unless Modelito explicitly supports that integration. Manage models separately for each runtime.
- **Model naming**: Both Ollama and oMLX typically use the format `name:tag` (e.g., `llama3:latest`). Ensure your model identifiers match the format expected by your selected runtime.
- **Authentication**: All model mutation operations (install, download, delete, serve, etc.) require API authentication. See `docs/SECURITY.md` for authentication setup.
- **GUI management**: The PyQt GUI provides both simple settings (provider/model selector) and advanced settings with runtime-specific controls for Ollama. oMLX local models load in simple settings when provider is set to `omlx`.

## Troubleshooting

- If you see errors about Modelito not being installed, reinstall LLM-r's project dependencies with `pip install -e .`. The current dependency is pinned in `pyproject.toml`.
- If you see errors about provider/model, check your environment variables and Modelito documentation.
- If oMLX local models are not appearing in the GUI, verify oMLX is running and models are installed using the `/api/omlx/local_models` endpoint.
- For local runtime status, use the status endpoints: `/api/ollama/status` or `/api/omlx/status`.
