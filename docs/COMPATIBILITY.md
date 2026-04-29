# Runtime Contract

LLM-r targets Ableton Live with AbletonOSC installed.

This repository maps tools to OSC addresses; exact support can vary by AbletonOSC version.
Use `GET /api/capabilities` in your deployed environment as the current runtime
contract for executable tools.

The current MIDI note and audio clip property tools are mapped to AbletonOSC's
Clip API in the upstream `master` branch. Browser search/load, plugin-chain
loading, warp marker CRUD, arrangement clip insertion, render/export, and
destructive sample editing are not exposed by upstream AbletonOSC at the time of
this update and require a deeper Remote Script or AbletonOSC extension before
LLM-r can execute them reliably.

LLM-r is still pre-release. Older development endpoint shapes, aliases, and
transitional docs are intentionally removed as the product changes. Current docs
and runtime capability output are the source of truth.
