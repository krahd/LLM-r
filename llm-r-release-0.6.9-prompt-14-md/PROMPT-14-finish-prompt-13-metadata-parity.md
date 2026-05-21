# Prompt 14 — LLM-r 0.6.9 release-candidate correction: finish Prompt 13, remove stale claims, and verify metadata parity

Repository: `krahd/LLM-r`  
Branch: `release/0.6.9`  
Prompt number: **Prompt 14**

You do not have memory of previous prompts. You must read the repository state directly.

Before editing, read:

- `STATUS.md`
- `llmr/app.py`
- `llmr/ableton_osc.py`
- `llmr/planner.py`
- `llmr/plan_summary.py`
- `tests/test_api.py`
- `tests/test_plan_summary.py`

In your final response, begin with:

```text
Completed Prompt 14: finish Prompt 13, remove stale claims, and verify metadata parity
```

## Goal

Finish the remaining release-candidate corrections that appear not to have landed after Prompt 13.

Current observed state on `release/0.6.9`:

1. `STATUS.md` still duplicates these two FastAPI bullets:
   - `AbletonAction` carries a `semantic_args` dict ...
   - `_serialize_action()` is the single serialisation helper ...
2. `STATUS.md` claims an execute parity test exists:
   - `test_execute_plan_response_includes_action_metadata`
   but repository search does not find that test.
3. `/api/execute_batch` still returns `execution_report` but does not return `executed_actions`.
4. `_serialize_action()` exists but is still typed as `-> dict` and has awkward inline formatting for `raw_for_transport`.

Keep this prompt focused. Do not add new UX features.

## Task 1 — Fix `STATUS.md` duplication

In `STATUS.md`, under `### FastAPI server`, remove duplicated bullets.

There should be only one bullet for:

```md
- `AbletonAction` carries a `semantic_args` dict ...
```

and only one bullet for:

```md
- `_serialize_action()` is the single serialisation helper ...
```

Do not rewrite the whole file unless necessary.

## Task 2 — Correct or implement the `/api/execute` metadata parity test

Inspect `tests/test_api.py`.

If `test_execute_plan_response_includes_action_metadata` does not exist, add it.

The test should:

1. Create a `StoredPlan` with one `AbletonAction` containing:
   - `tool=ToolName.fire_clip`
   - `address="/live/clip/fire"`
   - `args=[1, 0]`
   - `semantic_args={"track_index": 1, "clip_index": 0}`
   - `description="Fire clip"`
   - `destructive=False`
   - `transport="osc"`
2. Put the plan in `app_module.store`.
3. Monkeypatch `_run_actions` so no real Ableton/OSC call occurs.
4. Call the TestClient endpoint `POST /api/execute` with:
   - `plan_id`
   - `dry_run=True`
   - `approved=False`
5. Assert `executed_actions[0]` includes all of:

```python
"target_label"
"transport_label"
"transport_plain_label"
"safety_label"
"semantic_args"
"args"
"tool"
"address"
"description"
"destructive"
"transport"
```

6. Assert exact values:

```python
action["semantic_args"] == {"track_index": 1, "clip_index": 0}
action["args"] == [1, 0]
action["target_label"] == "Track 1 · Clip 0"
action["transport_label"] == "AbletonOSC"
action["transport_plain_label"] == "Ableton command"
action["safety_label"] == "Safe"
```

If a similar test already exists, ensure it checks all these fields and has the exact name or update `STATUS.md` to use the actual test name.

## Task 3 — Add `/api/execute_batch` action metadata parity

Update `execute_batch()` in `llmr/app.py`.

It currently returns:

```python
return {
    "executed_count": len(actions),
    "requires_approval": any(a.destructive for a in actions),
    "dry_run": req.dry_run,
    "executed_at": executed_at,
    "execution_report": execution_report,
}
```

Add:

```python
"executed_actions": [_serialize_action(a) for a in actions],
```

Do not remove or rename `execution_report`.

## Task 4 — Add an `/api/execute_batch` metadata test

Add a test in `tests/test_api.py`.

The test should:

1. Use `client.post("/api/execute_batch", json=...)`.
2. Use `dry_run=True`.
3. Use one call:

```python
{
    "tool": "fire_clip",
    "args": {"track_index": 2, "clip_index": 3}
}
```

4. Monkeypatch `_run_actions` so no real Ableton/OSC call occurs.
5. Assert response JSON includes:

```python
payload["executed_actions"][0]["semantic_args"] == {"track_index": 2, "clip_index": 3}
payload["executed_actions"][0]["args"] == [2, 3]
payload["executed_actions"][0]["target_label"] == "Track 2 · Clip 3"
payload["executed_actions"][0]["transport_label"] == "AbletonOSC"
payload["executed_actions"][0]["transport_plain_label"] == "Ableton command"
payload["executed_actions"][0]["safety_label"] == "Safe"
```

6. Assert `execution_report` remains present.

Do not require real Ableton, OSC, Modelito, Ollama, or oMLX.

## Task 5 — Clean `_serialize_action()` typing/style

In `llmr/app.py`, change:

```python
def _serialize_action(action: AbletonAction) -> dict:
```

to:

```python
def _serialize_action(action: AbletonAction) -> dict[str, Any]:
```

Reformat:

```python
raw_for_transport = {"tool": action.tool.value,
                     "transport": transport, "address": action.address}
```

to:

```python
raw_for_transport = {
    "tool": action.tool.value,
    "transport": transport,
    "address": action.address,
}
```

Do not alter behaviour except as required for tests.

## Task 6 — Correct `STATUS.md` test and API claims

After tests pass:

1. Keep the execute parity test claim only if the test actually exists and passes.
2. Add a line saying `/api/execute_batch` now includes `executed_actions` metadata if implemented.
3. Update the full-suite count only after running the full suite.
4. If you did not personally run a command in this prompt, do not claim it as “Last verified in Prompt 14”.
5. Preserve manual validation warnings.

## Validation commands

Run:

```bash
ruff check .
python -m pytest -q tests/test_api.py tests/test_plan_summary.py
python -m pytest -q
git diff --check
```

Do not claim real Ableton, Device Bridge, Ollama, or oMLX validation unless actually performed against real runtimes.

## Final response required format

Begin with:

```text
Completed Prompt 14: finish Prompt 13, remove stale claims, and verify metadata parity
```

Then report:

1. Files changed.
2. Exact fixes made.
3. Tests run and exact results.
4. Whether `STATUS.md` was updated.
5. Remaining limitations or release blockers.
