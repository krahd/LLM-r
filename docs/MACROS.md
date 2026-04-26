# Macro documentation for contributors

## How to add a new macro

1. Edit `llmr/macros.py`.
2. Add a new entry to `_STATIC_MACROS` with a unique name and a list of `PlannedToolCall` actions.
3. Example:

```python
_STATIC_MACROS["my_macro"] = [
    PlannedToolCall(tool=ToolName.set_tempo, args={"bpm": 100}),
    PlannedToolCall(tool=ToolName.fire_scene, args={"scene_index": 1}),
]
```

4. Test your macro using the API:
   - `GET /api/macros` to list macros
   - `POST /api/plan_macro` with `{ "name": "my_macro" }`

## Future: Editable macros
- The macro system is designed for runtime editing in the future.
- Contributions for runtime macro editing are welcome!
