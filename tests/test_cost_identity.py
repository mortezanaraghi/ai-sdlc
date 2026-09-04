import pytest

from ai_sdlc.core.types import Mission, MissionBudget
from ai_sdlc.platform.cost import BudgetExceeded, CostController
from ai_sdlc.platform.identity import Identity


def test_budget_exceeded_raises():
    cost = CostController()
    m = Mission(goal="t", budget=MissionBudget(max_usd=1.0))
    cost.charge(m, 0.4)
    cost.charge(m, 0.5)
    with pytest.raises(BudgetExceeded):
        cost.charge(m, 0.2)


def test_tool_call_budget():
    cost = CostController()
    m = Mission(goal="t", budget=MissionBudget(max_tool_calls=2))
    cost.charge(m, tool_calls=1)
    cost.charge(m, tool_calls=1)
    with pytest.raises(BudgetExceeded):
        cost.charge(m, tool_calls=1)


def test_identity_scope_token():
    ident = Identity()
    m = Mission(goal="t")
    tok = ident.issue(m, "Summarizer", {"memory:write"})
    assert ident.verify(tok.token, "memory:write", m.id) is True
    assert ident.verify(tok.token, "memory:read", m.id) is False
    assert ident.verify(tok.token, "memory:write", "wrong-mission") is False
    ident.revoke_mission(m.id)
    assert ident.verify(tok.token, "memory:write", m.id) is False
