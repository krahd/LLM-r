from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class DeviceBridgeError(RuntimeError):
    """Raised when the local Live Device Bridge cannot complete a request."""


def request_json(
    *,
    host: str,
    port: int,
    path: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        f"http://{host}:{port}{path}",
        data=body,
        headers={"Content-Type": "application/json"} if payload is not None else {},
        method=method,
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


def health(*, host: str, port: int, timeout: float = 2.0) -> dict[str, Any]:
    try:
        payload = request_json(host=host, port=port, path="/health", timeout=timeout)
        return {
            "ok": True,
            "status": payload.get("status", "ok"),
            "host": host,
            "port": port,
            "bridge": payload.get("bridge", "LLMRDeviceBridge"),
            "details": payload,
        }
    except DeviceBridgeError as exc:
        return {
            "ok": False,
            "status": "unreachable",
            "host": host,
            "port": port,
            "error": str(exc),
        }


def list_devices(
    *,
    host: str,
    port: int,
    query: str = "",
    device_type: str = "all",
    timeout: float = 10.0,
) -> dict[str, Any]:
    params = urllib.parse.urlencode({"query": query, "device_type": device_type})
    return request_json(
        host=host,
        port=port,
        path=f"/api/devices/list?{params}",
        timeout=timeout,
    )


def load_device(
    *,
    host: str,
    port: int,
    track_index: int,
    query: str,
    device_type: str,
    preset_query: str | None = None,
    browser_path: list[str] | str | None = None,
    allow_ambiguous: bool = False,
    timeout: float = 15.0,
) -> dict[str, Any]:
    payload = {
        "track_index": track_index,
        "query": query,
        "device_type": device_type,
    }
    if preset_query:
        payload["preset_query"] = preset_query
    if browser_path:
        payload["browser_path"] = browser_path
    if allow_ambiguous:
        payload["allow_ambiguous"] = True
    return request_json(
        host=host,
        port=port,
        path="/api/devices/load",
        method="POST",
        payload=payload,
        timeout=timeout,
    )


def resolve_device(
    *,
    host: str,
    port: int,
    track_index: int,
    query: str,
    device_type: str,
    preset_query: str | None = None,
    browser_path: list[str] | str | None = None,
    allow_ambiguous: bool = False,
    timeout: float = 10.0,
) -> dict[str, Any]:
    payload = {
        "track_index": track_index,
        "query": query,
        "device_type": device_type,
    }
    if preset_query:
        payload["preset_query"] = preset_query
    if browser_path:
        payload["browser_path"] = browser_path
    if allow_ambiguous:
        payload["allow_ambiguous"] = True
    return request_json(
        host=host,
        port=port,
        path="/api/devices/resolve",
        method="POST",
        payload=payload,
        timeout=timeout,
    )
