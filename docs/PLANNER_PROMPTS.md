# Planner prompt architecture

LLM-r uses a layered planner prompt rather than a single inline system prompt. The planner prompt is assembled from packaged Markdown sections under `llmr/planner_prompts/`, then augmented with the current executable tool catalogue, available Ableton context, and the optional user-configured extra planner guidance.

## Goals

- Make the planner behave like a DAW production planner, not a generic tool selector.
- Give smaller local models stricter output, duration, and musical constraints.
- Preserve the explicit JSON action-plan contract used by the API, GUI, web UI, and VST3 plug-in.
- Keep user-editable style guidance separate from the core schema/tool contract.

## Packaged sections

- `core_planner.md` — JSON contract, tool-use rules, safety rules.
- `ableton_context.md` — Session View, Arrangement View, index, and duration semantics.
- `composition_contract.md` — bounded MIDI generation and long-form musical structure guidance.
- `drums.md` — drum MIDI pitches and style guidance.
- `piano.md` — harmony, ballad, and piano-generation guidance.
- `effects_and_automation.md` — device/effect planning and truthful automation fallback rules.

## Prompt assembly

`llmr.prompts.compose_planner_prompt()` assembles:

1. packaged sections;
2. executable capabilities from `llmr.ableton_osc.capabilities()`;
3. runtime Ableton context when available;
4. optional extra guidance from `docs/LLM_ASSISTANT_PROMPT.md` or a user-selected prompt file.

The VST3/System Prompt editor should edit only the optional guidance layer by default. The packaged core prompt is part of the product contract and should remain read-only unless an explicit expert/developer mode is added.

## Repair pass

If the first model response cannot be parsed into a useful plan, `IntentPlanner` performs one repair call using the same prompt stack plus the invalid output. This is deliberately bounded to one retry to avoid UI stalls and runaway local-model loops.

## Known limitation

The current tool set still lacks true automation-envelope and Arrangement insertion tools. The planner prompt therefore instructs the model to avoid pretending that static parameter-setting is automation. Proper automation should be implemented as executable tools in a later release rather than only as prompt wording.
