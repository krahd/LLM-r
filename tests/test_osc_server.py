from llmr.osc_server import StateManager


def test_state_manager_snapshot_merge():
    sm = StateManager()
    snapshot = {"tempo": 140.0, "tracks": [{"volume": 0.8}],
                "devices": {"0": [{"parameters": [{"value": 0.2}]}]}}
    sm.update_from_snapshot(snapshot)
    s = sm.get_state()
    assert s["tempo"] == 140.0
    assert isinstance(s["tracks"], list)
    assert s["tracks"][0]["volume"] == 0.8
    assert sm.get_device_parameter(0, 0, 0) == 0.2
