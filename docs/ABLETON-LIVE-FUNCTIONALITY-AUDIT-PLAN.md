# LLM-r Audit & Implementation Plan for Broad Ableton Live Coverage

_Date: April 27, 2026_

## 1) Executive summary

LLM-r is currently a **solid minimal bridge**: it can generate action plans from prompts, persist plans/sessions/macros, and execute a **small set of OSC actions** safely (approval on destructive actions, dry-run support). The platform foundation is good, but present control surface is far from full Ableton Live coverage.

Today, LLM-r mostly handles:
- Track creation (MIDI/audio)
- Tempo
- Clip/scene launch + stop all clips
- Basic mixer controls (volume/mute/solo/arm)

To approach "full Ableton Live functionality surface", LLM-r needs:
1. A significantly expanded **capability schema** and tool catalog.
2. Bidirectional state sync and richer introspection (not only fire-and-forget commands).
3. Domain-specific planners (session, arrangement, devices, notes, automation).
4. Strong validation/authorization guardrails for high-impact operations.
5. A staged roadmap with acceptance tests and compatibility policy.

## 2) Current-state audit

## 2.1 Architecture snapshot

- API server via FastAPI (`llmr/app.py`).
- Planner + plan store (`llmr/planner.py`) with TTL pruning and persistence.
- OSC adapter (`llmr/ableton_osc.py`) that maps abstract tools to OSC addresses.
- Static + runtime macros (`llmr/macros.py`) with JSON persistence.
- Session/history persistence (`llmr/sessions.py`).
- Model provider abstraction via Modelito (`llmr/modelito_adapter.py`).

### Strengths
- Clear separation of concerns (API, planner, transport, storage).
- Good safety primitives (dry-run, approval gates, one-time execution semantics).
- Reasonable persistence for plans/macros/sessions.
- Test suite for core planner/API/model adapter flows.

### Constraints
- Small tool enum and capability map.
- No explicit domain model of Live set state (tracks/devices/clips/arrangement graph).
- Limited command argument validation beyond type coercion.
- No versioned compatibility layer for differing AbletonOSC/Live capabilities.
- No contract tests against a running Live+AblentonOSC instance.

## 2.2 Functional coverage matrix (high-level)

Legend:
- **Implemented** = directly available through current tool set.
- **Partial** = some support exists, but narrow/incomplete.
- **Missing** = no direct support today.

| Ableton Live surface | State |
|---|---|
| Transport (play/stop/continue/record/metronome/punch/count-in) | Missing |
| Tempo/time signature/global quantization/groove | Partial (tempo only) |
| Session view scenes/clips launching and stop | Partial |
| Clip editing (loop, warp, start/end, envelopes, transpose/gain) | Missing |
| MIDI note editing (create/read/update/delete notes) | Missing |
| Arrangement operations (locators, arrangement clips, automation lanes) | Missing |
| Track lifecycle (create/delete/duplicate/rename/reorder/freeze) | Partial (create only) |
| Mixer controls (volume/pan/sends/crossfader/returns/master) | Partial (volume/mute/solo only) |
| Devices (list/load/delete/reorder/enable/browse presets) | Missing |
| Device parameters (read/write, modulation, macros) | Missing |
| Racks/chains/macros | Missing |
| Browser integration (instruments/effects/samples loading) | Missing |
| I/O routing (audio/midi in/out, monitor, arm modes) | Missing |
| Clip/track color/name metadata operations | Missing |
| Capture/resampling/export/render | Missing |
| Undo/redo and transactional batching | Missing |
| Query/introspection endpoints for current Live set state | Missing |
| Follow actions/chance/probability/launch modes | Missing |
| User library/template operations | Missing |

## 2.3 Code-level findings and implications

1. `ToolName` currently defines 10 actions only. This tightly limits planner expressiveness and macro utility.
2. `AbletonOSCClient.to_action` is a simple if-chain; this will become brittle at scale and hard to version.
3. Planner prompt hardcodes available tools in a static string; high risk of drift as tools expand.
4. `execute_plan` sends sequential OSC calls but has no retry semantics, command result capture, or per-action status.
5. Current API is action-centric, not state-centric (few read APIs), which makes advanced planning unreliable.
6. Tests validate in-process behavior, but there is no integration harness that verifies actual Live-side effect.

## 3) Target capability model

Define a versioned tool taxonomy grouped by domain. Each tool should include:
- `name`, `domain`, `description`
- strict JSON schema for args
- safety level (`safe`, `confirm`, `blocked_without_flag`)
- idempotency hints
- minimum Live/AbletonOSC compatibility info

Proposed domains:
- `song`: transport, tempo, quantization, timeline, locators
- `session`: scenes, clip slots, launch settings
- `arrangement`: arrangement clips and automation operations
- `tracks`: lifecycle, grouping, routing, monitoring, mixer
- `devices`: enumerate/load/remove/reorder/enable
- `parameters`: read/write/automate device params
- `midi`: note CRUD and transformations
- `audio`: warp and clip audio properties where available
- `browser`: content lookup and load actions
- `project`: save, collect-all-and-save, export/render (gated)
- `utility`: undo/redo, selection, diagnostics

## 4) Implementation roadmap (phased)

## Phase 0 — Foundation hardening (1–2 weeks)

- Replace hardcoded planner tool list with generated capability prompt from registry.
- Refactor OSC mapping into a declarative registry (`tool -> address builder + validator + safety`).
- Add per-action validation errors before execution.
- Introduce action execution report structure (success/failure per step).
- Expand unit tests for validation and serialization edge cases.

**Exit criteria**
- Zero prompt-tool drift.
- Deterministic validation errors for malformed calls.
- Backward compatible existing API behavior.

## Phase 1 — Read model & introspection (2–4 weeks)

- Add Live state query endpoints and internal state snapshots (tracks/scenes/clips/devices/parameters).
- Add cache + invalidation strategy for frequent reads.
- Add API endpoints such as:
  - `GET /api/live/song`
  - `GET /api/live/tracks`
  - `GET /api/live/tracks/{id}/devices`
  - `GET /api/live/tracks/{id}/clips`
- Introduce typed read schemas with pagination for large sets.

**Exit criteria**
- Planner can inspect current set before proposing actions.
- UI can render a browsable model of the live set.

## Phase 2 — Core parity expansion (4–8 weeks)

Implement broad control primitives likely needed in most real workflows:
- Transport and timeline controls.
- Extended track operations (rename/delete/duplicate/reorder/freeze/returns/master).
- Mixer depth (pan/sends/crossfader).
- Scene/clip lifecycle ops (create/delete/duplicate, launch quantization, names/colors).
- Device list and parameter read/write for common devices.

**Exit criteria**
- End-to-end scenarios: sketch, arrange, mix-prep, live-performance prep.
- >100 stable capabilities with docs + tests.

## Phase 3 — MIDI/audio editing surface (6–10 weeks)

- MIDI note CRUD APIs and transformations (transpose, quantize, humanize, velocity shaping).
- Clip loop/warp markers where exposed.
- Arrangement clip editing and automation point editing (where API supports).
- Bulk-edit transactional operations with rollback strategy.

**Exit criteria**
- User can describe compositional edits in natural language and inspect deterministic plan diffs.

## Phase 4 — Safety, transactions, and policy engine (2–4 weeks)

- Multi-tier approvals by risk category.
- Dry-run simulation with predicted impact summary.
- Optional sandbox mode (disallow destructive/project-level ops).
- Undo integration and explicit confirmation UX.

**Exit criteria**
- Production-safe execution posture for performance and studio sessions.

## Phase 5 — Productization & UX (4–8 weeks, parallelizable)

- Web GUI/desktop improvements: capability explorer, state browser, plan diff, approval panels.
- Macro editor with parameterized templates and variables.
- Session memory and reusable workflows.
- Observability dashboard (latency, failure rates, command audit log).

**Exit criteria**
- Non-technical musician can safely execute common workflows end-to-end.

## 5) Recommended API evolution

- Keep current endpoints but add `/api/v2/...` for expanded surface.
- Add structured plan format with optional conditions:
  - preconditions (e.g., "track exists")
  - expected effects
  - rollback hints
- Add batch execution endpoint:
  - `POST /api/execute_batch` returning per-action statuses.
- Add capability filtering:
  - by domain, risk level, Live version, controller profile.

## 6) Testing strategy for full-surface growth

1. **Unit tests**
   - Registry mapping, validation, safety gating.
2. **Contract tests**
   - Golden JSON contracts for each endpoint and tool schema.
3. **Integration tests**
   - Against mocked OSC server and, separately, a real AbletonOSC test project.
4. **Scenario tests**
   - "Build drum sketch", "Prepare live set", "Mixdown prep".
5. **Resilience tests**
   - Missing tracks/devices, partial failures, rate spikes, reconnect behavior.
6. **Security tests**
   - Auth coverage, replay prevention for destructive commands, audit integrity.

## 7) Documentation backlog

Create or expand:
- `docs/CAPABILITIES.md` (machine+human readable catalog)
- `docs/LIVE-STATE-MODEL.md` (entity model and IDs)
- `docs/SAFETY-POLICY.md` (risk tiers + approvals)
- `docs/COMPATIBILITY.md` (Live/AbletonOSC/version matrix)
- `docs/SCENARIOS.md` (validated end-to-end recipes)

## 8) Prioritized backlog (first 10 implementation tickets)

1. Capability registry abstraction + generated planner prompt.
2. Replace if-chain in `to_action` with declarative mapping table.
3. Add strict per-tool arg validation and error contracts.
4. Add transport tools (play/stop/record/metronome).
5. Add track rename/delete/duplicate tools.
6. Add pan + send controls.
7. Add scene create/delete/rename + clip slot create/delete.
8. Add device enumeration endpoint.
9. Add parameter set/get endpoint.
10. Add real integration test harness with sample Live set.

## 9) Risks and mitigations

- **API capability mismatch across Live/AbletonOSC versions**
  - Mitigation: version handshake + capability negotiation endpoint.
- **Unsafe high-impact commands**
  - Mitigation: policy engine + explicit approvals + dry-run diffs.
- **Planner hallucination at large tool counts**
  - Mitigation: schema-constrained generation + tool retrieval by domain.
- **Performance degradation with deep introspection**
  - Mitigation: scoped reads + caching + selective refresh.

## 10) Definition of done for "broad Ableton surface coverage"

A milestone can be considered "broad coverage" (not absolute total parity) when:
- 80%+ of commonly used workflows (compose, arrange, mix prep, live prep) are executable through documented tools.
- All high-risk operations are gated by policy.
- Planner produces schema-valid calls at high reliability on benchmark prompts.
- Integration suite passes against at least one pinned Ableton Live + AbletonOSC setup.
- Docs include capability catalog, compatibility matrix, and scenario recipes.

---

This plan intentionally targets **broad practical parity** rather than promising unrestricted control of every internal Live feature. The architecture should remain modular so unsupported areas can be added incrementally without destabilizing core workflow reliability.
