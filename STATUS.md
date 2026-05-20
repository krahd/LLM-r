# LLM-r – Project Status

Last updated: 2026-05-20 12:44

## Project purpose

LLM-r bridges Ableton Live and LLM planners. The native VST3 plug-in is the
primary product surface. PyQt, the web UI, and FastAPI are companion surfaces
for setup, control, debugging, and automation around the same planning and
execution workflow.

The current product goal is a VST3-first Ableton tool that is safe to preview,
reviewable before mutation, explicit about transport and destructive actions,
clear about cloud vs local model choices through Modelito, and documented
truthfully.

## Current implementation state

Current package version: `0.6.9`.

Version metadata is currently aligned in `pyproject.toml`, `llmr/__init__.py`,
`native/vst3/llmr_vst3_plugin.cpp`, `scripts/build_vst3.sh`,
`docs/RELEASE.md`, `docs/DEVELOPMENT_PLAN.md`, and `STATUS.md`.

LLM-r currently provides:

- native macOS VST3 plug-in with prompt entry, Plan and Details tabs, dry-run,
    Auto-approve, destructive-action approval, provider/model settings, Device
    Bridge checks, and Ollama runtime controls
- FastAPI server with health, settings, model metadata, capabilities,
    planning, execution, macros, live state, history, streaming, Device Bridge,
    Ollama, and oMLX endpoints
- readiness model in `llmr/readiness.py` with `GET /api/readiness`
- upgraded plan presentation in PyQt and web UI with plan summaries, target
    labels, transport/safety breakdown, and clearer destructive/live warnings
- improved local runtime management in PyQt for Ollama and oMLX with clearer
    step-by-step workflow, bounded logs, and better empty states
- PyQt first-run onboarding wizard
- PyQt companion GUI with embedded and attached-server modes
- web UI companion surface with readiness chips, Plan Board, Run Log, and
    Details view
- Modelito-backed planner using cloud or local providers
- transport-aware execution through AbletonOSC and LLMRDeviceBridge
- Device Bridge status, candidate listing, and exact resolve endpoints
- OSC reply listener and partial live-state reconciliation
- static and runtime macros with persistence
- smoke-test tooling for real Ableton validation
- release workflow for sdist, wheel, and standalone companion binaries

Important UI boundary in the shipped build:

- VST3 is primary.
- PyQt is the richest setup/control/debug companion.
- Web UI is a lightweight browser companion.
- The shipped VST3 does not yet expose the PyQt/web readiness strip and does
    not yet ship an oMLX management UI.

## Product stance

LLM-r remains pre-1.0. The release bar is documentation truthfulness,
repeatable builds, safe plan review, and real manual validation of the Ableton
surfaces rather than compatibility with old internal builds.

Do not bump to `1.0.0` until native macOS VST3 build/install/load, real
AbletonOSC execution, Device Bridge browser/device loading, and real local
runtime behaviour have all been validated manually.

## Active focus

Recently completed:

1. Plan Board and action presentation improvements in PyQt and web UI.
2. Better local runtime UX in PyQt for Ollama and oMLX.
3. PyQt onboarding and readiness surfacing.
4. Documentation audit to remove UI overclaims and clarify the product-surface split.

Current focus:

1. Finish release-quality manual validation.
2. Keep docs aligned with shipped behaviour.
3. Decide whether VST3 should gain readiness/oMLX parity or whether those stay companion-surface features for this release.

## Architecture overview

LLM-r has a VST3-first architecture with Python companion services. The
planner emits typed, transport-aware plans. The executor routes actions to
AbletonOSC or the Device Bridge. The Remote Script runs inside Ableton Live for
browser/device loading. PyQt, web UI, and FastAPI sit beside the plug-in as
companion surfaces.

```text
VST3 plug-in
        -> prompt / plan / review / execute
        -> direct AbletonOSC actions
        -> Device Bridge-backed device_load actions

PyQt GUI / Web UI / API clients
        -> FastAPI server
                -> settings / readiness / capabilities
                -> planner / executor
                -> history / macros / sessions
                -> Ollama and oMLX endpoints

Planner
        -> Modelito
                -> OpenAI / Anthropic / Google / custom
                -> Ollama
                -> oMLX
```

## Setup and run instructions

Development install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e .[gui]
pip install -e .[dev]
```

Run server:

```bash
python3 backend/main.py
```

Run PyQt GUI:

```bash
python3 gui/pyqt_app.py
```

Build local VST3 on macOS:

```bash
./scripts/build_vst3.sh
```

Release-candidate automated validation:

```bash
python3 -m pytest -q
PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile gui/pyqt_app.py backend/device_server.py llmr/device_bridge.py llmr/osc_replies.py llmr/device_parameters.py remote_scripts/LLMRDeviceBridge/__init__.py remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py scripts/smoke_test_live_integration.py
ruff check .
python3 -m build
git diff --check
```

macOS-only VST3 validation:

```bash
./scripts/build_vst3.sh
bash scripts/test_install_vst3_and_open.sh "$HOME/Library/Audio/Plug-Ins/VST3"
```

Real Ableton smoke testing is documented in `docs/ABLETON_SMOKE_TEST.md`.

## Configuration and defaults

Important defaults:

- FastAPI host: `127.0.0.1`
- FastAPI port: `8787`
- AbletonOSC target: `127.0.0.1:11000`
- LLMRDeviceBridge target: `127.0.0.1:8788`
- default provider: `openai`
- default model: `gpt-4.1-mini`

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

Keep `LLMR_HOST=127.0.0.1` for normal local use.

## Native VST3 UI parity audit

Audit performed on 2026-05-20 by code inspection while updating docs. This was
not a manual plug-in smoke test.

Current parity findings:

- Plan/Details workflow, dry-run, Auto-approve, destructive approval, Device
    Bridge checks, and Ollama controls are present in VST3.
- PyQt and web UI expose readiness from `GET /api/readiness`; the shipped VST3
    does not currently expose that same readiness strip.
- PyQt exposes Ollama and oMLX runtime tabs; the shipped VST3 currently exposes
    Ollama controls only.
- PyQt ships onboarding; the VST3 currently ships only lighter initial guidance.

Implication for docs:

- Docs must describe VST3 as primary without claiming PyQt/web parity where it
    does not exist yet.

## Important files

- `README.md`: top-level product overview
- `STATUS.md`: current project snapshot
- `llmr/app.py`: FastAPI routes and web UI serving
- `llmr/readiness.py`: readiness computation
- `llmr/modelito_adapter.py`: Modelito provider/runtime helpers
- `native/vst3/llmr_vst3_plugin.cpp`: VST3 implementation
- `gui/pyqt_app.py`: PyQt companion GUI
- `web/index.html`: lightweight browser companion UI
- `docs/USER_MANUAL.md`: user-facing workflow guide
- `docs/MODELITO.md`: provider/runtime guide
- `docs/RELEASE.md`: release process and manual checklist
- `docs/ABLETON_SMOKE_TEST.md`: real Ableton validation checklist

## Recent documentation changes

- README now makes the product-surface hierarchy explicit.
- README now includes first-run and local-model guidance.
- USER_MANUAL now includes a UI tour, plan-review guidance, safety controls,
    and local-runtime setup flow.
- MODELITO now explains provider choice, model stores, and model-ID boundaries
    for ordinary users.
- RELEASE now includes a pre-release UI checklist and removes VST3 oMLX/readiness overclaim.
- DEVELOPMENT_PLAN now reflects completed UI work and the current VST3 parity boundary.

## Tests and verification status

This change set is documentation-only.

Automated validation run in this pass:

- not required for code correctness because no code changed

Manual/documentation validation run in this pass:

- code inspection of VST3, PyQt, and web UI surfaces to remove doc overclaims
- heading/link coherence review across edited Markdown files

Last recorded automated product validation before this docs pass, as documented
in the repository, included the expanded plan-summary/readiness tests and was
reported as 96 passing tests. That result was not re-run during this
documentation-only update.

## Manual validation still required

These are still outstanding and should be treated as release blockers for a
truthful release candidate:

- native macOS VST3 build verification
- native macOS VST3 install verification
- native macOS VST3 load/open verification inside Ableton Live
- real AbletonOSC smoke test
- LLMRDeviceBridge install verification in Ableton Live
- real Device Bridge browser/device loading
- ambiguous Device Bridge candidate flow verification
- real Ollama runtime verification against the shipped UI surfaces
- real oMLX runtime verification against the shipped PyQt/web/API surfaces

## Known risks and limitations

- Real Ableton execution is not covered by unit tests.
- Native VST3 load/install validation requires macOS and Ableton Live.
- Real local-runtime behaviour remains partially manual, especially for oMLX.
- Actual browser paths and candidate resolution behaviour need verification
    across different user libraries and plug-in inventories.
- Multi-device chain loading remains outside the current capability contract.

## Pending tasks

- run the manual release checklist from `docs/RELEASE.md`
- run the real smoke-test checklist from `docs/ABLETON_SMOKE_TEST.md`
- decide whether VST3 should gain readiness and oMLX-management parity before release

## Next steps

1. Build and install the macOS VST3 bundle.
2. Open the VST3 in Ableton Live and verify the documented first-run flow.
3. Run the disposable-set smoke tests for AbletonOSC and Device Bridge.
4. Manually verify local runtime flows for Ollama and oMLX.

## Longer-term steps

- expand live-state reconciliation where AbletonOSC exposes reliable readback
- broaden capability coverage for richer track/device workflows
- improve plan-diff/review tools before live execution
- decide whether companion-only features should migrate into the VST3

## Decisions

- VST3 remains the primary surface.
- PyQt remains the richest setup/control/debug companion.
- Web UI remains a lightweight browser companion.
- Documentation should not claim VST3 readiness/oMLX parity until that parity exists and has been validated.

Last updated: 2026-05-20 12:44
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

Last updated: 2026-05-20 12:39
