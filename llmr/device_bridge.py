from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class DeviceBridgeError(RuntimeError):
    """Raised when the local Live Device Bridge cannot complete a request."""


def load_device(
    *,
    host: str,
    port: int,
    track_index: int,
    query: str,
    device_type: str,
    timeout: float = 15.0,
) -> dict[str, Any]:
    payload = {
        "track_index": track_index,
        "query": query,
        "device_type": device_type,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"http://{host}:{port}/api/devices/load",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {"status": "ok"}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise DeviceBridgeError(f"Device Bridge HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise DeviceBridgeError(f"Device Bridge unavailable: {exc.reason}") from exc
    except TimeoutError as exc:
        raise DeviceBridgeError("Device Bridge request timed out") from exc
