---
name: b2b-experiment-standard
description: Use when designing, reviewing, auditing, or institutionalizing experiments on a B2B e-commerce platform (enterprise/account buyers, RFQ/quote, sellers, pricing, fulfillment). Produces experiment specs, 61-field metadata, pre-registration and analysis plans, data-quality gates, readout/decision records, and reusable templates; covers account-level/cluster/switchback/geo designs, SRM/contamination checks, CUPED/cluster-robust statistics, guardrails, heterogeneity, and long-term holdout. 中文触发词（B2B电商实验规范、实验设计、实验审计、读数、指标口径、SRM、异质性、长期效应、实验治理、61字段）
---

# B2B Experiment Standard

A decision-first operating system for B2B experiments: design the evidence, prove the data, estimate the effect, make a reversible decision, and leave a reusable asset.

## Use this skill when

- Designing an A/B, cluster, switchback, geo, or holdout experiment on a B2B platform.
- Reviewing an experiment design, readout, or rollout decision.
- Auditing SRM, exposure, balance, contamination, duplicate accounts, or metric lineage.
- Writing an experiment standard, field dictionary, pre-registration template, or decision record.
- Building an experiment platform schema, gates, RACI, or 30/60/90-day rollout plan.
- The business lever touches RFQ/quote, enterprise accounts, sellers, pricing, credit terms, fulfillment, or sales territories.

## Do not use this skill when

- The task is a pure B2C growth experiment with no account/seller/contract layer (use a general A/B testing skill).
- The question is only “run this SQL” or “make this chart” with no causal/decision component.
- The user wants a legal opinion on pricing or data processing; this skill flags the need for legal/finance review, it does not replace it.

## Operating principles

1. **Decision first.** If you cannot name the decision and the action for each result, do not run the experiment.
2. **Unit alignment.** Randomize at the level where the intervention acts and interference travels; default to company/account, not user.
3. **Pre-register.** Freeze the estimand, primary metric, window, population, test, subgroups, and decision thresholds before exposure.
4. **Evidence before outcome.** SRM, exposure, balance, contamination, duplicates, and lineage are gates, not appendix material.
5. **Estimate, don’t worship p.** Report relative and absolute lift, 95% CI, MDE, sample, and business value.
6. **Protect the ecosystem.** Guardrails have owners and veto power; a positive primary metric cannot buy a harmed buyer or seller experience.
7. **Think in windows.** B2B effects often arrive late; use 7/14/30-day cumulative views and 60/90-day or post-rollout holdout for durability.
8. **Make it reusable.** Every experiment ends with a document, SQL, dashboard, knowledge card, and a reusable lesson.

## Three modes

### Mode A — Design a new experiment

1. **Frame the decision** (G0): problem, baseline, affected population, expected value, cost of being wrong, alternatives.
2. **Write a falsifiable hypothesis** with mechanism, MDE, window, and refutation/guardrail threshold.
3. **Choose the unit** using the decision tree in `references/10-design.md`; check interference before sample size.
4. **Size the test**: baseline, variance/ICC, allocation, CUPED, attrition, cluster DEFF.
5. **Define the metric tree**: one primary, 2–4 secondary, 3–6 guardrails, counter-metric, exact SQL/口径.
6. **Pre-register** the analysis and decision rules; run the G1 review.
7. **Produce** a one-page design + 61-field metadata + power appendix; use `references/50-templates.md`.

### Mode B — Audit or review an existing experiment

1. Reconstruct the design from the 61-field record; flag missing fields.
2. Run the data-quality scorecard in `references/20-data-quality.md`; any S1 blocks readout.
3. Recompute the effect with the correct estimator (ITT, cluster-robust, delta, CUPED).
4. Check guardrails, pre-registered subgroups, multiple testing, and long-term windows.
5. Decide whether the evidence supports scale / target / iterate / stop / retest using `references/40-decision-longterm.md`.
6. Produce a gate table, corrected estimates, blockers, and a decision recommendation.

### Mode C — Build or institutionalize the standard

1. Start from `references/60-field-dictionary.md`; adapt names/owners, do not drop fields silently.
2. Add gates, RACI, pre-registration, and archive rules from `references/80-governance-platform.md`.
3. Add templates and SQL from `references/50-templates.md`.
4. Pilot on two experiments; measure pre-registration rate, DQ pass rate, time-to-decision, archive rate.
5. Roll out in 30/60/90-day waves; train owners and guardrail owners separately.

## Fast triage

| Request | Read first | Then |
|---|---|---|
| “Design an experiment for quote SLA / pricing / seller tool” | `references/00-triage.md` | `10-design.md`, `50-templates.md` |
| “How many samples / what MDE / is this powered?” | `references/10-design.md` § power | `30-metrics-statistics.md` § power |
| “SRM failed / exposure looks wrong / users duplicated” | `references/20-data-quality.md` | `30-metrics-statistics.md` § estimators |
| “Which metric / guardrail / SQL口径?” | `references/30-metrics-statistics.md` | `50-templates.md` § SQL |
| “How do we read this result / should we ship?” | `references/30-metrics-statistics.md` | `40-decision-longterm.md` |
| “Is the effect different by new/old, value, channel, category?” | `references/40-decision-longterm.md` § heterogeneity | `30-metrics-statistics.md` § multiple testing |
| “What about 7/14/30 days, decay, full rollout?” | `references/40-decision-longterm.md` § long-term | `20-data-quality.md` § holdout |
| “Write the experiment standard / field dictionary” | `references/60-field-dictionary.md` | `80-governance-platform.md`, `50-templates.md` |
| “Review this experiment / find the flaw” | `references/70-anti-patterns.md` | `00-triage.md`, `20-data-quality.md` |
| “Build the platform schema / gates / RACI” | `references/80-governance-platform.md` | `60-field-dictionary.md` |

## Non-negotiables

- **MUST** align the randomization unit with the intervention and interference level. Default: company/account. Use seller, geo, or switchback when supply or shared inventory creates spillover.
- **MUST** freeze the primary metric, window, population, estimator, subgroups, and decision thresholds before first exposure; record a plan hash.
- **MUST** pass SRM before reading the primary metric. Treat p < 0.001 as a blocking S1; do not “fix” it by reweighting without a pre-registered amendment.
- **MUST** analyze ITT as the primary population. Exposed/TOT/per-protocol are secondary and must be labeled.
- **MUST** use cluster-robust standard errors when randomization is at account/seller/geo level but outcomes are at order/user level.
- **MUST** use the delta method or bootstrap for ratio metrics (GMV/order, Q2O, quote acceptance); do not run a naive t-test on a ratio.
- **MUST** report absolute lift, relative lift, 95% CI, MDE, sample, and business value together. “p < 0.05” alone is not a finding.
- **MUST** give every guardrail an owner, threshold, and circuit-breaker action; guardrail owner has veto over scale.
- **MUST NOT** change the primary metric, denominator, window, or subgroup after seeing results. Any change is an amendment and is downgraded to exploratory if post-outcome.
- **MUST NOT** call a non-significant result “no effect” without checking CI upper bound, MDE, and achieved sample.
- **MUST NOT** peek continuously and stop on the first significant p-value. If monitoring is required, use a pre-registered sequential design.
- **MUST NOT** scale without a ramp plan, monitoring, rollback, and a long-term holdout/measurement plan.

## B2B defaults

| Lever | Default unit | Primary candidate | Guardrails |
|---|---|---|---|
| Search / recommendation / workbench UI | Company/account | Q2O conversion, quote acceptance, net GMV | Cancel, dispute, seller quote rate |
| Pricing / tiered discount / credit terms | Company/contract account | Net GMV, order size, conversion | Gross margin, price consistency, resale/arbitrage |
| Seller tool / fulfillment rule | Seller ID or seller cluster | On-time fulfillment, seller retention | Buyer dispute, net GMV, fulfillment cost |
| Inventory / supply allocation | Market/geo or switchback | Availability, fill rate | Price dispersion, seller/buyer fairness |
| Sales incentive / territory policy | Sales rep/team/territory | Win rate, activation | Cross-territory contamination, customer fairness |
| New buyer onboarding | Company | First order, time-to-first-order | Support burden, cancel/refund |

**Metric defaults:** 30 days is the primary window; report 7/14/30 cumulative; use 60/90 days or post-rollout holdout for repeat purchase, retention, seller behavior, and decay. Prefer Q2O, quote latency, quote acceptance, net GMV, buyer retention, seller retention, on-time fulfillment, dispute rate, and gross margin over vanity clicks.

## Output contracts

| Deliverable | Must contain |
|---|---|
| Experiment design | Decision, hypothesis, unit/interference, split, exposure, power, metric tree, guardrails, pre-registration, decision rules, rollback |
| 61-field metadata | All fields or explicit `N/A + reason`; field-level method/source/owner/evidence |
| DQ audit | Dimension scores, S1/S2/S3 findings, blocking decision, corrected sample |
| Readout | Data lock, SRM/DQ, primary + CI + p, guardrails, subgroups, long-term, sensitivity, limits |
| Decision record | Evidence, options, decision, rationale, dissent, owner, ramp/holdout, follow-up date |
| Standard / platform | Modules, fields, gates, RACI, data model, templates, rollout plan |

## Quality bar before you deliver

- [ ] 61 fields accounted for, or an explicit N/A with reason.
- [ ] Primary is singular and tied to the hypothesis; guardrails have owners/thresholds.
- [ ] Unit, exposure, analysis population, and estimator are mutually consistent.
- [ ] Power calculation is reproducible; cluster DEFF/CUPED/attrition are stated.
- [ ] SRM, balance, exposure, contamination, duplicate, and lineage checks are present.
- [ ] Effect is reported as absolute + relative + CI + MDE + business value.
- [ ] Multiple testing, subgroups, and long-term windows are pre-registered or labeled exploratory.
- [ ] Decision is one of scale / target / iterate / stop / retest, with a ramp/holdout plan.
- [ ] SQL, dashboard, document, and knowledge card links exist.

## Read next

| File | Purpose |
|---|---|
| `references/00-triage.md` | One-page checklist, decision tree, and the smallest viable experiment spec |
| `references/10-design.md` | Hypothesis, unit selection, exposure, split, period, mutual exclusion, power, special designs |
| `references/20-data-quality.md` | SRM, balance, exposure completeness, contamination, duplicates, lineage, scorecard |
| `references/30-metrics-statistics.md` | Metric tree/spec/SQL, estimators, CUPED, delta, multiple testing, power, sequential/Bayesian |
| `references/40-decision-longterm.md` | Heterogeneity, 7/14/30, decay, side effects, holdout, decision matrix |
| `references/50-templates.md` | Design one-pager, readout, decision record, experiment card, SQL skeletons |
| `references/60-field-dictionary.md` | 61 fields with type, required/N/A, definition, validation, owner |
| `references/70-anti-patterns.md` | 20 failure modes and three B2B cases |
| `references/80-governance-platform.md` | Stage-Gate, RACI, platform tables, compliance, 30/60/90 rollout |
| `assets/B2B电商平台实验规范.md` | Full reference standard (long-form, all sections) |
| `assets/实验字段字典.csv` | Machine-readable 61-field dictionary |

## Stop conditions

Stop and recommend a quasi-experiment, switchback, or a documented judgment call when:

- There is no stable unit or no measurable exposure.
- The population is too small for a credible MDE and no sensitivity lever exists.
- Interference cannot be contained by clustering, geo, or time switching.
- The intervention is irreversible, illegal, or ethically unacceptable to randomize.
- The metric cannot be observed within the decision horizon and no proxy is valid.
- The business cannot name a decision that would change based on the result.
