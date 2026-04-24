from __future__ import annotations

import json
import threading
from typing import Any

try:
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
    from pythonosc.udp_client import SimpleUDPClient
except Exception:  # pragma: no cover
    Dispatcher = None
    ThreadingOSCUDPServer = None
    SimpleUDPClient = None


class AbletonSimulator:
    """A tiny simulator that listens for OSC messages and updates an internal state.

    This is useful for local development and CI to validate OSC messages without a
    real Ableton instance.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 11000) -> None:
        self.host = host
        self.port = port
        self._disp = Dispatcher() if Dispatcher is not None else None
        self._server = None
        self._thread = None
        self.received: list[dict[str, Any]] = []
        self.state: dict[str, Any] = {"tracks": [], "devices": {}, "transport": {"playing": False}}

    def _generic_handler(self, addr: str, *args):
        self.received.append({"address": addr, "args": args})
        # allow simple state updates from snapshot
        if addr == "/llmr/state" and args:
            try:
                data = json.loads(args[0])
                self.state.update(data)
            except Exception:
                pass

    def start(self) -> None:
        if ThreadingOSCUDPServer is None:
            raise RuntimeError("python-osc is required for simulator")
        self._disp.map("/llmr/state", self._generic_handler)
        # catch-all for live addresses
        self._disp.map("/live/*", self._generic_handler)
        self._server = ThreadingOSCUDPServer((self.host, self.port), self._disp)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        try:
            if self._server:
                self._server.shutdown()
                self._server.server_close()
        except Exception:
            pass
