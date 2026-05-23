# LLM-r

**LLM-r** bridges [Ableton Live](https://www.ableton.com/) and large language models to automate music-production workflows. The **VST3 plug-in is the primary product surface**: describe what you want in plain language inside Ableton Live, review the generated plan, then dry-run or execute it.

The other surfaces are companions for the same workflow:

- **PyQt GUI**: control, setup, debugging, and local-runtime management companion
- **Web UI**: lightweight browser companion for planning, review, and readiness checks
- **FastAPI**: automation and headless surface for scripts, agents, and HTTP clients

```text
Natural language prompt in the VST3
        │
        ▼
  LLM-r planner  ────────────────►  Modelito-backed LLM runtime
                           (OpenAI / Anthropic / Google /
                            Ollama / oMLX / custom)
        │
        ▼
   Action plan  (dry-run or execute)
        │
        ▼
   AbletonOSC / Device Bridge ─────►  Ableton Live
```

---

## Features

- **Self-contained VST3 plug-in** — configure the LLM, write prompts, review plans, dry-run, and execute from inside Ableton Live
- **Clear surface split** — VST3 for primary in-Live use, PyQt for setup/debug/control, web UI for lightweight browser access, and FastAPI for automation/headless workflows
- **Natural-language planner** — the plug-in and `POST /api/plan` convert a free-text prompt into a typed, validated action plan
- **Safe execution** — dry-run mode, destructive-action approval step, and a strict capability registry
- **Macro system** — named sequences of actions (`idea_sketch`, `performance_prep`, …) with full CRUD via the API
- **Live state introspection** — query song settings, tracks, devices, clips, and parameters at runtime
- **Device loading** — load Live browser devices or plug-ins by name through the bundled LLMRDeviceBridge Remote Script
- **MIDI and clip editing** — add/remove MIDI notes, set note velocity through note payloads, rename/duplicate clips, and adjust clip loop/marker settings
- **Audio clip controls** — set clip gain, transpose/detune, warping, warp mode, and RAM mode for existing audio clips
- **Session history** — plans, executions, and sessions are persisted to disk and survive restarts
- **SSE streaming** — `POST /api/stream` for streaming LLM completions
- **Desktop GUI** — optional PyQt6 companion app with embedded mode, onboarding, server attach/start controls, readiness display, and local-runtime management tabs
- **Web UI** — optional browser companion with readiness chips, Active Model display, a compact basic provider/model editor, Plan Board, run log, and details view
- **Multi-provider LLM support** — use cloud or local models from the appropriate surface; local runtimes (Ollama and oMLX) are mediated by [Modelito](docs/MODELITO.md)

> Chat with Ableton Live.

That future project should be local-first, musician-facing, and self-contained from the user's point of view: install a VST3 / helper package, open Ableton Live, type what you want, review the plan, and execute it. Internally, it should use existing Ableton-control infrastructure rather than continuing to grow a private bridge and action protocol inside this repository.

---

## Why this repository is closed

LLM-r successfully demonstrated that an LLM can plan and execute Ableton Live operations through a typed capability layer, AbletonOSC, and an auxiliary Device Bridge. It also showed that the current architecture is not the right foundation for a polished product.

The decisive issues were:

- **The VST3 became too much of the product.** A plug-in instance is track/device-scoped, while the desired assistant is session/global. For a full Ableton assistant, a VST3 is a useful front panel, not the correct place to host the runtime, model management, bridge logic, diagnostics, and long-lived state.
- **The UI remained developer-oriented.** The settings, runtime controls, bridge status, provider selection, and diagnostics were useful during development but too technical and visually unpolished for musicians with no AI/development background.
- **The bridge layer duplicated existing work.** Existing projects already expose Ableton Live through MCP, AbletonOSC, Remote Scripts, and OSC/JSON control surfaces. LLM-r should not continue inventing its own private Ableton-control stack unless there is a specific missing capability.
- **Prompts alone are not enough.** Better system prompts help, but reliable musical behaviour requires real tools, Ableton state, musical abstractions, validators, and deterministic/semi-deterministic generators for clips, notes, variations, humanisation, effects, and automation.
- **Local model management must be productised.** Ordinary users should not see provider jargon, endpoint URLs, or implementation details. Ollama should be the default local runtime, hidden behind simple language such as “Local AI: Ready”.
- **MCP is valuable, but probably not the internal VST3 runtime path.** MCP is excellent as an interoperability layer and tool schema surface. For a musician-facing product, a local helper process should own the model runtime, Ableton control, diagnostics, and persistence, while the VST3 remains a thin UI.

---

## Quick Start

### 1. Start AbletonOSC

Install and enable the [AbletonOSC](https://github.com/ideoforms/AbletonOSC) MIDI Remote Script in Ableton Live. By default it listens on `127.0.0.1:11000`.

For instrument/effect/plug-in loading, also install and enable the bundled
`LLMR_Bridge` Remote Script. The VST3 now asks you to choose or confirm the
actual Ableton User Library folder first, then installs into:

`<User Library>/Remote Scripts/LLMR_Bridge`

This supports relocated User Libraries, including external SSD locations.

### 2. Launch

#### Option A — VST3 plug-in (primary)

Build/install the local VST3 bundle, then open the Ableton test set:

```bash
bash scripts/test_install_vst3_and_open.sh "$HOME/Library/Audio/Plug-Ins/VST3"
```

Open the `LLM-r` plug-in window in Ableton Live. The plug-in GUI is the main
user-facing workflow: provider/model settings, prompt entry, plan review,
dry-run, Auto-approve, destructive-action approval, Plan/Details tabs, and
Advanced Settings for cloud API keys, AbletonOSC, Device Bridge checks, and
Ollama runtime controls.

The VST3 now includes a minimal first-use readiness strip for model, AbletonOSC,
Device Bridge, and Dry run state. It is not full `GET /api/readiness` parity and
does not include an oMLX runtime-management UI. Use the companion surfaces for
full readiness checks and local runtime management.

#### Option B — Desktop GUI (optional)

```bash
python gui/pyqt_app.py
```

The GUI can run in embedded mode, attach to a running server, or start a local
server from the toolbar. Its main Settings dialog keeps the normal workflow
short: choose the provider, choose the model, set execution defaults, and save.
It also includes the most complete first-run/setup surface today: onboarding,
readiness display, and local runtime controls for both Ollama and oMLX
(service management, model download, serve, stop serving, delete). See
[docs/MODELITO.md](docs/MODELITO.md) for provider setup details. Use Open Help
in the toolbar to open the GitHub manual.

#### Option C — Server only (headless / API)

### 1. The right product framing is not “LLM-r”

The end-user proposition is clearer as:

#### Web UI (lightweight browser companion)

When the FastAPI server is running, open `http://127.0.0.1:8787` for a compact
browser companion. It is useful for remote/local browser access, readiness
checks, prompt testing, plan review, manual execution outside Ableton's
plug-in window, and basic provider/model changes for ordinary local setup.

The web UI intentionally stays narrow in scope: it can edit the active
provider/model pair, and displays read-only local runtime status (Ollama and oMLX
installation/running state, local model count, and currently served model count);
PyQt remains the full setup surface for API keys, Ollama/oMLX service management,
model download/serve/delete, and AbletonOSC configuration.

### First run

Use this sequence on a new install:

1. Open **Settings** and choose a provider/model.
2. Keep **Dry run** enabled.
3. Use **Test readiness** in Basic Settings.
4. For cloud providers, add the API key in Advanced Settings.
5. For `device_load`, open Advanced Settings -> Device Bridge and:
  - click **Choose Ableton User Library...**
  - in Live, right-click **User Library** in the Browser and choose **Show in Finder** to locate the folder
  - click **Install / Reinstall Bridge**
  - restart Live
  - in Live Settings -> Link, Tempo & MIDI -> Control Surface, choose `LLMR_Bridge` if it appears
  - click **Recheck** in LLM-r

If `LLMR_Bridge` does not appear in Live, check Live `Log.txt` for `LLMR`, `Bridge`, `RemoteScriptError`, `Traceback`, or `ImportError`.

Readiness checks:
In PyQt or web UI, read the readiness status directly.
In headless mode, call `GET /api/readiness`.
In the VST3, use the minimal readiness strip and run a dry run first; the plug-in does not claim the same readiness parity as the companion surfaces.

1. Try a safe prompt such as `Set the tempo to 120 BPM` or `Create one MIDI track named Ideas`.
2. Review the plan before executing.
3. Execute only after the plan looks correct and any destructive steps are intentional.

### Try these first

Safe first prompts for novice users:

- `Set tempo to 120 BPM and turn metronome on.`
- `Create one MIDI track named Drums.`
- `Create an audio track named Vox In and arm it.`
- `Create a 4-bar clip on track 0 and rename it Beat Sketch.`
- `Dry-run deleting clip 0 on track 0.`

More advanced prompts for professional users:

- `Set tempo to 126 BPM, set global quantization to 1 bar, and continue playback.`
- `Create a drums sketch: make a MIDI track, create a 4-bar clip, and add a basic kick/snare pattern.`
- `Duplicate clip 0 to clip 1 on track 1 and launch clip 1.`
- `Load Drum Rack on track 2.` *(requires Device Bridge)*
- `Load EQ Eight on track 1 and set a conservative gain staging level.` *(requires Device Bridge for loading)*

For live performance, keep Dry run on until the set is saved and tested. Avoid
Auto-approve with Dry run off during performance.

### Local models

LLM-r does not talk to Ollama or oMLX directly from planner code. **Modelito
mediates provider access** and normalises the planner-facing interface.

Ollama and oMLX are still separate local runtimes:

- Ollama has its own service, model store, and model IDs.
- oMLX has its own service, model store, and model IDs.
- A model pulled with `ollama pull` does **not** automatically become an oMLX model.
- If you want the same family in both runtimes, download it separately in each runtime and use the ID exposed by that runtime.

See [docs/MODELITO.md](docs/MODELITO.md) for the ordinary-user provider guide,
runtime differences, and model-ID notes.

Real Ollama/oMLX runtime validation is manual by default in this repository
unless you add dedicated integration tests for your target machine/runtime.

### 3. Send a prompt

Names and UI should avoid infrastructure terms such as LLM, MCP, provider, endpoint, agent, tool schema, or bridge. Those are implementation details.

### 2. A hybrid architecture is better than a pure VST3

A plausible future architecture is:

```text
VST3 front-end
  -> local helper app / daemon
  -> Ollama-backed local model
  -> planner / validator / executor
  -> AbletonOSC / MCP-derived Ableton tool layer
  -> Ableton Live
```

The user can still experience the product as a VST3, but the runtime should live outside the plug-in UI thread.

### 3. Ollama is the correct default local runtime

For the target user, Ollama is a better default than exposing multiple provider choices. A future product should use an existing Ollama installation if available, offer to start it if stopped, guide installation if missing, and download one recommended model. Advanced users can still configure models and endpoints.

Decisions for the successor project:

- no OpenClaw;
- no llama.cpp;
- no Claude / ChatGPT / Gemini as default product path;
- no cloud API keys required for normal use;
- oMLX and Modelito may remain advanced/internal options, but not the beginner-facing path.

### 4. MCP and AbletonOSC work should be reused

The successor should start by auditing and reusing existing open-source infrastructure, especially AbletonOSC MCP wrappers, instead of creating yet another bridge. The useful work is likely above that layer: musician UX, local model packaging, prompt presets, plan review, reliable musical actions, and a polished installer.

### 5. The missing layer is musical product design

Existing infrastructure exposes Ableton operations. The product challenge is to make prompts such as these work reliably:

- “Create a one-minute jazz drum track with fills and humanisation.”
- “Create a one-minute piano jazz ballad.”
- “Extend the selected loop to two minutes with variations.”
- “Add reverb and compression to the drums.”
- “Automate the filter opening over eight bars.”

That requires musical generators, Ableton context, arrangement/session awareness, validation, and concise plan review. It is not solved by dumping hundreds of raw tools into a model prompt.

---

## Macros

Macros are named sequences of Ableton actions. LLM-r ships with built-in static macros (`idea_sketch`, `performance_prep`) and supports runtime macros persisted to disk.

When to use macros:

- reuse a setup pattern you trust
- get a quick starter plan before refining with normal prompts
- standardize repetitive prep steps across sessions

Built-in macro names in this release:

- `idea_sketch`
- `performance_prep`

Macro discoverability in shipped surfaces:

- Web UI: built-in and runtime macro names can be listed and planned from the Macros panel.
- API/headless: use `/api/macros` and `/api/plan_macro`.

**List macros:**

### Ableton control, AbletonOSC, and MCP

- [AbletonOSC](https://github.com/ideoforms/AbletonOSC) — OSC Remote Script exposing much of Ableton Live’s Live Object Model. Strong base layer for broad Live control.
- [mawaha/AbleOscMcp](https://github.com/mawaha/AbleOscMcp) — AbletonOSC-to-MCP server with broad tool coverage, resources, subscriptions, musical helpers, and optional browser/device support through an additional Remote Script. This is probably the first project to audit before writing any new AbletonOSC MCP wrapper.
- [nozomi-koborinai/ableton-osc-mcp](https://github.com/nozomi-koborinai/ableton-osc-mcp) — Go-based MCP-to-AbletonOSC translator. Useful as a compact alternative implementation and distribution reference.
- [Simon-Kansara/ableton-live-mcp-server](https://github.com/Simon-Kansara/ableton-live-mcp-server) — Python/FastMCP AbletonOSC MCP server experiment. Useful as a reference for schema and mapping ideas, though it should be audited before use.
- [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp) — MCP server for Ableton Live that does not use AbletonOSC; it ships its own Remote Script and communicates with Live over JSON/TCP. Important because it covers browser/device-loading workflows differently from standard AbletonOSC.

### Chat / AI control products around Ableton Live

- [MIDI Agent](https://midiagent.com/) — commercial VST3/AU/AAX/standalone plug-in for prompt-based MIDI generation. Relevant because it shows a narrower, track-local VST shape for AI music generation.
- [Yuma / AbletonGPT](https://yuma.studio/) — desktop companion app for natural-language Ableton Live control. Relevant as an example of the “sidecar app rather than VST3” pattern.
- [OBSIDIAN Neural / ai-dj](https://github.com/innermost47/ai-dj) — open-source AI loop/performance instrument, VST3/AU/standalone. Relevant as a VST-based AI music precedent, but focused on audio loop generation rather than session-wide Ableton control.

### Local model runtime and provider infrastructure

- [Ollama](https://github.com/ollama/ollama) — recommended default runtime direction for a local-first musician product. Provides local model serving, model download, model listing, chat/completions, and a relatively user-friendly local-LLM ecosystem.
- [Modelito](https://github.com/krahd/modelito) — local/provider abstraction explored during LLM-r development. Still useful as an advanced/internal provider layer, but the successor product should hide provider complexity from ordinary users.

### Protocols and agent infrastructure

- [Model Context Protocol](https://modelcontextprotocol.io/) — open protocol for exposing tools, prompts, and resources to AI applications. Best treated as an interoperability layer and possible external-agent surface, not necessarily as the internal runtime boundary of a VST3 product.
- [Pi](https://github.com/earendil-works/pi) — agentic harness investigated as a possible planner/tool-calling layer. Potentially useful above MCP/tool layers, but not a replacement for musician-facing product design.

---

## VST3 Plug-in

The VST3 plug-in is the primary self-contained control surface. It does not
require the desktop GUI or FastAPI server for normal use. The plug-in stores its
own runtime settings in macOS user defaults and can:

- choose provider/model/endpoint and API key
- provider picker includes `openai`, `anthropic`, `google`, `ollama`, `omlx`, and `custom`
- use non-editable provider/model selectors plus an explicit Custom model field
- switch between Plan and Details response tabs
- copy/select text from the response panel
- keep provider/model, optional Custom model, Server/API base URL, Dry run, and
  Test readiness on the Basic Settings screen
- keep API keys, AbletonOSC, Device Bridge host/port, Bridge setup actions,
  Ollama controls, oMLX notes, destructive approval, and diagnostics in
  Advanced Settings
- show a minimal readiness strip for model, AbletonOSC, Device Bridge, and Dry run state
- show transport/device status checks and Ollama model/runtime state
- load the downloadable-model pull-down from the Ollama online model library
- open an in-plug-in Help dialog with the first dry-run path and Bridge setup notes
- save or cancel settings changes explicitly
- send the built-in LLM-r tool catalog and optional guidance to the LLM
- parse the returned JSON plan
- dry-run or execute the resulting AbletonOSC and Device Bridge actions
- auto-approve plans after planning while respecting the dry-run default
- block destructive actions unless explicitly allowed

The shipped VST3 currently does **not** provide:

- full PyQt/web readiness parity backed by `GET /api/readiness`
- an oMLX runtime-management tab
- the PyQt onboarding wizard
- bundled screenshots in the VST3 Help dialog

For full readiness checks and local runtime management (including oMLX), use the
PyQt GUI companion.

## Desktop GUI

The GUI is an optional companion. It can run LLM-r in embedded mode without a
separate server process, attach to a running server, or start/stop a local server
from the toolbar.

```bash
pip install PyQt6
python gui/pyqt_app.py
```

A **Settings** dialog (accessible from the toolbar) lets you configure everything at runtime:

- Main Settings: LLM provider, model, dry-run default, Auto-approve, and destructive-execution default
- Advanced Settings: provider API keys, assistant prompt guidance, Ableton OSC host/port, server URL, and API token
- Advanced Settings → Ollama: status, start/stop service, installed model picker, served model stop, downloadable-model picker, download, serve, and delete
- Advanced Settings → oMLX: status, start/stop service, local model picker, download, serve, stop serving, and delete; see [docs/MODELITO.md](docs/MODELITO.md)
- Readiness bar: ready-to-plan, ready-to-dry-run, and ready-to-execute state with hints
- Response tabs: Plan for action cards, Action Table for parsed tool calls, Run Log for execution reports, and Details for the complete payload plus parsed `llm_raw` when available
- Open Help opens the GitHub user manual from the toolbar

PyQt also includes a first-run onboarding wizard focused on safe initial setup:

- choose cloud or local provider/runtime (or configure later)
- for local runtimes, run real Install / Start Service / Refresh actions in-wizard
- pick a discovered local model or type an exact model ID manually
- keep safe defaults (Dry run on, Auto-approve off, destructive execution off)

Advanced Settings remains the full local-runtime management surface.

## Web UI

The web UI is a lightweight browser companion rather than the primary product
surface. It is useful when you want a quick plan/review/execute panel outside
Ableton Live without opening the PyQt app.

It currently provides:

- provider/model summary pulled from runtime settings
- readiness chips backed by `GET /api/readiness`
- plain-language prompt workflow: Create a plan -> preview only -> run in Ableton
- quick-start prompt templates grouped for novice, production, sound design, and safety tasks
- macro launcher using `/api/macros` and `/api/plan_macro` when available
- read-only capabilities browser using `/api/capabilities`
- Plan Board, Run Log, and Details tabs with copy-plan-json/copy-summary actions
- stronger live/destructive safety messaging and readiness-driven control disable states

GUI connection settings are persisted to `~/.llmr/gui.json`. Runtime settings are
pushed to the server via `PATCH /api/settings` when connected to HTTP mode, or
saved directly by the embedded backend.

If a server is already running when the GUI opens, it attaches to it instead of starting a new one.

---

Working product statement:

> A local-first VST3/helper system that lets musicians chat with Ableton Live.

Expected structure:

```text
chat-with-live/
  native/vst3/          # polished thin VST3 front-end
  helper/               # local backend, Ollama management, planner, executor
  prompts/              # curated musical task/system prompts
  installer/            # AbletonOSC / Remote Script / helper setup
  docs/                 # musician-facing documentation and screenshots
```

Possible internal dependency or fork:

```text
able-live-core/
  AbletonOSC / AbleOscMcp-derived control layer
  typed Live tools
  diagnostics
  optional MCP server export
```

First vertical slice:

---

## Documentation

| Document | Description |
| --- | --- |
| [docs/CAPABILITIES.md](docs/CAPABILITIES.md) | Full capability catalog |
| [docs/ABLETON_SMOKE_TEST.md](docs/ABLETON_SMOKE_TEST.md) | Real AbletonOSC + Device Bridge smoke-test checklist |
| [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md) | Current AbletonOSC runtime contract notes |
| [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md) | Current pre-release audit and roadmap |
| [docs/USER_MANUAL.md](docs/USER_MANUAL.md) | User-facing guide for the VST3 workflow |
| [docs/GUI-PLUGIN.md](docs/GUI-PLUGIN.md) | Technical GUI behavior and settings |
| [docs/LLM_ASSISTANT_PROMPT.md](docs/LLM_ASSISTANT_PROMPT.md) | Default planner guidance prompt |
| [docs/MACROS.md](docs/MACROS.md) | Macro authoring guide |
| [docs/MODELITO.md](docs/MODELITO.md) | Modelito integration details |
| [docs/RELEASE.md](docs/RELEASE.md) | Release and build instructions |
| [docs/SCENARIOS.md](docs/SCENARIOS.md) | Current executable workflow recipes |
| [docs/SECURITY.md](docs/SECURITY.md) | Security model and deployment advice |

---

## Current Limitations

- Real Ableton Live validation (transport, OSC, device loading) is required for release confidence and is not automated.
- Native VST3 build, install, and load should be verified on macOS before each release.
- The shipped VST3 plug-in exposes only a minimal first-use readiness strip; full readiness diagnostics and oMLX management remain in the companion surfaces.
- Real oMLX runtime validation is manual; automated tests cover the FastAPI routes with monkeypatched adapters only.
- Some advanced workflows (device loading, ambiguous browser resolution) require both AbletonOSC and the LLMRDeviceBridge Remote Script.
- Local model access via Ollama and oMLX is mediated by Modelito. Models pulled through Ollama are not automatically available to oMLX unless both runtimes expose the same model identifier.

---

## Repository state

This repository is kept for reference. It contains useful experiments in:

- VST3 UI prototyping;
- Modelito-based model-provider abstraction;
- Ollama/oMLX exploration;
- AbletonOSC action planning;
- Device Bridge experiments;
- dry-run / approval workflow;
- capability registry design;
- FastAPI, PyQt, and web companion surfaces;
- prompt architecture experiments;
- release engineering lessons.

It should not be presented as a finished product or used as the foundation for a polished musician-facing release without a significant architectural rewrite.
