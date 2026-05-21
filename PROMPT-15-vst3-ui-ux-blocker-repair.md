# Prompt 15 — LLM-r 0.6.9 VST3 UI/UX blocker repair and first-use smoke path

Repository: `krahd/LLM-r`  
Branch: `release/0.6.9`  
Prompt number: **Prompt 15**

You do not have memory of previous prompts. You must read the repository state directly.

Before editing, read:

- `STATUS.md`
- `README.md`
- `docs/USER_MANUAL.md`
- `docs/GUI-PLUGIN.md`
- `native/vst3/llmr_vst3_plugin.cpp`
- any VST3/JUCE UI helper files
- any VST3 build scripts
- any tests or scripts that validate native UI/build behaviour

In your final response, begin with:

```text
Completed Prompt 15: VST3 UI/UX blocker repair and first-use smoke path
```

## Context

Manual testing of the `0.6.9` VST3 in Ableton found major UI/UX blockers.

The plug-in opened, but the user could not test functionality because the VST3 interface is confusing and renders poorly.

Observed problems:

1. Main window renders poorly.
2. Button text is not centred.
3. It is not clear how to use the plug-in.
4. Help lacks screenshots or useful first-use guidance.
5. The Basic / Advanced Settings boundary is confusing.
6. In Basic Settings, text is truncated.
7. Provider/model pull-downs require clicking specifically on arrows instead of accepting clicks on the visible name/field.
8. Provider/model names can be edited instead of behaving as non-editable selectors.
9. Available models do not update when the provider changes.
10. Advanced Settings page is confusing.
11. Advanced Settings menu/drop-down controls have the same arrow-only click problem.
12. Downloadable model selector has the same arrow-only click problem.
13. Bridge check says the server is not reachable but offers no recovery action.
14. Two-finger trackpad scroll moves content horizontally a little.
15. Scrollbars remain visible even when the plug-in window is enlarged and no scrolling should be required.
16. Functionality could not be tested because the UI blocked basic use.

This is a release blocker for `0.6.9`.

## Goal

Make the VST3 primary surface usable enough for first-run testing in Ableton.

Do **not** attempt a full redesign. Implement a conservative repair pass that makes the plug-in legible, predictable, and testable.

The target is:

> A first-time user can open the VST3, understand the flow, configure provider/model enough to plan, understand Bridge status, and attempt a dry-run without fighting broken controls.

## Required product decision

Update `STATUS.md` immediately or at the end of the prompt to mark VST3 UI/UX as a release blocker until fixed and manually retested.

Do not leave `STATUS.md` implying VST3 validation is effectively complete.

## Task 1 — Fix basic rendering and layout

Inspect the VST3 editor layout code.

Fix:

1. Button text alignment.
   - Button labels must be centred vertically and horizontally.
   - No clipped button text at normal/default window size.

2. Text truncation in Basic Settings.
   - Labels and field values must fit at default size.
   - If space is limited, shorten labels rather than clipping values.
   - Prefer clear labels:
     - `Provider`
     - `Model`
     - `Server`
     - `Bridge`
     - `Dry run`
     - `Auto-approve`

3. Main window default size.
   - Increase default plug-in editor size if needed.
   - Choose a size that avoids unnecessary scrollbars for the main workflow.
   - Do not rely on tiny layouts.

4. Scrollbars.
   - Hide scrollbars when content fits.
   - Avoid permanent scrollbars after enlarging the window.
   - Prevent accidental horizontal scrolling from two-finger trackpad gestures unless horizontal content genuinely overflows.

5. Main workflow clarity.
   - Make the primary visible flow obvious:
     1. Configure provider/model
     2. Write prompt
     3. Plan
     4. Review plan/details
     5. Dry-run
     6. Execute only when ready

## Task 2 — Fix combo boxes / drop-downs

All provider/model/runtime/drop-down controls in the VST3 must behave like normal selectors.

Fix:

1. User can open the menu by clicking anywhere on the visible field, not only the arrow.
2. Provider/model names are not directly editable unless there is a deliberate `Custom…` option.
3. If custom model input is required, separate it clearly:
   - Provider selector: non-editable combo box.
   - Model selector: non-editable combo box where model list is known.
   - Custom model field: explicit text field labelled `Custom model`.
4. The model list must refresh when provider changes.
5. Downloadable model selector must use the same non-editable selector behaviour.
6. Advanced Settings selectors must use the same interaction model as Basic Settings.

## Task 3 — Repair provider/model dependency

When the provider changes:

1. Clear stale available-model list.
2. Fetch or compute available models for the selected provider.
3. Repopulate model selector.
4. Preserve current model only if it is valid for the new provider.
5. If model discovery fails, show a clear inline message:
   - `Could not list models for this provider. Enter a custom model or use PyQt Advanced Settings.`
6. Do not silently keep models from the previous provider.

## Task 4 — Simplify Basic vs Advanced Settings

Clarify the boundary.

### Basic Settings should contain only:

- Provider
- Model
- Optional custom model
- Server/API base URL if needed
- Dry-run default
- Save / Cancel / Test readiness

### Advanced Settings should contain:

- AbletonOSC host/port
- Device Bridge host/port
- Ollama controls
- oMLX note/status if present
- API token/server auth
- Debug/logging
- Runtime management links or actions

Add short explanatory copy:

```text
Basic Settings chooses the model used for planning.
Advanced Settings controls Ableton, Bridge, local runtimes, and diagnostics.
```

Avoid dense paragraphs.

## Task 5 — Bridge failure recovery

Current issue:

> Check Bridge says server is not reachable but offers no action.

Fix Bridge status UI.

When Bridge is unreachable, show:

1. Status:
   - `Device Bridge not reachable`

2. Likely cause:
   - `The Ableton Remote Script may not be installed, enabled, or running.`

3. Actions:
   - `Open setup help`
   - `Copy install path`
   - `Recheck`
   - If the app has an install helper, expose it.
   - If not, do not pretend it can install automatically.

4. Required setup text:
   - Where the Remote Script folder should be placed.
   - How to enable/select it in Ableton preferences.
   - That Ableton may need restart/rescan.

Do not make Device Bridge mandatory for all plans, but make its status understandable.

## Task 6 — Add first-use Help view

Add or improve a Help tab/dialog inside the VST3.

Minimum content:

1. “First dry-run in 60 seconds”
   - Step 1: keep Dry run enabled
   - Step 2: choose provider/model
   - Step 3: enter a simple prompt
   - Step 4: click Plan
   - Step 5: review Details
   - Step 6: click Execute while Dry run is still enabled

2. Example safe prompts:
   - `Set tempo to 120 BPM`
   - `Create a MIDI track called Drums`
   - `Load Drum Rack on the selected track`  
     Mark this as requiring Device Bridge.

3. Safety explanation:
   - Dry run does not mutate the Live set.
   - Live execution requires Dry run off.
   - Destructive actions require explicit approval.

4. Bridge explanation:
   - AbletonOSC handles core commands.
   - Device Bridge handles browser/device loading.
   - Device Bridge requires its Remote Script to be installed and reachable.

Screenshots are desirable but not required for this prompt unless the repo already has a screenshot system. If screenshots are not added, update docs to mark them as future work rather than claiming they exist.

## Task 7 — Add visible readiness guidance in VST3

If full `/api/readiness` parity is too large for this prompt, add a minimal readiness strip or status area:

- Model: configured / missing
- AbletonOSC: reachable / not checked / unreachable
- Device Bridge: reachable / unreachable / optional
- Dry run: on / off

Each failed state should have a next action.

Example:

```text
Model missing — open Basic Settings and choose a provider/model.
Bridge unreachable — open Help → Device Bridge setup.
AbletonOSC not checked — click Recheck.
```

## Task 8 — Update documentation truthfully

Update:

- `STATUS.md`
- `README.md`
- `docs/USER_MANUAL.md`
- `docs/GUI-PLUGIN.md` if present

Required changes:

1. Mark VST3 UI/UX as a release blocker until manually retested.
2. Document the repaired first-use flow.
3. Document that Basic Settings is only model/provider setup.
4. Document that Advanced Settings is for Ableton/local runtime/diagnostics.
5. Document Bridge troubleshooting.
6. Do not claim screenshots exist unless added.
7. Do not claim VST3 readiness parity unless implemented.

## Task 9 — Add low-risk tests if possible

If the VST3 UI code has no automated UI test framework, do not add fragile GUI tests.

Instead:

1. Add or update compile/build validation only.
2. Add small pure helper tests if you extract layout/model/provider helper logic.
3. Keep native build working.

## Validation commands

Run:

```bash
ruff check .
python -m pytest -q
git diff --check
```

If on macOS and feasible, run:

```bash
./scripts/build_vst3.sh
bash scripts/test_install_vst3_and_open.sh "$HOME/Library/Audio/Plug-Ins/VST3"
```

After building, manually open the VST3 in Ableton and verify:

1. Main window readable at default size.
2. Button text centred.
3. Basic Settings text not truncated.
4. Drop-downs open by clicking the field, not only the arrow.
5. Drop-downs are not editable unless explicitly custom.
6. Model list refreshes when provider changes.
7. Advanced Settings is understandable.
8. Bridge failure gives next actions.
9. No unwanted horizontal two-finger scrolling.
10. Scrollbars disappear when content fits.
11. A dry-run can be attempted from first-use instructions.

Do not claim real manual validation was completed unless you actually did it.

## Final response required format

Begin with:

```text
Completed Prompt 15: VST3 UI/UX blocker repair and first-use smoke path
```

Then report:

1. Files changed.
2. Exact UI/UX fixes made.
3. Tests/build commands run and exact results.
4. Manual Ableton/VST3 checks performed or still required.
5. Whether `STATUS.md` was updated.
6. Remaining release blockers.
