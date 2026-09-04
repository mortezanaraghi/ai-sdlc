from ai_sdlc.core.types import PolicyVerdict
from ai_sdlc.platform.policy import PolicyAgent


def test_blocks_ssn():
    p = PolicyAgent()
    r = p.check("Patient SSN: 123-45-6789")
    assert r.verdict == PolicyVerdict.BLOCK
    assert "phi.ssn" in r.matched_rules


def test_blocks_mrn():
    p = PolicyAgent()
    r = p.check("Lookup MRN: 0042-XYZ")
    assert r.verdict == PolicyVerdict.BLOCK
    assert "phi.mrn" in r.matched_rules


def test_routes_medical_claim_to_hitl():
    p = PolicyAgent()
    r = p.check("Our software cures hypertension and is FDA approved.")
    assert r.verdict == PolicyVerdict.ROUTE_HITL
    assert any(rule.startswith("reg.medical_claim") for rule in r.matched_rules)


def test_passes_clean_text():
    p = PolicyAgent()
    r = p.check("This is a perfectly innocuous message.")
    assert r.verdict == PolicyVerdict.PASS


def test_strict_phi_off_allows_dob():
    p = PolicyAgent(strict_phi=False)
    r = p.check("DOB: 1990-01-01")
    assert r.verdict == PolicyVerdict.PASS
