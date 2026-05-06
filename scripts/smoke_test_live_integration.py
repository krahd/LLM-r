#!/usr/bin/env python3
"""Smoke-test AbletonOSC plus LLMRDeviceBridge against a disposable Live set.

By default this is a read-only preflight: it checks AbletonOSC replies and the
Device Bridge health/list/resolve endpoints. Pass --execute to also set tempo
and load one browser item onto a track.
"""

from __future__ import annotations

import argparse
import json
import socket
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pythonosc.udp_client import SimpleUDPClient


def http_json(url: str, *, method: str = "GET", body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if body is not None else {},
        method=method,
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def device_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "track_index": args.track_index,
        "query": args.device_query,
        "device_type": args.device_type,
    }
    if args.preset_query:
        payload["preset_query"] = args.preset_query
    if args.browser_path:
        payload["browser_path"] = [part.strip()
                                   for part in args.browser_path.split(">") if part.strip()]
    if args.allow_ambiguous:
        payload["allow_ambiguous"] = True
    return payload


def check_device_bridge(args: argparse.Namespace) -> bool:
    base = f"http://{args.bridge_host}:{args.bridge_port}"
    print(f"Device Bridge: checking {base}/health")
    try:
        health = http_json(f"{base}/health")
    except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"  FAIL: {exc}")
        return False
    print(f"  OK: {health}")

    query = urllib.parse.urlencode({"query": args.device_query, "device_type": args.device_type})
    print(f"Device Bridge: listing candidates for {args.device_query!r}")
    try:
        devices = http_json(f"{base}/api/devices/list?{query}")
    except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"  FAIL: {exc}")
        return False
    print(f"  OK: {devices.get('count', 0)} candidate(s)")
    for item in devices.get("devices", [])[:5]:
        path = " > ".join(item.get("path", []))
        print(f"    - {item.get('name')} ({path})")

    print("Device Bridge: resolving load request without mutation")
    try:
        resolved = http_json(f"{base}/api/devices/resolve",
                             method="POST", body=device_payload(args))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"  FAIL: HTTP {exc.code}: {detail}")
        return False
    except (OSError, urllib.error.URLError) as exc:
        print(f"  FAIL: {exc}")
        return False
    print(f"  OK: {resolved.get('selected_item')} ({' > '.join(resolved.get('path', []))})")
    return True


def check_abletonosc(args: argparse.Namespace) -> bool:
    print(f"AbletonOSC: checking replies on {args.osc_host}:{args.osc_port}")
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        recv_sock.bind((args.reply_host, args.reply_port))
        recv_sock.settimeout(args.reply_timeout)
    except OSError as exc:
        print(f"  FAIL: cannot bind reply socket {args.reply_host}:{args.reply_port}: {exc}")
        return False

    client = SimpleUDPClient(args.osc_host, args.osc_port)
    client.send_message("/live/song/get/tempo", [])
    try:
        data, source = recv_sock.recvfrom(4096)
    except socket.timeout:
        print("  FAIL: no tempo reply received")
        recv_sock.close()
        return False
    finally:
        recv_sock.close()

    print(f"  OK: received {len(data)} byte OSC reply from {source[0]}:{source[1]}")
    if len(data) >= 12:
        try:
            print(f"  Raw tempo-like float: {struct.unpack('>f', data[-4:])[0]:.2f}")
        except struct.error:
            pass
    return True


def execute_mutations(args: argparse.Namespace) -> bool:
    print("Executing mutations in the current Live set.")
    print("Use only a disposable Live set for this step.")

    client = SimpleUDPClient(args.osc_host, args.osc_port)
    print(f"  AbletonOSC: setting tempo to {args.tempo}")
    client.send_message("/live/song/set/tempo", [float(args.tempo)])
    time.sleep(0.2)

    if args.skip_device_load:
        return True

    base = f"http://{args.bridge_host}:{args.bridge_port}"
    payload = device_payload(args)
    print(f"  Device Bridge: loading {args.device_query!r} on track {args.track_index}")
    try:
        loaded = http_json(f"{base}/api/devices/load", method="POST", body=payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"  FAIL: HTTP {exc.code}: {detail}")
        return False
    except (OSError, urllib.error.URLError) as exc:
        print(f"  FAIL: {exc}")
        return False
    print(f"  OK: {loaded}")
    return True


def write_report(args: argparse.Namespace, result: dict[str, Any]) -> None:
    if not args.report_json:
        return
    report_path = Path(args.report_json)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    existing: list[Any] = []
    if report_path.exists():
        try:
            loaded = json.loads(report_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                existing = loaded
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            existing = []

    existing.append(result)
    report_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=11000)
    parser.add_argument("--reply-host", default="127.0.0.1")
    parser.add_argument("--reply-port", type=int, default=11001)
    parser.add_argument("--reply-timeout", type=float, default=1.5)
    parser.add_argument("--bridge-host", default="127.0.0.1")
    parser.add_argument("--bridge-port", type=int, default=8788)
    parser.add_argument("--device-query", default="Drum Rack")
    parser.add_argument("--device-type", default="drum")
    parser.add_argument("--preset-query", default="")
    parser.add_argument("--browser-path", default="",
                        help="Exact candidate path separated by ' > '")
    parser.add_argument("--allow-ambiguous", action="store_true")
    parser.add_argument("--track-index", type=int, default=0)
    parser.add_argument("--tempo", type=float, default=120.0)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--skip-device-load", action="store_true")
    parser.add_argument("--live-version", default="",
                        help="Manual label for tested Ableton Live version")
    parser.add_argument("--run-label", default="", help="Optional freeform label for this run")
    parser.add_argument("--report-json", default="",
                        help="Optional path to append JSON smoke-test reports")
    args = parser.parse_args()

    if args.live_version:
        print(f"Live version label: {args.live_version}")
    if args.run_label:
        print(f"Run label: {args.run_label}")

    bridge_ok = check_device_bridge(args)
    osc_ok = check_abletonosc(args)
    mutation_ok = True
    if not (bridge_ok and osc_ok):
        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "live_version": args.live_version,
            "run_label": args.run_label,
            "execute": args.execute,
            "bridge_ok": bridge_ok,
            "osc_ok": osc_ok,
            "mutation_ok": False,
            "success": False,
            "device_query": args.device_query,
            "device_type": args.device_type,
        }
        write_report(args, result)
        return 1

    if args.execute:
        mutation_ok = execute_mutations(args)
        if not mutation_ok:
            result = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "live_version": args.live_version,
                "run_label": args.run_label,
                "execute": args.execute,
                "bridge_ok": bridge_ok,
                "osc_ok": osc_ok,
                "mutation_ok": mutation_ok,
                "success": False,
                "device_query": args.device_query,
                "device_type": args.device_type,
            }
            write_report(args, result)
            return 1

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "live_version": args.live_version,
        "run_label": args.run_label,
        "execute": args.execute,
        "bridge_ok": bridge_ok,
        "osc_ok": osc_ok,
        "mutation_ok": mutation_ok,
        "success": True,
        "device_query": args.device_query,
        "device_type": args.device_type,
    }
    write_report(args, result)

    print("Smoke test complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
