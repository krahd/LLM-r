from datetime import datetime, timezone

import pytest

from llmr.ableton_osc import AbletonAction
from llmr import app as app_module
from llmr.macros import init_macro_store
from llmr.planner import StoredPlan
from llmr.prompts import default_planner_extra_prompt, load_prompt_text, planner_extra_prompt
from llmr.schemas import ToolName
from llmr.sessions import SessionStore


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


@pytest.fixture(autouse=True)
def isolated_app_state(tmp_path):
    app_module.store = app_module.PlanStore(persist_path=str(tmp_path / "plans.json"))
    app_module.session_store = SessionStore(persist_path=str(tmp_path / "sessions.json"))
    app_module._plan_session_index.clear()
    app_module._live_state = {
        "song": {
            "tempo": 120.0,
            "is_playing": False,
            "session_record": False,
            "metronome": False,
            "time_signature": {"numerator": 4, "denominator": 4},
            "global_quantization": 4,
            "count_in": 1,
        },
        "tracks": [],
        "scenes": [],
    }
    init_macro_store(str(tmp_path / "macros.json"))


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
    monkeypatch.setattr(app_module, "modelito_models", lambda provider, model: [model, "dummy-model"])

    models = app_module.get_models()
    assert models["models"][0]["id"] == "dummy-model"

    model_ids = app_module.get_modelito_model_ids()
    assert model_ids["models"] == [app_module.settings.modelito_model, "dummy-model"]

    model_ids = app_module.get_modelito_model_ids(provider="anthropic", model="claude-3-sonnet")
    assert model_ids["provider"] == "anthropic"
    assert model_ids["default_model"] == "claude-3-sonnet"
    assert model_ids["models"] == ["claude-3-sonnet", "dummy-model"]

    metadata = app_module.get_model_metadata("dummy-model")
    assert metadata["available"] is True


def test_ollama_management_endpoints_delegate(monkeypatch):
    monkeypatch.setattr(app_module, "ollama_status", lambda: {"ok": True, "running": False})
    monkeypatch.setattr(app_module, "ollama_local_models", lambda: {"ok": True, "models": ["llama3"]})
    monkeypatch.setattr(app_module, "ollama_remote_models", lambda: {"ok": True, "models": ["mistral"]})
    monkeypatch.setattr(app_module, "ollama_start", lambda: {"ok": True, "message": "started"})
    monkeypatch.setattr(app_module, "ollama_stop", lambda: {"ok": True, "message": "stopped"})
    monkeypatch.setattr(app_module, "ollama_install", lambda: {"ok": True, "message": "installed"})
    monkeypatch.setattr(app_module, "ollama_download", lambda model: {"ok": True, "model": model})
    monkeypatch.setattr(app_module, "ollama_delete", lambda model: {"ok": True, "model": model})
    monkeypatch.setattr(app_module, "ollama_serve", lambda model: {"ok": True, "model": model})

    assert app_module.get_ollama_status()["ok"] is True
    assert app_module.get_ollama_local_models()["models"] == ["llama3"]
    assert app_module.get_ollama_remote_models()["models"] == ["mistral"]
    assert app_module.post_ollama_start()["message"] == "started"
    assert app_module.post_ollama_stop()["message"] == "stopped"
    assert app_module.post_ollama_install()["message"] == "installed"
    req = app_module.OllamaModelRequest(model="llama3")
    assert app_module.post_ollama_download(req)["model"] == "llama3"
    assert app_module.post_ollama_delete(req)["model"] == "llama3"
    assert app_module.post_ollama_serve(req)["model"] == "llama3"


def test_load_prompt_text(tmp_path):
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text("extra planner context", encoding="utf-8")

    assert load_prompt_text(str(prompt_path)) == "extra planner context"
    assert load_prompt_text(str(tmp_path / "missing.md")) == ""


def test_default_planner_extra_prompt_is_packaged():
    prompt = default_planner_extra_prompt()

    assert "You are an Ableton Live assistant operating through LLM-r." in prompt


def test_planner_extra_prompt_can_be_disabled(monkeypatch):
    monkeypatch.setattr(app_module.settings, "planner_extra_prompt_enabled", False)

    assert planner_extra_prompt(app_module.settings) == ""


def test_settings_include_planner_extra_prompt_toggle(monkeypatch):
    monkeypatch.setattr(app_module.settings, "planner_extra_prompt_enabled", True)
    monkeypatch.setattr(app_module.settings, "planner_extra_prompt_path", "docs/prompt.md")

    payload = app_module.get_settings()

    assert payload["planner_extra_prompt_enabled"] is True
    assert payload["planner_extra_prompt_path"] == "docs/prompt.md"


def test_update_settings_can_disable_planner_extra_prompt(monkeypatch):
    monkeypatch.setattr(app_module.settings, "planner_extra_prompt_enabled", True)
    monkeypatch.setattr(app_module.settings, "planner_extra_prompt_path", "docs/prompt.md")
    monkeypatch.setattr(type(app_module.settings), "save", lambda self: None)

    payload = app_module.update_settings(
        app_module.SettingsPatch(planner_extra_prompt_enabled=False)
    )

    assert payload["planner_extra_prompt_enabled"] is False


def test_build_planner_respects_planner_extra_prompt_toggle(monkeypatch, tmp_path):
    captured = {}
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text("enabled context", encoding="utf-8")

    class DummyPlanner:
        def __init__(self, llm, ableton, extra_prompt="") -> None:
            captured["extra_prompt"] = extra_prompt

    monkeypatch.setattr(app_module, "IntentPlanner", DummyPlanner)
    monkeypatch.setattr(app_module, "ModelitoClient", DummyModelitoClient)
    monkeypatch.setattr(app_module, "AbletonOSCClient", lambda host, port: object())
    monkeypatch.setattr(app_module.settings, "planner_extra_prompt_path", str(prompt_path))
    monkeypatch.setattr(app_module.settings, "planner_extra_prompt_enabled", False)

    app_module._build_planner()
    assert captured["extra_prompt"] == ""

    monkeypatch.setattr(app_module.settings, "planner_extra_prompt_enabled", True)
    app_module._build_planner()
    assert captured["extra_prompt"] == "enabled context"


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
            calls=[app_module.ToolCallInput(tool=ToolName.set_tempo, args={"bpm": 123})],
        )
    )
    assert created["name"] == "runtime_1"

    fetched = app_module.get_macro_by_name("runtime_1")
    assert fetched["source"] == "runtime"

    updated = app_module.update_macro(
        "runtime_1",
        app_module.MacroMutationRequest(
            name="runtime_1",
            calls=[app_module.ToolCallInput(tool=ToolName.set_tempo, args={"bpm": 124})],
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
    assert execute["execution_report"][0]["status"] == "dry_run"


def test_auth_dependency(monkeypatch):
    monkeypatch.setattr(app_module.settings, "api_token", "secret")
    try:
        app_module._require_auth("Bearer secret")
    finally:
        monkeypatch.setattr(app_module.settings, "api_token", "")


def test_capabilities_include_transport():
    payload = app_module.get_capabilities()
    names = {item["tool"] for item in payload["capabilities"]}
    assert "song_play" in names
    assert "song_stop" in names
    assert payload["count"] == len(payload["capabilities"])
    by_tool = {item["tool"]: item for item in payload["capabilities"]}
    assert by_tool["song_play"]["domain"] == "song"


def test_capabilities_filters_on_single_endpoint():
    payload = app_module.get_capabilities(domain="song", include_destructive=False)
    assert payload["count"] >= 1
    assert all(item["domain"] == "song" for item in payload["capabilities"])
    assert all(item["destructive"] is False for item in payload["capabilities"])


def test_capabilities_has_single_route():
    capability_paths = [route.path for route in app_module.app.routes if route.path.endswith("/capabilities")]
    assert capability_paths == ["/api/capabilities"]


def test_live_state_endpoints_after_execute(monkeypatch):
    def fake_run_actions(actions, **_kwargs):
        return (
            [
                {
                    "index": index,
                    "tool": action.tool.value,
                    "address": action.address,
                    "args": action.args,
                    "status": "sent",
                }
                for index, action in enumerate(actions)
            ],
            datetime.now(timezone.utc).isoformat(),
        )

    monkeypatch.setattr(app_module, "_run_actions", fake_run_actions)

    plan = StoredPlan(
        id="state-1",
        prompt="state",
        explanation="state",
        confidence=1.0,
        actions=[
            AbletonAction(
                tool=ToolName.create_midi_track,
                address="/live/song/create_midi_track",
                args=[-1],
                description="Create MIDI track",
                destructive=False,
            ),
            AbletonAction(
                tool=ToolName.track_rename,
                address="/live/track/set/name",
                args=[0, "Bass"],
                description="Rename track",
                destructive=False,
            ),
            AbletonAction(
                tool=ToolName.clip_create,
                address="/live/clip_slot/create_clip",
                args=[0, 0, 8.0],
                description="Create clip",
                destructive=False,
            ),
            AbletonAction(
                tool=ToolName.device_set_parameter,
                address="/live/device/set/parameter/value",
                args=[0, 0, 1, 0.75],
                description="Set parameter",
                destructive=False,
            ),
        ],
        llm_raw="{}",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    app_module.store.put(plan)

    app_module.execute_plan(app_module.ExecuteRequest(plan_id="state-1", dry_run=False))

    tracks_payload = app_module.get_live_tracks()
    assert tracks_payload["count"] >= 1
    assert tracks_payload["tracks"][0]["name"] == "Bass"

    clips_payload = app_module.get_live_track_clips(0)
    assert clips_payload["clips"][0]["length_beats"] == 8.0

    devices_payload = app_module.get_live_track_devices(0)
    assert devices_payload["devices"][0]["parameters"][1] == 0.75

    params_payload = app_module.get_live_track_parameters(0)
    assert params_payload["count"] >= 1
    assert params_payload["parameters"][0]["parameter_index"] == 1


def test_live_state_tracks_midi_notes_and_clip_audio_properties(monkeypatch):
    def fake_run_actions(actions, **_kwargs):
        return (
            [
                {
                    "index": index,
                    "tool": action.tool.value,
                    "address": action.address,
                    "args": action.args,
                    "status": "sent",
                }
                for index, action in enumerate(actions)
            ],
            datetime.now(timezone.utc).isoformat(),
        )

    monkeypatch.setattr(app_module, "_run_actions", fake_run_actions)

    payload = app_module.execute_batch(
        app_module.ExecuteBatchRequest(
            approved=True,
            calls=[
                app_module.ToolCallInput(tool=ToolName.create_midi_track, args={"index": -1}),
                app_module.ToolCallInput(
                    tool=ToolName.clip_create,
                    args={"track_index": 0, "clip_index": 0, "length_beats": 4},
                ),
                app_module.ToolCallInput(
                    tool=ToolName.midi_notes_add,
                    args={
                        "track_index": 0,
                        "clip_index": 0,
                        "notes": [
                            {"pitch": 60, "start_time": 0, "duration": 1, "velocity": 100},
                            {"pitch": 64, "start_time": 1, "duration": 1, "velocity": 90},
                        ],
                    },
                ),
                app_module.ToolCallInput(
                    tool=ToolName.clip_set_gain,
                    args={"track_index": 0, "clip_index": 0, "gain": 0.7},
                ),
                app_module.ToolCallInput(
                    tool=ToolName.clip_set_warp_mode,
                    args={"track_index": 0, "clip_index": 0, "warp_mode": 4},
                ),
                app_module.ToolCallInput(
                    tool=ToolName.midi_notes_remove,
                    args={
                        "track_index": 0,
                        "clip_index": 0,
                        "start_pitch": 60,
                        "pitch_span": 1,
                        "start_time": 0,
                        "time_span": 1,
                    },
                ),
            ],
        )
    )

    assert payload["executed_count"] == 6

    clips_payload = app_module.get_live_track_clips(0)
    clip = clips_payload["clips"][0]
    assert clip["gain"] == 0.7
    assert clip["warp_mode"] == 4
    assert clip["notes"] == [
        {"pitch": 64, "start_time": 1.0, "duration": 1.0, "velocity": 90.0, "mute": False}
    ]


def test_execute_batch_dry_run():
    payload = app_module.execute_batch(
        app_module.ExecuteBatchRequest(
            dry_run=True,
            calls=[
                app_module.ToolCallInput(tool=ToolName.set_tempo, args={"bpm": 127}),
                app_module.ToolCallInput(tool=ToolName.utility_undo, args={}),
            ],
        )
    )
    assert payload["dry_run"] is True
    assert payload["executed_count"] == 2
    assert all(item["status"] == "dry_run" for item in payload["execution_report"])


def test_execute_batch_dry_run_allows_destructive_preview():
    payload = app_module.execute_batch(
        app_module.ExecuteBatchRequest(
            dry_run=True,
            calls=[app_module.ToolCallInput(tool=ToolName.stop_all_clips, args={})],
        )
    )
    assert payload["requires_approval"] is True
    assert payload["execution_report"][0]["status"] == "dry_run"
