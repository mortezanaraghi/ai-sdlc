"""Per-mission budget enforcement. One of the circuit breakers."""
from __future__ import annotations

from ai_sdlc.core.types import Mission


class BudgetExceeded(RuntimeError):
    pass


class CostController:
    def charge(
        self, mission: Mission, usd: float = 0.0, tool_calls: int = 0
    ) -> None:
        mission.budget.spent_usd += usd
        mission.budget.tool_calls_used += tool_calls
        if mission.budget.spent_usd > mission.budget.max_usd:
            raise BudgetExceeded(
                f"mission {mission.id} exceeded USD budget: "
                f"{mission.budget.spent_usd:.4f} > {mission.budget.max_usd:.4f}"
            )
        if mission.budget.tool_calls_used > mission.budget.max_tool_calls:
            raise BudgetExceeded(
                f"mission {mission.id} exceeded tool-call budget: "
                f"{mission.budget.tool_calls_used} > {mission.budget.max_tool_calls}"
            )
