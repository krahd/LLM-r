# AGENTS.md

Canonical guidance for automated coding agents working in this repository.
This file is the source of truth for Codex, Claude, GitHub Copilot, and other
agents. Compatibility files may point back here, but these instructions must stay
complete on their own.

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
- `STATUS.md`: latest project status, audit summary, validation notes, and known
  next steps. Keep this file up to date whenever behavior, risk, validation, or
  next steps change.

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
- Keep `STATUS.md` current as part of implementation work. If you close a risk,
  add a feature, change validation coverage, or discover a new limitation, update
  `STATUS.md` in the same change set. Keep `STATUS.md` up to date and accurately
  timestamped at all times. Always update the `Last updated` field at the top of
  `STATUS.md` with the current date **and time** (format: `YYYY-MM-DD HH:MM`)
  whenever the file is modified.

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
PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile gui/pyqt_app.py backend/device_server.py llmr/device_bridge.py llmr/osc_replies.py llmr/device_parameters.py remote_scripts/LLMRDeviceBridge/__init__.py remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py scripts/smoke_test_live_integration.py
./scripts/build_vst3.sh
python3 -m build
git diff --check
```

Notes:

- `python3 -m build --no-isolation` can fail on local global packaging plugins;
  prefer normal isolated `python3 -m build`.
- Native VST3 validation builds `build/vst3/LLM-r.vst3`.
- Real Ableton smoke testing is documented in `docs/ABLETON_SMOKE_TEST.md` and
  assisted by `scripts/smoke_test_live_integration.py`.
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
- `STATUS.md` for current state, validation, residual risks, and next steps

If a runtime field is exposed by `GET /api/capabilities`, make sure tests cover
the Python registry and API serialization.

## Git Hygiene

- Inspect `git status --short` before editing and before committing.
- Do not revert user changes unless explicitly asked.
- Stage explicit paths when the worktree is mixed.
- Commit and push only when the user asks for it.
