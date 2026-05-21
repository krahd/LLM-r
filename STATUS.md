# STATUS — LLM-r 0.6.9 release candidate

Last updated: 2026-05-20 23:09

## Snapshot
- Version: `0.6.9`
- Branch: `release/0.6.9`
- Release state: pre-1.0 release candidate
- Primary surface: native VST3 plug-in
- Companion surfaces: PyQt GUI, web UI, FastAPI server
- Current stance: release hardening with truthful docs, conservative safety defaults, and manual Ableton validation before tag

## Product summary
LLM-r turns plain-language production requests into executable Ableton Live action plans. It is designed as a DAW control bridge, not a full composition engine or audio post-production suite.

The intended user workflow is: prompt -> plan -> review -> dry-run -> execute. The plan is explicit, safety-labelled, and reviewable before any live mutation. Dry run previews execution without mutating the set.

LLM-r connects to Ableton Live through AbletonOSC for core transport/track/clip/device operations and through LLMRDeviceBridge for browser/device loading workflows such as `device_load`.

LLM-r uses Modelito as the provider abstraction layer for cloud and local runtimes. In this release that includes OpenAI/Anthropic/Google plus local Ollama and oMLX, with runtime-specific model stores and controls.

## Shipped surfaces
### VST3 plug-in
- Supports provider/model selection (`openai`, `anthropic`, `google`, `ollama`, `omlx`, `custom`), prompt input, Plan/Details tabs, dry-run, auto-approve, destructive approval, Device Bridge checks, Save/Cancel settings, and Ollama controls in Advanced Settings.
- Deliberately does not yet include the PyQt/web readiness strip (`GET /api/readiness`) or a full oMLX management tab.
- Manual validation still needed before tag: real AbletonOSC smoke pass, Device Bridge candidate-resolution pass, and local-runtime smoke checks.

### PyQt GUI
- Supports embedded mode and HTTP-attached mode.
- Exposes full settings workflows and separates main settings from advanced runtime/network/provider settings.
- Exposes readiness state directly (plan, dry-run, execute readiness).
- Exposes Ollama and oMLX local runtime controls.
- Includes first-run onboarding with safe defaults and runtime setup helpers.

### Web UI
- Browser companion for quick planning and review outside the plug-in window.
- Exposes readiness chips and "what to fix next" guidance.
- Exposes Plan Board, Run Log, and Details views.
- Displays read-only local runtime status cards for Ollama and oMLX showing installation state, local model count, and currently served model count; marks active provider visually.
- Limitations: companion surface only; not a replacement for full PyQt runtime management or full in-Live workflow.

### FastAPI server
- Main route groups: health, settings, capabilities, planning, execution, macros, live state, sessions/history, readiness, local runtimes (Ollama/oMLX), Device Bridge, stream.
- Readiness output now treats provider/model status as blocking when credentials, local runtime availability, or configured local-model presence are missing.
- Plan responses now include canonical backend summary metadata (`summary`, `target_label`, transport labels, safety labels) so UI surfaces can share one display contract.
- Web UI now exposes a compact Basic Settings editor for provider/model changes only; PyQt remains the full setup surface for API keys, local-runtime management, and AbletonOSC configuration.
- Safety model: dry-run path, destructive approval gating, one-time plan execution, bounded/expiring plan store, Device Bridge preflight.
- Auth model: optional bearer token (`LLMR_API_TOKEN`) on write routes.

## Local model runtimes
### Ollama
- What works: status checks, local model list, download/serve/stop-serving helpers, planner routing through Modelito when provider is `ollama`.
- Diagnostics: missing Modelito helper capabilities now return structured payloads (`runtime`, `operation`, `candidates`) that explain what LLM-r attempted and next user action; intentional CLI fallback for stop-serving is preserved.
- Model-store note: Ollama models live in Ollama's store and are not automatically available to oMLX.
- Validation status: route layer and UI wiring covered; real runtime behaviour still requires manual smoke validation on target machine.

### oMLX
- What works: provider selection (`omlx`), API route layer, PyQt local runtime controls, planner routing through Modelito.
- Diagnostics: all adapter operations that probe candidate Modelito helpers now return standardized missing-capability payloads when no helper exists.
- Model-store note: oMLX models live in a separate store from Ollama.
- Validation status: API route tests and adapter logic are covered; full runtime behaviour is still manually validated.
- Important test boundary: current automated tests mainly mock the route/adapter layer; they are not a substitute for real oMLX runtime smoke tests.

## Ableton coverage
- song/transport
- tracks
- scenes/session
- clips
- MIDI basics
- audio clip properties
- devices/parameters
- macros
- live state/cache
- Device Bridge

## Safety
- Dry run: previews execution report without mutating the Live set.
- Destructive approval: destructive actions require explicit approval when not in dry run.
- One-time plan execution: a plan can only be executed once.
- Plan expiry/store bounds: plans expire and plan-store size is bounded.
- Device Bridge preflight: `device_load` plans preflight bridge availability before mixed execution.
- Ambiguous device-load handling: ambiguous candidates require explicit resolution/confirmation before live mutation.

## Test status
- Automated unit/API tests: present and broad across planning/execution/settings/runtime routes.
  - Last verified in Prompt 11: `python -m pytest -q` -> `147 passed, 4 warnings`.
- Web UI static smoke tests: present (`tests/test_web_ui_static.py`) for critical IDs, API endpoint strings, fallback functions, and safety copy in `web/index.html`.
  - Included in Prompt 11 full-suite run above.
- Ollama API route tests: present (`tests/test_ollama_api.py`) with mocked adapter/runtime boundaries.
  - Last verified in Prompt 11: included in `python -m pytest -q` run above.
- oMLX route tests: present (`tests/test_omlx_api.py`) with mocked runtime adapter behaviour.
  - Last verified in Prompt 11: included in `python -m pytest -q` run above.
- Plan summary tests: present (`tests/test_plan_summary.py`).
  - Last verified in Prompt 11: included in `python -m pytest -q` run above.
- Release workflow checks:
  - Last verified in Prompt 11: `ruff check .` passed.
  - Last verified in Prompt 11: `git diff --check` passed.
  - Last verified in Prompt 11: `./scripts/build_vst3.sh` passed.
  - Last verified in Prompt 11: `bash scripts/test_install_vst3_and_open.sh "$HOME/Library/Audio/Plug-Ins/VST3"` passed.
  - Expected command: `python3 -m build`.
- Not automated: browser-level web end-to-end automation, real Ableton Live mutation correctness, real Device Bridge browser behaviour, and real Ollama/oMLX runtime behaviour on release target machines.

## Manual validation required before tag
- VST3 build on macOS.
- VST3 install and Ableton scan.
- AbletonOSC real session smoke test.
- Device Bridge install/load/resolve test.
- Ollama runtime smoke test.
- oMLX runtime smoke test.
- Web UI smoke test (including local runtime status cards).

## Known limitations
- No warp marker CRUD.
- No render/export/loudness analysis workflow.
- No full plugin-chain construction workflow.
- No full arrangement composer workflow.
- No full identity-preserving project sync.
- VST3 does not yet include the full PyQt/web readiness strip or full oMLX management controls.
- Real Ableton Live, Device Bridge, Ollama, and oMLX runtime validation remains manual.

## 0.6.9 release blockers
- Complete real AbletonOSC smoke test on a disposable session and record outcomes.
- Complete Device Bridge install/load/resolve validation in a real Ableton session.
- Complete real Ollama runtime smoke test on the release target machine.
- Complete real oMLX runtime smoke test on the release target machine.
- Complete manual web and PyQt smoke passes on the release candidate build.

## Post-0.6.9 roadmap
1. Professional VST3 polish and validation.
2. Real Ableton integration harness.
3. Better live-state browser and plan diff.
4. Macro editor/templates.
5. Richer MIDI/audio transformations.
6. Device/plugin-chain workflows.
7. Readiness/oMLX parity decision for VST3.
8. Packaging/signing/notarisation if needed.

Last updated: 2026-05-20 23:09
