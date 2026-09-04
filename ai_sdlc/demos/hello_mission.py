"""End-to-end demo: PRDWriter takes an opportunity → draft → policy check →
HITL gate (auto-approved) → signed artifact → audit replay.

Run with the mock LLM (no API key required):
    python -m ai_sdlc.demos.hello_mission

Run for real:
    AI_SDLC_MOCK_LLM=0 ANTHROPIC_API_KEY=sk-... \\
        python -m ai_sdlc.demos.hello_mission
"""
from __future__ import annotations

import logging

from ai_sdlc.agents.specialists.prd_writer import PRDWriter
from ai_sdlc.agents.specialists.summarizer import Summarizer
from ai_sdlc.config import settings
from ai_sdlc.core.types import Mission
from ai_sdlc.orchestrator import Orchestrator


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    cfg = settings()
    print(f"[setup]   data_dir={cfg.data_dir}  mock_llm={cfg.mock_llm}  hitl={cfg.hitl_mode}\n")

    orch = Orchestrator(
        data_dir=cfg.data_dir,
        mock_llm=cfg.mock_llm,
        hitl_mode=cfg.hitl_mode,
    )
    orch.register_agent(PRDWriter())
    orch.register_agent(Summarizer())
    print(f"[setup]   registered agents: {orch.agents()}\n")

    mission = Mission(
        goal="Draft a PRD for the Mission Inspector tool",
        department="product",
        inputs={
            "opportunity": (
                "Mission Inspector — a unified timeline UI for ops and "
                "regulatory reviewers showing every agent step, artifact, "
                "and human approval per mission."
            )
        },
    )
    print(f"[submit]  mission={mission.id} → PRDWriter")
    result = orch.submit(mission, agent_name="PRDWriter")
    print(f"[done]    status={result.status}  cost=${result.budget.spent_usd:.4f}\n")

    if "prd_artifact_id" in result.outputs:
        print(f"[artifact] {result.outputs['prd_artifact_id']}")
        print("--- PRD (truncated) ---")
        print(result.outputs["text"][:500] + ("..." if len(result.outputs["text"]) > 500 else ""))
        print("-----------------------\n")

    print("[audit]   timeline:")
    for ev in orch.audit.for_mission(mission.id):
        print(
            f"  {ev.occurred_at}  {ev.actor:<14}  "
            f"{ev.event_type:<18}  ${ev.cost_usd:.4f}"
        )


if __name__ == "__main__":
    main()
