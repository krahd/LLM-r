from __future__ import annotations

import json
import threading
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

try:
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
except Exception:  # pragma: no cover
    Dispatcher = None
    ThreadingOSCUDPServer = None


@dataclass
class StateManager:
    """Holds a simple in-memory snapshot of the Live session state.

    The M4L device or simulator is expected to send a JSON snapshot to
    the `/llmr/state` OSC address with a single string argument containing
    the JSON object. This keeps state in sync for planning and undo.
    """

    _lock: threading.Lock = threading.Lock()
    _state: dict[str, Any] = None

    def __post_init__(self) -> None:
        self._state = {
            "tempo": 120.0,
            "transport": {"playing": False, "recording": False, "metronome": False},
            "tracks": [],
            "scenes": [],
            "selected_track": 0,
            "clips": {},
            "devices": {},
        }

    def update_from_snapshot(self, snapshot: dict[str, Any]) -> None:
        with self._lock:
            # Merge shallow keys
            for k, v in snapshot.items():
                self._state[k] = v

    def get_state(self) -> dict[str, Any]:
        with self._lock:
            return deepcopy(self._state)

    def get_device_parameter(self, track_index: int, device_index: int, parameter_index: int) -> Any:
        with self._lock:
            devs = self._state.get("devices", {}).get(str(track_index), [])
            if device_index < 0 or device_index >= len(devs):
                return None
            params = devs[device_index].get("parameters", [])
            if parameter_index < 0 or parameter_index >= len(params):
                return None
            return params[parameter_index].get("value")

    def set_device_parameter(self, track_index: int, device_index: int, parameter_index: int, value: Any) -> None:
        with self._lock:
            devs = self._state.setdefault("devices", {}).setdefault(str(track_index), [])
            while len(devs) <= device_index:
                devs.append({"parameters": []})
            params = devs[device_index].setdefault("parameters", [])
            while len(params) <= parameter_index:
                params.append({"value": None})
            params[parameter_index]["value"] = value

    def get_track_attr(self, track_index: int, attr: str) -> Any:
        with self._lock:
            tracks = self._state.get("tracks", [])
            if track_index < 0 or track_index >= len(tracks):
                return None
            return tracks[track_index].get(attr)


def _handle_state_snapshot(state_manager: StateManager):
    def _inner(addr: str, json_str: str) -> None:
        try:
            data = json.loads(json_str)
        except Exception:
            return
        state_manager.update_from_snapshot(data)

    return _inner


def start_osc_server(host: str, port: int, state_manager: StateManager):
    if Dispatcher is None or ThreadingOSCUDPServer is None:
        raise RuntimeError("python-osc is required to run the OSC server")

    disp = Dispatcher()
    disp.map("/llmr/state", _handle_state_snapshot(state_manager))

    server = ThreadingOSCUDPServer((host, port), disp)

    thr = threading.Thread(target=server.serve_forever, daemon=True)
    thr.start()
    return server


def stop_osc_server(server) -> None:
    try:
        server.shutdown()
        server.server_close()
    except Exception:
        pass
