from datetime import datetime, timezone

from llmr.ableton_osc import AbletonAction
from llmr import app as app_module
from llmr.planner import StoredPlan
from llmr.schemas import ToolName


class DummyPlanner:
    def __init__(self, plan: StoredPlan) -> None:
        self._plan = plan

    def plan(self, _prompt: str) -> StoredPlan:
        return self._plan


class DummyModelitoClient:
    def __init__(self, provider: str, model: str) -> None:
        self.provider = provider
        self.model = model

    def list_models(self):
        return [{"id": "dummy-model", "provider": self.provider}]

    def model_metadata(self, model: str | None = None):
        return {
            "model": model or self.model,
            "provider": self.provider,
            "available": True,
            "metadata": {"ctx": 128000},
        }

    def stream(self, prompt: str):
        yield f"chunk:{prompt[:5]}"
        yield "chunk:done"


def _build_plan(plan_id: str = "p1") -> StoredPlan:
    return StoredPlan(
        id=plan_id,
        prompt="set tempo",
        explanation="ok",
        confidence=0.8,
        actions=[
            AbletonAction(
                tool=ToolName.set_tempo,
                address="/live/song/set/tempo",
                args=[120.0],
                description="Set tempo",
                destructive=False,
            )
        ],
        llm_raw='{"ok":true}',
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def test_health():
    payload = app_module.health()
    assert payload["status"] == "ok"


def test_models_and_metadata(monkeypatch):
    monkeypatch.setattr(app_module, "ModelitoClient", DummyModelitoClient)

    models = app_module.get_models()
    assert models["models"][0]["id"] == "dummy-model"

    metadata = app_module.get_model_metadata("dummy-model")
    assert metadata["available"] is True


def test_stream_endpoint(monkeypatch):
    monkeypatch.setattr(app_module, "ModelitoClient", DummyModelitoClient)
    response = app_module.stream_completion(app_module.StreamRequest(prompt="hello world"))

    chunks = []
    import asyncio

    async def read_stream():
        async for chunk in response.body_iterator:
            chunks.append(chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk))

    asyncio.run(read_stream())
    body = "".join(chunks)
    assert "event: delta" in body
    assert "event: end" in body


def test_plan_and_session_history(monkeypatch):
    monkeypatch.setattr(app_module, "_build_planner", lambda: DummyPlanner(_build_plan("plan-a")))

    plan = app_module.create_plan(app_module.PromptRequest(prompt="set tempo to 120"))
    assert plan["plan_id"] == "plan-a"
    assert plan["session_id"]

    session = app_module.get_session(plan["session_id"])
    assert len(session["history"]) >= 1

    history = app_module.get_history(session_id=plan["session_id"], limit=20)
    assert history["count"] >= 1


def test_macro_crud():
    created = app_module.create_macro(
        app_module.MacroMutationRequest(
            name="runtime_1",
            calls=[app_module.MacroCallInput(tool=ToolName.set_tempo, args={"bpm": 123})],
        )
    )
    assert created["name"] == "runtime_1"

    fetched = app_module.get_macro_by_name("runtime_1")
    assert fetched["source"] == "runtime"

    updated = app_module.update_macro(
        "runtime_1",
        app_module.MacroMutationRequest(
            name="runtime_1",
            calls=[app_module.MacroCallInput(tool=ToolName.set_tempo, args={"bpm": 124})],
        ),
    )
    assert updated["calls"][0]["args"]["bpm"] == 124

    deleted = app_module.remove_macro("runtime_1")
    assert deleted["deleted"] is True


def test_execute_plan_dry_run(monkeypatch):
    monkeypatch.setattr(app_module, "_build_planner", lambda: DummyPlanner(_build_plan("plan-exec")))
    plan_resp = app_module.create_plan(app_module.PromptRequest(prompt="set tempo to 120"))

    execute = app_module.execute_plan(app_module.ExecuteRequest(plan_id=plan_resp["plan_id"], dry_run=True))
    assert execute["dry_run"] is True


def test_auth_dependency(monkeypatch):
    monkeypatch.setattr(app_module.settings, "api_token", "secret")
    try:
        app_module._require_auth("Bearer secret")
    finally:
        monkeypatch.setattr(app_module.settings, "api_token", "")
