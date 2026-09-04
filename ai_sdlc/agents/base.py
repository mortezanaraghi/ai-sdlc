"""Agent contract + LLM client wrapper.

An Agent is a function from (mission, context) -> outputs. The orchestrator
owns the lifecycle; agents are reusable. LLMClient is a thin wrapper around
the Anthropic SDK with a deterministic mock mode for tests/demos.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from logging import Logger
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ai_sdlc.core.types import Mission
    from ai_sdlc.platform.audit import AuditLog
    from ai_sdlc.platform.cost import CostController
    from ai_sdlc.platform.hitl import HITLCoordinator
    from ai_sdlc.platform.identity import ScopeToken
    from ai_sdlc.platform.memory import MemoryStore
    from ai_sdlc.platform.policy import PolicyAgent


@dataclass
class AgentSpec:
    name: str
    department: str
    model: str = "claude-opus-4-7"
    fallback_model: str = "claude-sonnet-4-6"
    tools: list[str] = field(default_factory=list)
    scopes: set[str] = field(default_factory=set)
    max_tool_calls: int = 20
    version: str = "0.1.0"


@dataclass
class AgentContext:
    """The runtime handles a specialist sees. Injected by the orchestrator."""

    mission: "Mission"
    llm: "LLMClient"
    audit: "AuditLog"
    memory: "MemoryStore"
    policy: "PolicyAgent"
    hitl: "HITLCoordinator"
    cost: "CostController"
    scope_token: "ScopeToken"
    log: Logger


class Agent(ABC):
    spec: AgentSpec

    @abstractmethod
    def run(self, ctx: AgentContext) -> dict[str, Any]: ...


class LLMClient:
    """Anthropic SDK with a deterministic mock fallback."""

    def __init__(self, mock: bool = True) -> None:
        self.mock = mock
        self._client = None
        if not mock:
            try:
                import anthropic  # type: ignore

                self._client = anthropic.Anthropic()
            except Exception:  # noqa: BLE001
                self.mock = True

    def complete(
        self,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int = 1024,
    ) -> tuple[str, float]:
        """Returns (text, estimated_cost_usd)."""
        if self.mock:
            return _mock_response(prompt), 0.0
        assert self._client is not None
        msg = self._client.messages.create(
            model=model,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        text = "".join(getattr(b, "text", "") for b in msg.content)
        usage = getattr(msg, "usage", None)
        cost = 0.0
        if usage is not None:
            # Coarse placeholder rates; real cost goes through model-router.
            cost = (
                usage.input_tokens * 3.0 + usage.output_tokens * 15.0
            ) / 1_000_000
        return text, cost


def _mock_response(prompt: str) -> str:
    """Canned outputs keyed on prompt content. Deterministic for tests."""
    p = prompt.lower()
    if "prd" in p or "product requirements" in p:
        return (
            "# PRD: Mission Inspector\n\n"
            "## Problem\n"
            "Ops and Regulatory reviewers need a single timeline view of agent "
            "missions, artifacts produced, and human approvals — today they "
            "stitch this from logs by hand.\n\n"
            "## Users\n"
            "Internal: ops on-call, RegAffairs reviewers, engineering tech-leads.\n\n"
            "## Success metrics\n"
            "- Mean time to review a mission drops 60%.\n"
            "- 100% of regulated missions surfaceable in <2s.\n\n"
            "## Scope\n"
            "- Mission list with status, owner, cost.\n"
            "- Per-mission timeline of audit events.\n"
            "- Artifact preview + signature status.\n"
            "- HITL decision history.\n\n"
            "## Out of scope\n"
            "- Editing artifacts.\n"
            "- Cross-tenant aggregation.\n"
        )
    if "summarize" in p or "summary" in p:
        return (
            "This is a deterministic mock summary. Real LLM calls are skipped "
            "because AI_SDLC_MOCK_LLM=1 (or anthropic isn't installed)."
        )
    if "test plan" in p:
        return (
            "Test plan:\n"
            "1. Smoke: mission completes for happy path.\n"
            "2. Policy: PHI in inputs blocks.\n"
            "3. Cost: exceeding budget halts mission.\n"
            "4. Audit: every event emitted in order.\n"
        )
    return "Mock LLM response."
