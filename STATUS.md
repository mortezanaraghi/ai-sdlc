# Implementation Status

This file tracks what's actually built vs. what's planned in `PLAN.md` and
`docs/roadmap.md`. Update it on every phase-relevant commit.

## Phase 0 — Foundations: **scaffolded & runnable**

| Capability | Status | Notes |
| --- | --- | --- |
| Mission + typed schemas | ✅ done | `ai_sdlc/core/types.py` (Pydantic v2) |
| Orchestrator (mission lifecycle, audit bookends) | ✅ minimal | `ai_sdlc/orchestrator.py` |
| Audit log (append-only) | ✅ SQLite | `ai_sdlc/platform/audit.py` — RFC 3161 signing TODO |
| Memory store | ✅ SQLite | `ai_sdlc/platform/memory.py` — KG + vectors TODO |
| Policy agent (PHI/PII + medical claims) | ✅ regex MVP | `ai_sdlc/platform/policy.py` — ML detectors TODO |
| HITL coordinator (auto / interactive / external) | ✅ minimal | `ai_sdlc/platform/hitl.py` — Slack/UI wiring TODO |
| Identity / scope tokens | ✅ minimal | `ai_sdlc/platform/identity.py` |
| Cost controller (budgets, circuit-break) | ✅ done | `ai_sdlc/platform/cost.py` |
| Eval runner (JSON suites) | ✅ minimal | `ai_sdlc/platform/evals.py` |
| MCP-style tool registry | ✅ skeleton | `ai_sdlc/tools/registry.py` |
| LLM client (Claude SDK + deterministic mock) | ✅ done | `ai_sdlc/agents/base.py` |
| Hello-mission demo | ✅ runs offline | `python -m ai_sdlc.demos.hello_mission` |
| Tests | ✅ smoke pass | policy, audit, memory, cost, identity, e2e |

**Phase 0 gaps before "production":**
- Durable workflow engine (Temporal). Today the run is in-process only.
- RFC 3161 timestamping + signed audit log.
- Vector store + knowledge graph in `MemoryStore`.
- Real MCP tool servers (currently a stub registry).
- Mission Inspector UI (today: stdout in `hello_mission`).
- Multi-tenant scoping.

## Phase 1 — Engineering loop: **first specialists, leads pending**

| Agent | Status |
| --- | --- |
| PRDWriter (Product) | ✅ first cut, mock LLM |
| Summarizer (platform) | ✅ first cut, mock LLM |
| ProductLead, EngineeringLead, QualityLead | 🟡 planned |
| TechDesigner, Coder-*, Reviewer, MigrationPlanner | 🟡 planned |
| TestDesigner, AutomationEng, AccessibilityAuditor | 🟡 planned |
| ReleaseManager, SREOps | 🟡 planned |

Phase 1 exit (per roadmap): non-regulated tool shipped by agent team, 30 days
in prod, 0 P1s. Not started.

## Phase 2 — Compliance & Security: **planned**

`SaMDClassifier`, `QMSAuthor`, `DesignControlsTrace`, `RiskMgmtISO14971`,
`HIPAACompliance`, `GDPRCompliance`, `AuditPrep`, `ThreatModeler`,
`VulnTriager`, `ClinicalSafety` — all 🟡.

## Phase 3 — Go-to-market: **planned**

Revenue + CX agents all 🟡.

## Phase 4 — Back office: **planned**

People, Finance, Legal, Ops/IT agents all 🟡.

## Phase 5 — Hardening: **planned**

Cost routing, multi-region, red-team, post-market loop — all 🟡.

## How to run

```bash
# Install
pip install -e ".[dev]"

# Run the demo (mock LLM, no API key)
python -m ai_sdlc.demos.hello_mission

# Run the tests
pytest -q

# Use a real Claude model
AI_SDLC_MOCK_LLM=0 ANTHROPIC_API_KEY=sk-... \
    python -m ai_sdlc.demos.hello_mission
```
