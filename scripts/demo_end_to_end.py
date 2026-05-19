#!/usr/bin/env python3
from __future__ import annotations
from llmr.schemas import ToolName
from llmr.planner import IntentPlanner, PlanStore
from llmr.ableton_osc import AbletonOSCClient
from llmr.osc_server import StateManager
from llmr.simulator import AbletonSimulator

import json
import os
import sys
import time
from typing import List

# ensure project root is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)



class DummyLLM:
    def __init__(self, response: str) -> None:
        self.response = response

    def complete(self, prompt: str):
        class Result:
            raw_text = ""

        r = Result()
        r.raw_text = self.response
        return r


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def write_svg(lines: List[str], path: str) -> None:
    height = max(200, 18 * (len(lines) + 2))
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}">',
        '<style>text{font-family:monospace;font-size:12px;}</style>',
    ]
    y = 18
    for line in lines:
        parts.append(f'<text x="8" y="{y}">{escape_xml(line)}</text>')
        y += 18
    parts.append("</svg>")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def main() -> None:
    print("Starting Ableton simulator on 127.0.0.1:11000...")
    sim = AbletonSimulator(host="127.0.0.1", port=11000)
    sim.start()
    time.sleep(0.1)

    # Prepare a fake state manager snapshot
    state = StateManager()
    state.update_from_snapshot(
        {
            "tempo": 120.0,
            "tracks": [{"volume": 0.75, "mute": False, "solo": False, "arm": False}],
            "devices": {"0": [{"parameters": [{"value": 0.3}, {"value": 0.5}]}]},
        }
    )

    # Build a canned plan via DummyLLM
    raw = json.dumps(
        {
            "explanation": "Demo: set tempo, adjust volume, fire a clip, tweak device param",
            "confidence": 0.95,
            "calls": [
                {"tool": "set_tempo", "args": {"bpm": 128}},
                {"tool": "set_track_volume", "args": {"track_index": 0, "volume": 0.6}},
                {"tool": "fire_clip", "args": {"track_index": 0, "clip_index": 0}},
                {"tool": "set_device_parameter", "args": {"track_index": 0,
                                                          "device_index": 0, "parameter_index": 0, "value": 0.9}},
            ],
        }
    )

    planner = IntentPlanner(llm=DummyLLM(raw), ableton=AbletonOSCClient("127.0.0.1", 11000))
    plan = planner.plan("demo plan")

    store = PlanStore()
    store.put(plan)

    print(f"Created plan {plan.id} with {len(plan.actions)} actions (confidence={plan.confidence})")

    # Dry-run (show OSC messages)
    print("Dry-run OSC messages:")
    for a in plan.actions:
        print(f"  {a.address} {a.args}")

    # Build undo snapshot against our fake state (best-effort)
    ableton = AbletonOSCClient("127.0.0.1", 11000)
    undo_actions = []
    for a in plan.actions:
        try:
            if a.tool == ToolName.set_device_parameter:
                ti = int(a.args.get("track_index", 0))
                di = int(a.args.get("device_index", 0))
                pi = int(a.args.get("parameter_index", 0))
                prev = state.get_device_parameter(ti, di, pi)
                if prev is not None:
                    undo_actions.append(
                        ableton.to_action(
                            ToolName.set_device_parameter,
                            {"track_index": ti, "device_index": di,
                                "parameter_index": pi, "value": prev},
                        )
                    )
            elif a.tool == ToolName.set_track_volume:
                ti = int(a.args.get("track_index", 0))
                prev = state.get_track_attr(ti, "volume")
                if prev is not None:
                    undo_actions.append(ableton.to_action(
                        ToolName.set_track_volume, {"track_index": ti, "volume": prev}))
        except Exception:
            pass

    if undo_actions:
        store.save_undo(plan.id, undo_actions)

    # Execute actions (send to simulator)
    print("Executing actions...")
    for action in plan.actions:
        ableton.send(action)
        time.sleep(0.05)

    store.mark_executed(plan.id)
    time.sleep(0.1)

    print("Simulator received:")
    for m in sim.received:
        print(" ", m)

    # Undo
    undo = store.get_undo(plan.id)
    if undo:
        print("Performing undo actions...")
        for u in undo:
            ableton.send(u)
            time.sleep(0.05)
    else:
        print("No undo actions available.")

    # Save a simple SVG 'screenshot' summarizing the run
    svg_lines = [
        f"Demo run: plan {plan.id}",
        f"Explanation: {plan.explanation}",
        "Executed actions:",
    ]
    for a in plan.actions:
        svg_lines.append(f"- {a.tool.value} -> {a.address} {a.args}")
    svg_lines.append("")
    svg_lines.append("Simulator received:")
    for m in sim.received:
        svg_lines.append(f"- {m['address']} {m['args']}")

    svg_path = os.path.join(ROOT, "docs", "screenshots", "demo-run.svg")
    write_svg(svg_lines, svg_path)
    print(f"Wrote demo screenshot to {svg_path}")

    try:
        sim.stop()
    except Exception:
        pass


if __name__ == "__main__":
    main()
