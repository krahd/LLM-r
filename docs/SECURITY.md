# Security

## Network exposure

LLM-r is designed for local use. By default the API binds to `0.0.0.0` (all interfaces), which exposes it to any device on your network. Unless you have a specific reason, always set:

```bash
export LLMR_HOST=127.0.0.1
```

Never expose LLM-r directly to the public internet. If remote access is required, place it behind a reverse proxy (nginx, Caddy) with TLS and authentication.

## API authentication

Set `LLMR_API_TOKEN` to a strong random string to protect write endpoints:

```bash
export LLMR_API_TOKEN=$(openssl rand -hex 32)
```

Include the token as a Bearer header on protected requests:

```http
Authorization: Bearer <token>
```

Protected endpoints: `POST/PUT/DELETE /api/macros`, `POST /api/execute`, `POST /api/execute_batch`, `PATCH /api/settings`.

Read-only endpoints (`GET /api/*`, `POST /api/plan`, `POST /api/plan_macro`) are intentionally unauthenticated for local convenience.

## LLM provider credentials

API keys for OpenAI, Anthropic, Google, etc. are handled entirely by [Modelito](https://github.com/krahd/modelito) through standard provider environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.). LLM-r never reads, logs, or stores them.

## Local settings file

Runtime settings (provider, model, assistant prompt guidance, Ableton host/port,
API token) are persisted to `.llmr/settings.json` in the working directory. The
API token is stored in plaintext in this file. Restrict its permissions:

```bash
chmod 600 .llmr/settings.json
```

## Desktop GUI

The GUI stores its connection settings (server URL and API token) in `~/.llmr/gui.json` as plaintext JSON. Apply the same permission restriction if this is a concern:

```bash
chmod 600 ~/.llmr/gui.json
```

## OSC transport

OSC messages are sent over unencrypted UDP. An attacker with network access to the Ableton host/port can send arbitrary OSC commands to Ableton Live. Keep `LLMR_ABLETON_HOST=127.0.0.1` (the default) to restrict OSC to loopback only.

## Destructive actions

Tools that irreversibly modify a session (track/scene/clip deletion, stop-all-clips) are marked `destructive: true`. They require `"approved": true` in the execute payload. Use `"dry_run": true` to inspect a plan before committing.
