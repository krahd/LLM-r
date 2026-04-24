API Key Authentication
======================

LLM-r supports a simple API-key based authentication for its HTTP API.

Environment variables
- `LLMR_API_KEY` — the secret API key (string). If empty, auth will fail when `require_auth` is enabled.
- `LLMR_REQUIRE_AUTH` — `0` (disabled) or `1` (enabled). Default: `0`.

How to call the API
- Use either `Authorization: Bearer <key>` or `X-API-Key: <key>` header on requests to protected endpoints (all `/api/*` except `/health` and `/`).

Examples
```http
POST /api/plan HTTP/1.1
Host: localhost:8787
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{"prompt":"Arm track 1 and start recording"}
```

Security notes
- Keep `LLMR_API_KEY` secret. When enabling `LLMR_REQUIRE_AUTH=1`, ensure the key is reasonably strong.
- For production use consider adding TLS and stronger auth (OAuth, mTLS), or placing the bridge behind a reverse proxy that handles auth.
