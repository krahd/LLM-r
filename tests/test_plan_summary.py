from llmr.plan_summary import infer_target_label, infer_target_labels, infer_transport, summarise_actions


def test_infer_target_label_uses_known_indices() -> None:
    args = {"track_index": 2, "clip_index": 0}
    assert infer_target_label(args) == "Track 2 · Clip 0"


def test_infer_target_label_uses_device_name() -> None:
    args = {"device_name": "Drum Rack"}
    assert infer_target_label(args) == "Device: Drum Rack"


def test_infer_target_label_falls_back_to_general() -> None:
    assert infer_target_label({"tempo": 128}) == "General"
    assert infer_target_label(None) == "General"


def test_infer_target_labels_handles_empty_values() -> None:
    args = {"track_name": " ", "scene_index": 3}
    assert infer_target_labels(args) == ["Scene 3"]


def test_infer_transport_prefers_explicit_field() -> None:
    action = {"tool": "device_load", "transport": "osc"}
    assert infer_transport(action) == "osc"


def test_infer_transport_detects_device_bridge_tool() -> None:
    action = {"tool": "device_load", "args": {"device_name": "EQ Eight"}}
    assert infer_transport(action) == "device_bridge"


def test_summarise_actions_counts_safety_and_transport() -> None:
    actions = [
        {
            "tool": "set_tempo",
            "args": {"tempo": 128},
            "address": "/live/song/set/tempo",
            "destructive": False,
        },
        {
            "tool": "device_load",
            "args": {"track_index": 1, "device_name": "Drum Rack"},
            "destructive": True,
        },
        {
            "tool": "delete_clip",
            "args": {"track_index": 2, "clip_index": 0},
            "transport": "custom",
            "destructive": True,
        },
    ]

    summary = summarise_actions(actions)

    assert summary["count"] == 3
    assert summary["safe_count"] == 1
    assert summary["destructive_count"] == 2
    assert summary["transport_counts"] == {"osc": 1, "device_bridge": 1, "other": 1}
    assert summary["destructive_tools"] == ["device_load", "delete_clip"]
