# Plan: An Agentic SDLC Platform for Healthcare Software

## 1. Goal

Automate the operational load of building and running healthcare software
with specialized AI agents, coordinated by an orchestrator, so a small human
team spends its time on judgment rather than execution. Cover the
full SDLC — ideation → design → build → test → release → operate → support →
sell — and the surrounding business functions that make a company viable
(HR, Finance, Legal/Compliance, IT, Ops, Revenue, CX).

"Healthcare" is not cosmetic. It drives non-negotiable constraints:

- **HIPAA / HITECH** (US PHI handling), **GDPR** (EU PII), state laws (e.g. CMIA)
- **FDA SaMD** classification and **21 CFR Part 11** for any regulated workflow
- **HITRUST / SOC 2 Type 2** for enterprise sales
- **Audit trails**, signed approvals, validated systems, and **human-in-the-loop**
  checkpoints on anything affecting patient safety or regulatory posture

The agent design must bake these in from day one — they cannot be added later.

## 2. Scope and explicit non-goals

In scope:

- Operating model: departments, roles, tasks (see `docs/operating-model.md`)
- Agent catalog: one specialized agent per task family (see `docs/agent-catalog.md`)
- Orchestrator architecture, memory, tools, HITL, audit (see `docs/architecture.md`)
- Phased delivery roadmap (see `docs/roadmap.md`)
- Framework selection criteria and a recommendation

Out of scope for this plan (deferred to implementation phases):

- Specific medical device application(s) the company will build
- Vendor/tool procurement
- Hiring and role-design plan for the human team
- Detailed cost model (sketched, not finalized)

## 3. Assumptions

- A **small human core** remains: a CEO/founder, a regulatory affairs lead, a
  privacy/security officer, and on-call clinicians for safety-relevant
  decisions. Agents do not sign FDA submissions or take on clinician liability.
- We are willing to invest 6–12 months in foundations before scaling out.
- We have access to frontier LLMs (Claude 4.x family by default), an
  identity provider, a data warehouse, and standard SaaS (GitHub, Linear/Jira,
  Slack, etc.).

## 4. Operating model (summary)

Detailed list in [`docs/operating-model.md`](./docs/operating-model.md). High
level — 12 departments, ~70 roles, ~250 task families:

| Department | Example task families |
| --- | --- |
| **Executive / Strategy** | Vision, OKRs, capital allocation, board reporting |
| **Product** | Discovery, PRDs, prioritization, roadmap, PMM, UX research, design |
| **Engineering** | Frontend, backend, mobile, data, ML, platform, SRE, release |
| **Quality** | Test design, automation, exploratory, performance, accessibility, V&V |
| **Security** | AppSec, threat modeling, pen-test, IR, vuln mgmt, secrets |
| **Regulatory / Compliance** | SaMD classification, QMS, 21 CFR Part 11, HIPAA, GDPR, audits |
| **Clinical** | Clinical evidence, safety case, post-market surveillance, MedDRA coding |
| **Customer Experience** | Tier 1–3 support, onboarding, training, knowledge base |
| **Revenue** | Marketing, demand gen, sales, contracts, customer success, renewals |
| **People / HR** | Job design, hiring, onboarding, performance, payroll, culture |
| **Finance** | AR/AP, FP&A, revenue recognition, tax, treasury |
| **Operations / IT / Legal** | Vendor mgmt, procurement, BAAs, DPAs, internal tooling, identity |

Each task family becomes either a **dedicated agent** or a **skill** on a
broader agent (criteria in `docs/agent-catalog.md`).

## 5. Agent architecture (summary)

Full design in [`docs/architecture.md`](./docs/architecture.md). Core ideas:

1. **Three tiers** — Orchestrator → Department Leads → Specialists. The
   orchestrator decomposes goals into department-scoped missions; leads plan
   and dispatch to specialists; specialists do the work using tools.
2. **Durable, event-driven runtime** — every agent step is a checkpointed
   event so we can pause, resume, replay, and audit. This is required for
   regulatory posture and for long-running work like a 6-month release cycle.
3. **Typed tool layer (MCP)** — every external action (Git, Jira, Salesforce,
   AWS, EHR sandbox, Stripe, Workday…) is a typed MCP tool with explicit
   schemas, permission scopes, and per-call audit records.
4. **Shared memory** — a knowledge graph + vector store + relational store of
   record (policies, SOPs, PRDs, designs, tickets, customer records, audit
   logs). Agents read/write through tools, never out-of-band.
5. **Human-in-the-loop checkpoints** — codified, not ad-hoc. Any action whose
   blast radius crosses a defined threshold (patient safety, PHI release,
   spend > $X, prod deploy, external comms, FDA submission) blocks on a
   signed human approval.
6. **Policy / guardrails** — a separate policy agent enforces HIPAA, GDPR,
   QMS, and brand rules on every outbound artifact before it leaves the company.

## 6. Framework selection

We need: stateful multi-agent orchestration, durable execution, typed tools,
HITL, observability, and a healthy ecosystem. Candidates:

| Framework | Strengths | Weaknesses |
| --- | --- | --- |
| **LangGraph** (LangChain) | Graph-based, checkpointed state, HITL, tracing via LangSmith, big ecosystem | Python-centric, opinionated state model |
| **Temporal** + agent layer | Best-in-class durable execution, replayable, polyglot | Not agent-native; need to layer reasoning on top |
| **Claude Agent SDK** | First-class tool use, MCP, sub-agents, strong reasoning | Single-provider lock-in unless abstracted |
| **CrewAI** | Easy role-based modeling | Weaker durability/state story |
| **AutoGen** | Multi-agent dialogue patterns | Less production-ready ops story |
| **OpenAI Agents SDK / Swarm** | Lightweight handoffs | Single-provider, thin orchestration |

**Recommendation:** combine **Temporal (durable execution)** + **LangGraph
(agent graphs)** + **Claude Agent SDK / MCP (reasoning & tools)**. Temporal
gives us audit-grade workflows; LangGraph gives us the agent topology;
Claude+MCP gives us the cognition and a typed tool surface. If a candidate
proves better primitives at the orchestration layer, swap it in — the ports
and adapters around it are designed so the rest stays.

Decision is **provisional** and confirmed in Phase 0 via a bake-off.

## 7. Phased roadmap (summary)

Detail in [`docs/roadmap.md`](./docs/roadmap.md). Six phases:

1. **Phase 0 — Foundations (4–6 weeks).** Framework bake-off; pick stack;
   stand up identity, memory, MCP tool registry, audit log, eval harness, and
   the policy agent. Deliverable: a working "hello world" agent that takes
   a goal, calls 2 tools, and gets HITL approval, end-to-end auditable.
2. **Phase 1 — Engineering loop (6–10 weeks).** PM/Eng/QA/SRE agents that can
   take a small spec → PR → tests → staging → prod with HITL gates. This is
   the highest-leverage loop and the riskiest to get wrong.
3. **Phase 2 — Compliance & Security (6 weeks, partly parallel).** RegAffairs,
   QMS, Security, Privacy agents. QMS bound to every artifact in Phase 1.
4. **Phase 3 — Go-to-market (6–8 weeks).** Marketing, Sales, CS, Support
   agents. Connect to CRM/CDP/Helpdesk.
5. **Phase 4 — Back office (6 weeks).** HR, Finance, Legal, IT agents.
6. **Phase 5 — Hardening & scale (ongoing).** Cost controls, multi-region,
   continuous eval, post-market surveillance, red-teaming.

## 8. Healthcare-specific guardrails (cross-cutting)

These are not a phase — they apply to every agent from day one.

- **PHI minimization** — agents request the least data needed; PHI never
  enters prompts unless the tool path is explicitly approved and logged.
- **De-identification** broker for any agent that needs population data.
- **BAA-covered model hosting** for any agent that may touch PHI.
- **21 CFR Part 11** — electronic signatures, immutable audit trail, time
  sync, role-based access for the QMS agent's artifacts.
- **Validation (IQ/OQ/PQ)** of agent workflows that touch the QMS.
- **Safety case** — clinical-safety agent produces and maintains a hazard
  log; any change with safety impact gates on the human clinical lead.
- **Model risk management** — every agent has model cards, eval scores,
  drift monitors, and a rollback path.

## 9. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Hallucinated regulatory advice | RegAffairs agent restricted to retrieval + cite-or-refuse; human RA lead signs all submissions |
| PHI leakage via prompt | Policy agent scans every prompt/response; PHI tools require scope tokens; eval suite includes PHI red-team |
| Runaway cost from agent loops | Per-workflow budgets, step caps, circuit breakers, Temporal timeouts |
| Vendor lock-in | Abstract model + tool layer behind a stable internal interface |
| Audit failure | Every step durably logged with inputs, outputs, signer; periodic replay drills |
| Over-automation of safety-critical decisions | Explicit HITL list with veto rights for clinical / RA / privacy officers |
| Framework churn | Re-evaluate at end of each phase; isolate framework code behind ports/adapters |

## 10. Success metrics

- **Phase 1 exit**: agent-driven team ships and operates a non-regulated
  internal tool with zero P1 incidents for 30 days; cycle time < a comparable
  human team.
- **Phase 2 exit**: passes a mock external HIPAA audit and an internal QMS audit.
- **Phase 4 exit**: end-to-end deal — lead → signed BAA → onboarded customer
  → live invoice — executed without a human in the critical path except at
  the codified HITL gates.
- **Steady state**: % of tasks fully automated, mean cost per resolved task,
  human override rate, escaped-defect rate, audit findings per quarter.

## 11. Open questions

1. **First product** — do we have a concrete healthcare product in mind, or
   do we want the "company" to also do the discovery? The former is easier
   to evaluate; the latter is the truer test.
2. **Human core** — confirm which roles stay human (we've assumed CEO, RA
   lead, privacy/security officer, clinical lead). Anything else?
3. **Compute budget** — is there a monthly LLM/infra ceiling we should
   design to? It changes which agents are "always-on" vs. on-demand.
4. **Geography** — US-only first, or US + EU from day one? Affects GDPR
   work in Phase 2.

## 12. Next steps

- Get answers to §11.
- Spin up Phase 0 bake-off: 1 week per framework, same toy workflow, score
  on the criteria in §6.
- Stand up the audit log + policy agent + MCP tool registry — these are
  prerequisites for everything else and should land in week 2 regardless of
  framework choice.
