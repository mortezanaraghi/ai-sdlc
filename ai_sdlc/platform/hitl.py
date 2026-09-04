"""Human-in-the-loop coordinator.

Modes:
  - auto:        approve everything immediately (CI, demos).
  - interactive: prompt on stdin for y/n (local dev).
  - external:    no-op resolver — production wiring will signal back later.
"""
from __future__ import annotations

from datetime import datetime, timezone

from ai_sdlc.core.types import HITLDecision, HITLRequest


class HITLCoordinator:
    VALID_MODES = ("auto", "interactive", "external")

    def __init__(self, mode: str = "auto") -> None:
        if mode not in self.VALID_MODES:
            raise ValueError(f"unknown hitl mode {mode!r}")
        self.mode = mode
        self.pending: dict[str, HITLRequest] = {}

    def request(self, req: HITLRequest) -> HITLRequest:
        if self.mode == "auto":
            return self._resolve(req, HITLDecision.APPROVED, "auto-approver")
        if self.mode == "interactive":
            return self._resolve_interactive(req)
        # external: store and return immediately as pending
        self.pending[req.id] = req
        return req

    def resolve_external(
        self,
        req_id: str,
        decision: HITLDecision,
        decided_by: str,
    ) -> HITLRequest:
        if req_id not in self.pending:
            raise KeyError(req_id)
        req = self.pending.pop(req_id)
        return self._resolve(req, decision, decided_by)

    def _resolve_interactive(self, req: HITLRequest) -> HITLRequest:
        print("\n--- HITL Required ---")
        print(f"Subject:   {req.subject}")
        print(f"Summary:   {req.summary}")
        if req.reasoning:
            print(f"Reasoning: {req.reasoning}")
        print(f"Suggested: {req.suggested_decision}")
        answer = input("Approve? [y/N]: ").strip().lower()
        decision = HITLDecision.APPROVED if answer == "y" else HITLDecision.REJECTED
        return self._resolve(req, decision, "human-cli")

    @staticmethod
    def _resolve(
        req: HITLRequest, decision: HITLDecision, by: str
    ) -> HITLRequest:
        req.decision = decision
        req.decided_by = by
        req.decided_at = datetime.now(timezone.utc)
        return req
