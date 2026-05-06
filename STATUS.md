# LLM-r – Project Status

Last updated: 2026-05-06 09:00

## Current State

LLM-r is at package version `0.6.8`. The main product surface is the native
VST3 plug-in, with the FastAPI server, web UI, and PyQt GUI available as
companion surfaces.

The runtime now has two action transports:

- `osc`: the default path through AbletonOSC on `127.0.0.1:11000`.
- `device_bridge`: the local LLMRDeviceBridge Remote Script HTTP bridge on
  `127.0.0.1:8788`, used by `device_load`.

The Python planner builds typed action plans from the declarative capability
registry in `llmr/ableton_osc.py`. The executor routes OSC actions through
AbletonOSC and routes `device_load` through `llmr/device_bridge.py`. The VST3
plug-in has its own direct action execution path and prompts users to install
LLMRDeviceBridge when device loading is needed.

Core coverage today includes song/transport setup, track and scene operations,
clip creation/editing, MIDI note add/remove/get requests, audio clip properties,
device parameter access by index, device deletion, undo/redo, and single browser
device or plug-in loading.

Additional integration support includes a real Ableton smoke-test harness,
Device Bridge health/candidate/resolve APIs, OSC reply listener status/recent-reply
APIs, and safe semantic parameter maps.
The API now binds to loopback by default.

The primary UI surfaces have been modernized around a Plan Board workflow. The
VST3 editor, PyQt GUI, and companion web UI now expose readiness/status chips,
clear Plan/Details or Plan/Run/Details panes, and an Auto-approve option for
running plans immediately after planning while respecting dry-run safeguards.

Project status now lives in this file, `STATUS.md`. Cross-agent repository
instructions are centralized in `AGENTS.md`, with compatibility entry points for
Claude (`CLAUDE.md`) and GitHub Copilot
(`.github/copilot-instructions.md`). Agent instructions require `STATUS.md` to
stay current whenever behavior, risk, validation, or next steps change.

## Audit Scope

Reviewed:

- Capability registry, schemas, planner prompt generation, API capability output,
  executor routing, and tests.
- LLMRDeviceBridge Remote Script request handling, Live-thread scheduling,
  browser traversal, and failure behavior.
- Native VST3 code paths around Device Bridge action creation/execution and the
  macOS combo-box popup warning.
- User-facing docs, release notes, compatibility notes, security notes, website
  copy, and assistant guidance prompt copies.

## Fixes Made

- Added `transport` to the public `Capability` schema and `/api/capabilities`
  response so clients can distinguish AbletonOSC tools from Device Bridge tools.
- Updated the generated planner system prompt to include `transport`, preventing
  the runtime tool catalog from presenting `device_load` as an ordinary OSC tool.
- Replaced remaining OSC-only executor error wording with transport-neutral
  action execution wording.
- Hardened LLMRDeviceBridge startup and request parsing:
  - accepts both `_Framework.ControlSurface` and `ableton.v2.control_surface`
    imports;
  - handles invalid `Content-Length` with `400`;
  - logs and skips startup instead of crashing the Remote Script when the bridge
    port is already bound;
  - uses queue-based browser traversal and resets the scan budget per browser
    root;
  - returns early on exact high-confidence matches.
- Fixed the native VST3 combo-box popup call to avoid relying on a direct
  selector that the compiler warns about.
- Synchronized docs around the current AbletonOSC plus Device Bridge contract,
  setup steps, security model, unsupported workflows, and GitHub/site copy.
- Added tests for Device Bridge transport metadata in the capability registry,
  API output, and planner prompt.
- Added a smoke-test harness, Device Bridge status/candidate/resolve endpoints,
  OSC reply listener hooks, recognized reply reconciliation, and allow-listed
  semantic parameter guardrails.
- Added pre-execution Device Bridge preflight so mixed OSC/device plans do not
  partially mutate a Live set before discovering that device loading is
  unavailable or ambiguous.
- Added exact Device Bridge resolve preflight for `device_load`, including
  confirmed browser paths and preset queries.
- Added a first-class VST3 ambiguous-candidate picker for Device Bridge
  `device_load` preflight. When resolve returns `409`, the plug-in now prompts
  for an exact candidate path and retries preflight with that path.
- Changed the API default bind host from `0.0.0.0` to `127.0.0.1`.
- Added `/api/live/refresh` to request AbletonOSC readback for supported
  song/track/device/clip data and reconcile recognized replies into live state.
- Expanded OSC reply reconciliation coverage for additional song/track/clip and
  device parameter reply shapes, including parameter value strings exposed by
  `/api/live/tracks/{track_id}/parameters`.
- Enhanced the real Ableton smoke-test harness with run labels and JSON report
  output to support repeatable multi-version validation tracking.
- Modernized the VST3, PyQt, web UI, docs site hero, and screenshot mockup
  around a darker DAW-style command surface with readiness chips, action cards,
  clearer run logs, and Details/debug panes.
- Added Auto-approve controls to the VST3 editor, PyQt GUI, PyQt settings, and
  web UI. Auto-approve executes immediately after planning, with dry-run mode
  still producing previews and existing destructive-action checks still applied.
- Renamed the project status report from `REPORT.md` to `STATUS.md` and added
  cross-agent instruction files for Codex, Claude, and GitHub Copilot.
- Bumped the release version to `0.6.8` across Python package metadata, VST3
  metadata, release docs, and project status.

## Validation

Passed:

- `python3 -m pytest -q` -> 58 tests passed.
- `PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile gui/pyqt_app.py backend/device_server.py llmr/device_bridge.py llmr/osc_replies.py llmr/device_parameters.py remote_scripts/LLMRDeviceBridge/__init__.py remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py scripts/smoke_test_live_integration.py`
- `./scripts/build_vst3.sh` -> built `build/vst3/LLM-r.vst3`.
- `python3 -m build` -> built `llm_r-0.6.8.tar.gz` and
  `llm_r-0.6.8-py3-none-any.whl`.
- Inline web UI script syntax check with `node -e`.
- `git diff --check`
- `python3 -m pytest -q tests/test_api.py tests/test_executor.py` -> 29 tests
  passed.
- `./scripts/build_vst3.sh` -> built `build/vst3/LLM-r.vst3` after adding the
  VST3 candidate picker flow.
- Real Ableton smoke test harness added at
  `scripts/smoke_test_live_integration.py`; it still requires a manual
  disposable Live set and was not executed in this audit environment.

Not verified in this run:

- Real Ableton Live execution with AbletonOSC and LLMRDeviceBridge enabled.
- Actual Live browser search/load behavior across different Ableton Live
  versions and user library contents.

## Residual Risks Closed

- `device_load` dependency on LLMRDeviceBridge is now explicit and preflighted.
  The API and VST3 UI expose bridge reachability, and execution blocks before
  any OSC mutation when the bridge is unavailable.
- Browser ambiguity is now discoverable through candidate listing and produces a
  fail-fast `409`/preflight error instead of silently loading the wrong item.
  Exact candidate paths and preset queries can be resolved before loading;
  multi-device chain loading remains outside the current capability contract
  rather than hidden risky behavior.
- Live state is no longer optimistic-only for supported reads. `/api/live/refresh`
  requests AbletonOSC readback and the OSC reply listener reconciles recognized
  song, track, device-parameter, and MIDI-note replies.
- Semantic device parameter automation is allow-listed and range-checked.
  Unsupported semantic names fail validation instead of guessing indexes.
- The HTTP API now binds to `127.0.0.1` by default. Binding to `0.0.0.0` is an
  explicit opt-in for deliberate remote access.

## Remaining External Verification

- Run the real Ableton smoke test in disposable Live sets across supported Live
  versions.
- Verify actual browser paths and candidate scoring against varied user
  libraries and plug-in installations.
- Expand reply parsing and semantic maps only from verified AbletonOSC/Live
  readback data.

## Next Steps

1. Run and refine the real Ableton smoke-test harness against multiple Ableton
   Live versions.
2. Validate the new VST3 candidate picker in real Ableton sessions by forcing
  ambiguous browser queries and confirming the selected path loads correctly.
3. Grow safe semantic parameter maps only from verified Live readback data.
4. Keep release packaging focused on one primary install path: VST3 bundle plus
   bundled Remote Script, with server/GUI clearly marked as companion tools.
