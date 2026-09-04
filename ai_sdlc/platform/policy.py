"""Policy agent: PHI/PII detection + regulatory-claim guardrails.

This is a deliberately simple regex-based first pass. Production replaces
with ML detectors and an allow-list policy DSL. Every outbound artifact
runs through `check()` before leaving the company boundary.
"""
from __future__ import annotations

import re

from ai_sdlc.core.types import PolicyResult, PolicyVerdict

_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_MRN = re.compile(r"\bMRN[:\s]+\S+", re.IGNORECASE)
_DOB = re.compile(r"\b(?:dob|date of birth)[:\s]+\S+", re.IGNORECASE)
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")

_MEDICAL_CLAIM_PHRASES = (
    "cures",
    "treats",
    "prevents",
    "diagnoses",
    "fda approved",
    "fda-approved",
    "clinically proven",
    "guaranteed to",
)


class PolicyAgent:
    """Gates every outbound artifact.

    Verdicts:
      - PASS:        no issues, ship it.
      - BLOCK:       hard fail (e.g., PHI in outbound copy).
      - ROUTE_HITL:  soft fail; route to a human for sign-off.
    """

    def __init__(self, strict_phi: bool = True) -> None:
        self.strict_phi = strict_phi

    def check(self, text: str, context: str = "outbound") -> PolicyResult:
        matched: list[str] = []

        if _SSN.search(text):
            matched.append("phi.ssn")
        if _MRN.search(text):
            matched.append("phi.mrn")
        if _DOB.search(text):
            matched.append("phi.dob")
        if _PHONE.search(text):
            matched.append("pii.phone")
        if _EMAIL.search(text):
            matched.append("pii.email")

        lowered = text.lower()
        for phrase in _MEDICAL_CLAIM_PHRASES:
            if phrase in lowered:
                matched.append(f"reg.medical_claim:{phrase}")

        phi_hits = [m for m in matched if m.startswith("phi.")]
        med_hits = [m for m in matched if m.startswith("reg.medical_claim")]

        if phi_hits and self.strict_phi:
            return PolicyResult(
                verdict=PolicyVerdict.BLOCK,
                matched_rules=matched,
                reasoning=(
                    f"PHI markers detected ({', '.join(phi_hits)}) in "
                    f"context={context!r}; blocked."
                ),
            )

        if med_hits:
            return PolicyResult(
                verdict=PolicyVerdict.ROUTE_HITL,
                matched_rules=matched,
                reasoning=(
                    f"Medical claim ({', '.join(med_hits)}) requires "
                    "regulatory affairs sign-off."
                ),
            )

        return PolicyResult(
            verdict=PolicyVerdict.PASS,
            matched_rules=matched,
            reasoning="No blocking issues.",
        )
