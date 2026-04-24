from __future__ import annotations
from fastapi import FastAPI, HTTPException

from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from llmr.ableton_osc import AbletonOSCClient, capabilities
from llmr.auth import require_api_key
from llmr.config import settings
from llmr.macros import list_macros
from llmr.modelito_adapter import ModelitoClient
from llmr.planner import IntentPlanner, PlanStore
from llmr.osc_server import StateManager, start_osc_server, stop_osc_server
from llmr.schemas import ToolName
from llmr.remote_script import RemoteScriptClient


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)


class MacroPlanRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class ExecuteRequest(BaseModel):
    plan_id: str
    approved: bool = False
    dry_run: bool = False


class UndoRequest(BaseModel):
    plan_id: str


app = FastAPI(title="LLM-r", version="1.3.0")

# runtime components
state_manager = StateManager()
_osc_server: Optional[object] = None
store = PlanStore(persist_path=settings.plan_store_path)


def _serialize_plan(plan) -> dict:
    return {
        "plan_id": plan.id,
        "prompt": plan.prompt,
        "explanation": plan.explanation,
        "confidence": plan.confidence,
        "requires_approval": plan.requires_approval,
        "created_at": plan.created_at,
        "executed_at": plan.executed_at,
        "planned_actions": [
            {
                "tool": a.tool.value,
                "address": a.address,
                "args": a.args,
                "description": a.description,
                "destructive": a.destructive,
            }
            for a in plan.actions
        ],
    }


def _build_planner() -> IntentPlanner:
    return IntentPlanner(
        llm=ModelitoClient(provider=settings.modelito_provider, model=settings.modelito_model),
        ableton=AbletonOSCClient(settings.ableton_host, settings.ableton_port),
    )


@app.on_event("startup")
def _on_startup() -> None:
    global _osc_server
    if settings.enable_osc_server:
        try:
            _osc_server = start_osc_server(settings.osc_listen_host,
                                           settings.osc_listen_port, state_manager)
        except Exception:
            _osc_server = None


@app.on_event("shutdown")
def _on_shutdown() -> None:
    global _osc_server
    if _osc_server is not None:
        try:
            stop_osc_server(_osc_server)
        finally:
            _osc_server = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.3.0"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/capabilities")
def get_capabilities(auth: None = Depends(require_api_key)) -> dict:
    return {
        "capabilities": [
            {
                "tool": c.tool.value,
                "description": c.description,
                "args_schema": c.args_schema,
                "destructive": c.destructive,
            }
            for c in capabilities()
        ]
    }


@app.get("/api/macros")
def get_macros(auth: None = Depends(require_api_key)) -> dict:
    return {"macros": list_macros()}


@app.post("/api/plan")
def create_plan(req: PromptRequest, auth: None = Depends(require_api_key)) -> dict:
    try:
        planner = _build_planner()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    plan = planner.plan(req.prompt.strip())
    store.put(plan)
    payload = _serialize_plan(plan)
    payload["llm_raw"] = plan.llm_raw
    return payload


@app.post("/api/plan_macro")
def create_macro_plan(req: MacroPlanRequest, auth: None = Depends(require_api_key)) -> dict:
    try:
        planner = _build_planner()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    plan = planner.plan(f"macro:{req.name.strip()}")
    if not plan.actions:
        raise HTTPException(status_code=404, detail="Unknown macro")

    store.put(plan)
    return _serialize_plan(plan)


@app.get("/api/plan/{plan_id}")
def get_plan(plan_id: str, auth: None = Depends(require_api_key)) -> dict:
    plan = store.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or expired")
    return _serialize_plan(plan)


@app.post("/api/execute")
def execute_plan(req: ExecuteRequest, auth: None = Depends(require_api_key)) -> dict:
    plan = store.get(req.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or expired")

    # Build the OSC messages we would send (for dry-run reporting)
    osc_messages = [{"address": a.address, "args": a.args, "tool": a.tool.value}
                    for a in plan.actions]

    if req.dry_run:
        return {
            "plan_id": plan.id,
            "executed_count": 0,
            "requires_approval": plan.requires_approval,
            "dry_run": True,
            "osc_messages": osc_messages,
        }

    # mapper is used to construct AbletonAction objects and to_action helpers
    mapper = AbletonOSCClient(settings.ableton_host, settings.ableton_port)
    # Choose executor: RemoteScriptClient (JSON bridge) or raw OSC client
    if settings.remote_script_enabled:
        executor = RemoteScriptClient(settings.remote_script_host, settings.remote_script_port)
    else:
        executor = mapper

    # Build undo snapshot for reversible actions using current state
    undo_actions: list = []
    for a in plan.actions:
        try:
            if a.tool == ToolName.set_device_parameter:
                ti = int(a.args.get("track_index", 0))
                di = int(a.args.get("device_index", 0))
                pi = int(a.args.get("parameter_index", 0))
                prev = state_manager.get_device_parameter(ti, di, pi)
                if prev is not None:
                    undo_actions.append(
                        ableton.to_action(
                            ToolName.set_device_parameter,
                            {"track_index": ti, "device_index": di,
                                "parameter_index": pi, "value": prev},
                        )
                    )
            elif a.tool == ToolName.set_track_volume:
                ti = int(a.args.get("track_index", 0))
                prev = state_manager.get_track_attr(ti, "volume")
                if prev is not None:
                    undo_actions.append(ableton.to_action(
                        ToolName.set_track_volume, {"track_index": ti, "volume": prev}))
            elif a.tool in (ToolName.set_track_mute, ToolName.set_track_solo, ToolName.arm_track):
                ti = int(a.args.get("track_index", 0))
                key = "mute" if a.tool == ToolName.set_track_mute else (
                    "solo" if a.tool == ToolName.set_track_solo else "arm")
                prev = state_manager.get_track_attr(ti, key)
                if prev is not None:
                    undo_actions.append(ableton.to_action(a.tool, {"track_index": ti, key: prev}))
        except Exception:
            # best-effort: skip undo for this action if anything goes wrong
            pass

    if undo_actions:
        store.save_undo(plan.id, undo_actions)

    # Execute actions
    for action in plan.actions:
        executor.send(action)

    store.mark_executed(plan.id)

    return {
        "plan_id": plan.id,
        "executed_count": len(plan.actions),
        "requires_approval": plan.requires_approval,
        "dry_run": False,
        "executed_at": plan.executed_at,
        "executed_actions": [
            {"tool": a.tool.value, "address": a.address, "args": a.args, "description": a.description} for a in plan.actions
        ],
        "osc_messages": osc_messages,
    }


@app.post("/api/undo")
def undo_plan(req: UndoRequest, auth: None = Depends(require_api_key)) -> dict:
    undo = store.get_undo(req.plan_id)
    if not undo:
        raise HTTPException(status_code=404, detail="No undo available for this plan")
    ableton = AbletonOSCClient(settings.ableton_host, settings.ableton_port)
    for a in undo:
        ableton.send(a)
    store.clear_undo(req.plan_id)
    return {"plan_id": req.plan_id, "undone": True}


@app.get("/api/state")
def get_state(auth: None = Depends(require_api_key)) -> dict:
    return state_manager.get_state()




class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)


class MacroPlanRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class ExecuteRequest(BaseModel):
    plan_id: str
    approved: bool = False
    dry_run: bool = False


app = FastAPI(title="LLM-r", version="1.3.0")
state_manager = StateManager()
_osc_server: Optional[object] = None
store = PlanStore(persist_path=settings.plan_store_path)


def _serialize_plan(plan) -> dict:
    return {
        "plan_id": plan.id,
        "prompt": plan.prompt,
        "explanation": plan.explanation,
        "confidence": plan.confidence,
        "requires_approval": plan.requires_approval,
        "created_at": plan.created_at,
        "executed_at": plan.executed_at,
        "planned_actions": [
            {
                "tool": a.tool.value,
                "address": a.address,
                "args": a.args,
                "description": a.description,
                "destructive": a.destructive,
            }
            for a in plan.actions
        ],
    }


def _build_planner() -> IntentPlanner:

    @app.on_event("startup")
    def _on_startup() -> None:
        global _osc_server
        if settings.enable_osc_server:
            try:
                _osc_server = start_osc_server(
                    settings.osc_listen_host, settings.osc_listen_port, state_manager)
            except Exception:
                _osc_server = None

    @app.on_event("shutdown")
    def _on_shutdown() -> None:
        global _osc_server
        if _osc_server is not None:
            try:
                stop_osc_server(_osc_server)
            finally:
                _osc_server = None

    class UndoRequest(BaseModel):
        plan_id: str
    return IntentPlanner(
        llm=ModelitoClient(provider=settings.modelito_provider, model=settings.modelito_model),
        ableton=AbletonOSCClient(settings.ableton_host, settings.ableton_port),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.3.0"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/capabilities")
def get_capabilities() -> dict:
    return {
        "capabilities": [
            {
                "tool": c.tool.value,
                "description": c.description,
                "args_schema": c.args_schema,
                "destructive": c.destructive,
            }
            for c in capabilities()
        ]
    }


@app.get("/api/macros")
def get_macros() -> dict:
    return {"macros": list_macros()}


@app.post("/api/plan")
def create_plan(req: PromptRequest) -> dict:
    try:
        planner = _build_planner()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    plan = planner.plan(req.prompt.strip())
    store.put(plan)
    payload = _serialize_plan(plan)
    payload["llm_raw"] = plan.llm_raw
    return payload


@app.post("/api/plan_macro")
def create_macro_plan(req: MacroPlanRequest) -> dict:
    try:
        planner = _build_planner()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    plan = planner.plan(f"macro:{req.name.strip()}")
    if not plan.actions:
        raise HTTPException(status_code=404, detail="Unknown macro")

    store.put(plan)
    return _serialize_plan(plan)


@app.get("/api/plan/{plan_id}")
def get_plan(plan_id: str) -> dict:
    plan = store.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or expired")
    return _serialize_plan(plan)


@app.post("/api/execute")
def execute_plan(req: ExecuteRequest) -> dict:
    plan = store.get(req.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or expired")

    # Build the OSC messages we would send (for dry-run reporting)
    osc_messages = [
        {"address": a.address, "args": a.args, "tool": a.tool.value} for a in plan.actions
    ]

    if req.dry_run:
        return {
            "plan_id": plan.id,
            "executed_count": 0,
            "requires_approval": plan.requires_approval,
            "dry_run": True,
            "osc_messages": osc_messages,
        }

    ableton = AbletonOSCClient(settings.ableton_host, settings.ableton_port)

    # Build undo snapshot for reversible actions using current state
    undo_actions: list = []
    for a in plan.actions:
        try:
            if a.tool == ToolName.set_device_parameter:
                ti = int(a.args.get("track_index", 0))
                di = int(a.args.get("device_index", 0))
                pi = int(a.args.get("parameter_index", 0))
                prev = state_manager.get_device_parameter(ti, di, pi)
                if prev is not None:
                    undo_actions.append(ableton.to_action(ToolName.set_device_parameter, {
                                        "track_index": ti, "device_index": di, "parameter_index": pi, "value": prev}))
            elif a.tool == ToolName.set_track_volume:
                ti = int(a.args.get("track_index", 0))
                prev = state_manager.get_track_attr(ti, "volume")
                if prev is not None:
                    undo_actions.append(ableton.to_action(
                        ToolName.set_track_volume, {"track_index": ti, "volume": prev}))
            elif a.tool in (ToolName.set_track_mute, ToolName.set_track_solo, ToolName.arm_track):
                ti = int(a.args.get("track_index", 0))
                key = "mute" if a.tool == ToolName.set_track_mute else (
                    "solo" if a.tool == ToolName.set_track_solo else "arm")
                prev = state_manager.get_track_attr(ti, key)
                if prev is not None:
                    undo_actions.append(ableton.to_action(a.tool, {"track_index": ti, key: prev}))
        except Exception:
            # best-effort: skip undo for this action if anything goes wrong
            pass

    if undo_actions:
        store.save_undo(plan.id, undo_actions)

    # Execute actions
    for action in plan.actions:
        ableton.send(action)

    store.mark_executed(plan.id)

    return {
        "plan_id": plan.id,
        "executed_count": len(plan.actions),
        "requires_approval": plan.requires_approval,
        "dry_run": False,
        "executed_at": plan.executed_at,
        "executed_actions": [
            {"tool": a.tool.value, "address": a.address, "args": a.args, "description": a.description} for a in plan.actions
        ],
        "osc_messages": osc_messages,
    }


@app.post("/api/undo")
def undo_plan(req: UndoRequest) -> dict:
    undo = store.get_undo(req.plan_id)
    if not undo:
        raise HTTPException(status_code=404, detail="No undo available for this plan")
    ableton = AbletonOSCClient(settings.ableton_host, settings.ableton_port)
    for a in undo:
        ableton.send(a)
    store.clear_undo(req.plan_id)
    return {"plan_id": req.plan_id, "undone": True}


@app.get("/api/state")
def get_state() -> dict:
    return state_manager.get_state()

    if plan.executed_at:
        raise HTTPException(status_code=409, detail="Plan already executed")

    if plan.requires_approval and not req.approved:
        raise HTTPException(
            status_code=400, detail="Plan includes destructive actions and requires approval")

    if not req.dry_run:
        ableton = AbletonOSCClient(settings.ableton_host, settings.ableton_port)
        for action in plan.actions:
            ableton.send(action)
        store.mark_executed(plan.id)

    return {
        "plan_id": plan.id,
        "executed_count": len(plan.actions),
        "requires_approval": plan.requires_approval,
        "dry_run": req.dry_run,
        "executed_at": plan.executed_at,
        "executed_actions": [
            {
                "tool": a.tool.value,
                "address": a.address,
                "args": a.args,
                "description": a.description,
            }
            for a in plan.actions
        ],
    }
