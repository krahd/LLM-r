# Modelito Integration Guide

LLM-r uses [Modelito](https://github.com/krahd/modelito) to connect to LLMs. You can use local or cloud models (OpenAI, Anthropic, Google, Ollama, etc.) by setting the following environment variables:

- `LLMR_PROVIDER` (e.g., `openai`, `anthropic`, `google`, `ollama`)
- `LLMR_MODEL` (e.g., `gpt-4.1-mini`, `claude-3-sonnet`, `gemini-pro`, `llama3`)

## Example

```bash
export LLMR_PROVIDER=ollama
export LLMR_MODEL=llama3
python backend/main.py
```

API keys and credentials are handled by Modelito. See [Modelito documentation](https://github.com/krahd/modelito) for details on configuring providers and models.

## Troubleshooting
- If you see errors about Modelito not being installed, reinstall LLM-r's project
  dependencies with `pip install -e .`. The current dependency is pinned in
  `pyproject.toml`.
- If you see errors about provider/model, check your environment variables and Modelito documentation.
