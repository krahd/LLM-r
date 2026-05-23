# LLM-r

**Status: closed / archived prototype.**

LLM-r is no longer being developed as a product. The project remains public as a research-and-development prototype, implementation archive, and record of what was learned while exploring natural-language control of Ableton Live from a VST3, desktop GUI, web UI, and FastAPI surface.

The next product direction is not to continue expanding LLM-r as-is. The work should move to a new, product-first project centred on the simpler end-user promise:

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

## What we learned

### 1. The right product framing is not “LLM-r”

The end-user proposition is clearer as:

> Chat with Ableton Live.

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

## Related projects and prior art

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

## Successor direction

A successor should probably be a new repository rather than a continuation of this one.

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

1. Install/open the VST3.
2. Detect or start Ollama.
3. Download or select the recommended local model.
4. Detect Ableton control layer.
5. Accept prompt: “Create a one-minute jazz drum track with fills and humanisation.”
6. Show a clear plan.
7. Execute safely in Ableton Live.
8. Produce musically acceptable material without exposing developer configuration.

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
