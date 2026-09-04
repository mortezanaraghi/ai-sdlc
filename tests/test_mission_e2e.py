import tempfile
from pathlib import Path

from ai_sdlc.agents.specialists.prd_writer import PRDWriter
from ai_sdlc.agents.specialists.summarizer import Summarizer
from ai_sdlc.core.types import Mission, MissionStatus
from ai_sdlc.orchestrator import Orchestrator


def test_prd_mission_end_to_end():
    with tempfile.TemporaryDirectory() as d:
        orch = Orchestrator(data_dir=Path(d), mock_llm=True, hitl_mode="auto")
        orch.register_agent(PRDWriter())
        mission = Mission(
            goal="test PRD",
            department="product",
            inputs={"opportunity": "a thing customers want"},
        )
        result = orch.submit(mission, "PRDWriter")
        assert result.status == MissionStatus.SUCCEEDED
        assert "prd_artifact_id" in result.outputs
        events = orch.audit.for_mission(mission.id)
        types = [e.event_type for e in events]
        for expected in (
            "mission.start",
            "agent.invoke",
            "llm.call",
            "policy.verdict",
            "hitl.decision",
            "artifact.create",
            "mission.end",
        ):
            assert expected in types, f"missing {expected} in {types}"


def test_summarizer_mission():
    with tempfile.TemporaryDirectory() as d:
        orch = Orchestrator(data_dir=Path(d), mock_llm=True, hitl_mode="auto")
        orch.register_agent(Summarizer())
        mission = Mission(
            goal="summarize",
            inputs={"topic": "internal eval results"},
        )
        result = orch.submit(mission, "Summarizer")
        assert result.status == MissionStatus.SUCCEEDED
        assert "summary_artifact_id" in result.outputs


def test_policy_blocks_phi_in_output():
    """Force the mock LLM to never matter — directly verify policy guards."""
    from ai_sdlc.platform.policy import PolicyAgent
    from ai_sdlc.core.types import PolicyVerdict

    p = PolicyAgent()
    r = p.check("Notes for patient SSN 999-11-2222")
    assert r.verdict == PolicyVerdict.BLOCK
