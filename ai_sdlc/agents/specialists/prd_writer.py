"""PRDWriter — first Product specialist. Drafts a PRD, runs the policy
check, requests HITL approval, persists the signed artifact."""
from __future__ import annotations

from typing import Any

from ai_sdlc.agents.base import Agent, AgentContext, AgentSpec
from ai_sdlc.core.types import (
    Artifact,
    AuditEvent,
    HITLDecision,
    HITLRequest,
    PolicyVerdict,
)


class PRDWriter(Agent):
    spec = AgentSpec(
        name="PRDWriter",
        department="product",
        tools=["memory.write_artifact", "policy.check", "hitl.request"],
        scopes={"memory:write", "policy:check", "hitl:request"},
    )

    def run(self, ctx: AgentContext) -> dict[str, Any]:
        opportunity = ctx.mission.inputs.get(
            "opportunity", "an unspecified opportunity"
        )
        prompt = (
            f"Write a PRD for: {opportunity}.\n"
            "Use the sections: Problem, Users, Success metrics, Scope, "
            "Out of scope. Keep it under 500 words."
        )
        text, cost = ctx.llm.complete(
            model=self.spec.model,
            system="You write rigorous product requirements documents in markdown.",
            prompt=prompt,
            max_tokens=1500,
        )
        ctx.cost.charge(ctx.mission, cost)
        ctx.audit.record(
            AuditEvent(
                mission_id=ctx.mission.id,
                actor=self.spec.name,
                event_type="llm.call",
                payload={"model": self.spec.model, "output_len": len(text)},
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

        approval = ctx.hitl.request(
            HITLRequest(
                mission_id=ctx.mission.id,
                subject=f"PRD draft: {opportunity[:60]}",
                summary=text[:400] + ("..." if len(text) > 400 else ""),
                risk_class="product.prd",
                required_approver_roles=["pm"],
                suggested_decision=HITLDecision.APPROVED,
                reasoning="Policy check passed; standard PRD review gate.",
            )
        )
        ctx.audit.record(
            AuditEvent(
                mission_id=ctx.mission.id,
                actor=self.spec.name,
                event_type="hitl.decision",
                payload=approval.model_dump(),
            )
        )
        if approval.decision != HITLDecision.APPROVED:
            return {
                "status": "rejected_by_hitl",
                "decision": approval.decision,
                "decided_by": approval.decided_by,
            }

        artifact = ctx.memory.write_artifact(
            Artifact(
                mission_id=ctx.mission.id,
                kind="prd",
                content=text,
                created_by=self.spec.name,
                signed=True,
            )
        )
        ctx.audit.record(
            AuditEvent(
                mission_id=ctx.mission.id,
                actor=self.spec.name,
                event_type="artifact.create",
                payload={"artifact_id": artifact.id, "kind": "prd"},
            )
        )
        return {"prd_artifact_id": artifact.id, "text": text}
