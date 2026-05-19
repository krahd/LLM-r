from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from typing import Any

from llmr.ableton_osc import AbletonAction


@dataclass
class RemoteScriptClient:
    """Simple JSON-over-UDP client targeting a MIDI Remote Script bridge.

    The payload is a small JSON object: {"address": "...", "args": [...], "tool": "..."}
    The remote script is expected to parse this and call into the Live Object Model.
    """

    host: str = "127.0.0.1"
    port: int = 20000

    def __post_init__(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def build_payload(self, action: AbletonAction) -> str:
        payload = {"address": action.address, "args": action.args, "tool": action.tool.value}
        return json.dumps(payload)

    def send(self, action: AbletonAction) -> None:
        data = self.build_payload(action).encode("utf-8")
        try:
            self._sock.sendto(data, (self.host, self.port))
        except Exception:
            # best-effort send; remote script may be offline during development
            pass
