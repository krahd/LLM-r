# Roadmap

## Done

- Editable macros — full CRUD via `POST/PUT/DELETE /api/macros`
- Optional API token authentication (`LLMR_API_TOKEN`)
- Settings GUI — provider, model, Ableton host/port editable at runtime
- Server auto-launch from the desktop GUI (single-app experience)
- Persistent plan, macro, and session storage
- Dry-run and destructive-action approval gates
- SSE streaming endpoint (`POST /api/stream`)
- Live state introspection (`GET /api/live/*`)

## Near-term

- More test coverage (API edge cases, macro expansion, error paths)
- Community macro contributions

## Mid-term

- Full-featured desktop GUI (beyond the current scaffold)
- Ableton-integrated plugin (Max for Live or Control Surface)
- Enhanced error reporting and structured logging

## Long-term

- Advanced composition workflows (multi-step, conditional, context-aware)
- Session recall and project state snapshots
- Community macro sharing / registry
