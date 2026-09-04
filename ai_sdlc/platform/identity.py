"""Mission-scoped capability tokens. Tools check these on every call."""
from __future__ import annotations

from dataclasses import dataclass
from secrets import token_urlsafe

from ai_sdlc.core.types import Mission


@dataclass
class ScopeToken:
    token: str
    mission_id: str
    agent: str
    scopes: frozenset[str]


class Identity:
    def __init__(self) -> None:
        self._tokens: dict[str, ScopeToken] = {}

    def issue(self, mission: Mission, agent: str, scopes: set[str]) -> ScopeToken:
        tok = ScopeToken(
            token=token_urlsafe(16),
            mission_id=mission.id,
            agent=agent,
            scopes=frozenset(scopes),
        )
        self._tokens[tok.token] = tok
        return tok

    def verify(self, token: str, required_scope: str, mission_id: str) -> bool:
        record = self._tokens.get(token)
        if record is None:
            return False
        if record.mission_id != mission_id:
            return False
        return required_scope in record.scopes

    def revoke_mission(self, mission_id: str) -> int:
        before = len(self._tokens)
        self._tokens = {
            k: v for k, v in self._tokens.items() if v.mission_id != mission_id
        }
        return before - len(self._tokens)
