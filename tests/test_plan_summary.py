from datetime import datetime, timezone

from llmr import app as app_module
from llmr.ableton_osc import AbletonAction
from llmr.planner import StoredPlan
from llmr.plan_summary import infer_target_label, infer_target_labels, infer_transport, summarise_actions
from llmr.schemas import ToolName


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


def test_serialize_plan_adds_safe_osc_display_metadata() -> None:
    plan = StoredPlan(
        id="plan-osc",
        prompt="set tempo",
        explanation="Set tempo safely",
        confidence=0.91,
        actions=[
            AbletonAction(
                tool=ToolName.set_tempo,
                address="/live/song/set/tempo",
                args=[120.0],
                description="Set song tempo",
                destructive=False,
                transport="osc",
            )
        ],
        llm_raw="{}",
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    payload = app_module._serialize_plan(plan)
    action = payload["planned_actions"][0]

    assert payload["summary"]["count"] == 1
    assert payload["summary"]["safe_count"] == 1
    assert payload["summary"]["destructive_count"] == 0
    assert payload["summary"]["transport_counts"]["osc"] == 1
    assert action["transport_label"] == "AbletonOSC"
    assert action["transport_plain_label"] == "Ableton command"
    assert action["safety_label"] == "Safe"
    assert action["target_label"] == "General"


def test_serialize_plan_adds_device_bridge_metadata() -> None:
    plan = StoredPlan(
        id="plan-device-load",
        prompt="load drum rack",
        explanation="Load a device",
        confidence=0.83,
        actions=[
            AbletonAction(
                tool=ToolName.device_load,
                address="",
                args=[1, "Drum Rack", "instrument", ""],
                description="Load Drum Rack",
                destructive=False,
                transport="device_bridge",
            )
        ],
        llm_raw="{}",
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    payload = app_module._serialize_plan(plan)
    action = payload["planned_actions"][0]

    assert payload["summary"]["transport_counts"]["device_bridge"] == 1
    assert action["transport_label"] == "Device Bridge"
    assert action["transport_plain_label"] == "Browser/device loading"


def test_serialize_plan_adds_destructive_safety_label() -> None:
    plan = StoredPlan(
        id="plan-destructive",
        prompt="delete clip",
        explanation="Delete clip",
        confidence=0.73,
        actions=[
            AbletonAction(
                tool=ToolName.clip_delete,
                address="/live/clip_slot/delete_clip",
                args=[1, 0],
                description="Delete clip",
                destructive=True,
                transport="osc",
            )
        ],
        llm_raw="{}",
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    payload = app_module._serialize_plan(plan)
    action = payload["planned_actions"][0]

    assert payload["summary"]["destructive_count"] == 1
    assert action["safety_label"] == "Destructive"
