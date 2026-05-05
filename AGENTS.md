# AGENTS.md

Guidance for automated coding agents working in this repository.

## Project Shape

LLM-r bridges Ableton Live and LLM planners. The main product surface is the
native VST3 plug-in. The FastAPI server, web UI, and PyQt GUI are companion
surfaces for the same planning/execution workflow.

The runtime has two action transports:

- `osc`: default AbletonOSC UDP transport, normally `127.0.0.1:11000`.
- `device_bridge`: local LLMRDeviceBridge Remote Script HTTP transport,
  normally `127.0.0.1:8788`, used by `device_load`.

Do not assume all actions are OSC actions. Preserve and propagate the
`transport` field wherever actions, capabilities, plans, reports, or docs are
touched.

## Important Paths

- `llmr/ableton_osc.py`: declarative tool registry, argument normalization, and
  `AbletonAction` construction.
- `llmr/schemas.py`: shared tool/capability/plan dataclasses.
- `llmr/planner.py`: planner prompt generation and plan persistence.
- `llmr/executor.py`: Python-side action execution and transport routing.
- `llmr/app.py`: FastAPI API, settings, live-state endpoints, and web UI.
- `llmr/device_bridge.py`: Python HTTP client for the Live Device Bridge.
- `remote_scripts/LLMRDeviceBridge/`: Ableton Live Remote Script that performs
  browser/device loading inside Live.
- `native/vst3/llmr_vst3_plugin.cpp`: self-contained VST3 implementation.
- `docs/` and `README.md`: user-facing documentation. Keep them synchronized
  with runtime behavior.
- `REPORT.md`: latest audit summary and known next steps.

## Development Rules

- Prefer existing project patterns over introducing new architecture.
- Keep changes focused; avoid unrelated formatting churn.
- Use structured parsing/serialization for JSON and plans.
- Treat Live-set mutation carefully. Destructive actions must keep approval
  checks intact.
- Do not make an external Python process import Ableton's `Live` API. Real
  device loading belongs in `remote_scripts/LLMRDeviceBridge`, because that code
  runs inside Ableton Live's control-surface Python runtime.
- Preserve loopback defaults for AbletonOSC and Device Bridge unless a task
  explicitly asks for remote access.
- Keep generated build outputs out of git. `build/`, `dist/`, and
  `llm_r.egg-info/` are ignored.

## Versioning

When bumping a release version, check all of these places:

- `pyproject.toml`
- `llmr/__init__.py`
- `native/vst3/llmr_vst3_plugin.cpp`
- `scripts/build_vst3.sh`
- release docs or tags in `docs/RELEASE.md`
- `docs/DEVELOPMENT_PLAN.md` if it states the current package version

## Validation

Use the narrowest checks that cover the change, then broaden for shared
behavior. For a general audit or release-facing change, run:

```bash
python3 -m pytest -q
PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile backend/device_server.py llmr/device_bridge.py remote_scripts/LLMRDeviceBridge/__init__.py remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py
./scripts/build_vst3.sh
python3 -m build
git diff --check
```

Notes:

- `python3 -m build --no-isolation` can fail on local global packaging plugins;
  prefer normal isolated `python3 -m build`.
- Native VST3 validation builds `build/vst3/LLM-r.vst3`.
- Real Ableton Live execution is not covered by unit tests. Call this out when
  relevant, especially for AbletonOSC, Device Bridge, or browser-loading work.

## Documentation Expectations

When capabilities change, update all affected docs:

- `README.md`
- `docs/CAPABILITIES.md`
- `docs/COMPATIBILITY.md`
- `docs/USER_MANUAL.md`
- `docs/SECURITY.md` for network or mutation behavior
- `docs/SCENARIOS.md` for what the planner should or should not attempt
- both prompt copies: `docs/LLM_ASSISTANT_PROMPT.md` and
  `llmr/LLM_ASSISTANT_PROMPT.md`

If a runtime field is exposed by `GET /api/capabilities`, make sure tests cover
the Python registry and API serialization.

## Git Hygiene

- Inspect `git status --short` before editing and before committing.
- Do not revert user changes unless explicitly asked.
- Stage explicit paths when the worktree is mixed.
- Commit and push only when the user asks for it.
