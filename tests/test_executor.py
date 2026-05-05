from llmr.ableton_osc import AbletonAction
from llmr.executor import execute_actions
from llmr.schemas import ToolName


def test_execute_actions_routes_device_load_to_bridge(monkeypatch):
    calls = []

    def fake_load_device(**kwargs):
        calls.append(kwargs)
        return {"status": "loaded", "name": kwargs["query"]}

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
