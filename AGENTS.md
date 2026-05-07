# AGENTS.md

Repository instructions for AI coding agents working in this project.

This file is the durable source of truth for GitHub Copilot, OpenAI Codex, Claude Code, and compatible coding agents. Read it before making changes. Compatibility files may point back here, but this file must stay complete on its own.

## 1: Non-negotiable rules

- Keep `STATUS.md` accurate at all times.
- `STATUS.md` must exist in the repository root.
- Do not finish a task that changes the project without reviewing and, when needed, updating `STATUS.md`.
- Do not invent project facts. Inspect the repository and record uncertainty explicitly.
- Do not overwrite user work or unrelated changes.
- Do not commit secrets, credentials, tokens, private keys, local environment files, generated build outputs, package artefacts, Live-set data, or generated sensitive data.
- Prefer small, focused changes over broad rewrites.
- Preserve existing public behaviour unless the task explicitly requires a change.
- Preserve the `transport` field wherever actions, capabilities, plans, reports, prompts, docs, or UI surfaces are touched.
- Verify meaningful changes with the narrowest reliable command available.
- Do not claim tests passed unless they were actually run.

## 2: Communication style

Use terse, factual, technical communication. Do not use playful, whimsical, cute, decorative, or filler progress phrases such as "combobulating", "cooking", "thinking...", "working on it", "let me dive in", "I'll get started", or "working my magic".

Allowed status-update style: "Reading files." "Found the issue." "Applying patch." "Tests passed." "Tests failed: <reason>."

No jokes, metaphors, fake enthusiasm, anthropomorphising, or decorative progress messages. Prefer concise present-tense technical updates. Use British English for prose documentation unless the repository consistently uses another variant.

## 3: Standard work loop

1. Read this file and `STATUS.md` before editing.
2. Inspect relevant files, docs, tests, package metadata, native build scripts, and CI workflows.
3. Identify the smallest safe change.
4. Search call sites before changing action schemas, transports, planner prompts, API routes, VST3 behaviour, Remote Script behaviour, version metadata, or release packaging.
5. Make focused edits.
6. Run relevant verification when possible.
7. Update documentation when behaviour, setup, architecture, commands, public APIs, or release state change.
8. Update `STATUS.md` if project state changed.
9. Report changed files, verification, and remaining issues.

## 4: Project-specific map

### 4.1: Project shape

- Purpose: bridge Ableton Live and LLM planners through a native VST3 plug-in plus companion server/UI surfaces.
- Main product surface: native VST3 plug-in.
- Companion surfaces: FastAPI server, web UI, PyQt GUI, smoke-test harness, and documentation site.
- Runtime transports:
  - `osc`: default AbletonOSC UDP transport, normally `127.0.0.1:11000`.
  - `device_bridge`: local LLMRDeviceBridge Remote Script HTTP transport, normally `127.0.0.1:8788`, used by `device_load`.

Do not assume all actions are OSC actions. Preserve and propagate the `transport` field wherever actions, capabilities, plans, reports, prompts, UI, tests, or docs are touched.

### 4.2: Important paths

- `README.md`: human-facing overview.
- `STATUS.md`: complete current project status report; mandatory upkeep.
- `llmr/ableton_osc.py`: declarative tool registry, argument normalisation, and `AbletonAction` construction.
- `llmr/schemas.py`: shared tool, capability, and plan dataclasses.
- `llmr/planner.py`: planner prompt generation and plan persistence.
- `llmr/executor.py`: Python-side action execution and transport routing.
- `llmr/app.py`: FastAPI API, settings, live-state endpoints, and web UI.
- `llmr/device_bridge.py`: Python HTTP client for the Live Device Bridge.
- `llmr/osc_replies.py`: OSC reply listener and reconciliation support.
- `llmr/device_parameters.py`: safe semantic device parameter maps.
- `remote_scripts/LLMRDeviceBridge/`: Ableton Live Remote Script that performs browser/device loading inside Live.
- `native/vst3/llmr_vst3_plugin.cpp`: self-contained VST3 implementation.
- `gui/pyqt_app.py`: PyQt companion UI.
- `backend/device_server.py`: companion backend/device server surface.
- `scripts/smoke_test_live_integration.py`: real Ableton smoke-test harness.
- `scripts/build_vst3.sh`: native VST3 build helper.
- `docs/`: user, security, compatibility, capability, smoke-test, release, and scenario documentation.
- `CLAUDE.md` and `.github/copilot-instructions.md`: compatibility entry points that should point back to this file without conflicting policy.

### 4.3: Safety invariants

- Treat Live-set mutation carefully. Destructive actions must keep approval checks intact.
- Keep dry-run, preflight, and destructive-action checks intact.
- Do not route `device_load` as an ordinary OSC action.
- Do not make an external Python process import Ableton's `Live` API. Real browser/device loading belongs in `remote_scripts/LLMRDeviceBridge`, because that code runs inside Ableton Live's control-surface Python runtime.
- Preserve loopback defaults for AbletonOSC and Device Bridge unless explicitly asked to support remote access.
- Preserve pre-execution Device Bridge preflight so mixed OSC/device plans do not partially mutate a Live set before discovering that device loading is unavailable or ambiguous.
- Preserve explicit handling of ambiguous Device Bridge candidates.
- Grow semantic device parameter maps only from verified AbletonOSC/Live readback data.
- Call out real Ableton verification gaps whenever work affects AbletonOSC, Device Bridge, browser loading, VST3 action execution, or Live-state reconciliation.

## 5: STATUS.md maintenance

`STATUS.md` is mandatory project state, not optional documentation.

Required timestamp line near the top:

```text
Last updated: YYYY-MM-DD HH:MM
```

Use 24-hour local time. If no other timezone is specified, use `America/Montevideo`. Duplicate the exact same line as the final line at the bottom of `STATUS.md`. Update both lines together.

`STATUS.md` must be a complete current snapshot, not a changelog. Include relevant sections for purpose, current implementation state, active focus, architecture, setup/run instructions, configuration, important files, recent changes, tests, risks, pending tasks, next steps, longer-term steps, and decisions.

## 6: Diagrams in STATUS.md

Include useful inline SVG architecture and flow diagrams when the structure is meaningful enough. Keep text inside boxes and canvas bounds. Keep arrows out of unrelated boxes and labels. Prefer generous spacing and simple SVG primitives. Update diagrams when architecture, module relationships, transport flow, execution flow, packaging shape, or deployment shape meaningfully changes.

## 7: Versioning, validation, and documentation

When bumping a release version, check all of these places:

- `pyproject.toml`
- `llmr/__init__.py`
- `native/vst3/llmr_vst3_plugin.cpp`
- `scripts/build_vst3.sh`
- release docs or tags in `docs/RELEASE.md`
- `docs/DEVELOPMENT_PLAN.md` if it states the current package version
- `STATUS.md`

Typical validation commands:

```bash
python3 -m pytest -q
PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile gui/pyqt_app.py backend/device_server.py llmr/device_bridge.py llmr/osc_replies.py llmr/device_parameters.py remote_scripts/LLMRDeviceBridge/__init__.py remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py scripts/smoke_test_live_integration.py
./scripts/build_vst3.sh
python3 -m build
git diff --check
```

Notes:

- `python3 -m build --no-isolation` can fail on local global packaging plugins; prefer normal isolated `python3 -m build`.
- Native VST3 validation builds `build/vst3/LLM-r.vst3`.
- Real Ableton smoke testing is documented in `docs/ABLETON_SMOKE_TEST.md` and assisted by `scripts/smoke_test_live_integration.py`.
- Real Ableton Live execution is not covered by unit tests. Record this clearly when relevant.

When capabilities change, update affected docs:

- `README.md`
- `docs/CAPABILITIES.md`
- `docs/COMPATIBILITY.md`
- `docs/USER_MANUAL.md`
- `docs/SECURITY.md` for network or mutation behaviour
- `docs/SCENARIOS.md` for planner expectations
- both prompt copies: `docs/LLM_ASSISTANT_PROMPT.md` and `llmr/LLM_ASSISTANT_PROMPT.md`
- `STATUS.md`

If a runtime field is exposed by `GET /api/capabilities`, make sure tests cover the Python registry and API serialisation.

## 8: Git and file safety

- Inspect `git status --short` before editing and before committing when local git is available.
- Do not revert user changes unless explicitly requested.
- Stage explicit paths when the worktree is mixed.
- Commit, push, create branches, create tags, create releases, or open pull requests only when explicitly requested.
- Keep generated build outputs out of git. `build/`, `dist/`, and `llm_r.egg-info/` are ignored.

## 9: Final response requirements

When finishing a task, report concisely: what changed, files changed, verification commands and results, whether `STATUS.md` was updated, and remaining issues or follow-up work.
