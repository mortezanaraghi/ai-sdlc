"""Append-only audit log. SQLite-backed; later swap for object-store + WORM index."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from ai_sdlc.core.types import AuditEvent

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    actor TEXT NOT NULL,
    actor_version TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    cost_usd REAL NOT NULL,
    occurred_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_mission ON audit_events(mission_id);
CREATE INDEX IF NOT EXISTS idx_audit_type ON audit_events(event_type);
"""


class AuditLog:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(_SCHEMA)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def record(self, event: AuditEvent) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    event.id,
                    event.mission_id,
                    event.actor,
                    event.actor_version,
                    event.event_type,
                    json.dumps(event.payload, default=str),
                    event.cost_usd,
                    event.occurred_at.isoformat(),
                ),
            )

    def for_mission(self, mission_id: str) -> list[AuditEvent]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT id, mission_id, actor, actor_version, event_type, "
                "payload, cost_usd, occurred_at FROM audit_events "
                "WHERE mission_id = ? ORDER BY occurred_at ASC, id ASC",
                (mission_id,),
            ).fetchall()
        return [
            AuditEvent(
                id=r[0],
                mission_id=r[1],
                actor=r[2],
                actor_version=r[3],
                event_type=r[4],
                payload=json.loads(r[5]),
                cost_usd=r[6],
                occurred_at=r[7],
            )
            for r in rows
        ]
