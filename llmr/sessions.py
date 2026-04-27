from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class PlanHistoryItem:
    plan_id: str
    prompt: str
    created_at: str
    executed_at: str | None = None
    explanation: str = ""
    confidence: float = 0.0


@dataclass
class SessionRecord:
    session_id: str
    created_at: str
    updated_at: str
    history: list[PlanHistoryItem] = field(default_factory=list)


class SessionStore:
    def __init__(self, persist_path: str | None = None) -> None:
        self._persist_path = Path(persist_path) if persist_path else None
        self._sessions: dict[str, SessionRecord] = {}
        self._load()

    def list_sessions(self) -> list[SessionRecord]:
        return sorted(self._sessions.values(), key=lambda s: s.updated_at, reverse=True)

    def get_or_create(self, session_id: str | None = None) -> SessionRecord:
        sid = session_id or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        record = self._sessions.get(sid)
        if record is None:
            record = SessionRecord(session_id=sid, created_at=now, updated_at=now)
            self._sessions[sid] = record
            self._save()
        return record

    def add_history(
        self,
        session_id: str,
        *,
        plan_id: str,
        prompt: str,
        explanation: str,
        confidence: float,
        created_at: str,
        executed_at: str | None = None,
    ) -> None:
        record = self.get_or_create(session_id)
        for existing in record.history:
            if existing.plan_id == plan_id:
                existing.executed_at = executed_at or existing.executed_at
                record.updated_at = datetime.now(timezone.utc).isoformat()
                self._save()
                return
        record.history.append(
            PlanHistoryItem(
                plan_id=plan_id,
                prompt=prompt,
                explanation=explanation,
                confidence=confidence,
                created_at=created_at,
                executed_at=executed_at,
            )
        )
        record.updated_at = datetime.now(timezone.utc).isoformat()
        self._save()

    def get_session(self, session_id: str) -> SessionRecord | None:
        return self._sessions.get(session_id)

    def get_history(self, session_id: str | None = None, limit: int = 50) -> list[PlanHistoryItem]:
        if session_id:
            record = self._sessions.get(session_id)
            if not record:
                return []
            return sorted(record.history, key=lambda h: h.created_at, reverse=True)[:limit]

        all_items: list[PlanHistoryItem] = []
        for record in self._sessions.values():
            all_items.extend(record.history)
        return sorted(all_items, key=lambda h: h.created_at, reverse=True)[:limit]

    def _save(self) -> None:
        if not self._persist_path:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(record) for record in self._sessions.values()]
        self._persist_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._persist_path or not self._persist_path.exists():
            return
        try:
            raw = json.loads(self._persist_path.read_text(encoding="utf-8"))
        except Exception:
            return

        loaded: dict[str, SessionRecord] = {}
        for item in raw or []:
            try:
                history = [PlanHistoryItem(**h) for h in item.get("history", [])]
                record = SessionRecord(
                    session_id=item["session_id"],
                    created_at=item["created_at"],
                    updated_at=item.get("updated_at", item["created_at"]),
                    history=history,
                )
                loaded[record.session_id] = record
            except Exception:
                continue
        self._sessions = loaded
