# Prompt 12 — LLM-r 0.6.9 release-candidate polish: semantic action metadata, execution-response parity, and readiness/doc truthfulness

You are continuing work on `krahd/LLM-r`, branch `release/0.6.9`.

IMPORTANT:
- Start by reading `STATUS.md`.
- Mention explicitly in your response that you are working on **Prompt 12**.
- Do not assume memory from any previous prompt.
- Inspect the repository before editing.
- Keep changes focused and release-candidate appropriate.
- Do not remove existing functionality.
- Run the full relevant test suite before reporting completion.
- Update `STATUS.md` only after verifying tests.

## Context

The current branch is close to `0.6.9`, but one important UX correctness issue remains:

The planner starts with semantic dict args such as:

```json
{"track_index": 1, "clip_index": 0, "device_name": "Drum Rack"}
```

But `AbletonAction.args` stores only the positional OSC/device-bridge argument list. As a result, `_serialize_plan()` often cannot infer useful target labels and falls back to `"General"`.

This hurts the Plan Board and professional UX: users need to see what each action affects.

There is also a smaller parity issue: `/api/execute` returns `executed_actions` without the same user-facing metadata used by `/api/plan`.

## Tasks

### 1. Preserve semantic action arguments

Implement one of these two approaches. Prefer the first if clean:

#### Preferred approach

Add an optional semantic/original args field to `AbletonAction`, for example:

```python
@dataclass
class AbletonAction:
    tool: ToolName
    address: str
    args: list[Any]
    description: str
    destructive: bool = False
    transport: str = "osc"
    semantic_args: dict[str, Any] = field(default_factory=dict)
```

Then update `AbletonOSCClient.to_action(...)` so every generated action preserves the original `PlannedToolCall.args` dict as `semantic_args`.

Also update:
- plan persistence save/load
- tests that construct `AbletonAction`
- any direct `AbletonAction(...)` construction sites

#### Alternative approach

If changing `AbletonAction` is too invasive, preserve semantic args in `StoredPlan` or a parallel action metadata structure. However, avoid fragile index-only coupling if possible.

### 2. Use semantic args for display metadata

Update `_serialize_plan()` so:

- `target_label` is derived from `semantic_args` when available.
- fallback remains current positional `args` behaviour.
- `planned_actions` includes both:
  - `args`: existing executable positional args, unchanged
  - `semantic_args`: semantic dict args for UI/debugging, when available

For example:

```json
{
  "tool": "fire_clip",
  "args": [1, 0],
  "semantic_args": {"track_index": 1, "clip_index": 0},
  "target_label": "Track 1 · Clip 0"
}
```

Do not break existing clients expecting `args`.

### 3. Create a shared action serialiser

Avoid duplicating plan/action metadata.

Add a helper in `llmr/app.py`, for example:

```python
def _serialize_action(action: AbletonAction) -> dict[str, Any]:
    ...
```

Use it in:

- `_serialize_plan()`
- `/api/execute` response
- anywhere else that emits action payloads and should share display metadata

The serialised action should include:

- `tool`
- `address`
- `args`
- `semantic_args`
- `description`
- `destructive`
- `transport`
- `target_label`
- `transport_label`
- `transport_plain_label`
- `safety_label`

### 4. Add tests for semantic target labels

Extend `tests/test_plan_summary.py` or add a new focused test file.

Required tests:

1. `fire_clip` action with semantic args:

```python
semantic_args={"track_index": 1, "clip_index": 0}
```

must serialise to:

```python
"target_label" == "Track 1 · Clip 0"
```

2. `device_load` action with semantic args:

```python
semantic_args={"track_index": 2, "device_name": "Drum Rack"}
```

must serialise to a target label containing both:

```python
"Track 2"
"Device: Drum Rack"
```

3. Persist/load roundtrip must preserve `semantic_args`.

4. `/api/execute` response must include the same action metadata fields as plan serialisation.

### 5. Clarify cloud credential readiness truth

Audit how cloud API keys are actually configured.

Current readiness checks environment variables directly:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `COHERE_API_KEY`
- `MISTRAL_API_KEY`

But the web UI copy says PyQt Advanced Settings handles API keys.

Determine which is true:

#### If API keys are environment-only for 0.6.9

Update docs/UI copy to say:

- cloud provider API keys are read from environment variables;
- Basic Settings only changes provider/model;
- PyQt Advanced Settings does not persist cloud API keys unless it actually does.

#### If PyQt does persist API keys

Update `compute_readiness()` so it checks the same source Modelito/LLM-r actually uses.

Do not invent a half-implemented secret store for this prompt unless it is already present.

### 6. Update STATUS.md

After tests pass, update `STATUS.md`:

- Change “Last verified in Prompt 11” entries to Prompt 12 where applicable.
- Add a note that plan/run action serialisation now preserves semantic args for clearer target labels.
- Keep the manual validation list intact.
- Keep browser-level E2E listed as not automated unless you actually add such tests.
- Preserve the existing concise release-candidate structure.

### 7. Run verification

Run:

```bash
ruff check .
python -m pytest -q
git diff --check
```

If available and fast enough on your machine, also run:

```bash
./scripts/build_vst3.sh
bash scripts/test_install_vst3_and_open.sh "$HOME/Library/Audio/Plug-Ins/VST3"
```

Do not claim manual Ableton, Device Bridge, Ollama, or oMLX validation unless you actually performed those against real runtimes.

## Expected final response

Mention **Prompt 12**.

Report:

1. Files changed.
2. What was fixed.
3. Tests run and exact result.
4. Any remaining limitations.
5. Whether `STATUS.md` was updated.

Keep the response factual and concise.
