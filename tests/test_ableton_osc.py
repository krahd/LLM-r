import pytest

from llmr.ableton_osc import AbletonOSCClient, capabilities
from llmr.schemas import ToolName


def test_capabilities_include_transport_tools():
    names = {cap.tool for cap in capabilities()}
    assert ToolName.song_play in names
    assert ToolName.song_stop in names
    assert ToolName.song_continue in names
    assert ToolName.song_record in names
    assert ToolName.song_metronome in names


def test_to_action_validates_volume_range():
    client = AbletonOSCClient("127.0.0.1", 11000)
    with pytest.raises(ValueError):
        client.to_action(ToolName.set_track_volume, {"track_index": 1, "volume": 2.0})


def test_to_action_maps_transport_toggle_args():
    client = AbletonOSCClient("127.0.0.1", 11000)
    action = client.to_action(ToolName.song_metronome, {"enabled": True})
    assert action.address == "/live/song/set/metronome"
    assert action.args == [1]


def test_to_action_new_track_pan_validation():
    client = AbletonOSCClient("127.0.0.1", 11000)
    with pytest.raises(ValueError):
        client.to_action(ToolName.track_set_pan, {"track_index": 0, "pan": 2.0})


def test_to_action_scene_rename_requires_name():
    client = AbletonOSCClient("127.0.0.1", 11000)
    with pytest.raises(ValueError):
        client.to_action(ToolName.scene_rename, {"scene_index": 1, "name": "   "})
