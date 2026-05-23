# LLM-r (Closed Project)

LLM-r is closed and no longer under active development.

This repository remains available as a reference implementation for:
- Ableton Live action planning from natural-language prompts
- safety-first execution workflows (preview/dry-run, destructive-action approval)
- multi-surface architecture experiments (VST3, FastAPI, PyQt, web UI)
- AbletonOSC and Device Bridge integration patterns

## Project Status

- State: closed
- Maintenance: no feature development planned
- Support: best-effort only; no SLA
- Releases: no new production releases planned from this codebase

If you need a production-grade musician-facing tool, treat this repository as research and starting material, not a finished product.

## Why It Was Closed

The codebase proved the core concept, but the architecture is not the right long-term foundation for a polished end-user product. The main constraints were:

- product/runtime responsibilities grew too large inside the VST3 surface
- user experience remained too technical for non-developer musicians
- duplicated effort vs existing Ableton control ecosystems
- reliable musical outcomes require deeper domain tooling beyond prompt engineering

## What Still Works (Reference Use)

The repository still contains working components useful for study and prototyping:

- VST3 plug-in flow: prompt -> plan -> preview/live execution
- FastAPI endpoints for planning, execution, settings, readiness, and runtime status
- PyQt companion app for setup/control workflows
- web command surface for lightweight browser-based planning/review
- Device Bridge path for browser/device loading flows
- macro and capability registries

Behaviour and compatibility are documented in [STATUS.md](STATUS.md) and [docs/](docs/).

## Recommended Use of This Repository

Use this repository to:

- inspect architecture and safety patterns
- reuse ideas, not assumptions
- prototype integrations with your own runtime/UI stack

Avoid using this repository as-is for:

- a commercial release without substantial redesign
- unattended high-risk live mutation flows
- assumptions of long-term compatibility guarantees

## Documentation Index

- [STATUS.md](STATUS.md)
- [docs/CAPABILITIES.md](docs/CAPABILITIES.md)
- [docs/USER_MANUAL.md](docs/USER_MANUAL.md)
- [docs/SECURITY.md](docs/SECURITY.md)
- [docs/ABLETON_SMOKE_TEST.md](docs/ABLETON_SMOKE_TEST.md)
- [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)
- [docs/SCENARIOS.md](docs/SCENARIOS.md)
- [docs/RELEASE.md](docs/RELEASE.md)

## License

MIT. See [LICENSE](LICENSE).
