"""Trivial specialist — generates a one-paragraph summary. Useful for tests
and as the smallest worked example of the Agent contract."""
from __future__ import annotations

from typing import Any

from ai_sdlc.agents.base import Agent, AgentContext, AgentSpec
from ai_sdlc.core.types import Artifact, AuditEvent, PolicyVerdict


class Summarizer(Agent):
    spec = AgentSpec(
        name="Summarizer",
        department="platform",
        tools=["memory.write_artifact", "policy.check"],
        scopes={"memory:write", "policy:check"},
    )

    def run(self, ctx: AgentContext) -> dict[str, Any]:
        topic = ctx.mission.inputs.get("topic", "an unspecified topic")
        prompt = f"Write a one-paragraph executive summary about: {topic}."
        text, cost = ctx.llm.complete(
            model=self.spec.model,
            system="You write tight, factual executive summaries.",
            prompt=prompt,
            max_tokens=300,
        )
        ctx.cost.charge(ctx.mission, cost)
        ctx.audit.record(
            AuditEvent(
                mission_id=ctx.mission.id,
                actor=self.spec.name,
                event_type="llm.call",
                payload={
                    "model": self.spec.model,
                    "prompt_len": len(prompt),
                    "output_len": len(text),
                },
                cost_usd=cost,
            )
        )

        verdict = ctx.policy.check(text)
        ctx.audit.record(
            AuditEvent(
                mission_id=ctx.mission.id,
                actor=self.spec.name,
                event_type="policy.verdict",
                payload=verdict.model_dump(),
            )
        )
        if verdict.verdict == PolicyVerdict.BLOCK:
            return {"status": "blocked", "reason": verdict.reasoning}

        artifact = ctx.memory.write_artifact(
            Artifact(
                mission_id=ctx.mission.id,
                kind="summary",
                content=text,
                created_by=self.spec.name,
            )
        )
        ctx.audit.record(
            AuditEvent(
                mission_id=ctx.mission.id,
                actor=self.spec.name,
                event_type="artifact.create",
                payload={"artifact_id": artifact.id, "kind": "summary"},
            )
        )
        return {"summary_artifact_id": artifact.id, "text": text}
