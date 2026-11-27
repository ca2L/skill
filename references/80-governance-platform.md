# 80 · Governance, platform, and rollout

A standard that lives only in a document fails. Governance makes the right behavior the default; the platform makes it cheap.

## 1. Operating model

| Layer | Responsibility |
|---|---|
| **Central experimentation team** | Standards, platform, methods, training, audit, meta-analysis |
| **Federated data scientists** | Design, analysis, DQ, decision support in business units |
| **Business DRI** | Decision, value, guardrail trade-off, rollout ownership |
| **Product/engineering** | Treatment implementation, flags, instrumentation, rollback |
| **Data engineering** | Assignment/exposure pipelines, lineage, freshness, reconciliation |
| **Guardrail owners** | Thresholds, monitoring, veto, remediation |
| **Legal/finance/security** | Pricing, credit, privacy, contract, competition review |
| **Leadership** | Portfolio priorities, resourcing, decision escalation |

Rule: one accountable DRI per experiment, one guardrail owner per guardrail, one platform owner for the system. Committees can advise; they cannot be accountable.

## 2. Stage-Gate G0–G7

| Gate | Question | Required artifacts | Exit criteria | Owner |
|---|---|---|---|---|
| **G0 Intake** | Is this worth experimenting? | Decision memo, baseline, affected population, alternatives, cost of inaction | Decision and owner named; baseline sourced | Business DRI |
| **G1 Design** | Is the design causal and decision-ready? | Design one-pager, 61-field draft, hypothesis, unit/interference, power, metric tree, pre-registration | Design checklist pass; guardrail owners named; legal/finance flagged | Experiment owner + DS |
| **G2 Launch** | Can we run it safely? | Tracking QA, assignment dry run, SRM simulation, flag/rollback, exposure schema, DQ plan | Dry run clean; rollback tested; monitoring live | Eng + DS |
| **G3 In-flight** | Is the experiment healthy? | SRM/exposure/guardrail health; no primary readout | No S1; guardrails within bounds | DS + guardrail owner |
| **G4 Readout** | Is the data valid and the analysis correct? | Data lock, DQ scorecard, analysis plan execution, sensitivity | DQ pass/conditional; analysis reproducible | DS + analyst |
| **G5 Decision** | What do we do? | Readout, decision matrix, decision record, dissent | Decision, owner, conditions recorded | Business DRI |
| **G6 Rollout** | Can we scale safely? | Ramp plan, monitoring, holdout, rollback trigger, comms | Ramp gates pass; holdout live | Business DRI + Eng |
| **G7 Archive** | Did we learn? | Doc, SQL, dashboard, KB card, reusable lesson, postmortem | Links resolve; lesson has boundary | Experiment owner |

Gate rules:
- No G1 without a decision and a pre-registered primary.
- No G2 without a tested rollback and a tracking QA.
- No G3/G4 primary readout before data lock.
- No G5 scale decision without guardrail sign-off and DQ status.
- No G7 closure without an archive bundle.

## 3. RACI

`R` responsible, `A` accountable, `C` consulted, `I` informed.

| Activity | Business DRI | Exp owner | DS | Analyst | Eng | Guardrail owner | Platform | Legal/Finance |
|---|---|---|---|---|---|---|---|---|
| Frame decision | A/R | C | C | I | I | C | I | I |
| Hypothesis/design | C | A/R | R | C | C | C | I | I |
| Power/sample | I | A | R | C | I | I | I | I |
| Instrumentation | I | A | C | C | R | I | C | I |
| Pre-registration | C | A/R | R | C | I | C | C | I |
| Launch/rollback | I | A | C | I | R | C | C | I |
| In-flight health | I | A | R | C | C | C | C | I |
| Readout | C | A | R | R | I | C | I | I |
| Decision | A/R | C | C | C | I | C | I | C |
| Rollout | A/R | C | C | C | R | C | I | C |
| Archive | I | A/R | C | R | C | I | C | I |

## 4. Pre-registration and amendments

### Pre-registration package

- design one-pager
- 61-field record (draft complete)
- primary/secondary/guardrail definitions with SQL hashes
- power appendix
- analysis plan (estimand, estimator, covariates, subgroups, multiplicity)
- decision rules
- plan hash (SHA-256 of the frozen package)

### Amendment rules

| Timing | Allowed? | Effect |
|---|---|---|
| Before exposure | Yes, versioned | Confirmatory if re-frozen before launch |
| After exposure, before outcome | Only for DQ/implementation defects | Document; may downgrade if metric/population changes |
| After outcome seen | No for confirmatory claims | Exploratory only; new experiment required |

Amendment log fields: date, change, reason, before/after exposure, approver, impact on confirmatory status.

## 5. Platform data model

### Core tables

```sql
-- One row per experiment; 61 fields can live in typed columns + JSONB for objects
CREATE TABLE exp_experiment (
  exp_id            TEXT PRIMARY KEY,
  name              TEXT NOT NULL,
  owner_id          TEXT NOT NULL,
  status            TEXT NOT NULL,
  start_at          TIMESTAMPTZ,
  end_at            TIMESTAMPTZ,
  unit_type         TEXT NOT NULL,
  layer             TEXT,
  plan_hash         TEXT,
  metadata          JSONB NOT NULL,
  created_at        TIMESTAMPTZ DEFAULT now(),
  updated_at        TIMESTAMPTZ DEFAULT now()
);

-- Immutable assignment; one row per unit per experiment
CREATE TABLE exp_assignment (
  exp_id            TEXT NOT NULL,
  unit_id           TEXT NOT NULL,
  unit_type         TEXT NOT NULL,
  variant           TEXT NOT NULL,
  bucket            INTEGER NOT NULL,
  salt              TEXT NOT NULL,
  assigned_at       TIMESTAMPTZ NOT NULL,
  strata            JSONB,
  PRIMARY KEY (exp_id, unit_id)
);

-- Append-only exposure; dedupe at query time by first exposure
CREATE TABLE exp_exposure (
  exp_id            TEXT NOT NULL,
  unit_id           TEXT NOT NULL,
  variant           TEXT NOT NULL,
  exposure_ts       TIMESTAMPTZ NOT NULL,
  surface           TEXT,
  source            TEXT,
  is_bot            BOOLEAN DEFAULT false,
  payload           JSONB
);

-- Metric registry: one definition per metric version
CREATE TABLE exp_metric (
  metric_id         TEXT NOT NULL,
  version           TEXT NOT NULL,
  name              TEXT NOT NULL,
  definition        TEXT NOT NULL,
  sql_hash          TEXT NOT NULL,
  owner_id          TEXT NOT NULL,
  direction         TEXT NOT NULL,
  created_at        TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (metric_id, version)
);

-- Analysis snapshots are immutable; re-running creates a new version
CREATE TABLE exp_analysis (
  analysis_id       TEXT PRIMARY KEY,
  exp_id            TEXT NOT NULL,
  data_lock_at      TIMESTAMPTZ NOT NULL,
  dq_status         TEXT NOT NULL,
  estimator         TEXT NOT NULL,
  result            JSONB NOT NULL,
  code_hash         TEXT NOT NULL,
  created_at        TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE exp_decision (
  exp_id            TEXT PRIMARY KEY,
  decision          TEXT NOT NULL,
  rationale         TEXT NOT NULL,
  owner_id          TEXT NOT NULL,
  decided_at        TIMESTAMPTZ NOT NULL,
  conditions        JSONB,
  dissent           TEXT
);

CREATE TABLE exp_audit (
  event_id          BIGSERIAL PRIMARY KEY,
  exp_id            TEXT NOT NULL,
  actor_id          TEXT NOT NULL,
  action            TEXT NOT NULL,
  before            JSONB,
  after             JSONB,
  created_at        TIMESTAMPTZ DEFAULT now()
);
```

### Design principles

- **One ID everywhere**: assignment, exposure, metric SQL, dashboard, decision, archive.
- **Assignment is immutable**; never rewrite buckets. A restart gets a new experiment ID.
- **Exposure is append-only**; dedupe in the analysis layer by first exposure.
- **Metric definitions are versioned**; a SQL change is a new version, not an edit.
- **Analysis snapshots are immutable**; preserve code hash and data lock.
- **No PII** in experiment tables; use pseudonymous IDs and a restricted mapping table.
- **Audit everything**: state transitions, plan changes, decision edits, access to sensitive cuts.

### APIs

| API | Purpose |
|---|---|
| `POST /experiments` | Create draft with 61-field metadata |
| `POST /experiments/{id}/freeze` | Freeze plan; returns plan hash |
| `GET /assign?exp_id=&unit_id=` | Deterministic assignment; idempotent |
| `POST /exposure` | Log exposure event; validate schema |
| `GET /experiments/{id}/health` | SRM, exposure, guardrail status |
| `POST /experiments/{id}/analyze` | Run pre-registered analysis; snapshot |
| `POST /experiments/{id}/decision` | Record decision with required fields |
| `GET /experiments/{id}/archive` | Archive bundle and links |

## 6. Automated gates

| Gate | Automation |
|---|---|
| G1 | Schema validation; 61 fields complete; exactly one primary; MDE present; guardrail owner present; plan hash |
| G2 | Assignment dry run; SRM simulation; event volume; flag/rollback check; exposure schema |
| G3 | SRM/exposure/guardrail alerts; no primary metric in the alerting job |
| G4 | DQ scorecard; SQL hash match; reconciliation; missingness; cluster count |
| G5 | Decision record required fields; guardrail sign-off; dissent field |
| G7 | Link resolution; archive completeness; lesson boundary present |

Automation should block the state transition, not send a reminder email.

## 7. Risk tiers and review

| Tier | Examples | Review |
|---|---|---|
| **R0** | Copy, internal tool, no buyer/seller impact | Owner + DS self-check |
| **R1** | Standard UI/UX, search ranking, onboarding | G1 design review |
| **R2** | Pricing, discount, credit terms, seller policy, privacy-adjacent | G1 + legal/finance + guardrail owner |
| **R3** | Irreversible, regulated, safety, cross-border data, public policy | Exec + legal + ethics review; consider not randomizing |

R2/R3 require a documented risk assessment and a rollback plan tested before launch.

## 8. Compliance and ethics

- **Purpose limitation**: use experiment data only for the registered question; secondary use requires review.
- **Data minimization**: collect only fields needed for assignment, exposure, outcomes, and guardrails.
- **Retention**: define retention for raw exposure/outcome data; aggregate before long-term storage.
- **Access**: role-based; sensitive cuts (price, margin, seller performance) restricted and audited.
- **Fairness**: do not target protected attributes; check disparate impact where relevant.
- **Price/competition**: no hidden discriminatory pricing; legal review for tiered/geo pricing; avoid resale/arbitrage.
- **Consent/contract**: ensure experiment use is covered by terms; check seller/buyer obligations.
- **Explainability**: be able to explain the change and the decision to a customer/regulator.
- **Do not randomize**: legally mandated service, safety-critical fulfillment, irreversible contract terms, vulnerable populations.

## 9. Program metrics

| Metric | Definition | Target (starting) |
|---|---|---|
| Pre-registration rate | Experiments with frozen plan before exposure / launched | ≥90% |
| DQ pass rate | G4 pass or conditional / readouts | ≥85% |
| Time to decision | Data lock → decision record | median ≤10 business days |
| Archive completeness | G7 bundles complete / closed experiments | ≥95% |
| Reuse rate | Lessons referenced by later experiments / archived | ≥30% |
| Guardrail incidents | Breaches per 100 experiments | downward trend |
| Decision durability | Decisions unchanged at 90 days / decisions | ≥80% |
| Portfolio win rate | Confirmed positive / completed | context, not a target |

Do not incentive “win rate” alone; it encourages safe, low-value experiments and hides null results.

## 10. 30/60/90 rollout

### Days 0–30: foundation

- Pick 2 pilot business units and 5 experiments.
- Adopt the 61-field record and one-page design.
- Run G0/G1 reviews; baseline the current cycle time and DQ issues.
- Publish templates, glossary, and two worked examples.
- Name guardrail owners for the pilot domains.

### Days 31–60: platform MVP

- Ship assignment/exposure APIs and the metric registry.
- Automate G1 schema checks and G4 DQ scorecard.
- Run 10–15 experiments through the gates; measure cycle time.
- Start a weekly experiment review (30 min, decisions only).
- Create the archive bundle and knowledge card format.

### Days 61–90: scale

- Enforce gates in the platform (state transitions).
- Add holdout/long-term tracking for 2–3 launches.
- Train business DRIs and guardrail owners separately.
- Publish the first meta-analysis (3–5 experiments, one domain).
- Review portfolio: value, learning, guardrail incidents, cycle time.

### Resistance playbook

| objection | response |
|---|---|
| “This slows us down.” | Measure cycle time before/after; automate G1/G4; most delay is rework from bad design |
| “Our sample is too small.” | Compute MDE; use CUPED/stratification/longer window; consider quasi-experiment |
| “Sales won’t follow the assignment.” | Randomize by rep/territory; log CRM actions; measure compliance |
| “We already know it works.” | Ask for the decision and the evidence; run a holdout or a smaller confirmatory test |
| “Every experiment is different.” | The 61 fields are the minimum; extension fields are allowed, omission is not |
| “Guardrails block innovation.” | Guardrails define the safe operating space; they make speed sustainable |

## 11. Maturity model

| Level | Characteristics |
|---|---|
| **L1 Ad hoc** | Experiments exist; no standard; results debated; no archive |
| **L2 Standardized** | 61 fields, templates, pre-registration, DQ checks; manual gates |
| **L3 Gated platform** | Automated assignment/exposure/registry; gates enforced; decision records |
| **L4 Portfolio** | Meta-analysis, holdouts, guardrail governance, prioritization by value/learning |
| **L5 Causal platform** | Always-on experimentation, heterogenous effects, sequential/adaptive designs, causal ML |

Do not jump to L5 tooling before L2 discipline. A platform cannot fix a culture that rewards significant results over decisions.

## 12. Common governance failures

- **Gate theater**: reviews happen, but no one can say no; gates become signatures.
- **Too many approvers**: cycle time balloons; owners disengage.
- **No guardrail authority**: guardrails are advisory; harm ships.
- **Platform without adoption**: teams route around it; shadow spreadsheets.
- **Metric gaming**: win-rate targets produce safe, trivial experiments.
- **Archive neglect**: the same experiment is rerun under a new name.
- **Central team bottleneck**: all reviews centralized; business units wait.
- **No escalation path**: disagreements stall; decisions default to HiPPO.
