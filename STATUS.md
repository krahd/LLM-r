# LLM-r – Project Status

Last updated: 2026-05-07 00:15

## Project purpose

LLM-r bridges Ableton Live and LLM planners. Its main product surface is a native VST3 plug-in, with FastAPI, web UI, PyQt GUI, Remote Script, and smoke-test tooling as companion surfaces for the same planning and execution workflow.

## Current implementation state

LLM-r is currently at package version `0.6.8`.

The runtime has two action transports:

- `osc`: default AbletonOSC UDP transport, normally `127.0.0.1:11000`.
- `device_bridge`: local LLMRDeviceBridge Remote Script HTTP transport, normally `127.0.0.1:8788`, used by `device_load`.

The Python planner builds typed action plans from the declarative capability registry in `llmr/ableton_osc.py`. The executor routes OSC actions through AbletonOSC and routes `device_load` through `llmr/device_bridge.py`. The VST3 plug-in has its own direct action execution path and prompts users to install LLMRDeviceBridge when device loading is needed.

Core coverage includes song/transport setup, track and scene operations, clip creation/editing, MIDI note add/remove/get requests, audio clip properties, device parameter access by index, device deletion, undo/redo, and single browser device or plug-in loading.

Additional integration support includes a real Ableton smoke-test harness, Device Bridge health/candidate/resolve APIs, OSC reply listener status/recent-reply APIs, and safe semantic parameter maps. The API binds to loopback by default.

Primary UI surfaces have been modernised around a Plan Board workflow. The VST3 editor, PyQt GUI, and companion web UI expose readiness/status chips, clear Plan/Details or Plan/Run/Details panes, and Auto-approve controls for running plans immediately after planning while preserving dry-run safeguards.

## Active focus

Current focus is release-facing stabilisation of the VST3-first product path, AbletonOSC plus Device Bridge transport correctness, real Ableton smoke validation, candidate resolution for device loading, Live-state reconciliation, and documentation alignment.

## Architecture overview

LLM-r has a VST3-first architecture with Python companion services. The capability registry and planner produce typed transport-aware plans. The executor and VST3 action path route actions to AbletonOSC or the Device Bridge. The Remote Script runs inside Ableton Live and performs browser/device loading. Companion UIs expose planning, execution, readiness, and debug/status surfaces.

### Architecture diagram

<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="560" viewBox="0 0 1080 560" role="img" aria-labelledby="llmr-arch-title llmr-arch-desc">
  <title id="llmr-arch-title">LLM-r architecture</title>
  <desc id="llmr-arch-desc">LLM-r routes transport-aware LLM action plans through a VST3 plugin, FastAPI server, AbletonOSC, and a Device Bridge Remote Script inside Ableton Live.</desc>
  <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10 z" /></marker></defs>
  <rect x="40" y="75" width="190" height="80" rx="10" fill="none" stroke="black" /><text x="135" y="106" text-anchor="middle" font-size="14">VST3 plug-in</text><text x="135" y="128" text-anchor="middle" font-size="12">primary product UI</text>
  <rect x="40" y="235" width="190" height="85" rx="10" fill="none" stroke="black" /><text x="135" y="266" text-anchor="middle" font-size="14">Companion UIs</text><text x="135" y="288" text-anchor="middle" font-size="12">web UI and PyQt</text><text x="135" y="306" text-anchor="middle" font-size="12">Plan Board</text>
  <rect x="305" y="150" width="210" height="100" rx="10" fill="none" stroke="black" /><text x="410" y="184" text-anchor="middle" font-size="14">FastAPI server</text><text x="410" y="206" text-anchor="middle" font-size="12">planner, capabilities,</text><text x="410" y="224" text-anchor="middle" font-size="12">settings, live state</text>
  <rect x="580" y="50" width="210" height="90" rx="10" fill="none" stroke="black" /><text x="685" y="82" text-anchor="middle" font-size="14">Planner and registry</text><text x="685" y="104" text-anchor="middle" font-size="12">transport-aware typed</text><text x="685" y="122" text-anchor="middle" font-size="12">action plans</text>
  <rect x="580" y="190" width="210" height="90" rx="10" fill="none" stroke="black" /><text x="685" y="222" text-anchor="middle" font-size="14">Executor</text><text x="685" y="244" text-anchor="middle" font-size="12">OSC routing and</text><text x="685" y="262" text-anchor="middle" font-size="12">Device Bridge preflight</text>
  <rect x="845" y="85" width="190" height="85" rx="10" fill="none" stroke="black" /><text x="940" y="116" text-anchor="middle" font-size="14">AbletonOSC</text><text x="940" y="138" text-anchor="middle" font-size="12">UDP loopback</text><text x="940" y="156" text-anchor="middle" font-size="12">127.0.0.1:11000</text>
  <rect x="845" y="235" width="190" height="95" rx="10" fill="none" stroke="black" /><text x="940" y="266" text-anchor="middle" font-size="14">LLMRDeviceBridge</text><text x="940" y="288" text-anchor="middle" font-size="12">Remote Script HTTP</text><text x="940" y="306" text-anchor="middle" font-size="12">inside Ableton Live</text>
  <rect x="580" y="380" width="210" height="80" rx="10" fill="none" stroke="black" /><text x="685" y="410" text-anchor="middle" font-size="14">Smoke testing</text><text x="685" y="432" text-anchor="middle" font-size="12">real Ableton harness</text>
  <line x1="230" y1="115" x2="305" y2="175" stroke="black" marker-end="url(#arrow)" /><line x1="230" y1="278" x2="305" y2="220" stroke="black" marker-end="url(#arrow)" /><line x1="515" y1="180" x2="580" y2="95" stroke="black" marker-end="url(#arrow)" /><line x1="515" y1="220" x2="580" y2="235" stroke="black" marker-end="url(#arrow)" /><line x1="790" y1="215" x2="845" y2="128" stroke="black" marker-end="url(#arrow)" /><line x1="790" y1="255" x2="845" y2="282" stroke="black" marker-end="url(#arrow)" /><line x1="685" y1="280" x2="685" y2="380" stroke="black" marker-end="url(#arrow)" />
</svg>

### Flow chart

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="360" viewBox="0 0 1100 360" role="img" aria-labelledby="llmr-flow-title llmr-flow-desc">
  <title id="llmr-flow-title">LLM-r transport-aware execution flow</title>
  <desc id="llmr-flow-desc">A prompt becomes a typed plan, the plan is preflighted, actions are routed by transport to AbletonOSC or Device Bridge, and Live state/replies are reconciled.</desc>
  <defs><marker id="flowarrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10 z" /></marker></defs>
  <rect x="25" y="145" width="120" height="65" rx="10" fill="none" stroke="black" /><text x="85" y="173" text-anchor="middle" font-size="12">User prompt</text><text x="85" y="191" text-anchor="middle" font-size="12">or command</text>
  <rect x="185" y="145" width="120" height="65" rx="10" fill="none" stroke="black" /><text x="245" y="173" text-anchor="middle" font-size="12">Planner</text><text x="245" y="191" text-anchor="middle" font-size="12">builds plan</text>
  <rect x="345" y="145" width="130" height="65" rx="10" fill="none" stroke="black" /><text x="410" y="173" text-anchor="middle" font-size="12">Validate and</text><text x="410" y="191" text-anchor="middle" font-size="12">preflight</text>
  <rect x="515" y="70" width="130" height="65" rx="10" fill="none" stroke="black" /><text x="580" y="98" text-anchor="middle" font-size="12">OSC action</text><text x="580" y="116" text-anchor="middle" font-size="12">transport</text>
  <rect x="515" y="220" width="130" height="65" rx="10" fill="none" stroke="black" /><text x="580" y="248" text-anchor="middle" font-size="12">Device load</text><text x="580" y="266" text-anchor="middle" font-size="12">transport</text>
  <rect x="710" y="70" width="130" height="65" rx="10" fill="none" stroke="black" /><text x="775" y="98" text-anchor="middle" font-size="12">AbletonOSC</text><text x="775" y="116" text-anchor="middle" font-size="12">mutates Live</text>
  <rect x="710" y="220" width="130" height="65" rx="10" fill="none" stroke="black" /><text x="775" y="248" text-anchor="middle" font-size="12">Bridge resolves</text><text x="775" y="266" text-anchor="middle" font-size="12">and loads</text>
  <rect x="905" y="145" width="150" height="65" rx="10" fill="none" stroke="black" /><text x="980" y="173" text-anchor="middle" font-size="12">Reconcile status</text><text x="980" y="191" text-anchor="middle" font-size="12">and replies</text>
  <line x1="145" y1="177" x2="185" y2="177" stroke="black" marker-end="url(#flowarrow)" /><line x1="305" y1="177" x2="345" y2="177" stroke="black" marker-end="url(#flowarrow)" />
  <path d="M 475 160 L 515 102" fill="none" stroke="black" marker-end="url(#flowarrow)" /><path d="M 475 194 L 515 252" fill="none" stroke="black" marker-end="url(#flowarrow)" />
  <line x1="645" y1="102" x2="710" y2="102" stroke="black" marker-end="url(#flowarrow)" /><line x1="645" y1="252" x2="710" y2="252" stroke="black" marker-end="url(#flowarrow)" />
  <path d="M 840 102 L 905 160" fill="none" stroke="black" marker-end="url(#flowarrow)" /><path d="M 840 252 L 905 194" fill="none" stroke="black" marker-end="url(#flowarrow)" />
</svg>

## Setup and run instructions

General validation/release-facing checks:

```bash
python3 -m pytest -q
PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile gui/pyqt_app.py backend/device_server.py llmr/device_bridge.py llmr/osc_replies.py llmr/device_parameters.py remote_scripts/LLMRDeviceBridge/__init__.py remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py scripts/smoke_test_live_integration.py
./scripts/build_vst3.sh
python3 -m build
git diff --check
```

Real Ableton smoke testing is documented in `docs/ABLETON_SMOKE_TEST.md` and assisted by:

```bash
python3 scripts/smoke_test_live_integration.py
```

## Configuration and environment variables

- Default AbletonOSC target: `127.0.0.1:11000`.
- Default LLMRDeviceBridge target: `127.0.0.1:8788`.
- FastAPI API binds to `127.0.0.1` by default.
- Remote binding to `0.0.0.0` is explicit opt-in and should be documented/security-reviewed when changed.

## Important files and directories

- `llmr/`: Python package source.
- `native/vst3/`: native VST3 implementation.
- `remote_scripts/LLMRDeviceBridge/`: Ableton Live Remote Script.
- `gui/`: PyQt GUI.
- `backend/`: companion backend/device server surface.
- `docs/`: user, release, compatibility, security, capabilities, scenario, and smoke-test docs.
- `scripts/`: build and integration helpers.
- `tests/`: automated Python tests.
- `CLAUDE.md`: Claude compatibility entry point.
- `.github/copilot-instructions.md`: GitHub Copilot compatibility entry point.

## Recent changes

- Added `transport` to the public `Capability` schema and `/api/capabilities` response.
- Updated the generated planner system prompt to include `transport`.
- Replaced OSC-only executor error wording with transport-neutral action execution wording.
- Hardened LLMRDeviceBridge startup, request parsing, browser traversal, and duplicate-port handling.
- Fixed a native VST3 combo-box popup warning path.
- Added Device Bridge transport metadata tests for capability registry, API output, and planner prompt.
- Added smoke-test harness, Device Bridge status/candidate/resolve endpoints, OSC reply listener hooks, recognised reply reconciliation, and allow-listed semantic parameter guardrails.
- Added pre-execution Device Bridge preflight and exact candidate-path resolution for `device_load`.
- Added VST3 ambiguous-candidate picker for Device Bridge `device_load` preflight.
- Changed API default bind host to `127.0.0.1`.
- Added `/api/live/refresh` readback and expanded OSC reply reconciliation.
- Modernised VST3, PyQt, web UI, docs site hero, and screenshot mockup around a darker Plan Board workflow.
- Added Auto-approve controls to VST3 editor, PyQt GUI, PyQt settings, and web UI while preserving dry-run and destructive-action checks.
- Renamed project status from `REPORT.md` to `STATUS.md`.
- Added cross-agent instruction files for Codex, Claude, and GitHub Copilot.
- Bumped release version to `0.6.8` across Python package metadata, VST3 metadata, release docs, and project status.

## Tests and verification status

Previously recorded validation:

- `python3 -m pytest -q` -> 58 tests passed.
- `PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile gui/pyqt_app.py backend/device_server.py llmr/device_bridge.py llmr/osc_replies.py llmr/device_parameters.py remote_scripts/LLMRDeviceBridge/__init__.py remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py scripts/smoke_test_live_integration.py` -> passed.
- `./scripts/build_vst3.sh` -> built `build/vst3/LLM-r.vst3`.
- `python3 -m build` -> built `llm_r-0.6.8.tar.gz` and `llm_r-0.6.8-py3-none-any.whl`.
- Inline web UI script syntax check with `node -e` -> passed.
- `git diff --check` -> passed.
- `python3 -m pytest -q tests/test_api.py tests/test_executor.py` -> 29 tests passed.
- VST3 rebuild after candidate picker flow -> built `build/vst3/LLM-r.vst3`.

Not verified in the previous recorded run:

- real Ableton Live execution with AbletonOSC and LLMRDeviceBridge enabled
- actual Live browser search/load behaviour across different Ableton Live versions and user library contents

No tests were run while creating this documentation-only status normalisation.

## Known issues, risks, and limitations

- Real Ableton Live execution requires manual disposable Live-set validation.
- Actual browser paths and candidate scoring need verification across varied user libraries and plug-in installations.
- Multi-device chain loading remains outside the current capability contract.
- Reply parsing and semantic maps should only expand from verified AbletonOSC/Live readback data.
- Real Ableton execution is not covered by unit tests.

## Pending tasks

- Run the real Ableton smoke-test harness across supported Live versions.
- Validate the VST3 candidate picker in real Ableton sessions with ambiguous browser queries.
- Continue growing safe semantic parameter maps from verified Live readback data only.

## Next steps

1. Run and refine the real Ableton smoke-test harness against multiple Ableton Live versions.
2. Validate the VST3 candidate picker in real Ableton sessions by forcing ambiguous browser queries and confirming the selected path loads correctly.
3. Grow safe semantic parameter maps only from verified Live readback data.
4. Keep release packaging focused on one primary install path: VST3 bundle plus bundled Remote Script, with server/GUI clearly marked as companion tools.

## Longer-term steps

1. Continue strengthening Live-state reconciliation through verified AbletonOSC replies.
2. Preserve VST3-first packaging and make companion surfaces clearly secondary.
3. Expand safe transport-aware capabilities only when AbletonOSC/Device Bridge behaviour is verified.

## Decisions and rationale

- The native VST3 plug-in is the main product surface.
- FastAPI server, web UI, and PyQt GUI are companion surfaces.
- `osc` and `device_bridge` are distinct transports and must remain explicit.
- Device loading belongs inside the Ableton Live Remote Script runtime, not in an external Python process importing Ableton's `Live` API.
- API loopback binding is the default security posture.

---

Last updated: 2026-05-07 00:15
