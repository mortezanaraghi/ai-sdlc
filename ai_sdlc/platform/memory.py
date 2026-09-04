"""Artifact memory. SQLite stand-in for the eventual KG + vector + relational triad."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from ai_sdlc.core.types import Artifact

_SCHEMA = """
CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    content TEXT NOT NULL,
    created_by TEXT NOT NULL,
    signed INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_artifacts_mission ON artifacts(mission_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_kind ON artifacts(kind);
"""


class MemoryStore:
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

    def write_artifact(self, art: Artifact) -> Artifact:
        with self._conn() as c:
            c.execute(
                "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    art.id,
                    art.mission_id,
                    art.kind,
                    json.dumps(art.content, default=str),
                    art.created_by,
                    int(art.signed),
                    art.created_at.isoformat(),
                ),
            )
        return art

    def get(self, art_id: str) -> Optional[Artifact]:
        with self._conn() as c:
            row = c.execute(
                "SELECT * FROM artifacts WHERE id = ?", (art_id,)
            ).fetchone()
        return _row_to_artifact(row) if row else None

    def search(
        self,
        mission_id: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> list[Artifact]:
        query = "SELECT * FROM artifacts WHERE 1=1"
        params: list = []
        if mission_id is not None:
            query += " AND mission_id = ?"
            params.append(mission_id)
        if kind is not None:
            query += " AND kind = ?"
            params.append(kind)
        query += " ORDER BY created_at ASC, id ASC"
        with self._conn() as c:
            rows = c.execute(query, params).fetchall()
        return [_row_to_artifact(r) for r in rows]


def _row_to_artifact(row: tuple) -> Artifact:
    return Artifact(
        id=row[0],
        mission_id=row[1],
        kind=row[2],
        content=json.loads(row[3]),
        created_by=row[4],
        signed=bool(row[5]),
        created_at=row[6],
    )
