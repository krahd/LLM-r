from datetime import datetime, timedelta, timezone

from llmr.ableton_osc import AbletonOSCClient
from llmr.planner import IntentPlanner, PlanStore, StoredPlan


class DummyLLM:
    def __init__(self, response: str) -> None:
        self.response = response

    def complete(self, prompt: str):
        class Result:
            raw_text = ""

        r = Result()
        r.raw_text = self.response
        return r


def test_planner_maps_new_actions():
    planner = IntentPlanner(
        llm=DummyLLM(
            '{"explanation":"ok","confidence":0.9,"calls":[{"tool":"set_track_volume","args":{"track_index":2,"volume":0.4}}]}'),
        ableton=AbletonOSCClient("127.0.0.1", 11000),
    )
    plan = planner.plan("lower track 2")
    assert plan.confidence == 0.9
    assert len(plan.actions) == 1
    assert plan.actions[0].address == "/live/track/set/volume"
    assert plan.actions[0].args == [2, 0.4]


def test_macro_planning_path():
    planner = IntentPlanner(
        llm=DummyLLM('{"explanation":"unused","confidence":0.1,"calls":[]}'),
        ableton=AbletonOSCClient("127.0.0.1", 11000),
    )
    plan = planner.plan("macro:idea_sketch")
    assert plan.confidence == 1.0
    assert plan.explanation == "Macro expansion plan."
    assert len(plan.actions) >= 2


def test_destructive_requires_approval_flag():
    planner = IntentPlanner(
        llm=DummyLLM(
            '{"explanation":"stop","confidence":0.7,"calls":[{"tool":"stop_all_clips","args":{}}]}'),
        ableton=AbletonOSCClient("127.0.0.1", 11000),
    )
    plan = planner.plan("stop everything")
    assert plan.requires_approval is True


def test_planner_handles_fenced_json():
    planner = IntentPlanner(
        llm=DummyLLM('```json\n{"explanation":"ok","confidence":0.5,"calls":[]}\n```'),
        ableton=AbletonOSCClient("127.0.0.1", 11000),
    )
    plan = planner.plan("noop")
    assert plan.confidence == 0.5


def test_planstore_prunes_expired():
    store = PlanStore(ttl_minutes=1)
    old = StoredPlan(
        id="old",
        prompt="x",
        explanation="x",
        confidence=0,
        actions=[],
        llm_raw="",
        created_at=(datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
    )
    store.put(old)
    assert store.get("old") is None


def test_planstore_marks_executed(tmp_path):
    persist = tmp_path / "plans.json"
    store = PlanStore(persist_path=str(persist))
    plan = StoredPlan(
        id="p1",
        prompt="x",
        explanation="x",
        confidence=0,
        actions=[],
        llm_raw="",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    store.put(plan)
    store.mark_executed("p1")
    assert store.get("p1").executed_at is not None


def test_planstore_persists_and_loads(tmp_path):
    persist = tmp_path / "plans.json"
    store1 = PlanStore(persist_path=str(persist))
    plan = StoredPlan(
        id="p2",
        prompt="prompt",
        explanation="ex",
        confidence=0.8,
        actions=[],
        llm_raw="raw",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    store1.put(plan)
    store2 = PlanStore(persist_path=str(persist))
    loaded = store2.get("p2")
    assert loaded is not None
    assert loaded.prompt == "prompt"


def test_planner_handles_bad_json():
    planner = IntentPlanner(llm=DummyLLM("not-json"), ableton=AbletonOSCClient("127.0.0.1", 11000))
    plan = planner.plan("whatever")
    assert plan.actions == []
    assert plan.confidence == 0.0
