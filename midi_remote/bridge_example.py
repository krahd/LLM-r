"""
Example bridge code for an Ableton MIDI Remote Script.

This is an annotated example — adapt it into your ControlSurface package.

Note: run inside Live's Python environment; do not import third-party packages.
"""
import json
import socket
import threading


class LLmRBridge:
    def __init__(self, song, host="127.0.0.1", port=20000):
        self.song = song
        self.host = host
        self.port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self.host, self.port))
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self):
        while self._running:
            try:
                data, addr = self._sock.recvfrom(65536)
                try:
                    msg = json.loads(data.decode("utf-8"))
                    self._handle(msg)
                except Exception:
                    # ignore parse errors
                    pass
            except Exception:
                break

    def _handle(self, msg):
        # msg example: {"address": "/live/song/set/tempo", "args": [128], "tool":"set_tempo"}
        addr = msg.get("address")
        args = msg.get("args", [])
        # map addresses to Live API calls; this is a tiny example
        if addr == "/live/song/set/tempo":
            try:
                bpm = float(args[0])
                # schedule on main thread if required by Live API
                self.song.bpm = bpm
            except Exception:
                pass
        elif addr == "/live/clip/fire":
            try:
                t = int(args[0])
                c = int(args[1])
                track = self.song.tracks[t]
                slot = track.clip_slots[c]
                slot.fire()
            except Exception:
                pass

    def stop(self):
        self._running = False
        try:
            self._sock.close()
        except Exception:
            pass
