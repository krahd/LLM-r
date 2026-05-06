from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Callable

try:
    from pythonosc.dispatcher import Dispatcher  # type: ignore
    from pythonosc.osc_server import ThreadingOSCUDPServer  # type: ignore
except ImportError:  # pragma: no cover
    Dispatcher = None  # type: ignore[assignment]
    ThreadingOSCUDPServer = None  # type: ignore[assignment]


OscReplyHandler = Callable[[str, list[Any]], None]


class OscReplyListener:
    def __init__(self, host: str, port: int, handler: OscReplyHandler) -> None:
        self.host = host
        self.port = port
        self._handler = handler
        self._server: ThreadingOSCUDPServer | None = None
        self._thread: threading.Thread | None = None
        self._error: str | None = None
        self._started_at: str | None = None

    def start(self) -> None:
        if self._server is not None:
            return
        if Dispatcher is None or ThreadingOSCUDPServer is None:
            self._error = "python-osc is required for OSC reply listening"
            return
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._handle)
        try:
            self._server = ThreadingOSCUDPServer((self.host, self.port), dispatcher)
        except OSError as exc:
            self._server = None
            self._error = str(exc)
            return
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._error = None

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        self._server = None
        self._thread = None

    def status(self) -> dict[str, Any]:
        return {
            "enabled": True,
            "listening": self._server is not None,
            "host": self.host,
            "port": self.port,
            "started_at": self._started_at,
            "error": self._error,
        }

    def _handle(self, address: str, *args: Any) -> None:
        self._handler(address, list(args))
