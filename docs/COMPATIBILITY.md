# Runtime Contract

LLM-r targets Ableton Live with AbletonOSC installed. Browser/device loading
also requires the LLMRDeviceBridge Remote Script to be installed and enabled in
an Ableton Control Surface slot.

This repository maps tools to OSC addresses; exact support can vary by AbletonOSC version.
Use `GET /api/capabilities` in your deployed environment as the current runtime
contract for executable tools.
Use `GET /api/device-bridge/status` and `GET /api/osc-replies/status` to check
the optional runtime support services.

The current MIDI note and audio clip property tools are mapped to AbletonOSC's
Clip API in the upstream `master` branch. `device_load` is mapped to the
LLMRDeviceBridge Remote Script because AbletonOSC does not expose browser
loading. Plugin-chain loading beyond one browser item, warp marker CRUD,
arrangement clip insertion, render/export, and destructive sample editing remain
outside the current runtime contract.

LLM-r is still pre-release. Older development endpoint shapes, aliases, and
transitional docs are intentionally removed as the product changes. Current docs
and runtime capability output are the source of truth.
