# STATUS — LLM-r (Closed Project)

Last updated: 2026-05-23 03:36

## Snapshot
- Version: `0.6.9`
- Branch: `fix/0.6.9-vst3-ux-runtime-blockers`
- Release state: closed/archived reference repository
- Primary surface: native VST3 plug-in
- Companion surfaces: PyQt GUI, web UI, FastAPI server
- Current stance: project closed; code retained for archival/reference use and experimentation

## Product summary
LLM-r turns plain-language production requests into executable Ableton Live action plans. It is designed as a DAW control bridge, not a full composition engine or audio post-production suite.

Project note: this repository is now closed. Existing behaviour is preserved for reference, but no new production release cycle is planned from this codebase.

The intended VST3 user workflow is: prompt -> Run. Run plans first, then automatically executes the validated action list in Preview mode or live mode depending on Settings. Preview mode preserves the dry-run safety path and does not mutate the Live set.

LLM-r connects to Ableton Live through AbletonOSC for core transport/track/clip/device operations and through LLMRDeviceBridge for browser/device loading workflows such as `device_load`.

LLM-r uses Modelito as the provider abstraction layer for cloud and local runtimes. In this release that includes OpenAI/Anthropic/Google plus local Ollama and oMLX, with runtime-specific model stores and controls.

## Shipped surfaces
### VST3 plug-in
- Supports provider/model selection (`openai`, `anthropic`, `google`, `ollama`, `omlx`, `custom`), prompt input, Result/Details tabs, one-click Run, Preview mode, destructive approval, Device Bridge checks, modal single-screen Save/Cancel settings, and Ollama controls.
- Prompt 16-22 branch audit and repair pass completed on `fix/0.6.9-vst3-ux-runtime-blockers` with a checked-in audit report at `docs/0.6.9-VST3-UX-RUNTIME-AUDIT.md`.
- Prompt 17 execution semantics repair: Execute no longer follows the old dry-run default mode. Current VST3 UX routes the visible Run action through planning first, then Preview/live execution according to the Settings safety mode.
- Prompt 18 main UI updates: multiline prompt composer (`NSTextView`), clearer readiness wording, and a new header `System Prompts` action.
- Prompt 20 system prompt workflow: fixed System Prompts window with preset selector + edit/save/save-as/load/reset; prompt preset/custom persistence via `llmr.vst3.system_prompt_preset` and `llmr.vst3.system_prompt_custom`; planner prompt still appends `toolCatalogPrompt()`.
- Prompt 21 reliability updates: added duration parsing helpers (`minute`, `second`, `bar` -> beats), drum/piano deterministic fallback generators, and a 90s bounded provider wait in `callLLM`.
- Prompt 19 settings refactor now complete: Settings opens as a fixed-size modal sheet/window, Save/Cancel are explicit at the top and bottom, and the in-plugin Basic/Advanced toggle flow was removed from the active UI path.
- Current VST3 UX follow-up: System Prompt preset selection now updates the editor, Settings automatically refreshes Ollama status on open, the prompt placeholder hides while typing, the main surface has one Run action plus Cancel, and LLM requests wait in five-minute intervals with Continue Waiting / Wait Without Timeout / Cancel Request choices.
- Prompt 15 follow-up fixes: main-screen readiness labels now show a green/red icon plus plain white text without chip backgrounds/borders; the current Settings window is a compact non-scrolling modal surface.
- Prompt 16 bridge installer repair: VST3 no longer treats `~/Music/Ableton/User Library` as install authority; Settings now requires selecting/confirming the actual Ableton User Library, persists that choice (`llmr.vst3.bridge_user_library_path`), installs bridge files to `<User Library>/Remote Scripts/LLMR_Bridge`, validates `__init__.py`, detects double-nesting, exposes Reveal/Copy/Recheck/Help recovery actions, and shows explicit selected/target/status lines with reachability guidance.
- Prompt 16 settings/wrench hang fix: opening Settings avoids Bridge probes and blocking UI-thread HTTP; it now starts only an asynchronous Ollama status refresh. Bridge/Ollama actions include in-flight guards to prevent overlapping probes, and global bottom status messages from Bridge checks are concise/single-line instead of multiline diagnostics.
- Deliberately does not yet include the PyQt/web readiness strip (`GET /api/readiness`) or a full oMLX management tab.
- Manual validation still needed before tag: real AbletonOSC smoke pass, Prompt 16 VST3 bridge path-selection/install/reachability retest in Ableton (including relocated/external User Library), Device Bridge candidate-resolution pass, and local-runtime smoke checks.

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
- `AbletonAction` carries a `semantic_args` dict (preserved from the planner's original named-arg dict) so `_serialize_action()` can produce correct `target_label` values without reinterpreting positional OSC args.
- `_serialize_action()` is the single serialisation helper for `/api/plan`, `/api/execute`, and `/api/execute_batch`, ensuring display metadata parity across all execution surfaces.
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
- Preview mode: uses the dry-run execution path to preview the execution report without mutating the Live set.
- Destructive approval: destructive actions require explicit approval when not in dry run.
- One-time plan execution: a plan can only be executed once.
- Plan expiry/store bounds: plans expire and plan-store size is bounded.
- Device Bridge preflight: `device_load` plans preflight bridge availability before mixed execution.
- Ambiguous device-load handling: ambiguous candidates require explicit resolution/confirmation before live mutation.

## Test status
- Automated unit/API tests: present and broad across planning/execution/settings/runtime routes.
  - Last verified in Prompt 13: `python -m pytest -q` -> `153 passed, 4 warnings`.
- Web UI static smoke tests: present (`tests/test_web_ui_static.py`) for critical IDs, API endpoint strings, fallback functions, and safety copy in `web/index.html`.
  - Included in Prompt 13 full-suite run above.
- Ollama API route tests: present (`tests/test_ollama_api.py`) with mocked adapter/runtime boundaries.
  - Last verified in Prompt 13: included in `python -m pytest -q` run above.
- oMLX route tests: present (`tests/test_omlx_api.py`) with mocked runtime adapter behaviour.
  - Last verified in Prompt 13: included in `python -m pytest -q` run above.
- Plan summary tests: present (`tests/test_plan_summary.py`).
  - Prompt 12 additions: semantic-label tests for `fire_clip`/`device_load` with `semantic_args`, positional-fallback test, `PlanStore` roundtrip preservation test.
  - Last verified in Prompt 13: included in `python -m pytest -q` run above.
- Execute parity tests: `test_execute_plan_response_includes_action_metadata` in `tests/test_api.py` verifies `/api/execute` `executed_actions` contain all display fields: `target_label`, `transport_label`, `transport_plain_label`, `safety_label`, `semantic_args`, `tool`, `address`, `args`, `description`, `destructive`, `transport`.
  - Prompt 14 fix: corrected `address` to `/live/clip/fire` (canonical AbletonOSC address for `fire_clip`).
  - Last verified in Prompt 14: included in `python -m pytest -q` run above.
- Execute-batch metadata tests: `test_execute_batch_response_includes_executed_actions_metadata` verifies `/api/execute_batch` `executed_actions` match `/api/execute` metadata shape.
  - Prompt 14 fix: added `assert action["args"] == [2, 3]` assertion.
  - Last verified in Prompt 14: included in `python -m pytest -q` run above.
- VST3 static regression tests now include prompt-sequence checks:
  - `tests/test_vst3_settings_side_effects.py` verifies Execute dispatch is no longer tied to `executeLastPlan(currentDryRunDefault())`, prompt input uses multiline text view wiring, Settings is modal/no-scroll, Ollama refreshes on open, and the main surface has Run plus Cancel.
  - `tests/test_vst3_fallback_static.py` verifies duration/fallback helper function presence, planner fallback wiring, and the longer continue/cancel LLM wait path.
  - `tests/test_vst3_system_prompts_static.py` verifies System Prompts storage keys, preset-change wiring, and prompt composition pipeline.
- Release workflow checks:
  - Last verified in Prompt 19 follow-up: `python -m pytest -q` passed (`169 passed, 4 warnings`).
  - Last verified in Prompt 19 follow-up: `./scripts/build_vst3.sh` passed.
  - Last verified in Prompt 19 follow-up: `python -m pytest -q tests/test_vst3_settings_side_effects.py` passed (`6 passed`).
  - Last verified in Prompt 14: `ruff check .` passed.
  - Last verified in Prompt 14: `git diff --check` passed.
  - Last verified in Prompt 11: `bash scripts/test_install_vst3_and_open.sh "$HOME/Library/Audio/Plug-Ins/VST3"` passed.
  - Expected command: `python3 -m build`.
- Not automated: browser-level web end-to-end automation, real Ableton Live mutation correctness, real Device Bridge browser behaviour, and real Ollama/oMLX runtime behaviour on release target machines.

## Manual validation status
- This repository is closed; there is no active release-tag gate.
- If you still run this code, validate manually on your own target machine before trusting live execution.
- High-risk/manual areas remain: real Ableton mutation correctness, Device Bridge behaviour, and local runtime integration (Ollama/oMLX).

## Known limitations
- No warp marker CRUD.
- No render/export/loudness analysis workflow.
- No full plugin-chain construction workflow.
- No full arrangement composer workflow.
- No full identity-preserving project sync.
- VST3 does not yet include the full PyQt/web readiness strip or full oMLX management controls.
- Real Ableton Live, Device Bridge, Ollama, and oMLX runtime validation remains manual.

## Closure implications
- Treat this codebase as reference material, not as a maintained product branch.
- Documentation has been updated to clearly mark the project as closed.
- Website surfaces now show a dismissible "project closed" overlay so closure status is visible at first load.
- Website surfaces now also show a persistent closed-status badge in the top header/nav after overlay dismissal.

## Successor directions (outside this repository)
1. Keep the VST3 as a thin front-end and move runtime responsibilities to a local helper process.
2. Reuse existing AbletonOSC/MCP ecosystem pieces instead of expanding a private bridge stack.
3. Productise local runtime UX (simple local defaults, minimal provider jargon).
4. Focus on dependable musical tooling (validators/generators), not prompt-only orchestration.

Last updated: 2026-05-23 03:36
