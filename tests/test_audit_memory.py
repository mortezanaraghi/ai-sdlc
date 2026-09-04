import tempfile
from pathlib import Path

from ai_sdlc.core.types import Artifact, AuditEvent
from ai_sdlc.platform.audit import AuditLog
from ai_sdlc.platform.memory import MemoryStore


def test_audit_round_trip():
    with tempfile.TemporaryDirectory() as d:
        log = AuditLog(Path(d) / "audit.sqlite")
        log.record(
            AuditEvent(
                mission_id="m1",
                actor="tester",
                event_type="mission.start",
                payload={"k": 1},
            )
        )
        log.record(
            AuditEvent(
                mission_id="m1",
                actor="tester",
                event_type="mission.end",
                payload={"k": 2},
                cost_usd=0.5,
            )
        )
        events = log.for_mission("m1")
        assert [e.event_type for e in events] == ["mission.start", "mission.end"]
        assert events[1].cost_usd == 0.5
        assert events[0].payload == {"k": 1}


def test_memory_round_trip():
    with tempfile.TemporaryDirectory() as d:
        mem = MemoryStore(Path(d) / "memory.sqlite")
        art = Artifact(
            mission_id="m1", kind="prd", content="hello", created_by="tester"
        )
        mem.write_artifact(art)
        fetched = mem.get(art.id)
        assert fetched is not None
        assert fetched.content == "hello"
        assert len(mem.search(mission_id="m1")) == 1
        assert len(mem.search(kind="prd")) == 1
        assert len(mem.search(kind="design")) == 0
