# Architecture

How the agents actually run.

## Topology

```
                                    ┌──────────────────────────┐
                                    │   Human stakeholders     │
                                    │ (CEO, RA, Privacy, Clin) │
                                    └────────────┬─────────────┘
                                                 │ HITL approvals, vetoes
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           Orchestrator (Tier 0)                          │
│   Goal intake → decomposition → routing → reconciliation → reporting     │
└────────────┬──────────────┬──────────────┬──────────────┬───────────────┘
             │              │              │              │
             ▼              ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
       │ Product  │   │ Eng Lead │   │ RegComp  │   │  Revenue │  … one Lead
       │  Lead    │   │          │   │   Lead   │   │   Lead   │     per dept.
       └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
            │              │              │              │
            ▼              ▼              ▼              ▼
        Specialists    Specialists    Specialists    Specialists

                  ┌────────────────────────────────────────┐
                  │  Tier 0 platform services (shared)     │
                  │  Memory · Tools(MCP) · Policy · Audit  │
                  │  HITL · Eval · Identity · Cost         │
                  └────────────────────────────────────────┘
```

## Runtime

Durable workflow engine (**Temporal**, candidate) underneath an agent graph
framework (**LangGraph**, candidate). Why both:

- The agent framework expresses the *cognitive* topology (graph of agents,
  conditional edges, retries, sub-agents).
- The workflow engine gives us *durable execution*: every step is persisted,
  workflows survive process restarts, can be replayed deterministically for
  audit and debugging, and can sleep for days/weeks (e.g., a 510(k)
  submission lifecycle).

Each mission becomes a workflow instance with:

- Stable workflow ID (used as the audit correlation key)
- Versioned graph definition (so old workflows replay against their original
  logic)
- Activity steps for every tool call and LLM call
- Signals for HITL approvals
- Timers for SLAs

## Memory

Three stores, all written through the **Memory Librarian** agent's tools:

1. **Knowledge graph** — entities and relations: PRDs, designs, services,
   customers, contracts, policies, controls, hazards, risks, tickets,
   incidents. Used for traceability (e.g., "which PRDs link to hazard H-12?")
   and required for design controls.
2. **Vector store** — chunked embeddings of documents and conversations, for
   semantic retrieval.
3. **Relational system of record** — for tabular things that aren't in
   SaaS yet (mission registry, artifact registry, eval results, audit log).

Retention policies (especially for PHI and HR data) are enforced at the
Librarian layer. Agents cannot bypass.

## Tools (MCP)

Every external action is a typed MCP tool. Categories:

- **Source control & CI** — GitHub, Buildkite/Actions
- **Tracking** — Jira/Linear
- **Comms** — Slack, email, status page
- **CRM/CDP/Helpdesk** — Salesforce/HubSpot, Segment, Zendesk
- **Cloud** — AWS/GCP/Azure read-only by default, write tools require
  elevated scopes
- **Data** — Snowflake/BigQuery, dbt
- **Finance** — NetSuite, Stripe, banking
- **HR/IT** — Workday/Rippling, Okta, MDM
- **Healthcare** — FHIR sandbox, HL7 listener, EHR connectors (BAA-gated)
- **Internal** — memory.\*, audit.\*, policy.\*, hitl.\*

Per-call enforcement: tool ID + caller agent ID + mission ID + scope token.
The Identity service issues scope tokens at mission start; tools refuse
calls without a valid token.

## Policy / guardrails

A **Policy Agent** mediates every outbound artifact (PR body, email, doc,
support reply) before it leaves the company boundary. Checks:

- PHI / PII detectors (regex + ML, with allow-listing for legit cases)
- Prompt-injection / data-exfil heuristics on tool inputs and outputs
- Brand & tone (per playbook)
- Regulatory claims filter (no medical claims without RA sign-off)

A violation either blocks (hard fail) or routes to HITL (soft fail),
depending on the rule's severity.

## Human-in-the-loop

HITL is **codified**, not ad-hoc. The HITL Coordinator agent exposes typed
approval requests with:

- Subject, summary, full artifact link
- Risk classification & policy citation that triggered the gate
- Suggested decision + reasoning
- Required approver role(s) and quorum
- SLA timer

Approvers respond in Slack or a web UI; their decision is signed and stored
on the audit log. The mission resumes (or aborts) automatically.

Mandatory HITL list (initial):

- Prod deploy of any service that processes PHI
- Any PHI release outside the company boundary
- FDA / notified-body submissions
- Contract redlines outside the playbook
- Spend over a department-specific threshold
- Public comms (marketing, status page incident updates)
- Hiring offers
- Payroll runs and AP runs over threshold
- Clinical-safety-relevant changes

## Audit

Every step — mission start, agent invocation, tool call, LLM call, HITL
decision, artifact creation, policy verdict — emits an event to an
append-only, signed log (object store + write-once index). Events carry:

- Correlation IDs (mission, workflow, agent)
- Actor (agent ID + version) and authority (scope token ID)
- Inputs, outputs (or hashes for large payloads)
- Model + prompt version
- Cost (tokens, $)
- Policy decisions

Replays use this log as the source of truth. For 21 CFR Part 11 workflows,
the log is cryptographically signed and time-synced (RFC 3161).

## Evaluation

Three layers, all owned by the Eval Runner:

1. **Unit evals** per agent: input → expected output on a fixed dataset.
   Run on every change, gate merges.
2. **Workflow evals** per mission template: end-to-end on golden scenarios,
   including HITL stubs.
3. **Online monitoring**: drift, refusal rate, override rate, escaped-defect
   rate, customer-reported issues attributable to an agent.

Agents are **versioned**. Promotion from `candidate` → `production` requires
passing the suite at or above the promotion gate, plus a shadow period.

## Observability

LangSmith (or equivalent) for trace inspection during dev; Temporal UI for
workflow inspection; a custom "Mission Inspector" UI for ops/RA reviewers
that joins workflow state, audit events, artifacts, and HITL decisions in
one timeline.

## Failure modes & circuit breakers

- **Per-mission budget cap** (tokens, $, wall clock, tool calls). Trip → halt.
- **Loop detector** — same agent + same prompt > N times → halt, escalate.
- **Tool error rate** — per tool, per mission. Trip → fall back / halt.
- **Policy refusal storm** — Policy agent rejecting too many outputs from
  one agent → quarantine that agent version, alert Eval Runner.
- **Cross-tenant data check** — fail-closed on any access to a tenant the
  mission isn't scoped to.

## Deployment

- All agent code, prompts, and tool schemas are in this repo; promotion is
  gated by the Eval Runner.
- Separate envs: `dev` (no real data), `staging` (synthetic PHI only),
  `prod` (real, BAA-covered).
- Two-person rule for prod prompt/policy changes.
