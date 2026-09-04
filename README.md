# ai-sdlc

A blueprint and reference implementation of an **agentic SDLC platform built
against healthcare-grade compliance constraints** — specialized agents across
Product, Engineering, QA, DevOps, Security, Compliance, Operations and Finance,
coordinated by an orchestrator, with governance (policy, audit, human-in-the-
loop, evaluation) built into the runtime rather than bolted on afterwards.

Agents carry execution; humans keep judgment. Regulatory submissions, clinical
safety decisions, and PHI release are gated on named human roles by design —
see [§3](./PLAN.md) and the mandatory HITL list in
[`docs/architecture.md`](./docs/architecture.md).

## Status

Phase 0 (Foundations) is **scaffolded and runnable**. Phase 1+ are stubbed.
See [`STATUS.md`](./STATUS.md) for a per-component breakdown.

## Quick start

```bash
pip install -e ".[dev]"

# Run the end-to-end demo (mock LLM, no API key required).
python -m ai_sdlc.demos.hello_mission

# Run the test suite.
pytest -q
```

What the demo does:

1. Spins up the Tier-0 platform services (audit log, memory, policy, HITL,
   identity, cost controller).
2. Registers two specialists (`PRDWriter`, `Summarizer`).
3. Submits a mission: "draft a PRD for the Mission Inspector tool".
4. `PRDWriter` calls the (mocked) LLM, runs the output through the policy
   agent, requests a HITL approval (auto-approved in demo mode), and
   persists a signed artifact.
5. Replays the full audit trail to stdout.

Set `AI_SDLC_MOCK_LLM=0` and provide `ANTHROPIC_API_KEY` to run with real
Claude.

## Repository layout

```
ai_sdlc/
  core/types.py            # Mission, AuditEvent, HITLRequest, Artifact, …
  platform/                # Tier-0 services
    audit.py  memory.py  policy.py  hitl.py
    identity.py  cost.py  evals.py
  tools/registry.py        # MCP-shaped tool registry
  agents/
    base.py                # Agent contract + LLM client (with mock mode)
    specialists/           # PRDWriter, Summarizer (P0/P1 preview)
    leads/                 # Department leads (planned)
  orchestrator.py          # Mission lifecycle
  demos/hello_mission.py   # End-to-end demo
docs/
  operating-model.md       # Departments, roles, ~250 task families
  agent-catalog.md         # Tier 0/1/2 agents, per-agent contract
  architecture.md          # Runtime, memory, tools, HITL, audit, evals
  roadmap.md               # P0 → P5 phased delivery
PLAN.md                    # The plan
STATUS.md                  # Live implementation status
evals/                     # Eval suites (JSON)
tests/                     # pytest smoke + e2e tests
```

## Documents

- [`PLAN.md`](./PLAN.md) — the plan
- [`docs/operating-model.md`](./docs/operating-model.md) — departments, roles, tasks
- [`docs/agent-catalog.md`](./docs/agent-catalog.md) — agents and their contracts
- [`docs/architecture.md`](./docs/architecture.md) — orchestrator, memory, tools, HITL
- [`docs/roadmap.md`](./docs/roadmap.md) — phased delivery
- [`STATUS.md`](./STATUS.md) — what's actually built right now
