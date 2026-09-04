# Operating Model — Departments, Roles, Tasks

A first-pass map of the functions inside a healthcare software company, and
which of them agents can carry.
Roles are listed for clarity; each role's tasks become one or more **agents**
(see `agent-catalog.md`).

Convention: tasks marked **[HITL]** require a human approval gate, **[PHI]**
may touch protected health information, **[REG]** is regulator-facing.

---

## 1. Executive / Strategy

Roles: CEO (human), Chief of Staff agent, Strategy Analyst agent, Board Liaison agent.

Tasks:
- Vision & narrative drafting; refresh quarterly
- Multi-year strategy synthesis from market, competitor, clinical evidence
- OKR cascade & weekly tracking
- Capital allocation modeling, runway scenarios
- Board pack assembly **[HITL]**
- M&A target scanning
- Crisis comms drafts **[HITL]**

## 2. Product

Roles: Group PM, PM, PMM, UX Researcher, Product Designer, Design Systems Engineer.

Tasks:
- Opportunity discovery from interviews, tickets, churn analysis
- Jobs-to-be-done synthesis
- PRD authoring & maintenance
- Roadmap & prioritization (RICE/ICE)
- Spec slicing into engineering-ready stories
- Usability studies (synthesis from recordings/transcripts)
- Wireframes → high-fidelity mocks → component specs
- Design system maintenance (tokens, components, accessibility)
- Pricing & packaging analysis
- Launch plan, positioning, messaging
- Win/loss interviews & synthesis
- Beta program management

## 3. Engineering

Roles: Frontend, Backend, Mobile (iOS/Android), Data Eng, ML Eng, Platform/DevEx,
SRE, Release Engineer, Solutions/Integrations Eng.

Tasks:
- Spec → technical design doc (with alternatives + chosen approach)
- Implementation (PRs) **[HITL on prod-impacting]**
- Code review (style, correctness, security, perf, accessibility)
- Migrations (schema, data) **[HITL]**
- Refactors with safety nets (tests, feature flags)
- ETL & warehouse modeling
- Feature store, training pipelines, model registry
- CI/CD pipelines, build/test caching
- Infra-as-code (Terraform/Pulumi), cost tagging
- Observability (logs, metrics, traces, SLOs)
- Incident response runbooks & on-call
- Release notes & change records **[REG]**
- Customer-specific integrations (FHIR, HL7v2, X12)

## 4. Quality

Roles: QA Lead, Test Automation Eng, Exploratory Tester, Perf Eng, Accessibility Auditor,
V&V Engineer.

Tasks:
- Test plan from PRD
- Unit/integration/E2E test generation & maintenance
- Exploratory testing scenarios from user journeys
- Perf budgets & load tests
- Accessibility audits (WCAG 2.2 AA)
- Verification & Validation per QMS **[REG]**
- Defect triage & regression analysis
- Release readiness scorecard **[HITL]**

## 5. Security

Roles: AppSec, Cloud Sec, IR Lead, Vuln Mgmt, Sec Architect.

Tasks:
- Threat modeling (STRIDE/LINDDUN for privacy)
- SAST/DAST/SCA pipeline tuning & triage
- Secrets scanning & rotation
- Cloud posture (CSPM), IAM least-privilege
- Pen-test scheduling, fixing, retesting
- Vulnerability mgmt SLAs
- Incident response: detect → contain → eradicate → recover **[HITL]**
- Security questionnaires for sales (RFP responses)
- Bug bounty triage

## 6. Regulatory / Compliance / Privacy

Roles: Regulatory Affairs Lead (human), QMS Specialist agent, Privacy Officer (human),
Privacy Analyst agent, Compliance Analyst agent.

Tasks:
- SaMD classification & risk class determination **[REG]**
- 510(k) / De Novo / PMA strategy drafting **[HITL][REG]**
- QMS (ISO 13485 / 21 CFR 820) authoring & change control
- Design controls (DHF, design inputs/outputs, traceability matrix)
- Risk management (ISO 14971) — hazard analysis, FMEA
- Post-market surveillance & MDR/MDV reports **[REG]**
- HIPAA: BAAs, risk analysis, breach assessment **[HITL][PHI]**
- GDPR: ROPA, DPIAs, DSARs **[HITL]**
- HITRUST / SOC 2 evidence collection & continuous monitoring
- Audit prep (internal + external) **[REG]**
- Policy library maintenance (versioned, signed)

## 7. Clinical

Roles: Chief Medical Officer (human, fractional ok), Clinical Evidence agent,
Clinical Safety agent, Medical Writer agent.

Tasks:
- Literature review & clinical evaluation reports
- Clinical study protocol drafting **[HITL]**
- Safety case maintenance, hazard log
- Adverse event review & coding (MedDRA) **[HITL][REG]**
- Clinical content review (patient-facing copy) **[HITL]**

## 8. Customer Experience / Support

Roles: Tier 1/2/3 Support agents, Onboarding Specialist, Training & Enablement,
Knowledge Base Editor.

Tasks:
- Triage incoming tickets, route or auto-resolve
- Diagnose with logs/traces (read-only prod access)
- Customer comms (acknowledgement, status, resolution)
- Onboarding workflows for new customers/users
- KB article authoring & freshness audits
- Training content (videos, docs) generation
- VoC synthesis → product feedback loop
- Status page updates during incidents **[HITL]**

## 9. Revenue (Marketing + Sales + CS)

Roles: Marketing (Content, SEO, Demand Gen, Brand), Sales (SDR, AE, SE),
Customer Success Manager, Renewals.

Tasks:
- ICP & persona maintenance
- Content calendar, blog/whitepaper/case-study drafting **[HITL on brand]**
- SEO research & on-page optimization
- Paid campaign setup & optimization **[HITL on spend]**
- Lead scoring & routing
- Outbound sequencing (compliant with CAN-SPAM / GDPR)
- Discovery → demo → proposal **[HITL on price/legal]**
- RFP/security-questionnaire response
- Contract redlines (within playbook) **[HITL]**
- Onboarding handoff, success plans
- Health scoring, churn risk alerts
- QBRs and renewal motions **[HITL on commit]**

## 10. People / HR

Roles: HRBP, Recruiter, People Ops, L&D, Comp & Benefits.

Tasks:
- Job description authoring
- Sourcing & screening (resume → structured fit score)
- Scheduling & interviewer kits
- Offer modeling & comp benchmarking **[HITL]**
- Onboarding workflows (accounts, equipment, training)
- Performance review cycle facilitation
- 1:1 cadence prompts, sentiment synthesis
- Payroll runs **[HITL]**
- Policy authoring & employee handbook updates
- Offboarding & access revocation

## 11. Finance

Roles: Controller, FP&A, AR, AP, Tax, Treasury.

Tasks:
- Daily cash & treasury monitoring
- AR: invoicing, dunning, application of payments
- AP: vendor onboarding, 3-way match, payment runs **[HITL]**
- Expense policy enforcement
- Monthly close (accruals, reconciliations, journal entries)
- Revenue recognition (ASC 606) for SaaS
- FP&A: budget vs. actuals, forecasts, scenario models
- Tax provisioning & filings **[HITL]**
- Audit support
- Board financial pack **[HITL]**

## 12. Legal

Roles: General Counsel (human, fractional), Contract Mgmt agent, Privacy Counsel agent.

Tasks:
- Standard contract drafting (MSA, DPA, BAA, NDA) from templates
- Redline review against playbook **[HITL on out-of-bounds]**
- Vendor risk assessments
- IP filings tracking
- Litigation/discovery support **[HITL]**
- Regulatory inquiry handling **[HITL][REG]**

## 13. Operations / IT / Internal

Roles: BizOps, IT/Helpdesk, Identity & Access, Procurement, Vendor Mgmt.

Tasks:
- Identity lifecycle (joiner/mover/leaver) via SCIM
- Endpoint posture & device management
- SaaS license inventory & rationalization
- Procurement requests, PO workflow
- Vendor due diligence (security, privacy, financial)
- Internal tooling (data apps, automations)
- Internal helpdesk
- Office/remote operations (if applicable)

---

## Cross-cutting capabilities (shared by all departments)

- **Document generation** — templated artifacts with traceable inputs
- **Search & retrieval** — corporate memory and policy retrieval
- **Calendar & scheduling**
- **Comms** — Slack/email/SMS with policy filtering
- **Reporting** — recurring dashboards, anomaly detection
- **Workflow automation** — long-running, durable, resumable

These become **platform agents/services** consumed by department agents
rather than being re-implemented per department.
