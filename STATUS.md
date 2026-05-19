# LLM-r – Project Status

Last updated: 2026-05-19 21:00

## Project purpose

LLM-r bridges Ableton Live and LLM planners. Its primary product surface is the native VST3 plug-in. FastAPI, the web UI, the PyQt GUI, the Device Bridge Remote Script, and smoke-test tooling are companion surfaces for the same planning and execution workflow.

The professional product goal is a self-contained Ableton Live plug-in that is safe, reliable, and understandable for musicians; clear local/cloud model selection through Modelito; dry-runnable and reviewable plans before mutating a Live set; accurate documentation that describes only shipped behaviour; and repeatable release builds and validation steps.

## Current implementation state

Current package version: `0.6.9`.

Version metadata currently appears in `pyproject.toml`, `llmr/__init__.py`, `native/vst3/llmr_vst3_plugin.cpp`, `scripts/build_vst3.sh`, `docs/RELEASE.md`, `docs/DEVELOPMENT_PLAN.md`, and `STATUS.md`.
All sources are consistent at `0.6.9`.

LLM-r currently provides:

- native macOS VST3 plug-in with provider/model settings, Plan/Details response tabs, readiness checks, dry-run, Auto-approve, destructive-action approval, and direct AbletonOSC plus Device Bridge execution
- FastAPI server with health, settings, model metadata, capabilities, planning, execution, macro, live-state, history, streaming, Modelito, Ollama, and oMLX endpoints
- PyQt companion GUI with embedded and HTTP backends, plan/review/execute workflow, settings, provider/model selection, and local runtime controls for Ollama and oMLX
- web UI companion surface
- Modelito-backed planner using configured cloud or local providers
- runtime capability registry generated from `llmr/ableton_osc.py`
- typed action plans and transport-aware execution reports
- AbletonOSC transport for normal Live actions
- LLMRDeviceBridge Remote Script transport for Live browser/device loading
- Device Bridge status, candidate browsing, and exact resolve endpoints
- OSC reply listener and partial Live-state reconciliation
- static and runtime macros with persistence
- session history and persisted plan/macro/session stores
- smoke-test tooling for real Ableton validation
- release workflow for source distributions, wheels, and PyInstaller binaries

## Product stance

LLM-r is still pre-1.0. Compatibility with unreleased internal versions is less important than a coherent, polished, reliable product.

Recommended next bump after the current audit: `0.6.9`, not `1.0.0`.

Do not bump to `1.0.0` until real macOS VST3 build/install/load has been verified, real AbletonOSC execution has been smoke-tested, Device Bridge install/load workflow has been tested in Ableton Live, README/user manual/release docs/development plan/status agree, packaging and release workflow have been validated, and known documentation overclaims have been removed.

## Active focus

Current focus should move from feature implementation to release-quality hardening:

1. Make documentation match the shipped product exactly.
2. Close the automated test gap around oMLX API routes.
3. Verify native VST3 build/install/load on macOS.
4. Verify real AbletonOSC and Device Bridge smoke workflows.
5. Clean packaging/release metadata and remove tracked local artefacts.
6. Prepare a clean `0.6.9` release candidate.

## Architecture overview

LLM-r has a VST3-first architecture with Python companion services. The capability registry and planner produce typed, transport-aware plans. The executor and VST3 action path route actions to AbletonOSC or the Device Bridge. The Remote Script runs inside Ableton Live and performs browser/device loading. Companion UIs expose planning, execution, readiness, settings, model management, and debug/status surfaces.

### Architecture diagram

```text
VST3 plug-in
    -> provider/model/settings
    -> plan/review/execute
    -> AbletonOSC actions
    -> Device Bridge actions

PyQt GUI / Web UI / API clients
    -> FastAPI server
        -> settings, capabilities, model metadata
        -> planner
        -> executor
        -> history, macros, sessions
        -> Ollama and oMLX management endpoints

Planner
    -> ModelitoClient
        -> OpenAI / Anthropic / Google / custom
        -> Ollama
        -> oMLX

Executor
    -> osc transport
        -> AbletonOSC
        -> Ableton Live
    -> device_bridge transport
        -> LLMRDeviceBridge Remote Script
        -> Ableton Live browser/device loading
```

### Execution flow

```text
User prompt
    -> planner builds strict JSON action plan
    -> validate tool names, arguments, safety, transport
    -> preflight Device Bridge actions
    -> dry-run or execute
        -> OSC actions go to AbletonOSC
        -> device_load goes to LLMRDeviceBridge
    -> collect report
    -> update plan/session/history state
    -> reconcile recognised AbletonOSC replies where available
```

### LLM provider flow

```text
User selects provider/model
    -> settings/env vars
    -> ModelitoClient(provider, model)
    -> provider-specific Modelito adapter
    -> planner receives model response
    -> LLM-r parses/repairs/validates action JSON
```

Ollama and oMLX are local runtime options mediated by Modelito. LLM-r should not bypass Modelito for planner calls.

## Setup and run instructions

Development install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e .[gui]
pip install -e .[dev]
```

Run tests:

```bash
python3 -m pytest -q
```

Run server:

```bash
python3 backend/main.py
```

Run GUI:

```bash
python3 gui/pyqt_app.py
```

Build local VST3 on macOS:

```bash
./scripts/build_vst3.sh
```

Local release build:

```bash
python3 -m build
./scripts/build_release.sh
```

Recommended release-candidate validation:

```bash
python3 -m pytest -q
PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile gui/pyqt_app.py backend/device_server.py llmr/device_bridge.py llmr/osc_replies.py llmr/device_parameters.py remote_scripts/LLMRDeviceBridge/__init__.py remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py scripts/smoke_test_live_integration.py
ruff check .
python3 -m build
git diff --check
```

macOS-only validation:

```bash
./scripts/build_vst3.sh
bash scripts/test_install_vst3_and_open.sh "$HOME/Library/Audio/Plug-Ins/VST3"
```

Real Ableton smoke testing is documented in `docs/ABLETON_SMOKE_TEST.md`.

## Configuration and environment variables

Important defaults:

- FastAPI host: `127.0.0.1`
- FastAPI port: `8787`
- AbletonOSC target: `127.0.0.1:11000`
- LLMRDeviceBridge target: `127.0.0.1:8788`
- Modelito provider: `openai`
- Modelito model: `gpt-4.1-mini`
- planner guidance prompt: enabled by default
- API token: unset by default

Important environment variables:

- `LLMR_PROVIDER`
- `LLMR_MODEL`
- `LLMR_HOST`
- `LLMR_PORT`
- `LLMR_ABLETON_HOST`
- `LLMR_ABLETON_PORT`
- `LLMR_DEVICE_BRIDGE_ENABLED`
- `LLMR_DEVICE_BRIDGE_HOST`
- `LLMR_DEVICE_BRIDGE_PORT`
- `LLMR_OSC_REPLY_ENABLED`
- `LLMR_OSC_REPLY_HOST`
- `LLMR_OSC_REPLY_PORT`
- `LLMR_PLAN_STORE_PATH`
- `LLMR_MACRO_STORE_PATH`
- `LLMR_SESSION_STORE_PATH`
- `LLMR_SETTINGS_PATH`
- `LLMR_API_TOKEN`

Keep `LLMR_HOST=127.0.0.1` for normal local use. Binding to `0.0.0.0` is a security-sensitive deployment choice.

## Current API surface

The FastAPI surface includes health, settings/model endpoints, the capability registry, planning/execution, streaming, macro CRUD and macro planning, live state, Device Bridge status/devices/resolve, OSC reply status/recent endpoints, Ollama local-runtime management, oMLX local-runtime management, model metadata, sessions, and history.

oMLX endpoints currently implemented:

- `GET /api/omlx/status`
- `GET /api/omlx/local_models`
- `GET /api/omlx/remote_models`
- `GET /api/omlx/running_models`
- `POST /api/omlx/start`
- `POST /api/omlx/stop`
- `POST /api/omlx/install`
- `POST /api/omlx/download`
- `POST /api/omlx/delete`
- `POST /api/omlx/serve`
- `POST /api/omlx/stop_serving`

## Important files and directories

- `README.md`: top-level product overview and API summary.
- `STATUS.md`: current project status and roadmap.
- `AGENTS.md`: durable coding-agent instructions.
- `pyproject.toml`: package metadata and dependency declarations.
- `llmr/`: Python package source.
- `llmr/app.py`: FastAPI server and API route surface.
- `llmr/planner.py`: LLM planner integration and plan persistence.
- `llmr/executor.py`: Python-side execution and transport routing.
- `llmr/ableton_osc.py`: tool registry and AbletonOSC action mapping.
- `llmr/modelito_adapter.py`: Modelito adapter helpers and local runtime management wrappers.
- `llmr/device_bridge.py`: Python HTTP client for the Live Device Bridge.
- `llmr/osc_replies.py`: OSC reply listener and reconciliation.
- `native/vst3/llmr_vst3_plugin.cpp`: self-contained VST3 implementation.
- `gui/pyqt_app.py`: PyQt companion GUI.
- `remote_scripts/LLMRDeviceBridge/`: Ableton Live Remote Script.
- `backend/`: server/device-server entry points.
- `web/`: companion web UI.
- `docs/`: user, release, security, capability, compatibility, Modelito, scenario, and smoke-test documentation.
- `scripts/`: VST3 build/install helpers, release helper, probes, and real Ableton smoke-test harness.
- `tests/`: automated Python tests.
- `.github/workflows/release.yml`: release artifact workflow.

## Audit findings: codebase

### Good state

- The package requires Python 3.11+ and depends on `modelito>=1.4.5`.
- Version metadata is consistently `0.6.9` across pyproject.toml, llmr/__init__.py, VST3 source, VST3 build script, and related docs.
- The API uses `LocalModelRequest` for both Ollama and oMLX model-operation endpoints.
- oMLX API routes are present and covered by dedicated automated tests in `tests/test_omlx_api.py`.
- PyQt has a real oMLX management tab and local-model loading path.
- Modelito remains the provider abstraction for planner calls.
- Release workflow builds artifacts on `v*` tags and now includes validation + tag/version consistency checks.
- `gui_run.log` has been removed from tracking; `*.log` is in `.gitignore`.
- `pytest-asyncio` is declared in dev deps; `asyncio_default_fixture_loop_scope = "function"` is set.
- README updated for oMLX and Modelito.
- `docs/USER_MANUAL.md` updated with oMLX section and provider flow.
- `docs/RELEASE.md` updated with pre-tag checklist and version consistency guide.
- `docs/DEVELOPMENT_PLAN.md` updated current version and priorities.

### Issues to fix before bumping release

All pre-`0.6.9` release hygiene tasks are now complete. The following are the remaining gaps before declaring a final release:

1. Real Ableton Live execution is not covered by unit tests — requires manual smoke testing.
2. Native VST3 build/install/load on macOS requires manual verification.
3. LLMRDeviceBridge install and browser/device loading requires manual verification in Ableton.
4. Real oMLX runtime behaviour is not automated — only the FastAPI route layer is tested.

## Audit findings: documentation

### README

README is strong as a high-level overview, but before release it should:

- include oMLX in the top architecture diagram provider list
- include oMLX in the GUI/Advanced Settings section
- mention `docs/MODELITO.md` from the local provider/model section
- use `ruff check .` rather than `ruff .`
- include a short “Current limitations” section pointing to real Ableton smoke-test requirements

### docs/USER_MANUAL.md

Needs updates:

- add oMLX to requirements and provider list
- add an oMLX section parallel to the Ollama section
- explain that Ollama-pulled models are not automatically available to oMLX
- mention the PyQt oMLX tab if user-facing
- distinguish VST3 Advanced Settings from PyQt Advanced Settings if their local-runtime surfaces differ

### docs/MODELITO.md

Good and mostly current. Improve before release:

- avoid using `llama3:latest` as the oMLX example unless that exact ID is known to work in Modelito/oMLX
- link back to the user manual and README
- add a short “Which provider should I use?” section for ordinary users

### docs/RELEASE.md

Needs updates:

- bump tag example from `v0.6.8` to the next intended version when bumping
- mention oMLX controls alongside Ollama controls
- add a mandatory pre-tag checklist
- add tag/version consistency checks
- state which artifacts are considered primary versus companion

### docs/DEVELOPMENT_PLAN.md

Needs updates:

- current package version should be bumped with release
- current baseline should mention oMLX local-runtime controls
- prioritised work should emphasise release polish, tests, docs, native validation, and smoke testing
- remove stale pre-oMLX wording

## Tests and verification status

Last run: 2026-05-19.

```
python3 -m pytest -q          -> 73 passed (includes 13 new tests/test_omlx_api.py)
ruff check .                  -> All checks passed
python3 -m py_compile ...     -> passed (all Python surfaces)
git diff --check              -> passed
```

Test suite covers:

- FastAPI route tests for capabilities, settings, plans, execution, macros, live-state, history, streaming, Ollama routes, oMLX routes (all 11 endpoints, including model-arg forwarding and 422 validation)
- planner unit tests
- executor unit tests
- Modelito adapter unit tests
- OSC action mapping tests

Manual validation still required:

- real Ableton Live execution with AbletonOSC
- LLMRDeviceBridge install and browser/device loading
- native macOS VST3 build/install/load
- ambiguous Device Bridge candidate picker
- real oMLX install/runtime behaviour

## Known issues, risks, and limitations

- Real Ableton execution is not covered by unit tests.
- Native VST3 build/install/load validation requires macOS and Ableton Live.
- Actual browser paths and candidate scoring need verification across varied user libraries and plug-in installations.
- Real oMLX runtime validation remains manual; automated tests cover FastAPI routes with monkeypatched adapters only.
- Multi-device chain loading remains outside the current capability contract.
- Reply parsing and semantic maps should expand only from verified AbletonOSC/Live readback data.
- Semantic parameter maps remain intentionally conservative.

## Release-readiness checklist for `0.6.9`

Completed:

- [x] Add explicit `/api/omlx/...` route tests (`tests/test_omlx_api.py`, 13 tests)
- [x] Remove tracked `gui_run.log` and ignore logs (`*.log` in `.gitignore`)
- [x] Update README oMLX/Modelito wording, add limitations section, fix `ruff check .`
- [x] Update `docs/USER_MANUAL.md` for oMLX and Modelito provider flow
- [x] Update `docs/RELEASE.md` with pre-tag checklist and version consistency guide
- [x] Update `docs/DEVELOPMENT_PLAN.md` with current baseline and priorities
- [x] Add `pytest-asyncio` to dev deps and set `asyncio_default_fixture_loop_scope`
- [x] Add validate job with tests/lint/version check to release workflow
- [x] Bump version to `0.6.9` in all sources
- [x] 73 tests pass, ruff clean, py_compile clean, git diff --check clean

Still required (manual):

- [ ] Native macOS VST3 build/install/load verification
- [ ] Real Ableton Live smoke test
- [ ] LLMRDeviceBridge install and browser/device loading
- [ ] Real oMLX runtime test

```bash
python3 -m pytest -q
ruff check .
PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile gui/pyqt_app.py backend/device_server.py llmr/device_bridge.py llmr/osc_replies.py llmr/device_parameters.py remote_scripts/LLMRDeviceBridge/__init__.py remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py scripts/smoke_test_live_integration.py
python3 -m build
git diff --check
```

Recommended macOS validation:

```bash
./scripts/build_vst3.sh
bash scripts/test_install_vst3_and_open.sh "$HOME/Library/Audio/Plug-Ins/VST3"
python3 scripts/smoke_test_live_integration.py
```

## Roadmap

### Phase 1 — Release hygiene and truthfulness

Goal: make the repository internally consistent.

Tasks:

- add oMLX API route tests
- remove tracked local log artefact
- update README, user manual, release docs, development plan, and status
- reconcile pytest async config
- add release workflow tests and version guard
- rerun normal validation
- bump to `0.6.9`

Exit criteria:

- docs agree with shipped behaviour
- no known false claims in status/docs
- tests and lint pass
- release metadata is consistent

### Phase 2 — Professional packaging

Goal: make a user-installable pre-release.

Tasks:

- validate GitHub release workflow on tag
- confirm artifacts contain expected wheel/sdist/binaries
- confirm VST3 bundle shape and metadata
- document install path clearly
- decide whether PyInstaller GUI/server binaries are release-grade or experimental
- make the VST3 + Remote Script the obvious primary install path

Exit criteria:

- a user can download the release and understand what to install
- release assets are named clearly
- release notes include limitations and setup requirements

### Phase 3 — Real Ableton validation

Goal: prove that LLM-r works in real Ableton Live, not only in unit tests.

Tasks:

- run AbletonOSC smoke tests against a disposable Live set
- validate Device Bridge installation and Control Surface setup
- validate browser search, ambiguous candidate resolution, exact candidate path loading
- validate VST3 plan/dry-run/execute workflow
- validate dry-run/destructive safeguards in the plug-in
- record supported Ableton Live versions

Exit criteria:

- smoke-test checklist passes on at least one supported Live version
- failures are documented as known limitations or fixed
- user manual reflects real setup steps

### Phase 4 — Product UX polish

Goal: make the plug-in pleasant and understandable.

Tasks:

- clarify first-run onboarding in VST3
- add stronger readiness/error messages
- improve model/provider setup flow
- add capability/help view or link from plug-in
- improve plan-review affordances
- make local runtime states easier to understand

Exit criteria:

- a new user can install, choose a model, dry-run, and execute a simple safe plan without reading developer docs

### Phase 5 — Musical usefulness

Goal: make LLM-r meaningfully useful in normal production workflows.

Tasks:

- expand verified scenario recipes
- improve planner prompt examples
- add more safe semantic parameter maps from real readback
- improve MIDI transformations where readback supports it
- add more macros for common workflows
- add capability explorer/live-state browser in GUI/web if useful

Exit criteria:

- common requests such as arrangement setup, drum sketching, device loading, basic mixing, and clip edits work reliably within the declared capability contract

### Phase 6 — Public 1.0 criteria

Do not call this 1.0 until:

- primary VST3 install path is reliable
- real Ableton smoke tests are repeatable
- docs are user-grade
- release artifacts are validated
- safety model is stable
- unsupported workflows are clearly explained
- at least one full end-to-end demo scenario is documented and reproducible

## Pending tasks

Immediate (remaining):

- build and install VST3 on macOS (manual)
- run real Ableton smoke test (manual)
- run LLMRDeviceBridge install/load test in Ableton (manual)
- run real oMLX runtime test (manual)
- publish a clean `0.6.9` pre-release tag when manual validation passes

Longer-term:

- strengthen Live-state reconciliation
- expand safe capabilities from verified AbletonOSC/Device Bridge behaviour
- improve first-run UX
- improve release packaging and install documentation
- decide what must be native VST3-only versus companion Python/server functionality

## Decisions and rationale

- The native VST3 plug-in is the main product surface.
- FastAPI, web UI, and PyQt GUI are companion surfaces.
- Modelito is the provider abstraction; LLM-r should not implement provider-specific planner clients directly.
- `osc` and `device_bridge` are distinct transports and must remain explicit.
- Device loading belongs in the Ableton Live Remote Script runtime, not in an external Python process importing Ableton’s `Live` API.
- API loopback binding is the default security posture.
- Dry-run and destructive-action approval are core safety features.
- Semantic parameter maps should remain conservative and verified.
- Pre-1.0 releases should favour correctness and clarity over backwards compatibility with unreleased internal states.

---

Last updated: 2026-05-19 21:00
