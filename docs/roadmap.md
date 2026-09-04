# Roadmap

Six phases. Dates are relative; calendar dates added once we lock framework
and team.

## Phase 0 — Foundations (4–6 weeks)

Goal: pick the stack and stand up the platform agents so every later phase
inherits audit, HITL, policy, eval, and durable execution for free.

Workstreams:
- **Framework bake-off** (week 1–2): LangGraph, Temporal+agent layer,
  Claude Agent SDK, CrewAI, AutoGen. Same toy
  workflow ("draft PRD → generate test plan → request HITL approval →
  publish artifact"). Score on durability, HITL, observability, typed
  tools, multi-provider support, ops maturity, team velocity.
- **Tier 0 agents**: Orchestrator skeleton, Policy, Memory Librarian,
  Audit Recorder, HITL Coordinator, Identity, Eval Runner, Cost Controller.
- **MCP tool registry** with first 10 tools (memory.\*, audit.\*, policy.\*,
  hitl.\*, github.\*, slack.\*).
- **Environments**: dev / staging / prod, with secrets management and
  identity wiring (Okta or equivalent).
- **Mission Inspector v0** — single timeline of workflow + audit + HITL.

Exit criteria:
- Stack selected, ADR written.
- "Hello mission" runs end-to-end: 2 specialists, 1 HITL gate, signed audit
  log entries for every step, replayable from the log.
- Eval Runner blocks promotion of an intentionally broken prompt.

## Phase 1 — Engineering loop (6–10 weeks)

Goal: agent team can take a small, **non-regulated** spec and ship it.

Agents introduced:
- Product Lead, ProductDiscovery, PRDWriter, RoadmapPlanner
- Eng Lead, TechDesigner, Coder-Backend, Coder-Frontend, Reviewer,
  MigrationPlanner, ReleaseManager, SREOps
- Quality Lead, TestDesigner, AutomationEng, AccessibilityAuditor

Tools added: GitHub (full), Linear/Jira, CI/CD, feature flags, staging
deploy, observability read.

Mandatory HITL: prod deploys, schema migrations, anything customer-visible.

Exit criteria: agent team ships an internal-only tool (e.g., the Mission
Inspector itself), runs it for 30 days, P1 incidents = 0, mean cycle time
spec→prod ≤ a baseline.

## Phase 2 — Compliance & Security (6 weeks, partly parallel with Phase 1)

Goal: bring the regulatory backbone online so anything we build is
QMS-tracked from inception.

Agents introduced:
- RegComp Lead, SaMDClassifier, QMSAuthor, DesignControlsTrace,
  RiskMgmtISO14971, HIPAACompliance, GDPRCompliance, AuditPrep
- Security Lead, ThreatModeler, VulnTriager, SecQuestionnaireResponder,
  SecretsHygienist
- Clinical Lead (working with human CMO), ClinicalSafety

QMS bound to Phase 1 artifacts retroactively. Hazard log + traceability
matrix live.

Exit criteria: mock external HIPAA audit & internal QMS audit pass; first
SaMD classification decision recorded with full traceability.

## Phase 3 — Go-to-market (6–8 weeks)

Goal: agents handle the demand→cash motion within HITL guardrails.

Agents introduced:
- Revenue Lead, ContentMarketer, SEOAnalyst, DemandGen, SDR, AE,
  SolutionsEngineer, CSMHealth, RenewalsManager
- CX Lead, SupportTriage, SupportTier2, SupportTier3, KBEditor,
  OnboardingCoach

Tools added: CRM, marketing automation, helpdesk, status page, contract
mgmt, e-sign.

Mandatory HITL: pricing, contracts outside playbook, public comms.

Exit criteria: a deal taken from inbound lead → signed BAA → onboarded
customer → first invoice, with humans only at codified HITL gates.

## Phase 4 — Back office (6 weeks)

Goal: HR, Finance, Legal, IT fully agent-operated.

Agents introduced:
- People Lead, JDWriter, Sourcer, Screener, InterviewScheduler,
  OfferModeler, OnboardingProvisioner, PerfReviewFacilitator
- Finance Lead, AROps, APOps, ExpenseGuardian, Closer, RevRec, FPAModeler
- Legal Lead, ContractDrafter, RedlineReviewer, VendorRisk
- Ops/IT Lead, IdentityLifecycle, DeviceFleet, LicenseSteward, Procurement,
  ITHelpdesk

Exit criteria: a full monthly close runs agent-led; new-hire onboarding
runs agent-led; vendor onboarding runs agent-led; all with HITL only at
defined gates.

## Phase 5 — Hardening & scale (continuous)

Continuous workstreams:
- Cost controls and model routing (cheaper models where evals allow)
- Multi-region (US + EU) for GDPR
- Continuous eval, drift monitoring, red-teaming (incl. prompt-injection,
  PHI exfil, multi-agent collusion)
- Post-market surveillance loop into Product backlog
- Bake-off re-runs annually to avoid framework lock-in

## Cross-phase: skills the platform must already have

Even though listed in Phase 0, these never "finish":

- Eval suites for every agent (grow with every incident)
- Audit log integrity (periodic replay drills)
- HITL fatigue management (consolidate, batch, prioritize approvals)
- Documentation that an external auditor can read and verify
