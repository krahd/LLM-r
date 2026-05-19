from llmr.ableton_osc import AbletonOSCClient
from llmr.schemas import ToolName


def test_to_action_addresses():
    client = AbletonOSCClient("127.0.0.1", 11000)
    a = client.to_action(ToolName.set_tempo, {"bpm": 128})
    assert a.address == "/live/song/set/tempo"
    a = client.to_action(ToolName.fire_clip, {"track_index": 1, "clip_index": 2})
    assert a.address == "/live/clip/fire"
    a = client.to_action(ToolName.set_device_parameter, {
                         "track_index": 0, "device_index": 0, "parameter_index": 1, "value": 0.5})
    assert a.address == "/live/device/set/parameter"
