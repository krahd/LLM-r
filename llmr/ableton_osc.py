from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Any

from llmr.schemas import Capability, ToolName

try:
    from pythonosc.udp_client import SimpleUDPClient  # type: ignore
except Exception:  # pragma: no cover
    class SimpleUDPClient:  # type: ignore[override]
        def __init__(self, host: str, port: int) -> None:
            self.host = host
            self.port = port
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        def send_message(self, address: str, args: list[Any]) -> None:
            payload = f"{address} {args}".encode("utf-8")
            self._sock.sendto(payload, (self.host, self.port))


@dataclass
class AbletonAction:
    tool: ToolName
    address: str
    args: list[Any]
    description: str
    destructive: bool = False


class AbletonOSCClient:
    def __init__(self, host: str, port: int) -> None:
        self._udp = SimpleUDPClient(host, port)

    def send(self, action: AbletonAction) -> None:
        self._udp.send_message(action.address, action.args)

    def to_action(self, tool: ToolName, args: dict[str, Any]) -> AbletonAction:
        if tool == ToolName.create_midi_track:
            return AbletonAction(tool, "/live/song/create_midi_track", [args.get("index", -1)], "Create MIDI track")
        if tool == ToolName.create_audio_track:
            return AbletonAction(tool, "/live/song/create_audio_track", [args.get("index", -1)], "Create audio track")
        if tool == ToolName.set_tempo:
            bpm = float(args.get("bpm", 120))
            return AbletonAction(tool, "/live/song/set/tempo", [bpm], f"Set tempo to {bpm} BPM")
        if tool == ToolName.fire_clip:
            t, c = int(args.get("track_index", 0)), int(args.get("clip_index", 0))
            return AbletonAction(tool, "/live/clip/fire", [t, c], f"Fire clip {c} on track {t}")
        if tool == ToolName.stop_all_clips:
            return AbletonAction(tool, "/live/song/stop_all_clips", [], "Stop all clips", destructive=True)
        if tool == ToolName.set_track_volume:
            t, v = int(args.get("track_index", 0)), float(args.get("volume", 0.8))
            return AbletonAction(tool, "/live/track/set/volume", [t, v], f"Set track {t} volume to {v}")
        if tool == ToolName.set_track_mute:
            t, m = int(args.get("track_index", 0)), int(bool(args.get("mute", True)))
            return AbletonAction(tool, "/live/track/set/mute", [t, m], f"Set track {t} mute={bool(m)}")
        if tool == ToolName.set_track_solo:
            t, s = int(args.get("track_index", 0)), int(bool(args.get("solo", True)))
            return AbletonAction(tool, "/live/track/set/solo", [t, s], f"Set track {t} solo={bool(s)}")
        if tool == ToolName.arm_track:
            t, a = int(args.get("track_index", 0)), int(bool(args.get("arm", True)))
            return AbletonAction(tool, "/live/track/set/arm", [t, a], f"Set track {t} arm={bool(a)}")
        if tool == ToolName.fire_scene:
            s = int(args.get("scene_index", 0))
            return AbletonAction(tool, "/live/scene/fire", [s], f"Fire scene {s}")
        raise ValueError(f"Unsupported tool: {tool}")


def capabilities() -> list[Capability]:
    return [
        Capability(tool=ToolName.create_midi_track, description="Create MIDI track", args_schema={"index": "int (optional)"}),
        Capability(tool=ToolName.create_audio_track, description="Create audio track", args_schema={"index": "int (optional)"}),
        Capability(tool=ToolName.set_tempo, description="Set global tempo", args_schema={"bpm": "float"}),
        Capability(tool=ToolName.fire_clip, description="Launch clip slot", args_schema={"track_index": "int", "clip_index": "int"}),
        Capability(tool=ToolName.stop_all_clips, description="Stop all running clips", args_schema={}, destructive=True),
        Capability(tool=ToolName.set_track_volume, description="Set track volume", args_schema={"track_index": "int", "volume": "0..1"}),
        Capability(tool=ToolName.set_track_mute, description="Toggle mute", args_schema={"track_index": "int", "mute": "bool"}),
        Capability(tool=ToolName.set_track_solo, description="Toggle solo", args_schema={"track_index": "int", "solo": "bool"}),
        Capability(tool=ToolName.arm_track, description="Arm/disarm recording", args_schema={"track_index": "int", "arm": "bool"}),
        Capability(tool=ToolName.fire_scene, description="Launch scene", args_schema={"scene_index": "int"}),
    ]
