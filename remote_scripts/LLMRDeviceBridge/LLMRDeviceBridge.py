import json
import threading
import traceback
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

try:
    from _Framework.ControlSurface import ControlSurface
except ImportError:
    from ableton.v2.control_surface import ControlSurface


HOST = "127.0.0.1"
PORT = 8788
MAX_BROWSER_ITEMS = 6000


def _json_response(handler, status, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class _BridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, _format, *args):
        return

    @property
    def bridge(self):
        return self.server.bridge

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            _json_response(self, 200, {"status": "ok", "bridge": "LLMRDeviceBridge"})
            return
        if parsed.path == "/api/devices/list":
            params = parse_qs(parsed.query)
            query = (params.get("query") or [""])[0]
            device_type = (params.get("device_type") or ["all"])[0]
            try:
                payload = self.bridge.run_on_live_thread(
                    lambda: self.bridge.list_devices(query=query, device_type=device_type)
                )
                _json_response(self, 200, payload)
            except Exception as exc:
                _json_response(self, 500, {"error": str(exc)})
            return
        _json_response(self, 404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/devices/load":
            _json_response(self, 404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            _json_response(self, 400, {"error": "invalid Content-Length"})
            return
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            request = json.loads(raw)
        except Exception:
            _json_response(self, 400, {"error": "invalid JSON body"})
            return
        try:
            payload = self.bridge.run_on_live_thread(lambda: self.bridge.load_device(request))
            _json_response(self, 200, payload)
        except LookupError as exc:
            _json_response(self, 404, {"error": str(exc)})
        except ValueError as exc:
            _json_response(self, 400, {"error": str(exc)})
        except Exception as exc:
            _json_response(self, 500, {"error": str(exc)})


class _BridgeServer(ThreadingHTTPServer):
    allow_reuse_address = True

    def __init__(self, server_address, handler_class, bridge):
        self.bridge = bridge
        ThreadingHTTPServer.__init__(self, server_address, handler_class)


class LLMRDeviceBridge(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._server = None
        self._server_thread = None
        self._start_server()

    def disconnect(self):
        self._stop_server()
        ControlSurface.disconnect(self)

    def _start_server(self):
        if self._server:
            return
        try:
            self._server = _BridgeServer((HOST, PORT), _BridgeHandler, self)
        except OSError as exc:
            self.log_message("LLM-r Device Bridge could not bind %s:%d: %s" % (HOST, PORT, exc))
            self._server = None
            return
        self._server_thread = threading.Thread(target=self._server.serve_forever)
        self._server_thread.daemon = True
        self._server_thread.start()
        self.log_message("LLM-r Device Bridge listening on %s:%d" % (HOST, PORT))

    def _stop_server(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        self._server_thread = None

    def run_on_live_thread(self, callback, timeout=10.0):
        done = threading.Event()
        result = {}

        def wrapped():
            try:
                result["value"] = callback()
            except Exception:
                result["error"] = traceback.format_exc()
            finally:
                done.set()

        self.schedule_message(0, wrapped)
        if not done.wait(timeout):
            raise RuntimeError("Timed out waiting for Live API")
        if "error" in result:
            raise RuntimeError(result["error"])
        return result.get("value")

    def list_devices(self, query="", device_type="all"):
        query = str(query or "").strip()
        matches = []
        for item in self._search_browser(query, device_type, limit=40):
            matches.append(
                {
                    "name": getattr(item, "name", ""),
                    "is_loadable": bool(getattr(item, "is_loadable", False)),
                }
            )
        return {"devices": matches, "count": len(matches)}

    def load_device(self, request):
        track_index = int(request.get("track_index", 0))
        query = str(request.get("query") or request.get("device_name") or "").strip()
        device_type = str(request.get("device_type") or "instrument").strip()
        if not query:
            raise ValueError("'query' is required")

        track = self._track_at(track_index)
        item = self._find_browser_item(query, device_type)
        if item is None:
            raise LookupError("No loadable browser item matched '%s'" % query)

        self.song().view.selected_track = track
        self.application().browser.load_item(item)
        return {
            "status": "loaded",
            "track_index": track_index,
            "query": query,
            "device_type": self._normalize_device_type(device_type),
            "loaded_item": getattr(item, "name", query),
        }

    def _track_at(self, track_index):
        tracks = list(self.song().tracks)
        if track_index < 0 or track_index >= len(tracks):
            raise ValueError("Track index %d is out of range" % track_index)
        return tracks[track_index]

    def _find_browser_item(self, query, device_type):
        matches = self._search_browser(query, device_type, limit=1)
        return matches[0] if matches else None

    def _search_browser(self, query, device_type, limit):
        normalized_query = self._normalize_name(query)
        candidates = []
        for root in self._browser_roots(device_type):
            stack = deque([root])
            scanned = 0
            while stack and scanned < MAX_BROWSER_ITEMS:
                item = stack.popleft()
                scanned += 1
                name = getattr(item, "name", "")
                if bool(getattr(item, "is_loadable", False)):
                    score = self._match_score(normalized_query, name)
                    if score:
                        candidates.append((score, name.lower(), item))
                        if len(candidates) >= limit and score == 3:
                            return [row[2] for row in sorted(candidates, key=lambda row: (-row[0], row[1]))[:limit]]
                try:
                    children = list(getattr(item, "children", []) or [])
                except Exception:
                    children = []
                stack.extend(children)
        candidates.sort(key=lambda row: (-row[0], row[1]))
        return [row[2] for row in candidates[:limit]]

    def _browser_roots(self, device_type):
        browser = self.application().browser
        normalized = self._normalize_device_type(device_type)
        by_type = {
            "instrument": ("instruments",),
            "audio_effect": ("audio_effects",),
            "midi_effect": ("midi_effects",),
            "plugin": ("plugins",),
            "drum": ("drums", "instruments"),
            "all": (
                "sounds",
                "drums",
                "instruments",
                "audio_effects",
                "midi_effects",
                "plugins",
                "max_for_live",
            ),
        }
        roots = []
        for attr in by_type.get(normalized, by_type["all"]):
            try:
                root = getattr(browser, attr)
            except Exception:
                root = None
            if root is not None:
                roots.append(root)
        return roots

    def _normalize_device_type(self, value):
        raw = str(value or "instrument").strip().lower().replace(" ", "_")
        aliases = {
            "instruments": "instrument",
            "audio_effects": "audio_effect",
            "effect": "audio_effect",
            "effects": "audio_effect",
            "midi_effects": "midi_effect",
            "plugins": "plugin",
            "drums": "drum",
        }
        raw = aliases.get(raw, raw)
        if raw in ("instrument", "audio_effect", "midi_effect", "plugin", "drum", "all"):
            return raw
        return "instrument"

    def _normalize_name(self, value):
        return "".join(ch for ch in str(value or "").lower() if ch.isalnum())

    def _match_score(self, normalized_query, name):
        normalized_name = self._normalize_name(name)
        if not normalized_query:
            return 1
        if normalized_name == normalized_query:
            return 3
        if normalized_query in normalized_name:
            return 2
        return 0
