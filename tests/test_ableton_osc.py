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
    assert ToolName.utility_undo in names
    assert ToolName.utility_redo in names
    assert ToolName.midi_notes_add in names
    assert ToolName.clip_set_gain in names


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


def test_to_action_adds_midi_notes():
    client = AbletonOSCClient("127.0.0.1", 11000)
    action = client.to_action(
        ToolName.midi_notes_add,
        {
            "track_index": 1,
            "clip_index": 2,
            "notes": [
                {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
                {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 88, "mute": True},
            ],
        },
    )
    assert action.address == "/live/clip/add/notes"
    assert action.args == [1, 2, 60, 0.0, 0.5, 100.0, 0, 64, 0.5, 0.5, 88.0, 1]


def test_to_action_validates_midi_notes():
    client = AbletonOSCClient("127.0.0.1", 11000)
    with pytest.raises(ValueError):
        client.to_action(
            ToolName.midi_notes_add,
            {
                "track_index": 0,
                "clip_index": 0,
                "notes": [{"pitch": 200, "start_time": 0, "duration": 1, "velocity": 100}],
            },
        )


def test_to_action_removes_midi_note_range():
    client = AbletonOSCClient("127.0.0.1", 11000)
    action = client.to_action(
        ToolName.midi_notes_remove,
        {
            "track_index": 0,
            "clip_index": 1,
            "start_pitch": 36,
            "pitch_span": 12,
            "start_time": 0.0,
            "time_span": 4.0,
        },
    )
    assert action.address == "/live/clip/remove/notes"
    assert action.args == [0, 1, 36, 12, 0.0, 4.0]


def test_to_action_sets_audio_clip_properties():
    client = AbletonOSCClient("127.0.0.1", 11000)
    gain = client.to_action(ToolName.clip_set_gain, {"track_index": 0, "clip_index": 0, "gain": 0.75})
    warp_mode = client.to_action(
        ToolName.clip_set_warp_mode, {"track_index": 0, "clip_index": 0, "warp_mode": 4}
    )
    assert gain.address == "/live/clip/set/gain"
    assert gain.args == [0, 0, 0.75]
    assert warp_mode.address == "/live/clip/set/warp_mode"
    assert warp_mode.args == [0, 0, 4]


def test_to_action_validates_clip_property_ranges():
    client = AbletonOSCClient("127.0.0.1", 11000)
    with pytest.raises(ValueError):
        client.to_action(ToolName.clip_set_gain, {"track_index": 0, "clip_index": 0, "gain": 2})
    with pytest.raises(ValueError):
        client.to_action(ToolName.clip_set_pitch_coarse, {"track_index": 0, "clip_index": 0, "semitones": 99})


def test_to_action_device_bulk_parameter_values():
    client = AbletonOSCClient("127.0.0.1", 11000)
    action = client.to_action(
        ToolName.device_set_parameters,
        {"track_index": 0, "device_index": 1, "values": [0.1, 0.2, 0.3]},
    )
    assert action.address == "/live/device/set/parameters/value"
    assert action.args == [0, 1, 0.1, 0.2, 0.3]
