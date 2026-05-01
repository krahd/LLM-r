# Development Plan

This is the single planning and audit document for the current pre-release LLM-r
codebase. Older roadmap, audit, and patch-plan documents have been removed so
the project has one source of truth.

Current package version: `0.6.2`

## Product Stance

LLM-r has not been released yet. Until the first public release, implementation
quality and a coherent current API matter more than compatibility with older
internal versions. Remove obsolete aliases, outdated docs, and transitional
code instead of preserving behavior that no released user depends on.

Versioning stays below `1.0.0` until the first public release. The previous
`1.5.4` development version was renumbered to `0.5.4` to reflect the current
pre-release status without implying a stable 1.x API.

## Current Baseline

LLM-r currently provides:

- FastAPI server with health, settings, model metadata, capabilities, planning,
  execution, macros, live state, history, and SSE streaming endpoints.
- Modelito-backed planner that asks the configured LLM for a strict JSON plan.
- Runtime capability registry generated from `llmr/ableton_osc.py`.
- Optional assistant prompt guidance in `docs/LLM_ASSISTANT_PROMPT.md`, enabled
  by default and configurable through settings.
- Declarative AbletonOSC tool mapping with argument normalization and validation.
- Safe execution controls: dry-run, destructive-action approval, one-time plan
  execution, per-action execution report.
- Static and runtime macros with API CRUD and persistence.
- Session history and persisted plan/macro/session stores.
- Optimistic live-state cache exposed through `/api/live/*`, updated after
  executed actions.
- Self-contained native VST3 editor with LLM provider/model/endpoint settings,
  prompt entry, plan review, dry-run, destructive-action approval, and direct
  AbletonOSC execution.
- PyQt desktop GUI that can connect to a running server or operate in embedded
  mode, with settings for provider, model, prompt guidance, AbletonOSC, server
  URL, and API token.

## Current Ableton Coverage

Implemented directly through the capability registry:

- Song setup and transport: tempo, play, stop, continue, session record,
  metronome, time signature, global quantization, count-in.
- Track operations: create MIDI/audio track, rename, duplicate, delete, arm,
  volume, mute, solo, pan, send level.
- Session operations: create/rename/delete scenes, create/delete clips, fire
  clips and scenes, stop all clips.
- Clip operations: duplicate clips, duplicate MIDI loops, rename clips, set clip
  colors, launch behavior, loop/start/end markers, and muted state.
- MIDI note basics: request notes, add note lists, clear notes, and remove notes
  by pitch/time range. Timing or velocity edits are represented as remove/add
  operations over a known note range.
- Audio clip properties: gain, transpose/detune, warping toggle, warp mode, RAM
  mode, and marker/loop controls exposed by AbletonOSC.
- Device and parameter basics: request device/parameter values and names, set
  one or more parameter values by index, and delete devices by index.
- Utility: undo and redo.

Known limits:

- No direct note-ID update API is exposed through the current AbletonOSC
  mapping. Humanize, quantize, transpose, and velocity shaping require either
  known note data from LLM-r state or a read/transform/write flow that listens
  for AbletonOSC replies.
- No warp marker CRUD, export, render, resampling, destructive sample-file
  editing, or loudness analysis yet.
- No browser/device loading, preset browsing, plugin-chain construction, rack
  editing, or return/master-specific controls yet.
- Live state is an optimistic cache, not a full bidirectional sync with Ableton
  Live.
- Device parameter writes still require known indexes. Semantic mapping such as
  "set compressor threshold" requires richer parameter readback and naming.

## Source Notes

The current bridge approach is based on using Ableton Live Remote Scripts and
AbletonOSC as the DAW control surface. Important references:

- Ableton Help Center: controlling Live using Max for Live.
- Ableton Help Center: installing third-party remote scripts.
- AbletonOSC repository: https://github.com/ideoforms/AbletonOSC
- AbletonOSC paper / Zenodo DOI: https://zenodo.org/doi/10.5281/zenodo.11189234

## Prioritized Work

1. **Real Ableton integration harness**
   - Add a mocked OSC server contract suite.
   - Add an optional real Live + AbletonOSC test project for smoke tests.
   - Verify command side effects instead of only validating action serialization.

2. **State reconciliation**
   - Replace the optimistic-only live-state model with read-backed snapshots
     where AbletonOSC exposes reads.
   - Add refresh and cache invalidation paths.
   - Preserve track/scene/clip identity when indexes shift.

3. **Capability expansion for core workflows**
   - Track reorder, color, routing, monitoring, returns, and master controls.
   - Clip follow actions, arrangement clips, and richer clip readback.
   - Device enable/bypass, list/load/reorder, racks, and semantic parameter maps.
   - Browser lookup and loading for instruments, effects, samples, and presets.

4. **MIDI and audio editing**
   - Add an OSC reply listener for `midi_notes_get` and device/clip queries.
   - Add note-ID update flows when the bridge exposes IDs.
   - Transformations: quantize, humanize, transpose, velocity shaping, legato,
     chord/rhythm generation.
   - Extend AbletonOSC or ship a companion Remote Script for warp marker CRUD and
     arrangement audio clip insertion.

5. **Planner and plan model**
   - Add structured preconditions and expected effects to plans.
   - Add staged plans for ambiguous, risky, or long-running workflows.
   - Add capability retrieval by domain when the tool catalog grows too large
     for one prompt.

6. **Safety and transactions**
   - Add finer-grained safety levels beyond `safe` and `confirm`.
   - Add operation grouping and rollback/undo hints.
   - Add policy controls for live performance mode, studio mode, and destructive
     project-level operations.

7. **Desktop and web UX**
   - Capability explorer and live-state browser.
   - Plan diff/review panel before execution.
   - Macro editor with parameterized macro templates.
   - Streaming planner output and execution progress.

8. **Modelito integration cleanup**
   - Once Modelito exposes stable normalized model-list and metadata contracts,
     remove local normalization fallback logic from `llmr/modelito_adapter.py`.
   - Surface provider/model contract errors clearly instead of inferring fields.

## Definition Of Done For First Public Release

- README and docs describe exactly the shipped behavior.
- No obsolete plan/audit docs remain outside this file.
- Current tests pass locally without Ableton Live.
- Optional integration tests document the expected AbletonOSC setup.
- GUI and API expose the same runtime settings.
- Unsupported musical requests are handled honestly by the planner prompt.
- Destructive operations are gated and dry-runnable.
- License, package metadata, and release instructions are accurate.
