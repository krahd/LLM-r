from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from llmr.ableton_osc import AbletonOSCClient, capabilities
from llmr.config import settings
<<<<<<< HEAD
=======
from llmr.macros import list_macros
>>>>>>> pr-2
from llmr.modelito_adapter import ModelitoClient
from llmr.planner import IntentPlanner, PlanStore


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)


<<<<<<< HEAD
=======
class MacroPlanRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)


>>>>>>> pr-2
class ExecuteRequest(BaseModel):
    plan_id: str
    approved: bool = False
    dry_run: bool = False


<<<<<<< HEAD
app = FastAPI(title="LLM-r", version="1.1.0")
store = PlanStore()
=======
app = FastAPI(title="LLM-r", version="1.3.0")
store = PlanStore(persist_path=settings.plan_store_path)
>>>>>>> pr-2


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
            from __future__ import annotations

            from fastapi import FastAPI, HTTPException
            from fastapi.responses import HTMLResponse
            from pydantic import BaseModel, Field

            from llmr.ableton_osc import AbletonOSCClient, capabilities
            from llmr.config import settings
            from llmr.macros import list_macros
            from llmr.modelito_adapter import ModelitoClient
            from llmr.planner import IntentPlanner, PlanStore


            class PromptRequest(BaseModel):
                prompt: str = Field(min_length=1, max_length=2000)


            class MacroPlanRequest(BaseModel):
                name: str = Field(min_length=1, max_length=128)


            class ExecuteRequest(BaseModel):
                plan_id: str
                approved: bool = False
                dry_run: bool = False


            app = FastAPI(title="LLM-r", version="1.3.0")
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

                if plan.executed_at:
                    raise HTTPException(status_code=409, detail="Plan already executed")

                if plan.requires_approval and not req.approved:
                    raise HTTPException(status_code=400, detail="Plan includes destructive actions and requires approval")

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
