# LLM-r - Project Status

Last updated: 2026-05-20 13:19

## Purpose

LLM-r connects natural-language planning to Ableton Live execution. The native
VST3 plug-in is the primary product surface. FastAPI, web, and PyQt are
companion surfaces for setup, diagnostics, and automation.

## Release Candidate Snapshot

- Version: `0.6.9`
- Active branch: `release/0.6.9`
- Release stance: pre-1.0 release candidate, not final
- Priority for this branch: correctness, truthful docs, UI/UX clarity, release hygiene

Version metadata is aligned in:

- `pyproject.toml`
- `llmr/__init__.py`
- `native/vst3/llmr_vst3_plugin.cpp`
- `scripts/build_vst3.sh`
- `docs/RELEASE.md`
- `docs/DEVELOPMENT_PLAN.md`
- `STATUS.md`

## Shipped Surfaces

### Native VST3 (primary)

- Prompt entry, plan generation, execution controls
- Plan and Details tabs
- Dry run and Auto-approve toggles
- Destructive-action guard
- Device Bridge preflight and candidate-resolution safeguards
- Ollama runtime controls

Current boundary:

- The shipped VST3 does not expose the same readiness strip as PyQt/web
- The shipped VST3 does not expose a full oMLX management tab

### PyQt Companion GUI

- Embedded mode and HTTP mode
- Readiness bar and refresh workflow
- Ollama and oMLX runtime management flows
- Onboarding and richer plan/report surfaces

### Web Companion UI

- Browser UI served by FastAPI
- Readiness chips from `GET /api/readiness`
- Plan/review/execute flow with live safety messaging

### FastAPI Surface

- Planning, execution, settings, macros, history, sessions
- Device Bridge routes
- Local runtime routes for Ollama and oMLX
- Readiness endpoint

## Architecture and Safety Invariants

- Planner uses Modelito abstraction for providers/runtimes.
- `transport` must remain explicit (`osc` vs `device_bridge`) through planning,
  execution, reporting, and docs.
- `device_load` remains routed through LLMRDeviceBridge, not ordinary OSC.
- Loopback defaults are preserved for OSC and Device Bridge.
- Dry-run and destructive-action safeguards remain mandatory.
- Pre-execution Device Bridge preflight remains in place for mixed plans.

## Current Validation State

Completed on this branch:

- `python -m pytest -q` (full test suite)
- `ruff check .`
- requested `py_compile` entry-point checks
- `git diff --check`

Additional RC work completed in this pass:

- removed ad hoc `.gitignore` entries
- corrected stale/overclaiming language in docs
- repaired malformed `STATUS.md` (single canonical snapshot retained)
- added dedicated ollama API route coverage to mirror oMLX style

## Known Limitations and Risks

- Real Ableton Live execution is not covered by unit tests.
- VST3 parity with companion readiness/oMLX surfaces is intentionally incomplete.
- Real local runtime behaviour (especially oMLX on target machines) still needs
  manual validation.
- Device Bridge candidate quality depends on actual Live browser/library state.

## Manual Validation Required Before Tag

These remain required before publishing the release tag:

1. Build and install the native macOS VST3 bundle.
2. Open VST3 inside Ableton Live and verify first-run flow.
3. Run AbletonOSC smoke scenarios on disposable set.
4. Verify Device Bridge install and `device_load` candidate resolution paths.
5. Verify real Ollama runtime flows from shipped UI.
6. Verify real oMLX runtime flows from companion surfaces.

Reference checklists:

- `docs/RELEASE.md`
- `docs/ABLETON_SMOKE_TEST.md`

## Active Focus

1. Keep docs and behaviour aligned (no overclaims).
2. Complete manual Ableton/runtime validation for 0.6.9.
3. Decide whether VST3 should gain readiness/oMLX parity in the next cycle.

## Short Post-0.6.9 Roadmap

1. Improve first-run guidance and diagnostics in primary VST3 UX.
2. Expand verified semantic parameter coverage from real Ableton readback.
3. Improve live-state reconciliation and plan-review clarity.
4. Decide product boundary: companion-only features vs VST3 parity.

## Important Paths

- `llmr/app.py`
- `llmr/executor.py`
- `llmr/ableton_osc.py`
- `llmr/readiness.py`
- `llmr/modelito_adapter.py`
- `llmr/device_bridge.py`
- `native/vst3/llmr_vst3_plugin.cpp`
- `remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py`
- `gui/pyqt_app.py`
- `web/index.html`

Last updated: 2026-05-20 13:19
