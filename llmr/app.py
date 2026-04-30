from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from pathlib import Path

from llmr import __version__
from llmr.ableton_osc import AbletonOSCClient, capabilities
from llmr.config import settings
from llmr.executor import execute_actions as _run_actions
from llmr.macros import (
    delete_runtime_macro,
    init_macro_store,
    list_macros,
    serialize_macro,
    upsert_runtime_macro,
)
from llmr.modelito_adapter import (
    ModelitoClient,
    modelito_models,
    ollama_delete,
    ollama_download,
    ollama_install,
    ollama_local_models,
    ollama_remote_models,
    ollama_serve,
    ollama_start,
    ollama_status,
    ollama_stop,
)
from llmr.planner import IntentPlanner, PlanStore
from llmr.prompts import planner_extra_prompt
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


class ToolCallInput(BaseModel):
    tool: ToolName
    args: dict[str, Any] = Field(default_factory=dict)


class ExecuteBatchRequest(BaseModel):
    calls: list[ToolCallInput] = Field(default_factory=list)
    approved: bool = False
    dry_run: bool = False


class StreamRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)


class MacroMutationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    calls: list[ToolCallInput] = Field(default_factory=list)


class SettingsPatch(BaseModel):
    modelito_provider: str | None = None
    modelito_model: str | None = None
    planner_extra_prompt_enabled: bool | None = None
    planner_extra_prompt_path: str | None = None
    ableton_host: str | None = None
    ableton_port: int | None = None
    api_token: str | None = None


class OllamaModelRequest(BaseModel):
    model: str = Field(min_length=1, max_length=256)


app = FastAPI(title="LLM-r", version=__version__)
store = PlanStore(persist_path=settings.plan_store_path)
init_macro_store(settings.macro_store_path)
session_store = SessionStore(persist_path=settings.session_store_path)
_plan_session_index: dict[str, str] = {}

_live_state: dict[str, Any] = {
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


def _ensure_track(track_index: int) -> dict[str, Any]:
    while len(_live_state["tracks"]) <= track_index:
        idx = len(_live_state["tracks"])
        _live_state["tracks"].append(
            {
                "track_index": idx,
                "name": f"Track {idx + 1}",
                "volume": 0.8,
                "pan": 0.0,
                "mute": False,
                "solo": False,
                "arm": False,
                "sends": {},
                "clips": [],
                "devices": [],
            }
        )
    return _live_state["tracks"][track_index]


def _ensure_scene(scene_index: int) -> dict[str, Any]:
    while len(_live_state["scenes"]) <= scene_index:
        idx = len(_live_state["scenes"])
        _live_state["scenes"].append({"scene_index": idx, "name": f"Scene {idx + 1}"})
    return _live_state["scenes"][scene_index]


def _new_clip(clip_index: int, length_beats: float = 4.0) -> dict[str, Any]:
    return {
        "clip_index": clip_index,
        "name": f"Clip {clip_index + 1}",
        "length_beats": length_beats,
        "notes": [],
        "color": None,
        "color_index": None,
        "gain": None,
        "pitch_coarse": 0,
        "pitch_fine": 0.0,
        "start_marker": 0.0,
        "end_marker": length_beats,
        "loop_start": 0.0,
        "loop_end": length_beats,
        "looping": False,
        "position": 0.0,
        "warping": None,
        "warp_mode": None,
        "ram_mode": None,
        "muted": False,
        "launch_mode": 0,
        "launch_quantization": 0,
        "velocity_amount": 1.0,
    }


def _ensure_clip(track_index: int, clip_index: int, length_beats: float = 4.0) -> dict[str, Any]:
    track = _ensure_track(track_index)
    while len(track["clips"]) <= clip_index:
        idx = len(track["clips"])
        track["clips"].append(_new_clip(idx, length_beats=4.0))
    return track["clips"][clip_index]


def _apply_action_to_live_state(action) -> None:
    tool = action.tool.value
    args = action.args
    song = _live_state["song"]

    if tool == "set_tempo":
        song["tempo"] = float(args[0])
    elif tool == "song_play":
        song["is_playing"] = True
    elif tool == "song_stop":
        song["is_playing"] = False
    elif tool == "song_record":
        song["session_record"] = bool(args[0])
    elif tool == "song_metronome":
        song["metronome"] = bool(args[0])
    elif tool == "song_set_time_signature":
        song["time_signature"] = {"numerator": int(args[0]), "denominator": int(args[1])}
    elif tool == "song_set_global_quantization":
        song["global_quantization"] = int(args[0])
    elif tool == "song_set_count_in":
        song["count_in"] = int(args[0])
    elif tool in {"create_midi_track", "create_audio_track"}:
        index = int(args[0])
        if index < 0:
            _ensure_track(len(_live_state["tracks"]))
        else:
            _ensure_track(index)
    elif tool in {"set_track_volume", "set_track_mute", "set_track_solo", "arm_track", "track_set_pan"}:
        track = _ensure_track(int(args[0]))
        mapping = {
            "set_track_volume": "volume",
            "set_track_mute": "mute",
            "set_track_solo": "solo",
            "arm_track": "arm",
            "track_set_pan": "pan",
        }
        track[mapping[tool]] = args[1]
    elif tool == "track_set_send":
        track = _ensure_track(int(args[0]))
        track["sends"][int(args[1])] = float(args[2])
    elif tool == "track_rename":
        _ensure_track(int(args[0]))["name"] = str(args[1])
    elif tool == "track_delete":
        index = int(args[0])
        if 0 <= index < len(_live_state["tracks"]):
            _live_state["tracks"].pop(index)
            for idx, tr in enumerate(_live_state["tracks"]):
                tr["track_index"] = idx
    elif tool == "track_duplicate":
        index = int(args[0])
        if 0 <= index < len(_live_state["tracks"]):
            original = dict(_live_state["tracks"][index])
            original["clips"] = [dict(c) for c in original["clips"]]
            original["devices"] = [dict(d) for d in original["devices"]]
            _live_state["tracks"].insert(index + 1, original)
            for idx, tr in enumerate(_live_state["tracks"]):
                tr["track_index"] = idx
    elif tool == "scene_create":
        index = int(args[0])
        if index < 0 or index >= len(_live_state["scenes"]):
            _ensure_scene(len(_live_state["scenes"]))
        else:
            _live_state["scenes"].insert(index, {"scene_index": index, "name": f"Scene {index + 1}"})
            for idx, sc in enumerate(_live_state["scenes"]):
                sc["scene_index"] = idx
    elif tool == "scene_delete":
        index = int(args[0])
        if 0 <= index < len(_live_state["scenes"]):
            _live_state["scenes"].pop(index)
            for idx, sc in enumerate(_live_state["scenes"]):
                sc["scene_index"] = idx
    elif tool == "scene_rename":
        _ensure_scene(int(args[0]))["name"] = str(args[1])
    elif tool == "clip_create":
        track_index = int(args[0])
        clip_index = int(args[1])
        _ensure_track(track_index)
        _ensure_clip(track_index, clip_index)
        _live_state["tracks"][track_index]["clips"][clip_index] = _new_clip(clip_index, length_beats=float(args[2]))
    elif tool == "clip_delete":
        track = _ensure_track(int(args[0]))
        clip_index = int(args[1])
        track["clips"] = [c for c in track["clips"] if c["clip_index"] != clip_index]
    elif tool == "clip_duplicate_to":
        source = _ensure_clip(int(args[0]), int(args[1]))
        target_track_index = int(args[2])
        target_clip_index = int(args[3])
        _ensure_track(target_track_index)
        _ensure_clip(target_track_index, target_clip_index)
        duplicate = dict(source)
        duplicate["clip_index"] = target_clip_index
        duplicate["notes"] = [dict(note) for note in source.get("notes", [])]
        _live_state["tracks"][target_track_index]["clips"][target_clip_index] = duplicate
    elif tool == "clip_duplicate_loop":
        clip = _ensure_clip(int(args[0]), int(args[1]))
        loop_start = float(clip.get("loop_start", 0.0))
        loop_end = float(clip.get("loop_end", clip.get("length_beats", 4.0)))
        loop_length = max(loop_end - loop_start, 0.0)
        if loop_length > 0:
            new_notes = []
            for note in clip.get("notes", []):
                duplicated = dict(note)
                duplicated["start_time"] = float(duplicated["start_time"]) + loop_length
                new_notes.append(duplicated)
            clip["notes"].extend(new_notes)
            clip["loop_end"] = loop_end + loop_length
            clip["end_marker"] = max(float(clip.get("end_marker", loop_end)), clip["loop_end"])
            clip["length_beats"] = clip["loop_end"] - loop_start
    elif tool == "clip_rename":
        _ensure_clip(int(args[0]), int(args[1]))["name"] = str(args[2])
    elif tool in {
        "clip_set_color",
        "clip_set_color_index",
        "clip_set_gain",
        "clip_set_pitch_coarse",
        "clip_set_pitch_fine",
        "clip_set_start_marker",
        "clip_set_end_marker",
        "clip_set_loop_start",
        "clip_set_loop_end",
        "clip_set_looping",
        "clip_set_position",
        "clip_set_warping",
        "clip_set_warp_mode",
        "clip_set_ram_mode",
        "clip_set_muted",
        "clip_set_launch_mode",
        "clip_set_launch_quantization",
        "clip_set_velocity_amount",
    }:
        field_map = {
            "clip_set_color": "color",
            "clip_set_color_index": "color_index",
            "clip_set_gain": "gain",
            "clip_set_pitch_coarse": "pitch_coarse",
            "clip_set_pitch_fine": "pitch_fine",
            "clip_set_start_marker": "start_marker",
            "clip_set_end_marker": "end_marker",
            "clip_set_loop_start": "loop_start",
            "clip_set_loop_end": "loop_end",
            "clip_set_looping": "looping",
            "clip_set_position": "position",
            "clip_set_warping": "warping",
            "clip_set_warp_mode": "warp_mode",
            "clip_set_ram_mode": "ram_mode",
            "clip_set_muted": "muted",
            "clip_set_launch_mode": "launch_mode",
            "clip_set_launch_quantization": "launch_quantization",
            "clip_set_velocity_amount": "velocity_amount",
        }
        clip = _ensure_clip(int(args[0]), int(args[1]))
        clip[field_map[tool]] = args[2]
        if tool == "clip_set_loop_end":
            clip["length_beats"] = max(float(args[2]) - float(clip.get("loop_start", 0.0)), 0.0)
        elif tool == "clip_set_loop_start":
            clip["length_beats"] = max(float(clip.get("loop_end", args[2])) - float(args[2]), 0.0)
    elif tool == "midi_notes_add":
        clip = _ensure_clip(int(args[0]), int(args[1]))
        for offset in range(2, len(args), 5):
            pitch, start_time, duration, velocity, mute = args[offset:offset + 5]
            clip["notes"].append(
                {
                    "pitch": int(pitch),
                    "start_time": float(start_time),
                    "duration": float(duration),
                    "velocity": float(velocity),
                    "mute": bool(mute),
                }
            )
    elif tool in {"midi_notes_remove", "midi_notes_clear"}:
        clip = _ensure_clip(int(args[0]), int(args[1]))
        if len(args) == 2:
            clip["notes"] = []
        else:
            start_pitch, pitch_span, start_time, time_span = int(args[2]), int(args[3]), float(args[4]), float(args[5])
            end_pitch = start_pitch + pitch_span
            end_time = start_time + time_span
            clip["notes"] = [
                note
                for note in clip.get("notes", [])
                if not (
                    start_pitch <= int(note["pitch"]) < end_pitch
                    and start_time <= float(note["start_time"]) < end_time
                )
            ]
    elif tool == "device_set_parameter":
        track = _ensure_track(int(args[0]))
        device_index = int(args[1])
        while len(track["devices"]) <= device_index:
            track["devices"].append({"device_index": len(track["devices"]), "name": "Device", "parameters": {}})
        track["devices"][device_index]["parameters"][int(args[2])] = float(args[3])
    elif tool == "device_set_parameters":
        track = _ensure_track(int(args[0]))
        device_index = int(args[1])
        while len(track["devices"]) <= device_index:
            track["devices"].append({"device_index": len(track["devices"]), "name": "Device", "parameters": {}})
        for parameter_index, value in enumerate(args[2:]):
            track["devices"][device_index]["parameters"][parameter_index] = float(value)
    elif tool == "device_delete":
        track = _ensure_track(int(args[0]))
        device_index = int(args[1])
        if 0 <= device_index < len(track["devices"]):
            track["devices"].pop(device_index)
            for idx, device in enumerate(track["devices"]):
                device["device_index"] = idx


def _execute_actions(actions: list[Any], *, approved: bool, dry_run: bool) -> tuple[list[dict[str, Any]], str | None]:
    try:
        report, executed_at = _run_actions(
            actions,
            ableton_host=settings.ableton_host,
            ableton_port=settings.ableton_port,
            approved=approved,
            dry_run=dry_run,
        )
    except PermissionError as exc:
        _raise_api_error(status_code=400, code="approval_required", message=str(exc))
        return [], None  # unreachable
    except RuntimeError as exc:
        _raise_api_error(status_code=502, code="osc_send_failed", message=str(exc))
        return [], None  # unreachable

    if not dry_run:
        for action in actions:
            _apply_action_to_live_state(action)

    return report, executed_at


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
        extra_prompt=planner_extra_prompt(settings),
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
    return {"status": "ok", "version": __version__}


_WEB_ROOT = Path(__file__).parent.parent / "web"


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    html = _WEB_ROOT / "index.html"
    if not html.exists():
        return "<h1>LLM-r</h1><p>Web UI not found.</p>"
    return html.read_text(encoding="utf-8")


@app.get("/api/capabilities")
def get_capabilities(
    domain: str | None = None,
    safety: str | None = None,
    include_destructive: bool = True,
) -> dict:
    rows = []
    for cap in capabilities():
        if domain and cap.domain != domain:
            continue
        if safety and cap.safety != safety:
            continue
        if not include_destructive and cap.destructive:
            continue
        rows.append(
            {
                "tool": cap.tool.value,
                "description": cap.description,
                "args_schema": cap.args_schema,
                "destructive": cap.destructive,
                "domain": cap.domain,
                "safety": cap.safety,
            }
        )
    return {"capabilities": rows, "count": len(rows)}


@app.get("/api/live/song")
def get_live_song_state() -> dict:
    return {"song": _live_state["song"]}


@app.get("/api/live/tracks")
def get_live_tracks() -> dict:
    return {"tracks": _live_state["tracks"], "count": len(_live_state["tracks"])}


@app.get("/api/live/tracks/{track_id}/devices")
def get_live_track_devices(track_id: int) -> dict:
    if track_id < 0 or track_id >= len(_live_state["tracks"]):
        _raise_api_error(status_code=404, code="track_not_found", message="Track not found")
    return {"track_index": track_id, "devices": _live_state["tracks"][track_id]["devices"]}


@app.get("/api/live/tracks/{track_id}/clips")
def get_live_track_clips(track_id: int) -> dict:
    if track_id < 0 or track_id >= len(_live_state["tracks"]):
        _raise_api_error(status_code=404, code="track_not_found", message="Track not found")
    return {"track_index": track_id, "clips": _live_state["tracks"][track_id]["clips"]}


@app.get("/api/live/tracks/{track_id}/parameters")
def get_live_track_parameters(track_id: int) -> dict:
    if track_id < 0 or track_id >= len(_live_state["tracks"]):
        _raise_api_error(status_code=404, code="track_not_found", message="Track not found")
    devices = _live_state["tracks"][track_id]["devices"]
    flattened = [
        {"device_index": device["device_index"], "parameter_index": p_idx, "value": value}
        for device in devices
        for p_idx, value in device.get("parameters", {}).items()
    ]
    return {"track_index": track_id, "parameters": flattened, "count": len(flattened)}


@app.get("/api/settings")
def get_settings() -> dict:
    return {
        "modelito_provider": settings.modelito_provider,
        "modelito_model": settings.modelito_model,
        "planner_extra_prompt_enabled": settings.planner_extra_prompt_enabled,
        "planner_extra_prompt_path": settings.planner_extra_prompt_path,
        "ableton_host": settings.ableton_host,
        "ableton_port": settings.ableton_port,
    }


@app.patch("/api/settings", dependencies=[Depends(_require_auth)])
def update_settings(req: SettingsPatch) -> dict:
    if req.modelito_provider is not None:
        settings.modelito_provider = req.modelito_provider
    if req.modelito_model is not None:
        settings.modelito_model = req.modelito_model
    if req.planner_extra_prompt_enabled is not None:
        settings.planner_extra_prompt_enabled = req.planner_extra_prompt_enabled
    if req.planner_extra_prompt_path is not None:
        settings.planner_extra_prompt_path = req.planner_extra_prompt_path
    if req.ableton_host is not None:
        settings.ableton_host = req.ableton_host
    if req.ableton_port is not None:
        settings.ableton_port = req.ableton_port
    if req.api_token is not None:
        settings.api_token = req.api_token
    settings.save()
    return get_settings()


@app.get("/api/models")
def get_models() -> dict:
    client = ModelitoClient(provider=settings.modelito_provider, model=settings.modelito_model)
    return {
        "provider": settings.modelito_provider,
        "default_model": settings.modelito_model,
        "models": client.list_models(),
    }


@app.get("/api/modelito/models")
def get_modelito_model_ids(provider: str | None = None, model: str | None = None) -> dict:
    current_provider = (provider or settings.modelito_provider).strip()
    current_model = (model or settings.modelito_model).strip()
    return {
        "provider": current_provider,
        "default_model": current_model,
        "models": modelito_models(current_provider, current_model),
    }


@app.get("/api/ollama/status")
def get_ollama_status() -> dict:
    return ollama_status()


@app.get("/api/ollama/local_models")
def get_ollama_local_models() -> dict:
    return ollama_local_models()


@app.get("/api/ollama/remote_models")
def get_ollama_remote_models() -> dict:
    return ollama_remote_models()


@app.post("/api/ollama/start", dependencies=[Depends(_require_auth)])
def post_ollama_start() -> dict:
    return ollama_start()


@app.post("/api/ollama/stop", dependencies=[Depends(_require_auth)])
def post_ollama_stop() -> dict:
    return ollama_stop()


@app.post("/api/ollama/install", dependencies=[Depends(_require_auth)])
def post_ollama_install() -> dict:
    return ollama_install()


@app.post("/api/ollama/download", dependencies=[Depends(_require_auth)])
def post_ollama_download(req: OllamaModelRequest) -> dict:
    return ollama_download(req.model)


@app.post("/api/ollama/delete", dependencies=[Depends(_require_auth)])
def post_ollama_delete(req: OllamaModelRequest) -> dict:
    return ollama_delete(req.model)


@app.post("/api/ollama/serve", dependencies=[Depends(_require_auth)])
def post_ollama_serve(req: OllamaModelRequest) -> dict:
    return ollama_serve(req.model)


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

    execution_report, _ = _execute_actions(plan.actions, approved=req.approved, dry_run=req.dry_run)
    if not req.dry_run:
        plan = store.mark_executed(plan.id) or plan

    session_id = _plan_session_index.pop(plan.id, None)
    if session_id:
        session_store.add_history(
            session_id,
            plan_id=plan.id,
            prompt=plan.prompt,
            explanation=plan.explanation,
            confidence=plan.confidence,
            created_at=plan.created_at,
            executed_at=plan.executed_at,
        )

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
        "execution_report": execution_report,
    }


@app.post("/api/execute_batch", dependencies=[Depends(_require_auth)])
def execute_batch(req: ExecuteBatchRequest) -> dict:
    if not req.calls:
        _raise_api_error(status_code=400, code="empty_batch", message="At least one call is required")
    ableton = AbletonOSCClient(settings.ableton_host, settings.ableton_port)
    try:
        actions = [ableton.to_action(call.tool, call.args) for call in req.calls]
    except ValueError as exc:
        _raise_api_error(status_code=400, code="invalid_call", message=str(exc))
    execution_report, executed_at = _execute_actions(actions, approved=req.approved, dry_run=req.dry_run)
    return {
        "executed_count": len(actions),
        "requires_approval": any(a.destructive for a in actions),
        "dry_run": req.dry_run,
        "executed_at": executed_at,
        "execution_report": execution_report,
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
