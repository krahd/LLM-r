# Ableton Live Smoke Test

Use this checklist only with a disposable Ableton Live set.

## Setup

1. Install and enable AbletonOSC in a Control Surface slot.
2. Install and enable LLMRDeviceBridge in a separate Control Surface slot.
3. Restart Ableton Live after installing either Remote Script.
4. Open a new empty Live set and save it as a throwaway test project.
5. Keep AbletonOSC on `127.0.0.1:11000`.
6. Keep LLMRDeviceBridge on `127.0.0.1:8788`.

## Read-Only Preflight

```bash
python3 scripts/smoke_test_live_integration.py
```

Expected result:

- Device Bridge `/health` returns `status: ok`.
- Device Bridge candidate listing returns at least one browser result for
  `Drum Rack`.
- Device Bridge resolve validates the exact `device_load` request without
  loading the item.
- AbletonOSC replies to `/live/song/get/tempo` on reply port `11001`.

## Mutating Smoke Test

This changes the current Live set. Run it only in the disposable set.

```bash
python3 scripts/smoke_test_live_integration.py --execute
```

Expected result:

- Ableton tempo changes to `120`.
- `Drum Rack` is loaded on track `0`.

If the Device Bridge returns `409`, the browser query matched multiple
candidates. Run the preflight again, inspect the printed candidate paths, and
use a more specific `--device-query`, `--preset-query`, or exact
`--browser-path 'Root > Folder > Item'`. Use `--allow-ambiguous` only after
choosing the candidate intentionally.

## API-Level Checks

With `llmr serve` running:

```bash
curl -s http://127.0.0.1:8787/api/device-bridge/status
curl -s 'http://127.0.0.1:8787/api/device-bridge/devices?query=Drum%20Rack&device_type=drum'
curl -s -X POST http://127.0.0.1:8787/api/device-bridge/resolve \
  -H 'Content-Type: application/json' \
  -d '{"track_index":0,"query":"Drum Rack","device_type":"drum"}'
curl -s http://127.0.0.1:8787/api/osc-replies/status
curl -s http://127.0.0.1:8787/api/live/song
```

The Device Bridge status should show `ok: true`. The OSC reply status should
show `listening: true` when the server listener is enabled and the reply port is
available.
