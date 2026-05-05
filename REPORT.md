# LLM-r Audit Report

Date: 2026-05-05

## Current State

LLM-r is at package version `0.6.7`. The main product surface is the native
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

## Validation

Passed:

- `python3 -m pytest -q` -> 48 tests passed.
- `PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile backend/device_server.py llmr/device_bridge.py remote_scripts/LLMRDeviceBridge/__init__.py remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py`
- `./scripts/build_vst3.sh` -> built `build/vst3/LLM-r.vst3`.
- `python3 -m build` -> built `llm_r-0.6.7.tar.gz` and
  `llm_r-0.6.7-py3-none-any.whl`.
- `git diff --check`

Not verified in this run:

- Real Ableton Live execution with AbletonOSC and LLMRDeviceBridge enabled.
- Actual Live browser search/load behavior across different Ableton Live
  versions and user library contents.

## Residual Risks

- `device_load` depends on a Remote Script running inside Live; if it is not
  enabled, the executor reports a bridge failure.
- Browser search is name-based and intentionally simple. It does not yet expose
  an interactive browse/confirm flow, preset disambiguation, or multi-device
  chain loading.
- The live-state cache remains optimistic for actions sent without OSC replies.
  Readback-dependent workflows still need an OSC reply listener.
- Device parameter changes are index-based. Semantic parameter names and safe
  parameter maps are still future work.
- The HTTP API default host remains `0.0.0.0`; production or shared-network use
  should set `LLMR_API_TOKEN` and bind to loopback unless remote access is
  deliberate.

## Next Steps

1. Add a real Ableton smoke-test checklist or harness that verifies AbletonOSC
   plus LLMRDeviceBridge startup, `device_load`, and a basic OSC action in a
   disposable Live set.
2. Add bridge health/status exposure in the API and VST3 UI so users can see
   whether LLMRDeviceBridge is reachable before executing a plan.
3. Implement an OSC reply listener and reconcile the live-state cache from real
   Ableton responses.
4. Improve device loading with browsable candidates, user confirmation for
   ambiguous matches, preset selection, and clearer plugin/device type handling.
5. Add semantic device parameter mappings for common Live devices and safe
   guardrails for parameter automation.
6. Keep release packaging focused on one primary install path: VST3 bundle plus
   bundled Remote Script, with server/GUI clearly marked as companion tools.
