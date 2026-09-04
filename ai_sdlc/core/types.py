"""Core typed schemas. All cross-component messages flow through these."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class MissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_HITL = "waiting_hitl"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MissionBudget(BaseModel):
    max_usd: float = 5.0
    max_tool_calls: int = 50
    max_wall_seconds: int = 600
    spent_usd: float = 0.0
    tool_calls_used: int = 0


class Mission(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    id: str = Field(default_factory=lambda: _new_id("mission"))
    goal: str
    department: str = "platform"
    status: MissionStatus = MissionStatus.PENDING
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    parent_id: Optional[str] = None
    budget: MissionBudget = Field(default_factory=MissionBudget)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class AuditEvent(BaseModel):
    """Append-only record. Every step of every mission emits one of these."""

    id: str = Field(default_factory=lambda: _new_id("evt"))
    mission_id: str
    actor: str  # agent name or "orchestrator"/"system"
    actor_version: str = "0.1.0"
    event_type: str  # mission.start | agent.invoke | tool.call | llm.call |
    #                  policy.verdict | hitl.request | hitl.decision |
    #                  artifact.create | mission.end | error
    payload: dict[str, Any] = Field(default_factory=dict)
    cost_usd: float = 0.0
    occurred_at: datetime = Field(default_factory=_now)


class HITLDecision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class HITLRequest(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("hitl"))
    mission_id: str
    subject: str
    summary: str
    artifact_ref: Optional[str] = None
    risk_class: str = "default"
    required_approver_roles: list[str] = Field(default_factory=lambda: ["pm"])
    suggested_decision: Optional[HITLDecision] = None
    reasoning: Optional[str] = None
    decision: HITLDecision = HITLDecision.PENDING
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=_now)


class PolicyVerdict(str, Enum):
    PASS = "pass"
    BLOCK = "block"
    ROUTE_HITL = "route_hitl"


class PolicyResult(BaseModel):
    verdict: PolicyVerdict
    matched_rules: list[str] = Field(default_factory=list)
    reasoning: str = ""


class Artifact(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("art"))
    mission_id: str
    kind: str  # prd | design | code_patch | support_reply | qms_doc | ...
    content: Any
    created_by: str  # agent name
    signed: bool = False
    created_at: datetime = Field(default_factory=_now)
