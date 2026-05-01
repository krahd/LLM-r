# LLM-r User Manual

LLM-r is a VST3 assistant for Ableton Live. You type a production request, LLM-r asks your selected language model for an executable plan, shows you the plan in plain language, and can send the resulting OSC commands to Ableton Live through AbletonOSC.

## Requirements

- macOS with Ableton Live
- AbletonOSC installed and running in Live
- The LLM-r VST3 plug-in installed in your VST3 folder
- One model provider:
  - OpenAI, Anthropic, or Google with an API key
  - Ollama running locally with at least one downloaded model

## First Run

1. Open Ableton Live.
2. Add the LLM-r VST3 plug-in to any track.
3. Open the plug-in window.
4. Click **Settings**.
5. Choose a provider and model.
6. For cloud providers, open **Advanced Settings** and enter the API key.
7. Confirm the AbletonOSC host and port. The default is `127.0.0.1:11000`.
8. Click **Save**.

Settings are only applied when you click **Save**. Click **Cancel** to close settings without applying changes.

## Main Screen

The main screen has a prompt field, an assistant response area, and execution controls.
Press **Return** in the prompt field to send the request, or click **Send**.

### Chat Tab

The **Chat** tab is the normal user-facing view. It shows:

- your request
- the assistant's interpreted plan
- planned Ableton steps in plain language
- safety notes for destructive operations
- execution or dry-run results

The chat view is selectable. Use standard macOS shortcuts such as `Cmd+C`, `Cmd+A`, and normal text selection.

### Raw JSON Tab

The **Raw JSON** tab is for debugging. It shows the provider response and the internal action payload that LLM-r built from it. Use it when a plan fails, a provider returns invalid JSON, or you need to inspect the exact OSC/action details.

### Dry Run and Execute

Keep **Dry run** enabled when testing. A dry run shows what would be sent to Ableton without changing the Live set.

Click **Execute** only after reviewing the plan. Destructive actions, such as deleting tracks or clips, require **Allow destructive actions** in Settings and dry run must be off.

## Settings

The basic Settings screen is intentionally short:

- **Provider**: `openai`, `anthropic`, `google`, `ollama`, or `custom`
- **Model**: a provider-specific pull-down
- **Dry run default**: whether the main screen starts in dry-run mode
- **Allow destructive actions**: permits destructive actions when dry run is off

Use **Save** to apply changes. Use **Cancel** to discard changes.

## Advanced Settings

Advanced Settings contains fields that are not needed for every request:

- provider endpoint
- provider API key
- LLM-r guidance prompt toggle
- AbletonOSC host and port
- Ollama service and model controls

### Provider API Keys

OpenAI uses the OpenAI API key.

Anthropic uses the Anthropic API key.

Google uses a Gemini API key. The default Google endpoint is the Gemini `v1beta` API base. LLM-r builds the final `generateContent` URL from the selected model.

For custom providers, enter the endpoint expected by that provider. Custom provider support assumes an OpenAI-compatible chat-completions response.

## Ollama

Ollama controls live in **Advanced Settings**.

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

Open **Raw JSON**. The model may have returned invalid JSON, used unsupported tool names, or answered conversationally instead of returning an action plan.

### Ollama installed models are empty

Make sure Ollama is running, then click **Refresh Status**. LLM-r uses the local API at `http://127.0.0.1:11434`.

### Download fails

Start Ollama first. Then click **Refresh Online**, choose a model, and click **Download** again.

### Ableton does not change

Check that AbletonOSC is installed, active, and listening on the host/port shown in Advanced Settings. Keep **Dry run** off when you actually want to execute.

### I still see an older UI

Ableton may be loading an older VST3 bundle from its plug-in cache. Rebuild and reinstall the VST3, restart Ableton, and rescan plug-ins.

## Safety Notes

LLM-r can send real edit commands to Ableton. Use dry runs for review, keep destructive actions disabled unless needed, and save important Live sets before executing destructive plans.
