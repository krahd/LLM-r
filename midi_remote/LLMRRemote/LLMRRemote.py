"""Control Surface scaffold for LLM-r remote script.

This file is intentionally conservative so it can be inspected outside of Live.
Adapt and extend when integrating into a specific Live version.
"""
from __future__ import annotations

try:
    # Live provides a ControlSurface base in its runtime; import when available.
    from _Framework.ControlSurface import ControlSurface  # type: ignore
except Exception:
    # Fallback stub for offline inspection / testing
    class ControlSurface:  # type: ignore
        def __init__(self, *a, **k):
            pass


class LLMRRemote(ControlSurface):
    """Minimal ControlSurface subclass that starts the LLmR bridge.

    Live expects a top-level class inside the remote script package. This
    scaffold will attempt to import and start the `LLmRBridge` when a valid
    `c_instance` with a `song()` attribute is available.
    """

    def __init__(self, c_instance=None):
        super().__init__()
        self.c_instance = c_instance
        self.song = None
        self.bridge = None
        try:
            if self.c_instance is not None:
                # In Live, c_instance.song() returns the song object.
                self.song = self.c_instance.song()
        except Exception:
            self.song = None

        try:
            # Local relative import to avoid top-level dependency on Live.
            from ..bridge_example import LLmRBridge

            if self.song is not None:
                self.bridge = LLmRBridge(self.song)
        except Exception:
            # Running outside Live or missing bridge implementation.
            self.bridge = None

    def disconnect(self):
        try:
            if self.bridge:
                self.bridge.stop()
        except Exception:
            pass
