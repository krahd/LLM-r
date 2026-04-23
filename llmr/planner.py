from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from llmr.ableton_osc import AbletonAction, AbletonOSCClient
from llmr.macros import get_macro
from llmr.modelito_adapter import ModelitoClient
from llmr.schemas import PlanEnvelope, PlannedToolCall, ToolName, parse_plan_envelope


_SYSTEM_PROMPT = """You are the LLM-r planner for Ableton Live.
Return ONLY valid JSON matching schema:
{
  "explanation": "short explanation",
  "confidence": 0.0,
  "calls": [
    {"tool": "set_tempo", "args": {"bpm": 128}},
    {"tool": "fire_clip", "args": {"track_index": 0, "clip_index": 0}}
  ]
}
Available tools:
create_midi_track, create_audio_track, set_tempo, fire_clip, stop_all_clips,
set_track_volume, set_track_mute, set_track_solo, arm_track, fire_scene.
"""


@dataclass
class StoredPlan:
    id: str
    prompt: str
    explanation: str
    confidence: float
    actions: list[AbletonAction]
    llm_raw: str
    created_at: str
    executed_at: str | None = None

    @property
    def requires_approval(self) -> bool:
        return any(a.destructive for a in self.actions)


class PlanStore:
    def __init__(
        self,
        max_items: int = 256,
        ttl_minutes: int = 60,
        persist_path: str | None = None,
    ) -> None:
        self._plans: dict[str, StoredPlan] = {}
        self._max_items = max_items
        self._ttl = timedelta(minutes=ttl_minutes)
        self._persist_path = Path(persist_path) if persist_path else None
        self._load()

    def put(self, plan: StoredPlan) -> None:
        self.prune()
        if len(self._plans) >= self._max_items:
            oldest = sorted(self._plans.values(), key=lambda p: p.created_at)[0]
            self._plans.pop(oldest.id, None)
        self._plans[plan.id] = plan
        self._save()

    def get(self, plan_id: str) -> StoredPlan | None:
        self.prune()
        return self._plans.get(plan_id)

    def mark_executed(self, plan_id: str) -> StoredPlan | None:
        plan = self.get(plan_id)
        if not plan:
            return None
        plan.executed_at = datetime.now(timezone.utc).isoformat()
        self._save()
        return plan

    def prune(self) -> None:
        now = datetime.now(timezone.utc)
        keep: dict[str, StoredPlan] = {}
        for pid, plan in self._plans.items():
            created = datetime.fromisoformat(plan.created_at)
            if now - created <= self._ttl:
                keep[pid] = plan
        if len(keep) != len(self._plans):
            self._plans = keep
            self._save()

    def _save(self) -> None:
        if not self._persist_path:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        serialized = [
            {
                "id": p.id,
                "prompt": p.prompt,
                "explanation": p.explanation,
                "confidence": p.confidence,
                "actions": [
                    {
                        "tool": a.tool.value,
                        "address": a.address,
                        "args": a.args,
                        "description": a.description,
                        "destructive": a.destructive,
                    }
                    for a in p.actions
                ],
                "llm_raw": p.llm_raw,
                "created_at": p.created_at,
                "executed_at": p.executed_at,
            }
            for p in self._plans.values()
        ]
        self._persist_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._persist_path or not self._persist_path.exists():
            return
        try:
            raw = json.loads(self._persist_path.read_text(encoding="utf-8"))
        except Exception:
            return
        plans: dict[str, StoredPlan] = {}
        for item in raw:
            actions = [
                AbletonAction(
                    tool=ToolName(a["tool"]),
                    address=a["address"],
                    args=a["args"],
                    description=a["description"],
                    destructive=bool(a.get("destructive", False)),
                )
                for a in item.get("actions", [])
            ]
            p = StoredPlan(
                id=item["id"],
                prompt=item.get("prompt", ""),
                explanation=item.get("explanation", ""),
                confidence=float(item.get("confidence", 0.0)),
                actions=actions,
                llm_raw=item.get("llm_raw", ""),
                created_at=item["created_at"],
                executed_at=item.get("executed_at"),
            )
            plans[p.id] = p
        self._plans = plans
        self.prune()


class IntentPlanner:
    def __init__(self, llm: ModelitoClient, ableton: AbletonOSCClient) -> None:
        self.llm = llm
        self.ableton = ableton

    def plan(self, user_prompt: str) -> StoredPlan:
        macro_calls = _maybe_parse_macro_prompt(user_prompt)
        if macro_calls is not None:
            return _build_stored_plan(
                prompt=user_prompt,
                explanation="Macro expansion plan.",
                confidence=1.0,
                calls=macro_calls,
                llm_raw='{"source":"macro"}',
                ableton=self.ableton,
            )

        result = self.llm.complete(f"{_SYSTEM_PROMPT}\nUser request: {user_prompt}")
        envelope = _parse_envelope(result.raw_text)
        return _build_stored_plan(
            prompt=user_prompt,
            explanation=envelope.explanation,
            confidence=envelope.confidence,
            calls=envelope.calls,
            llm_raw=result.raw_text,
            ableton=self.ableton,
        )


def _build_stored_plan(
    prompt: str,
    explanation: str,
    confidence: float,
    calls: list[PlannedToolCall],
    llm_raw: str,
    ableton: AbletonOSCClient,
) -> StoredPlan:
    actions = [ableton.to_action(call.tool, call.args) for call in calls]
    return StoredPlan(
        id=str(uuid.uuid4()),
        prompt=prompt,
        explanation=explanation,
        confidence=confidence,
        actions=actions,
        llm_raw=llm_raw,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _maybe_parse_macro_prompt(prompt: str) -> list[PlannedToolCall] | None:
    if not prompt.lower().startswith("macro:"):
        return None
    name = prompt.split(":", 1)[1].strip()
    return get_macro(name)


def _parse_envelope(text: str) -> PlanEnvelope:
    candidate = _extract_json_candidate(text)
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        data = {"explanation": "Could not parse LLM output as JSON.", "confidence": 0.0, "calls": []}
    try:
        return parse_plan_envelope(data)
    except Exception:
        return PlanEnvelope(explanation="LLM output invalid for schema.", confidence=0.0, calls=[])


def _extract_json_candidate(text: str) -> str:
    src = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", src, flags=re.IGNORECASE)
    if fence:
        return fence.group(1)
    start = src.find("{")
    end = src.rfind("}")
    if start != -1 and end > start:
        return src[start : end + 1]
    return src
