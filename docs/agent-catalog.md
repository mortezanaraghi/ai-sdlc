# Agent Catalog

How we turn the operating model (`operating-model.md`) into agents.

## Design rules

1. **One responsibility, one agent.** If two tasks share inputs, tools, and
   evaluation criteria, they collapse into one agent with two skills. If they
   diverge on any of those, split.
2. **Specialists are stateless to themselves, stateful through the runtime.**
   All memory goes through the shared memory tools, not the agent's local
   prompt history.
3. **Tools are typed (MCP).** No "execute shell" catch-all. Each capability
   is a named tool with a JSONSchema and a permission scope.
4. **Department Lead agents plan; Specialists execute.** Specialists don't
   pick goals; they take a typed mission, do the work, return a typed result.
5. **Every agent has an eval set** before it's allowed to run unattended.

## Agent tiers

### Tier 0 — Platform agents (shared)

| Agent | Role |
| --- | --- |
| **Orchestrator** | Receives top-level goals; decomposes; routes missions to Department Leads; reconciles results |
| **Policy / Guardrail** | Pre- and post-filters every outbound artifact for HIPAA, GDPR, brand, profanity, prompt-injection |
| **Memory Librarian** | Owns corporate memory: write paths, schema validation, retention, deletion |
| **Audit Recorder** | Streams every step to an append-only, signed audit log |
| **Identity / Permissions** | Issues scoped tool tokens to other agents per mission |
| **HITL Coordinator** | Opens approval requests in Slack/email; tracks decisions; signs artifacts |
| **Eval Runner** | Runs offline/online evals; gates promotions of agent versions |
| **Cost Controller** | Tracks token spend per mission; enforces budgets, circuit-breaks loops |

### Tier 1 — Department Leads

One per department in `operating-model.md`. Each Lead:

- Owns the department's goals and KPIs
- Maintains its playbook in memory
- Plans department-scoped missions
- Dispatches to specialists; aggregates results
- Reports up to the Orchestrator

Lead agents are deliberately thin — most of the cognitive work happens in
specialists. Leads exist for planning, prioritization, and reporting.

### Tier 2 — Specialists

Below are the **anchor specialists** per department. Not exhaustive — the
catalog will grow during implementation. Each is a candidate to be its own
agent or a skill of a sibling, decided by the design rules above.

#### Product
- ProductDiscovery (interviews + tickets → opportunities)
- PRDWriter
- RoadmapPlanner
- UXResearcher
- DesignerUI
- DesignSystemMaintainer
- PMM (positioning, launch)

#### Engineering
- TechDesigner (TDD authoring)
- Coder-Frontend, Coder-Backend, Coder-Mobile, Coder-Data, Coder-ML
- Reviewer (code review)
- MigrationPlanner
- SREOps (alerts, runbooks, on-call)
- ReleaseManager
- IntegrationsEng (FHIR/HL7/X12)

#### Quality
- TestDesigner
- AutomationEng (unit/integration/e2e)
- ExploratoryTester
- PerfEng
- AccessibilityAuditor
- VnVEngineer (regulated V&V)

#### Security
- ThreatModeler
- VulnTriager
- IRCommander
- SecQuestionnaireResponder
- SecretsHygienist

#### Regulatory / Compliance / Privacy
- SaMDClassifier
- QMSAuthor
- DesignControlsTrace
- RiskMgmtISO14971
- PostMarketSurveillance
- HIPAACompliance
- GDPRCompliance (DPIA, DSAR, ROPA)
- AuditPrep

#### Clinical
- ClinicalEvidence
- ClinicalSafety
- MedicalWriter

#### Customer Experience
- SupportTriage
- SupportTier2 (diagnose with read-only prod tools)
- SupportTier3 (with eng handoff)
- KBEditor
- OnboardingCoach

#### Revenue
- ContentMarketer
- SEOAnalyst
- DemandGen
- SDR (sequencing within compliance)
- AE (discovery → proposal, HITL gates)
- SolutionsEngineer
- CSMHealth
- RenewalsManager

#### People / HR
- JDWriter
- Sourcer
- Screener
- InterviewScheduler
- OfferModeler
- OnboardingProvisioner
- PerfReviewFacilitator
- PolicyAuthor

#### Finance
- AROps, APOps
- ExpenseGuardian
- Closer (monthly close)
- RevRec
- FPAModeler
- TaxPrep

#### Legal
- ContractDrafter
- RedlineReviewer
- VendorRisk

#### Operations / IT
- IdentityLifecycle
- DeviceFleet
- LicenseSteward
- Procurement
- InternalToolsBuilder
- ITHelpdesk

## Agent specification template

Every agent lives in source with this contract:

```yaml
name: PRDWriter
owner_department: Product
mission_input_schema: <jsonschema>
mission_output_schema: <jsonschema>
tools:
  - memory.search
  - memory.write_artifact
  - interviews.read
  - tickets.read
prompt: prompts/prd_writer.md
model:
  primary: claude-opus-4-7
  fallback: claude-sonnet-4-6
guardrails:
  - phi_filter: strict
  - max_tokens_per_mission: 200000
  - max_tool_calls: 40
hitl:
  on_outputs: [final_prd]   # final PRD requires PM approval
evals:
  suite: evals/prd_writer/
  promotion_gate: 0.85
audit:
  retention_days: 3650
```

The orchestrator only knows agents through this contract — never their
implementation.
