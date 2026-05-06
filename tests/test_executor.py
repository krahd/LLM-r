import pytest

from llmr.ableton_osc import AbletonAction
from llmr.device_bridge import DeviceBridgeError
from llmr.executor import execute_actions
from llmr.schemas import ToolName


def test_execute_actions_routes_device_load_to_bridge(monkeypatch):
    calls = []

    def fake_load_device(**kwargs):
        calls.append(kwargs)
        return {"status": "loaded", "name": kwargs["query"]}

    monkeypatch.setattr("llmr.executor.device_bridge_health", lambda **_kwargs: {"ok": True})
    monkeypatch.setattr(
        "llmr.executor.resolve_device",
        lambda **_kwargs: {"status": "resolved", "selected_item": "Drum Rack"},
    )
    monkeypatch.setattr("llmr.executor.load_device", fake_load_device)

    action = AbletonAction(
        tool=ToolName.device_load,
        address="/api/devices/load",
        args=[0, "Drum Rack", "drum"],
        description="Load device",
        transport="device_bridge",
    )
    report, executed_at = execute_actions(
        [action],
        ableton_host="127.0.0.1",
        ableton_port=11000,
        device_bridge_host="127.0.0.1",
        device_bridge_port=8788,
        approved=False,
        dry_run=False,
    )

    assert executed_at is not None
    assert report[0]["status"] == "sent"
    assert report[0]["transport"] == "device_bridge"
    assert report[0]["response"]["name"] == "Drum Rack"
    assert calls[0]["track_index"] == 0
    assert calls[0]["device_type"] == "drum"


def test_execute_actions_preflights_device_bridge_before_osc(monkeypatch):
    sent = []

    class DummyClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def send(self, action):
            sent.append(action.tool)

    monkeypatch.setattr("llmr.executor.AbletonOSCClient", DummyClient)
    monkeypatch.setattr(
        "llmr.executor.device_bridge_health",
        lambda **_kwargs: {"ok": False, "error": "connection refused"},
    )

    actions = [
        AbletonAction(
            tool=ToolName.set_tempo,
            address="/live/song/set/tempo",
            args=[123.0],
            description="Set tempo",
        ),
        AbletonAction(
            tool=ToolName.device_load,
            address="/api/devices/load",
            args=[0, "Drum Rack", "drum"],
            description="Load device",
            transport="device_bridge",
        ),
    ]

    with pytest.raises(RuntimeError, match="Device Bridge unavailable"):
        execute_actions(
            actions,
            ableton_host="127.0.0.1",
            ableton_port=11000,
            approved=False,
            dry_run=False,
        )

    assert sent == []


def test_execute_actions_preflights_ambiguous_device_load(monkeypatch):
    monkeypatch.setattr("llmr.executor.device_bridge_health", lambda **_kwargs: {"ok": True})
    monkeypatch.setattr(
        "llmr.executor.resolve_device",
        lambda **_kwargs: (_ for _ in ()).throw(
            DeviceBridgeError("Device Bridge HTTP 409: ambiguous")
        ),
    )

    action = AbletonAction(
        tool=ToolName.device_load,
        address="/api/devices/load",
        args=[0, "Echo", "all"],
        description="Load device",
        transport="device_bridge",
    )

    with pytest.raises(RuntimeError, match="Device Bridge resolve failed"):
        execute_actions(
            [action],
            ableton_host="127.0.0.1",
            ableton_port=11000,
            approved=False,
            dry_run=False,
        )


def test_execute_actions_passes_device_load_resolution_options(monkeypatch):
    resolved = []
    loaded = []

    def fake_resolve(**kwargs):
        resolved.append(kwargs)
        return {"status": "resolved", "selected_item": "Analog Pad"}

    def fake_load(**kwargs):
        loaded.append(kwargs)
        return {"status": "loaded", "loaded_item": "Analog Pad"}

    monkeypatch.setattr("llmr.executor.device_bridge_health", lambda **_kwargs: {"ok": True})
    monkeypatch.setattr("llmr.executor.resolve_device", fake_resolve)
    monkeypatch.setattr("llmr.executor.load_device", fake_load)

    action = AbletonAction(
        tool=ToolName.device_load,
        address="/api/devices/load",
        args=[
            0,
            "Analog",
            "instrument",
            {
                "preset_query": "Warm Pad",
                "browser_path": ["Instruments", "Analog", "Warm Pad"],
                "allow_ambiguous": True,
            },
        ],
        description="Load preset",
        transport="device_bridge",
    )

    report, _executed_at = execute_actions(
        [action],
        ableton_host="127.0.0.1",
        ableton_port=11000,
        approved=False,
        dry_run=False,
    )

    assert report[0]["status"] == "sent"
    assert resolved[0]["preset_query"] == "Warm Pad"
    assert resolved[0]["browser_path"] == ["Instruments", "Analog", "Warm Pad"]
    assert resolved[0]["allow_ambiguous"] is True
    assert loaded[0]["preset_query"] == "Warm Pad"
