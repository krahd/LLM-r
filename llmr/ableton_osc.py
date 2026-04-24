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
        if tool == ToolName.start_transport:
            return AbletonAction(tool, "/live/transport/play", [], "Start transport")
        if tool == ToolName.stop_transport:
            return AbletonAction(tool, "/live/transport/stop", [], "Stop transport")
        if tool == ToolName.start_recording:
            return AbletonAction(tool, "/live/transport/record", [1], "Start recording")
        if tool == ToolName.stop_recording:
            return AbletonAction(tool, "/live/transport/record", [0], "Stop recording")
        if tool == ToolName.save_set:
            return AbletonAction(tool, "/live/song/save", [], "Save current set")
        if tool == ToolName.export_audio:
            path = args.get("path", "")
            return AbletonAction(tool, "/live/song/export_audio", [path], "Export audio (may be long-running)", destructive=True)
        if tool == ToolName.duplicate_clip:
            t, c = int(args.get("track_index", 0)), int(args.get("clip_index", 0))
            return AbletonAction(tool, "/live/clip/duplicate", [t, c], f"Duplicate clip {c} on track {t}")
        if tool == ToolName.delete_clip:
            t, c = int(args.get("track_index", 0)), int(args.get("clip_index", 0))
            return AbletonAction(tool, "/live/clip/delete", [t, c], f"Delete clip {c} on track {t}", destructive=True)
        if tool == ToolName.set_device_parameter:
            t = int(args.get("track_index", 0))
            d = int(args.get("device_index", 0))
            p = int(args.get("parameter_index", 0))
            v = float(args.get("value", 0.0))
            return AbletonAction(tool, "/live/device/set/parameter", [t, d, p, v], f"Set device param {p} on device {d} track {t} to {v}")
        if tool == ToolName.get_device_parameter:
            t = int(args.get("track_index", 0))
            d = int(args.get("device_index", 0))
            p = int(args.get("parameter_index", 0))
            return AbletonAction(tool, "/live/device/get/parameter", [t, d, p], f"Get device param {p} on device {d} track {t}")
        if tool == ToolName.create_scene:
            idx = int(args.get("index", -1))
            return AbletonAction(tool, "/live/scene/create", [idx], "Create scene")
        if tool == ToolName.duplicate_scene:
            idx = int(args.get("scene_index", 0))
            return AbletonAction(tool, "/live/scene/duplicate", [idx], f"Duplicate scene {idx}")
        if tool == ToolName.move_clip:
            st, sc, dt, dc = int(args.get("src_track", 0)), int(args.get("src_clip", 0)), int(
                args.get("dest_track", 0)), int(args.get("dest_clip", 0))
            return AbletonAction(tool, "/live/clip/move", [st, sc, dt, dc], f"Move clip {sc} from track {st} to clip {dc} on track {dt}", destructive=True)
        if tool == ToolName.select_track:
            t = int(args.get("track_index", 0))
            return AbletonAction(tool, "/live/track/select", [t], f"Select track {t}")
        if tool == ToolName.rename_track:
            t = int(args.get("track_index", 0))
            name = str(args.get("name", ""))
            return AbletonAction(tool, "/live/track/rename", [t, name], f"Rename track {t} to {name}")
        if tool == ToolName.toggle_metronome:
            on = int(bool(args.get("on", True)))
            return AbletonAction(tool, "/live/transport/metronome", [on], f"Set metronome {bool(on)}")
        if tool == ToolName.set_loop:
            enabled = int(bool(args.get("enabled", True)))
            start = float(args.get("start", 0.0))
            end = float(args.get("end", 0.0))
            return AbletonAction(tool, "/live/song/set/loop", [enabled, start, end], f"Set loop enabled={bool(enabled)} start={start} end={end}")
        if tool == ToolName.set_track_send:
            t = int(args.get("track_index", 0))
            s = int(args.get("send_index", 0))
            v = float(args.get("value", 0.0))
            return AbletonAction(tool, "/live/track/set/send", [t, s, v], f"Set send {s} on track {t} to {v}")
        if tool == ToolName.insert_return_track:
            idx = int(args.get("index", -1))
            return AbletonAction(tool, "/live/track/insert_return", [idx], "Insert return track")
        if tool == ToolName.delete_track:
            idx = int(args.get("track_index", 0))
            return AbletonAction(tool, "/live/track/delete", [idx], f"Delete track {idx}", destructive=True)
        raise ValueError(f"Unsupported tool: {tool}")


def capabilities() -> list[Capability]:
    return [
        Capability(tool=ToolName.create_midi_track, description="Create MIDI track",
                   args_schema={"index": "int (optional)"}),
        Capability(tool=ToolName.create_audio_track, description="Create audio track",
                   args_schema={"index": "int (optional)"}),
        Capability(tool=ToolName.set_tempo, description="Set global tempo",
                   args_schema={"bpm": "float"}),
        Capability(tool=ToolName.fire_clip, description="Launch clip slot",
                   args_schema={"track_index": "int", "clip_index": "int"}),
        Capability(tool=ToolName.stop_all_clips, description="Stop all running clips",
                   args_schema={}, destructive=True),
        Capability(tool=ToolName.set_track_volume, description="Set track volume",
                   args_schema={"track_index": "int", "volume": "0..1"}),
        Capability(tool=ToolName.set_track_mute, description="Toggle mute",
                   args_schema={"track_index": "int", "mute": "bool"}),
        Capability(tool=ToolName.set_track_solo, description="Toggle solo",
                   args_schema={"track_index": "int", "solo": "bool"}),
        Capability(tool=ToolName.arm_track, description="Arm/disarm recording",
                   args_schema={"track_index": "int", "arm": "bool"}),
        Capability(tool=ToolName.fire_scene, description="Launch scene",
                   args_schema={"scene_index": "int"}),
        Capability(tool=ToolName.start_transport,
                   description="Start transport (play)", args_schema={}),
        Capability(tool=ToolName.stop_transport, description="Stop transport", args_schema={}),
        Capability(tool=ToolName.start_recording, description="Start recording", args_schema={}),
        Capability(tool=ToolName.stop_recording, description="Stop recording", args_schema={}),
        Capability(tool=ToolName.save_set, description="Save current set", args_schema={}),
        Capability(tool=ToolName.export_audio, description="Export audio to file path",
                   args_schema={"path": "string (file path)"}, destructive=True),
        Capability(tool=ToolName.duplicate_clip, description="Duplicate a clip",
                   args_schema={"track_index": "int", "clip_index": "int"}),
        Capability(tool=ToolName.delete_clip, description="Delete a clip", args_schema={
                   "track_index": "int", "clip_index": "int"}, destructive=True),
        Capability(tool=ToolName.set_device_parameter, description="Set device parameter", args_schema={
                   "track_index": "int", "device_index": "int", "parameter_index": "int", "value": "float"}),
        Capability(tool=ToolName.get_device_parameter, description="Get device parameter", args_schema={
                   "track_index": "int", "device_index": "int", "parameter_index": "int"}),
        Capability(tool=ToolName.create_scene, description="Create a new scene",
                   args_schema={"index": "int (optional)"}),
        Capability(tool=ToolName.duplicate_scene, description="Duplicate a scene",
                   args_schema={"scene_index": "int"}),
        Capability(tool=ToolName.move_clip, description="Move a clip", args_schema={
                   "src_track": "int", "src_clip": "int", "dest_track": "int", "dest_clip": "int"}, destructive=True),
        Capability(tool=ToolName.select_track, description="Select track",
                   args_schema={"track_index": "int"}),
        Capability(tool=ToolName.rename_track, description="Rename track",
                   args_schema={"track_index": "int", "name": "string"}),
        Capability(tool=ToolName.toggle_metronome,
                   description="Enable/disable metronome", args_schema={"on": "bool"}),
        Capability(tool=ToolName.set_loop, description="Set loop range and enable",
                   args_schema={"enabled": "bool", "start": "float", "end": "float"}),
        Capability(tool=ToolName.set_track_send, description="Set track send level",
                   args_schema={"track_index": "int", "send_index": "int", "value": "float"}),
        Capability(tool=ToolName.insert_return_track, description="Insert a return track",
                   args_schema={"index": "int (optional)"}),
        Capability(tool=ToolName.delete_track, description="Delete a track",
                   args_schema={"track_index": "int"}, destructive=True),
    ]
