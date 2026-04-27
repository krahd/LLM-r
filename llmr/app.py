from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from llmr.ableton_osc import AbletonOSCClient, capabilities
from llmr.config import settings
from llmr.macros import (
    delete_runtime_macro,
    init_macro_store,
    list_macros,
    serialize_macro,
    upsert_runtime_macro,
)
from llmr.modelito_adapter import ModelitoClient
from llmr.planner import IntentPlanner, PlanStore
from llmr.schemas import PlannedToolCall, ToolName
from llmr.sessions import SessionStore


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, min_length=1, max_length=128)


class MacroPlanRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    session_id: str | None = Field(default=None, min_length=1, max_length=128)


class ExecuteRequest(BaseModel):
    plan_id: str
    approved: bool = False
    dry_run: bool = False


class StreamRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)


class MacroCallInput(BaseModel):
    tool: ToolName
    args: dict[str, Any] = Field(default_factory=dict)


class MacroMutationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    calls: list[MacroCallInput] = Field(default_factory=list)


app = FastAPI(title="LLM-r", version="1.5.0")
store = PlanStore(persist_path=settings.plan_store_path)
init_macro_store(settings.macro_store_path)
session_store = SessionStore(persist_path=settings.session_store_path)
_plan_session_index: dict[str, str] = {}


def _error_payload(
    *,
    code: str,
    message: str,
    request_id: str,
    diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "diagnostics": diagnostics or {},
        },
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _raise_api_error(
    *,
    status_code: int,
    code: str,
    message: str,
    diagnostics: dict[str, Any] | None = None,
) -> None:
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message, "diagnostics": diagnostics or {}},
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
    payload = _error_payload(
        code=str(detail.get("code", "http_error")),
        message=str(detail.get("message", "Request failed")),
        diagnostics=detail.get("diagnostics", {}),
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    payload = _error_payload(
        code="validation_error",
        message="Request validation failed",
        diagnostics={"errors": exc.errors()},
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    payload = _error_payload(
        code="internal_error",
        message="Unexpected server error",
        diagnostics={"exception": exc.__class__.__name__},
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload)


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


def _require_auth(authorization: str | None = Header(default=None)) -> None:
    if not settings.api_token:
        return
    if not authorization or not authorization.startswith("Bearer "):
        _raise_api_error(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth_required",
            message="Missing bearer token",
        )
    token = authorization.split(" ", 1)[1]
    if token != settings.api_token:
        _raise_api_error(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_token",
            message="Invalid API token",
        )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.5.0"}


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


@app.get("/api/models")
def get_models() -> dict:
    client = ModelitoClient(provider=settings.modelito_provider, model=settings.modelito_model)
    return {
        "provider": settings.modelito_provider,
        "default_model": settings.modelito_model,
        "models": client.list_models(),
    }


@app.get("/api/model_metadata")
def get_model_metadata(model: str | None = None) -> dict:
    client = ModelitoClient(provider=settings.modelito_provider, model=settings.modelito_model)
    return client.model_metadata(model)


@app.post("/api/stream")
def stream_completion(req: StreamRequest):
    client = ModelitoClient(provider=settings.modelito_provider, model=settings.modelito_model)

    def event_stream():
        yield "event: start\ndata: {}\n\n"
        try:
            for chunk in client.stream(req.prompt.strip()):
                payload = json.dumps({"delta": chunk})
                yield f"event: delta\ndata: {payload}\n\n"
            yield "event: end\ndata: {}\n\n"
        except Exception as exc:
            payload = json.dumps({"message": str(exc)})
            yield f"event: error\ndata: {payload}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/macros")
def get_macros() -> dict:
    return {"macros": list_macros()}


@app.get("/api/macros/{name}")
def get_macro_by_name(name: str) -> dict:
    macro = serialize_macro(name)
    if not macro:
        _raise_api_error(status_code=404, code="macro_not_found", message="Unknown macro")
    return macro


@app.post("/api/macros", dependencies=[Depends(_require_auth)])
def create_macro(req: MacroMutationRequest) -> dict:
    calls = [PlannedToolCall(tool=call.tool, args=call.args) for call in req.calls]
    upsert_runtime_macro(req.name.strip(), calls)
    return serialize_macro(req.name.strip()) or {}


@app.put("/api/macros/{name}", dependencies=[Depends(_require_auth)])
def update_macro(name: str, req: MacroMutationRequest) -> dict:
    if name != req.name:
        _raise_api_error(
            status_code=400,
            code="macro_name_mismatch",
            message="Path name and payload name must match",
        )
    calls = [PlannedToolCall(tool=call.tool, args=call.args) for call in req.calls]
    upsert_runtime_macro(name.strip(), calls)
    return serialize_macro(name.strip()) or {}


@app.delete("/api/macros/{name}", dependencies=[Depends(_require_auth)])
def remove_macro(name: str) -> dict:
    existed = delete_runtime_macro(name.strip())
    if not existed:
        _raise_api_error(status_code=404, code="macro_not_found", message="Unknown runtime macro")
    return {"deleted": True, "name": name.strip()}


@app.post("/api/plan")
def create_plan(req: PromptRequest) -> dict:
    planner = _build_planner()
    plan = planner.plan(req.prompt.strip())
    store.put(plan)
    session = session_store.get_or_create(req.session_id)
    _plan_session_index[plan.id] = session.session_id
    session_store.add_history(
        session.session_id,
        plan_id=plan.id,
        prompt=plan.prompt,
        explanation=plan.explanation,
        confidence=plan.confidence,
        created_at=plan.created_at,
        executed_at=plan.executed_at,
    )
    payload = _serialize_plan(plan)
    payload["llm_raw"] = plan.llm_raw
    payload["session_id"] = session.session_id
    return payload


@app.post("/api/plan_macro")
def create_macro_plan(req: MacroPlanRequest) -> dict:
    planner = _build_planner()
    plan = planner.plan(f"macro:{req.name.strip()}")
    if not plan.actions:
        _raise_api_error(status_code=404, code="macro_not_found", message="Unknown macro")

    store.put(plan)
    session = session_store.get_or_create(req.session_id)
    _plan_session_index[plan.id] = session.session_id
    session_store.add_history(
        session.session_id,
        plan_id=plan.id,
        prompt=plan.prompt,
        explanation=plan.explanation,
        confidence=plan.confidence,
        created_at=plan.created_at,
        executed_at=plan.executed_at,
    )
    payload = _serialize_plan(plan)
    payload["session_id"] = session.session_id
    return payload


@app.get("/api/plan/{plan_id}")
def get_plan(plan_id: str) -> dict:
    plan = store.get(plan_id)
    if not plan:
        _raise_api_error(status_code=404, code="plan_not_found", message="Plan not found or expired")
    return _serialize_plan(plan)


@app.post("/api/execute", dependencies=[Depends(_require_auth)])
def execute_plan(req: ExecuteRequest) -> dict:
    plan = store.get(req.plan_id)
    if not plan:
        _raise_api_error(status_code=404, code="plan_not_found", message="Plan not found or expired")

    if plan.executed_at:
        _raise_api_error(status_code=409, code="plan_already_executed", message="Plan already executed")

    if plan.requires_approval and not req.approved:
        _raise_api_error(
            status_code=400,
            code="approval_required",
            message="Plan includes destructive actions and requires approval",
        )

    if not req.dry_run:
        ableton = AbletonOSCClient(settings.ableton_host, settings.ableton_port)
        for action in plan.actions:
            ableton.send(action)
        store.mark_executed(plan.id)

    session_id = _plan_session_index.get(plan.id)
    if session_id:
        updated = store.get(plan.id)
        session_store.add_history(
            session_id,
            plan_id=plan.id,
            prompt=plan.prompt,
            explanation=plan.explanation,
            confidence=plan.confidence,
            created_at=plan.created_at,
            executed_at=updated.executed_at if updated else None,
        )

    return {
        "plan_id": plan.id,
        "executed_count": len(plan.actions),
        "requires_approval": plan.requires_approval,
        "dry_run": req.dry_run,
        "executed_at": store.get(plan.id).executed_at if store.get(plan.id) else None,
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


@app.get("/api/sessions")
def get_sessions() -> dict:
    sessions = session_store.list_sessions()
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
                "history_count": len(s.history),
            }
            for s in sessions
        ]
    }


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    session = session_store.get_session(session_id)
    if not session:
        _raise_api_error(status_code=404, code="session_not_found", message="Session not found")
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "history": [item.__dict__ for item in session.history],
    }


@app.get("/api/history")
def get_history(session_id: str | None = None, limit: int = 50) -> dict:
    limit = min(max(limit, 1), 500)
    history = session_store.get_history(session_id=session_id, limit=limit)
    return {"history": [item.__dict__ for item in history], "count": len(history)}
