"""Tier-0 Orchestrator. Owns mission lifecycle, wires platform services to
agents, emits the mission.start/mission.end audit bookends."""
from __future__ import annotations

import logging
from pathlib import Path

from ai_sdlc.agents.base import Agent, AgentContext, LLMClient
from ai_sdlc.core.types import AuditEvent, Mission, MissionStatus
from ai_sdlc.platform.audit import AuditLog
from ai_sdlc.platform.cost import BudgetExceeded, CostController
from ai_sdlc.platform.hitl import HITLCoordinator
from ai_sdlc.platform.identity import Identity
from ai_sdlc.platform.memory import MemoryStore
from ai_sdlc.platform.policy import PolicyAgent


class Orchestrator:
    def __init__(
        self,
        *,
        data_dir: Path,
        mock_llm: bool = True,
        hitl_mode: str = "auto",
    ) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.audit = AuditLog(self.data_dir / "audit.sqlite")
        self.memory = MemoryStore(self.data_dir / "memory.sqlite")
        self.policy = PolicyAgent()
        self.hitl = HITLCoordinator(mode=hitl_mode)
        self.identity = Identity()
        self.cost = CostController()
        self.llm = LLMClient(mock=mock_llm)

        self._agents: dict[str, Agent] = {}
        self._log = logging.getLogger("ai_sdlc.orchestrator")

    def register_agent(self, agent: Agent) -> None:
        if agent.spec.name in self._agents:
            raise ValueError(f"agent {agent.spec.name!r} already registered")
        self._agents[agent.spec.name] = agent

    def agents(self) -> list[str]:
        return sorted(self._agents)

    def submit(self, mission: Mission, agent_name: str) -> Mission:
        if agent_name not in self._agents:
            raise KeyError(f"unknown agent {agent_name!r}")
        agent = self._agents[agent_name]
        mission.status = MissionStatus.RUNNING

        self.audit.record(
            AuditEvent(
                mission_id=mission.id,
                actor="orchestrator",
                event_type="mission.start",
                payload={
                    "goal": mission.goal,
                    "agent": agent_name,
                    "inputs": mission.inputs,
                    "budget": mission.budget.model_dump(),
                },
            )
        )
        token = self.identity.issue(mission, agent_name, agent.spec.scopes)
        ctx = AgentContext(
            mission=mission,
            llm=self.llm,
            audit=self.audit,
            memory=self.memory,
            policy=self.policy,
            hitl=self.hitl,
            cost=self.cost,
            scope_token=token,
            log=self._log.getChild(agent_name),
        )

        try:
            self.audit.record(
                AuditEvent(
                    mission_id=mission.id,
                    actor="orchestrator",
                    event_type="agent.invoke",
                    payload={"agent": agent_name, "version": agent.spec.version},
                )
            )
            result = agent.run(ctx)
            mission.outputs = result
            terminal_failure_markers = ("blocked", "rejected_by_hitl")
            if result.get("status") in terminal_failure_markers:
                mission.status = MissionStatus.FAILED
            else:
                mission.status = MissionStatus.SUCCEEDED
        except BudgetExceeded as e:
            mission.outputs = {"error": "budget_exceeded", "detail": str(e)}
            mission.status = MissionStatus.FAILED
            self.audit.record(
                AuditEvent(
                    mission_id=mission.id,
                    actor="orchestrator",
                    event_type="error",
                    payload={"kind": "BudgetExceeded", "detail": str(e)},
                )
            )
        except Exception as e:  # noqa: BLE001
            mission.outputs = {"error": "exception", "detail": str(e)}
            mission.status = MissionStatus.FAILED
            self.audit.record(
                AuditEvent(
                    mission_id=mission.id,
                    actor="orchestrator",
                    event_type="error",
                    payload={"kind": type(e).__name__, "detail": str(e)},
                )
            )
        finally:
            self.identity.revoke_mission(mission.id)
            self.audit.record(
                AuditEvent(
                    mission_id=mission.id,
                    actor="orchestrator",
                    event_type="mission.end",
                    payload={
                        "status": mission.status.value
                        if hasattr(mission.status, "value")
                        else mission.status,
                        "cost_usd": mission.budget.spent_usd,
                        "tool_calls": mission.budget.tool_calls_used,
                    },
                )
            )

        return mission
