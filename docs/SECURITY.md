# Security Model

- LLM-r is intended to run locally by default. For maximum safety, bind to `127.0.0.1`.
- Never expose the API to the public internet without authentication or a reverse proxy.
- API keys and credentials are handled by Modelito and are never logged or exposed by LLM-r.
- If you see a warning about running on a public interface, review your deployment settings.
- For advanced deployments, consider adding authentication or running behind a secure proxy.
