import json
import threading
import traceback
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

try:
    from _Framework.ControlSurface import ControlSurface
except ImportError:
    try:
        from ableton.v3.control_surface import ControlSurface
    except ImportError:
        from ableton.v2.control_surface import ControlSurface


HOST = "127.0.0.1"
PORT = 8788
MAX_BROWSER_ITEMS = 6000


class AmbiguousDeviceError(Exception):
    def __init__(self, query, candidates):
        Exception.__init__(self, "Multiple browser items matched '%s'" % query)
        self.query = query
        self.candidates = candidates


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
        if parsed.path not in ("/api/devices/load", "/api/devices/resolve"):
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
            if parsed.path == "/api/devices/resolve":
                payload = self.bridge.run_on_live_thread(
                    lambda: self.bridge.resolve_device(request)
                )
            else:
                payload = self.bridge.run_on_live_thread(lambda: self.bridge.load_device(request))
            _json_response(self, 200, payload)
        except AmbiguousDeviceError as exc:
            _json_response(self, 409, {"error": str(exc), "candidates": exc.candidates})
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

    def _log(self, message):
        # Compatibility shim: ableton.v3 may not expose log_message.
        if hasattr(self, "log_message"):
            self.log_message(message)
        else:
            import sys
            print("[LLMRDeviceBridge] " + str(message), file=sys.stderr)

    def disconnect(self):
        self._stop_server()
        ControlSurface.disconnect(self)

    def _start_server(self):
        if self._server:
            return
        try:
            self._server = _BridgeServer((HOST, PORT), _BridgeHandler, self)
        except OSError as exc:
            self._log("LLM-r Device Bridge could not bind %s:%d: %s" % (HOST, PORT, exc))
            self._server = None
            return
        self._server_thread = threading.Thread(target=self._server.serve_forever)
        self._server_thread.daemon = True
        self._server_thread.start()
        self._log("LLM-r Device Bridge listening on %s:%d" % (HOST, PORT))

    def _stop_server(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        self._server_thread = None

    def _schedule_on_live_thread(self, callback):
        # Live 12 (ableton.v3) exposes `call_later`; older versions use
        # `schedule_message`.  Fall back gracefully whichever is available.
        if hasattr(self, "call_later"):
            self.call_later(0, callback)
        else:
            self.schedule_message(0, callback)

    def run_on_live_thread(self, callback, timeout=10.0):
        done = threading.Event()
        result = {}

        def wrapped():
            try:
                result["value"] = callback()
            except Exception as exc:
                result["error"] = exc
                result["traceback"] = traceback.format_exc()
            finally:
                done.set()

        self._schedule_on_live_thread(wrapped)
        if not done.wait(timeout):
            raise RuntimeError("Timed out waiting for Live API")
        if "error" in result:
            self._log("LLM-r Device Bridge Live callback failed:\n%s" % result.get("traceback", ""))
            raise result["error"]
        return result.get("value")

    def list_devices(self, query="", device_type="all"):
        query = str(query or "").strip()
        matches = []
        for item, path, score in self._search_browser_matches(query, device_type, limit=40):
            matches.append(
                {
                    "name": getattr(item, "name", ""),
                    "path": path,
                    "device_type": self._normalize_device_type(device_type),
                    "score": score,
                    "is_loadable": bool(getattr(item, "is_loadable", False)),
                }
            )
        return {"devices": matches, "count": len(matches)}

    def load_device(self, request):
        resolved = self._resolve_device_item(request)
        track = resolved["track"]
        item = resolved["item"]
        self.song().view.selected_track = track
        self.application().browser.load_item(item)
        return {
            "status": "loaded",
            "track_index": resolved["track_index"],
            "query": resolved["query"],
            "preset_query": resolved["preset_query"],
            "device_type": resolved["device_type"],
            "loaded_item": getattr(item, "name", resolved["query"]),
            "path": resolved["path"],
            "score": resolved["score"],
            "selection_mode": resolved["selection_mode"],
        }

    def resolve_device(self, request):
        resolved = self._resolve_device_item(request)
        return {
            "status": "resolved",
            "track_index": resolved["track_index"],
            "query": resolved["query"],
            "preset_query": resolved["preset_query"],
            "device_type": resolved["device_type"],
            "selected_item": getattr(resolved["item"], "name", resolved["query"]),
            "path": resolved["path"],
            "score": resolved["score"],
            "selection_mode": resolved["selection_mode"],
            "is_loadable": bool(getattr(resolved["item"], "is_loadable", False)),
        }

    def _resolve_device_item(self, request):
        track_index = int(request.get("track_index", 0))
        query = str(request.get("query") or request.get("device_name") or "").strip()
        preset_query = str(request.get("preset_query") or request.get("preset") or "").strip()
        device_type = self._normalize_device_type(request.get("device_type") or "instrument")
        browser_path = self._coerce_path(request.get("browser_path") or request.get("path"))
        if not query and not browser_path:
            raise ValueError("'query' is required")

        track = self._track_at(track_index)
        allow_ambiguous = self._allow_ambiguous(request.get("allow_ambiguous", False))
        selection_mode = "query"
        if browser_path:
            match = self._find_browser_item_by_path(browser_path, device_type)
            if match is None:
                raise LookupError("No loadable browser item matched path '%s'" %
                                  " > ".join(browser_path))
            item, path = match
            score = 3
            selection_mode = "browser_path"
        elif preset_query:
            matches = self._preset_matches(query, preset_query, device_type)
            if not matches:
                raise LookupError(
                    "No preset '%s' matched browser item '%s'" % (preset_query, query)
                )
            item, path, score = self._select_match(
                query + " / " + preset_query,
                matches,
                allow_ambiguous,
                device_type,
            )
            selection_mode = "preset"
        else:
            matches = self._search_browser_matches(query, device_type, limit=8)
            if not matches:
                raise LookupError("No loadable browser item matched '%s'" % query)
            item, path, score = self._select_match(query, matches, allow_ambiguous, device_type)

        return {
            "track": track,
            "track_index": track_index,
            "query": query or getattr(item, "name", ""),
            "preset_query": preset_query or None,
            "device_type": device_type,
            "item": item,
            "path": path,
            "score": score,
            "selection_mode": selection_mode,
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
        return [match[0] for match in self._search_browser_matches(query, device_type, limit)]

    def _search_browser_matches(self, query, device_type, limit):
        normalized_query = self._normalize_name(query)
        candidates = []
        for root in self._browser_roots(device_type):
            root_name = getattr(root, "name", "") or self._normalize_device_type(device_type)
            stack = deque([(root, [root_name])])
            scanned = 0
            while stack and scanned < MAX_BROWSER_ITEMS:
                item, path = stack.popleft()
                scanned += 1
                name = getattr(item, "name", "")
                if bool(getattr(item, "is_loadable", False)):
                    score = self._match_score(normalized_query, name)
                    if score:
                        item_path = path if path and path[-1] == name else path + [name]
                        candidates.append((score, name.lower(), item, item_path))
                        if len(candidates) >= limit and score == 3:
                            rows = sorted(candidates, key=lambda row: (-row[0], row[1]))[:limit]
                            return [(row[2], row[3], row[0]) for row in rows]
                try:
                    children = list(getattr(item, "children", []) or [])
                except Exception:
                    children = []
                for child in children:
                    child_name = getattr(child, "name", "")
                    child_path = path + ([child_name] if child_name else [])
                    stack.append((child, child_path))
        candidates.sort(key=lambda row: (-row[0], row[1]))
        return [(row[2], row[3], row[0]) for row in candidates[:limit]]

    def _candidate_payload(self, item, path, score, device_type="all"):
        return {
            "name": getattr(item, "name", ""),
            "path": path,
            "score": score,
            "device_type": self._normalize_device_type(device_type),
            "is_loadable": bool(getattr(item, "is_loadable", False)),
        }

    def _select_match(self, query, matches, allow_ambiguous, device_type):
        top_score = matches[0][2]
        tied = [match for match in matches if match[2] == top_score]
        if len(tied) > 1 and not allow_ambiguous:
            raise AmbiguousDeviceError(
                query,
                [self._candidate_payload(match[0], match[1], match[2], device_type)
                 for match in tied[:8]],
            )
        return matches[0]

    def _preset_matches(self, query, preset_query, device_type):
        normalized_query = self._normalize_name(query)
        matches = []
        for item, path, score in self._search_browser_matches(preset_query, device_type, limit=40):
            if normalized_query and not self._path_contains(path, normalized_query):
                continue
            matches.append((item, path, score))
        return matches

    def _find_browser_item_by_path(self, requested_path, device_type):
        normalized_path = [self._normalize_path_segment(segment) for segment in requested_path]
        for root in self._browser_roots(device_type):
            root_name = getattr(root, "name", "") or self._normalize_device_type(device_type)
            root_key = self._normalize_path_segment(root_name)
            remaining = normalized_path
            if remaining and remaining[0] == root_key:
                remaining = remaining[1:]
            match = self._follow_path(root, [root_name], remaining)
            if match is not None:
                return match
        return None

    def _follow_path(self, item, path, remaining):
        if not remaining:
            if bool(getattr(item, "is_loadable", False)):
                item_name = getattr(item, "name", "")
                item_path = path if path and path[-1] == item_name else path + [item_name]
                return item, item_path
            return None
        try:
            children = list(getattr(item, "children", []) or [])
        except Exception:
            children = []
        target = remaining[0]
        for child in children:
            child_name = getattr(child, "name", "")
            if self._normalize_path_segment(child_name) == target:
                child_path = path + ([child_name] if child_name else [])
                return self._follow_path(child, child_path, remaining[1:])
        return None

    def _path_contains(self, path, normalized_query):
        for segment in path:
            if normalized_query in self._normalize_name(segment):
                return True
        return False

    def _coerce_path(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return [str(segment).strip() for segment in value if str(segment).strip()]
        if isinstance(value, tuple):
            return [str(segment).strip() for segment in value if str(segment).strip()]
        raw = str(value).strip()
        if not raw:
            return []
        if ">" in raw:
            return [segment.strip() for segment in raw.split(">") if segment.strip()]
        return [segment.strip() for segment in raw.split("/") if segment.strip()]

    def _allow_ambiguous(self, value):
        return value is True or str(value).strip().lower() in ("1", "true", "yes", "on")

    def _normalize_path_segment(self, value):
        return str(value or "").strip().lower()

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
