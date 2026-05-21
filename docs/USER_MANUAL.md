# LLM-r User Manual

LLM-r is a VST3 assistant for Ableton Live. You type a production request, LLM-r asks your selected language model for an executable plan, shows you the plan in plain language, and can send the resulting commands to Ableton Live through AbletonOSC and the optional LLM-r Device Bridge.

The VST3 plug-in is the primary product surface. The PyQt GUI, web UI, and FastAPI server are companion surfaces for setup, control, debugging, automation, and headless workflows.

## Requirements

- macOS with Ableton Live
- AbletonOSC installed and running in Live
- LLMRDeviceBridge installed and enabled in Live for device/browser loading
- The LLM-r VST3 plug-in installed in your VST3 folder
- One model provider:
  - OpenAI, Anthropic, or Google with an API key
  - Ollama or oMLX running locally with at least one downloaded model
  - See [MODELITO.md](MODELITO.md) for provider setup

LLM-r uses Modelito as a provider abstraction layer:

```
LLM-r → Modelito → provider/runtime
```

You configure the provider and model in LLM-r; Modelito handles the connection to the underlying runtime.

## First Run

### VST3 first run (primary surface)

1. Open Ableton Live.
2. Add the LLM-r VST3 plug-in to any track.
3. Open the plug-in window.
4. Click **Settings**.
5. Choose a provider and model.
  - Provider picker options in VST3: `openai`, `anthropic`, `google`, `ollama`, `omlx`, `custom`.
  - Provider and model controls are selectors, not editable text fields.
  - Use **Custom model** only for unlisted model IDs or the `custom` provider.
  - For `omlx`, select the provider/model in VST3 and use the PyQt companion for local runtime management tasks.
6. Keep **Preview only; do not change Live** enabled and click **Test readiness**.
7. For cloud providers, open **Settings** and enter the API key.
8. Confirm the AbletonOSC host and port. The default is `127.0.0.1:11000`.
9. If you want device loading:
  - in Live's Browser, right-click **User Library** and choose **Show in Finder**
  - in LLM-r Settings, click **Choose Ableton User Library...** and select that folder
  - click **Install / Reinstall Bridge**
  - restart Live
  - in Live Settings -> Link, Tempo & MIDI -> Control Surface, choose `LLMR_Bridge` if it appears
  - click **Recheck**
  - if it does not appear, check Live `Log.txt` for `LLMR`, `Bridge`, `RemoteScriptError`, `Traceback`, or `ImportError`
10. Click **Save**.
11. Run one safe prompt, click **Run**, and review **Result** and **Details**. Turn Preview only off in Settings when you are ready for live execution.

### PyQt first-run wizard (companion surface)

When you open the PyQt GUI for the first time, LLM-r shows a guided wizard.

1. Choose a source: cloud (`openai`, `anthropic`, `google`), local (`ollama`, `omlx`), or configure later.
2. For cloud providers:
  - choose or type a model ID
  - optionally paste an API key
  - note that planning will fail until a valid API key is configured
3. For local providers:
  - **Install**, **Start Service**, and **Refresh** call the real local runtime actions
  - **Refresh** reads runtime status and local models
  - choose a discovered model, or type an exact model ID manually
  - if no local models are found, the wizard tells you to use Advanced Settings to download one
4. Review safety defaults on the finish step:
  - **Dry run** stays on by default
  - **Auto-approve** stays off by default
  - destructive execution stays off by default
5. If you pick **I'll configure this later**, the wizard asks for confirmation before marking first run complete.

Advanced Settings remains the full runtime-management surface for local runtimes.

Use VST3 **Settings** or PyQt **Advanced Settings** to check Device Bridge reachability before executing
plans that include `device_load`. Execution also resolves each device-load
candidate before sending any mutations, so ambiguous browser matches block until
the plan uses a specific candidate path or a confirmed ambiguous choice.

Settings are only applied when you click **Save**. Click **Cancel** to close settings without applying changes.

## UI Tour

### VST3 plug-in

This is the main in-Live workflow and the best choice for normal use while producing.

Use it for:

- typing prompts inside Ableton Live
- reviewing a plan before it touches the set
- previewing and executing from the plug-in window
- cloud-provider setup and Ollama setup that fits inside the plug-in's Settings window

The shipped VST3 currently includes a multiline prompt composer, a one-click **Run** flow, Result and Details tabs, Preview mode, destructive approval, Device Bridge checks/recovery actions, a minimal readiness strip, a System Prompts window, in-plug-in Help, modal Save/Cancel Settings, and Ollama controls. It does not show the same full readiness strip or oMLX management tab that the companion surfaces show.

Use the PyQt companion when you need full readiness checks or full local runtime management.

### PyQt GUI

This is the best setup, control, and debugging companion.

Use it for:

- first-run onboarding
- readiness checks before planning or live execution
- switching between embedded and attached-server workflows
- managing local runtimes for both Ollama and oMLX
- inspecting plan details, parsed actions, and run logs outside Ableton

### Web UI

This is the best lightweight browser companion.

Use it for:

- quick prompt tests in a browser
- checking readiness and "what to fix next" guidance without opening the PyQt app
- using Quick Starts (novice, production, sound design, safety) to fill prompts quickly
- launching saved macros from the browser companion when macro endpoints are available
- browsing read-only capabilities grouped by domain
- reviewing the Plan Board, Run Log, and Details tabs from a browser
- simple remote/local access while the FastAPI server is running

The web companion keeps safety defaults visible and explicit:

- preview mode should stay on during setup and experimentation
- live execution warnings are persistent when preview is off
- destructive live plans require explicit approval and confirmation

## Main Screen

The main screen is a command surface with readiness chips, a prompt field, a
Result view, Details view, and a single **Run** button. Run plans first, then
executes the validated actions in Preview or live mode depending on Settings.

The VST3 **Help** button opens an in-plug-in guide called "First preview in 60
seconds". It covers keeping Preview only enabled, choosing provider/model,
entering a safe prompt, clicking Run, and reviewing Details before live
execution. It also explains AbletonOSC versus Device Bridge. Screenshots are
future work; the current Help is text-only.

### Result Tab

The **Result** tab is the normal user-facing view. It shows:

- your request
- the assistant's interpreted Plan Board
- planned Ableton steps with safety and transport labels
- safety notes for destructive operations
- execution or preview results

The result view is selectable. Use standard macOS shortcuts such as `Cmd+C`, `Cmd+A`, and normal text selection.

## Reviewing A Plan

Treat the plan as the last review step before anything reaches Ableton.

Check these items before you execute:

- whether the explanation matches what you asked for
- which tracks, clips, scenes, or devices the actions target
- whether any step is marked destructive
- whether any `device_load` step is ambiguous and needs a more exact browser path or preset choice
- whether Preview only is still on for a safe first run

If the plan is wrong, edit the prompt and plan again. Do not execute a plan just because the model answered confidently.

### Details Tab

The **Details** tab is for debugging. It shows the provider response and the
internal action payload that LLM-r built from it. Use it when a plan fails, a
provider returns invalid JSON, or you need to inspect the exact OSC/action
details.

LLM-r asks supported providers for structured JSON responses. If a model still
answers with prose, LLM-r first asks the model to repair the answer into the
action schema. For common drum-loop requests, it can also fall back to a local
2-bar MIDI drum-loop plan so the workflow still produces executable actions.

### Run and Preview

Click **Run** to have LLM-r plan and then execute the validated action list.
With **Preview only; do not change Live** enabled, execution produces a preview
report and never mutates the Live set. With Preview only disabled, LLM-r sends
the actions to Ableton after the same preflight checks.

For live performance, keep Preview only on until the set is saved and tested.
Destructive actions, such as deleting tracks or clips, require **Allow
destructive actions** in Settings.

## Safety Controls

### Preview only

Preview only shows the execution report without mutating the Live set. This should stay on during setup and when testing a new provider or prompt style.

### Destructive approval

LLM-r marks destructive steps separately. Deleting tracks, clips, scenes, notes, or devices requires explicit destructive approval and Preview only must be off.

### Device Bridge preflight

`device_load` is preflighted before execution. LLM-r checks whether the Device Bridge is reachable and resolves the browser candidate before it starts mutating the set. If the candidate is ambiguous, execution stops instead of partially changing the set.

## Settings

The VST3 Settings window is modal, fixed-size, and intentionally kept to one screen:

- **Provider**: `openai`, `anthropic`, `google`, `ollama`, `omlx`, or `custom`
- **Model**: a non-editable provider-specific selector
- **Custom model**: explicit text field for unlisted model IDs or the `custom` provider
- **Server**: provider default or API base URL
- **API key**: cloud-provider credential
- **Preview only; do not change Live**: whether Run previews instead of mutating Live
- **Allow destructive actions**: permits destructive live actions when Preview only is off
- **AbletonOSC and Device Bridge**: host/port and bridge installation/recheck controls
- **Ollama**: status refresh, start/stop/install, installed model, serve, stop serve, test, online refresh, and download
- **Test readiness**: updates the minimal VST3 readiness guidance

Use **Save** to apply changes. Use **Cancel** to discard changes. Opening
Settings refreshes the local Ollama status automatically.

## Readiness

Readiness answers three separate questions:

- can LLM-r create a plan?
- can LLM-r preview that plan safely?
- can LLM-r execute that plan live?

The PyQt GUI and web UI expose full readiness directly. In headless mode, call `GET /api/readiness`. The VST3 exposes a smaller first-use strip: model configured/missing, AbletonOSC configured/not checked, Device Bridge reachable/unreachable/optional, and Preview/live state. Keep Preview only on first and treat PyQt/web as the source for full readiness diagnostics.

### Provider API Keys

OpenAI uses the OpenAI API key.

Anthropic uses the Anthropic API key.

Google uses a Gemini API key. The default Google endpoint is the Gemini `v1beta` API base. LLM-r builds the final `generateContent` URL from the selected model.

For custom providers, enter the endpoint expected by that provider. Custom provider support assumes an OpenAI-compatible chat-completions response.

## Ollama

Ollama controls live in the VST3 **Settings** window and in the PyQt companion runtime screens.

### Status

The Ollama status line shows whether the local Ollama API is running, how many local models are installed, and which models are currently loaded in memory.

Click **Refresh Status** to update this display.

### Start and Stop

**Start Ollama** starts the local service if the `ollama` executable or the Ollama app is installed.

**Stop Ollama** stops the local Ollama process.

### Installed Models

The **Installed model** pull-down is populated from the local Ollama API. If it is empty:

- start Ollama
- click **Refresh Status**
- download a model if none are installed

Use **Serve** to load the selected model and keep it alive. Use **Stop Serving** to unload it. Use **Test** to send a tiny local request and confirm the selected model responds.

When `ollama` is selected as the provider, LLM-r uses the local Ollama endpoint
`http://127.0.0.1:11434/api/chat` by default. The endpoint is restored during
Save and before planning, so a stale cloud-provider endpoint is not reused for
local Ollama plans.

### Downloadable Models

The **Downloadable model** pull-down is populated from the Ollama online model library. Click **Refresh Online** to reload the catalog.

Click **Download** to pull the selected model through Ollama. Large models can take a long time and require enough disk space and memory.

## oMLX

Full oMLX controls live in the PyQt companion **Advanced Settings -> oMLX** screen. The VST3 can select `omlx` as a provider and shows a Settings note, but it does not manage the oMLX runtime in this release.

The flow from LLM-r through to oMLX is: LLM-r → Modelito → oMLX runtime.

### Status

The oMLX status line shows whether the local oMLX runtime is available and which models are installed or running.

Click **Refresh Status** to update this display.

### Start and Stop

**Start oMLX** starts the local oMLX service if the runtime is installed.

**Stop oMLX** stops the oMLX process.

### Local Models

The **Local model** pull-down is populated from the local oMLX runtime. Use **Serve** to load the selected model. Use **Stop Serving** to unload it.

Use **Delete** to remove a downloaded model from local storage.

### Downloadable Models

The **Downloadable model** pull-down lists models available for download. Click **Download** to pull the selected model. Large models require significant disk space and download time.

### Note on Ollama and oMLX model compatibility

Ollama-pulled models are not automatically available to oMLX. The two runtimes maintain separate model stores. If you want a model accessible through oMLX, download it through the oMLX controls. The provider abstraction is handled by Modelito; see [MODELITO.md](MODELITO.md) for details.

When `omlx` is selected as the provider in Settings, LLM-r routes planning requests through the oMLX runtime. Switch the provider back to `ollama` or a cloud provider to use a different runtime.

## Local Runtime Setup Flow

Use this order for local runtimes:

1. Decide which runtime you want.
  - Use Ollama if you already use Ollama.
  - Use oMLX if you want Apple Silicon local MLX-style runtime support.
2. Start the runtime service.
3. Refresh status.
4. Download one model into that runtime's own model store.
5. Serve or activate the model if the runtime requires it.
6. Set the matching LLM-r provider and model.
7. Keep Preview only on and test a safe prompt first.

Ollama and oMLX do not share a model store. Download the model separately in the runtime you plan to use.

Real runtime validation for local runtimes is manual by default in this project.
Use the local controls as operational helpers, then verify behaviour in your real environment.

## Choosing Models

For simple Ableton control, smaller instruction models are usually enough. Start with a small or medium model before trying very large models.

Good local starting points:

- `llama3.1`
- `llama3.2`
- `qwen3`
- `qwen2.5`
- `mistral`
- `gemma3`

For cloud providers, choose a fast and inexpensive model first, then move to a stronger model if the planner produces weak or incomplete plans.

## Troubleshooting

### The assistant says it could not build actions

Open **Details**. The model may have returned invalid JSON, used unsupported tool names, or answered conversationally instead of returning an action plan.

For local models, try a stronger instruction-following model if this happens
often. The plug-in can repair some non-JSON responses, but models that ignore
tool names or invent unsupported tools will still produce weaker plans.

### Ollama installed models are empty

Make sure Ollama is running, then click **Refresh Status**. LLM-r uses the local API at `http://127.0.0.1:11434`.

### Download fails

Start Ollama first. Then click **Refresh Online**, choose a model, and click **Download** again.

### Ableton does not change

Check that AbletonOSC is installed, active, and listening on the host/port shown in Settings. If the failed step is `device_load`, also check that `LLMR_Bridge` is installed in the active User Library and enabled in a Control Surface slot after restarting Live. A `409` or ambiguous-candidate error means the browser query needs a more specific device name, preset query, or candidate path. Turn **Preview only** off when you actually want to execute live.

### Device Bridge not reachable

The VST3 Settings Bridge area shows this status when the local Remote
Script HTTP server does not answer. It now distinguishes disk install status
from runtime reachability and shows both the selected User Library path and the
exact install target.

Likely causes are that `LLMR_Bridge` is not installed in Ableton's active User
Library, Live has not been restarted, the script is not selected in a Control
Surface slot, or Live blocked the script due to an import/runtime error.

Use the VST3 actions:

- **Choose Ableton User Library...**: select the actual Ableton User Library folder (internal or external SSD).
- **Install / Reinstall Bridge**: installs to `<User Library>/Remote Scripts/LLMR_Bridge`.
- **Reveal Installed Bridge**: opens Finder at the installed bridge folder.
- **Copy Install Path**: copies the exact bridge folder path.
- **Open setup help**: shows the setup steps inside the plug-in.
- **Recheck**: tests the configured Bridge host/port again.

The User Library may be on an external SSD. This is supported as long as the drive is mounted before launching Live.

After installation, restart Ableton Live, open Settings -> Link, Tempo & MIDI,
set an empty Control Surface slot to `LLMR_Bridge` if present, and rescan/restart
if Live still does not start the bridge. If `LLMR_Bridge` does not appear,
inspect Live `Log.txt` for `LLMR`, `Bridge`, `RemoteScriptError`, `Traceback`, or `ImportError`.

### I still see an older UI

Ableton may be loading an older VST3 bundle from its plug-in cache. Rebuild and reinstall the VST3, restart Ableton, and rescan plug-ins.

## Safety Notes

LLM-r can send real edit commands to Ableton. Use dry runs for review, keep destructive actions disabled unless needed, and save important Live sets before executing destructive plans.
