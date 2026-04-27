# Macro documentation for contributors

## Built-in and runtime macros

LLM-r supports two macro sources:
- **Static macros** in `llmr/macros.py` (`_STATIC_MACROS`)
- **Runtime macros** persisted to `LLMR_MACRO_STORE_PATH` (default `.llmr/macros.json`)

## Runtime macro API

- `GET /api/macros` → list names
- `GET /api/macros/{name}` → fetch one macro (includes `source`: `static`/`runtime`)
- `POST /api/macros` → create runtime macro
- `PUT /api/macros/{name}` → update runtime macro
- `DELETE /api/macros/{name}` → delete runtime macro

When `LLMR_API_TOKEN` is set, create/update/delete endpoints require bearer auth.

## Static macro contribution flow

1. Edit `llmr/macros.py`.
2. Add a new entry to `_STATIC_MACROS` with a unique name and a list of `PlannedToolCall` actions.
3. Example:

```python
_STATIC_MACROS["my_macro"] = [
    PlannedToolCall(tool=ToolName.set_tempo, args={"bpm": 100}),
    PlannedToolCall(tool=ToolName.fire_scene, args={"scene_index": 1}),
]
```

4. Test via:
   - `GET /api/macros`
   - `POST /api/plan_macro` with `{ "name": "my_macro" }`
