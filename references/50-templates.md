# 50 · Templates

Copy, fill, and delete what does not apply. A template is a starting point, not evidence.

## 1. Design one-pager

```markdown
# EXP-{BU}-{YYYYMMDD}-{NNN} — {Name}

**Owner:** {name}  **Backup:** {name}  **Status:** draft / review / approved
**Decision:** {what changes if positive / negative / flat}
**Deadline:** {date}

## Problem and evidence
- Current baseline: {metric} = {value}, source {table/dashboard}
- Pain: {who, how often, cost}
- Why now: {trigger}

## Hypothesis
Because {mechanism}, {lever} for {population} will move {primary} by ≥ {MDE}
within {window}, while {guardrail} stays within {threshold}.
We would be wrong if {refutation}.

## Design
- Unit: {company/seller/geo/time block}; why: {interference}
- Split: {50/50}; ramp: {5% → 25% → 50%}
- Treatment: {one change, version/config}
- Control: {current production, version}
- Exposure: {event, dedupe, window}
- Period: {start} to {end}; business cycle: {week/month}
- Mutual exclusion: {layer, checks}

## Metrics
- Primary: {name, formula, window, denominator}
- Secondary: {2–4}
- Guardrails: {3–6, owner, threshold}
- Counter-metric: {1–2}

## Power
- Baseline: {p or mean/σ}; ICC: {value}; cluster size: {m}
- MDE: {absolute/relative}; α: 0.05; power: 0.80
- Required n/arm: {n}; available: {n}; attrition: {x%}
- CUPED: {yes/no, expected ρ}

## Analysis
- ITT; estimator: {diff/regression/cluster-robust/delta}
- Covariates: {pre-period only}
- Subgroups: {3–5, pre-registered}
- Multiplicity: {BH/Holm/none}
- Missing/outlier rules: {pre-registered}

## Decision rules
- Scale if: CI lower > {MBE}, guardrails pass, no S1
- Target if: credible interaction in {segment}
- Iterate if: {condition}
- Stop if: {harm/confident null}
- Retest if: {inconclusive reason}

## Ops
- Guardrail owner: {name}; circuit breaker: {trigger/action}
- Rollback: {path, owner}
- Holdout: {5–10%, duration}
- Comms: {sales/support/seller}

## Risks
- {risk} → {mitigation}
```

## 2. Pre-registration record

```yaml
experiment_id: EXP-SEARCH-20261118-01
title: Promised delivery date on quote page
owner: zhang.li
status: preregistered
preregistered_at: 2026-11-18T10:00:00+08:00
plan_hash: sha256:...

population:
  include: [active_buyer, quote_requested]
  exclude: [test_account, internal_account, sanctioned_region]
  unit: company_id

design:
  type: cluster_randomized
  arms: [control, treatment]
  split: [0.5, 0.5]
  strata: [buyer_segment, baseline_gmv_band, region]
  salt: exp_search_20261118_01
  ramp: [0.05, 0.25, 0.50, 1.0]
  start: 2026-11-20
  end: 2026-12-20

hypothesis:
  mechanism: lead-time uncertainty causes quote abandonment
  mde_relative: 0.08
  window_days: 30
  refutation: Q2O flat and quote latency up

metrics:
  primary:
    id: D02
    name: quote_to_order
    formula: orders / quote_requests
    window_days: 30
    sql_hash: sha256:...
  secondary: [quote_acceptance, quote_latency_p50, net_gmv]
  guardrails:
    - id: D04
      name: quote_cancellation_rate
      max_increase_pp: 2.0
      owner: ops.quote
  counter: [discount_depth]

analysis:
  estimand: ITT
  estimator: cluster_robust_ols
  cluster: company_id
  covariates: [pre_gmv_30d, pre_orders_30d, buyer_segment]
  cuped: true
  subgroups: [new_vs_existing, high_vs_low_value, channel]
  multiplicity: benjamini_hochberg
  alpha: 0.05
  power: 0.80

decision:
  scale_if: ci_lower_relative > 0.08 and guardrails_pass
  target_if: interaction_p_adj < 0.05 in preregistered_segment
  stop_if: guardrail_breach or ci_upper_relative < 0.0
  retest_if: ci_width > 0.15

ops:
  guardrail_owner: wang.wu
  rollback: feature_flag off, owner: eng-oncall
  holdout: 0.05 for 60 days
```

## 3. 61-field metadata example

```yaml
experiment:
  id: EXP-SEARCH-20261118-01
  name: Promised delivery date on quote page
  owner: zhang.li
  start: 2026-11-20
  end: 2026-12-20
  status: running
  background: |
    Quote abandonment is 38%; interviews cite lead-time uncertainty.
  business_goal: |
    Raise Q2O by 8% relative without increasing cancellations.

design:
  hypothesis: |
    Showing a promised delivery date reduces uncertainty and raises Q2O.
  treatment: |
    Quote page shows P50/P90 promised delivery date; control shows none.
  control: current quote page v3.2
  randomization_unit: company_id
  exposure: |
    quote_page_view with experiment_id and variant; first exposure per company.
  ratio: 50/50
  period_days: 30
  mutual_exclusion: layer=quote_ux; no overlapping quote experiments

data_quality:
  sample_size: 12400 companies (6200/arm)
  srm_p: 0.42
  pre_balance_max_smd: 0.031
  exposure_complete: 0.982
  contamination: 0.011
  duplicate_users: 0.004
  lineage_complete: true

metrics:
  north_star: net_gmv
  primary: quote_to_order
  secondary: [quote_acceptance, quote_latency_p50, net_gmv]
  guardrail: [quote_cancellation_rate, dispute_rate]
  definition: |
    Q2O = orders attributed to quotes / quote requests, 30-day window.
  sql: sql/q2o_v3.sql
  preset: true

statistics:
  effect: 0.094
  relative_lift: 0.112
  absolute_lift: 0.0094
  ci: [0.021, 0.167]
  p_value: 0.008
  multiple_testing: BH
  power: 0.81

heterogeneity:
  new_vs_existing: {effect_new: 0.15, effect_existing: 0.07, interaction_p: 0.21}
  high_vs_low_value: {effect_high: 0.12, effect_low: 0.09, interaction_p: 0.55}
  frequency: {effect_high: 0.10, effect_low: 0.11, interaction_p: 0.72}
  channel: {web: 0.12, app: 0.08, api: 0.05}
  category: {industrial: 0.13, consumables: 0.07}
  seller: {top: 0.10, long_tail: 0.09}
  other: {region: {east: 0.11, west: 0.09}}

long_term:
  d7: 0.12
  d14: 0.11
  d30: 0.094
  post_rollout: pending
  decay: false
  side_effects: none detected

decision:
  experiment_conclusion: positive
  business_conclusion: ship with holdout
  scale: true
  stop: false
  target: false
  retest: false

archive:
  document: wiki/exp/EXP-SEARCH-20261118-01
  sql: sql/q2o_v3.sql
  dashboard: dash/quote-q2o
  knowledge_base: kb/quote-lead-time
  reusable_lesson: lead-time transparency lifts Q2O, strongest for new buyers
```

## 4. Analysis plan

```markdown
# Analysis plan — EXP-{ID}

## Data lock
- Lock at: {timestamp}; partitions: {list}
- DQ gate: pass / conditional / blocked
- Analysis population: {definition}

## Primary
- Estimand: ITT
- Model: {Y ~ T + covariates; cluster SE at company}
- Effect: absolute and relative, 95% CI
- Test: two-sided, α=0.05
- CUPED: {yes/no; pre-period covariate}

## Secondary
- {metric}: {model}; multiplicity {method}

## Guardrails
- {metric}: non-inferiority bound {value}; owner {name}

## Subgroups
- {list}; interaction test; adjusted p

## Sensitivity
- unadjusted vs adjusted
- winsorized vs raw
- exposed vs assigned
- alternative window

## Long-term
- 7/14/30/60/90; holdout {x%} for {days}
```

## 5. Readout report

```markdown
# Readout — EXP-{ID}

**Status:** complete / interim  **Data lock:** {date}  **Owner:** {name}

## 1. Decision summary
- Recommendation: scale / target / iterate / stop / retest
- Why: {2–3 sentences}
- Guardrail status: pass / breach

## 2. Design recap
- Unit, split, period, exposure, population
- Any amendments: {list}

## 3. Data quality
| Check | Result | Status |
|---|---|---|
| SRM | p= | |
| Balance | max SMD= | |
| Exposure | % | |
| Contamination | % | |
| Duplicates | % | |
| Lineage | pass/fail | |

## 4. Primary result
| Metric | Control | Treatment | Abs | Rel | 95% CI | p | MDE |
|---|---:|---:|---:|---:|---|---:|---:|

## 5. Secondary and guardrails
| Metric | Rel lift | CI | p | Threshold | Status |
|---|---:|---|---:|---|---|

## 6. Heterogeneity
| Subgroup | Rel lift | CI | Interaction p | Pre-registered |
|---|---:|---|---:|---|

## 7. Long-term
- 7/14/30/60/90 trajectory
- Holdout/DID/ITS results
- Decay/side effects

## 8. Sensitivity
- Adjusted vs unadjusted
- Winsorized vs raw
- Exposed vs ITT

## 9. Limitations
- {power, contamination, novelty, external validity}

## 10. Recommendation and next steps
- Decision, owner, ramp, holdout, follow-up
```

## 6. Decision record

```markdown
# Decision record — EXP-{ID}

- Date:
- Attendees:
- Evidence: {primary, CI, p, MDE, guardrails, DQ}
- Options:
  1. Scale
  2. Target
  3. Iterate
  4. Stop
  5. Retest
- Decision:
- Rationale:
- Dissent:
- Conditions: {ramp, holdout, monitoring}
- Owner / deadline:
- Follow-up:
```

## 7. Experiment card (Confluence/Notion)

```markdown
## EXP-{ID} — {Name}
**Owner:** {name} | **Status:** {status} | **Dates:** {start}–{end}
**Decision:** {one line}
**Primary:** {metric} | **MDE:** {x%} | **Result:** {lift, CI}
**Guardrails:** {pass/breach}
**Unit:** {company/seller/geo} | **Sample:** {n/arm}
**Readout:** {link} | **SQL:** {link} | **Dashboard:** {link}
**Lesson:** {one line}
```

## 8. SQL skeletons

### Assignment and exposure funnel

```sql
WITH assigned AS (
  SELECT unit_id, variant
  FROM exp_assignment
  WHERE exp_id = '{{exp_id}}'
    AND assigned_at >= '{{start}}' AND assigned_at < '{{end}}'
),
exposed AS (
  SELECT DISTINCT unit_id, variant
  FROM exp_exposure
  WHERE exp_id = '{{exp_id}}'
    AND event_time >= '{{start}}' AND event_time < '{{end}}'
),
outcome AS (
  SELECT unit_id,
         MAX(CASE WHEN order_time < '{{start}}' + INTERVAL '30 day' THEN 1 ELSE 0 END) AS converted
  FROM orders
  WHERE order_time >= '{{start}}' AND order_time < '{{end}}' + INTERVAL '30 day'
  GROUP BY unit_id
)
SELECT a.variant,
       COUNT(DISTINCT a.unit_id) AS assigned,
       COUNT(DISTINCT e.unit_id) AS exposed,
       COUNT(DISTINCT o.unit_id) AS with_outcome,
       AVG(o.converted) AS conversion
FROM assigned a
LEFT JOIN exposed e ON a.unit_id = e.unit_id AND a.variant = e.variant
LEFT JOIN outcome o ON a.unit_id = o.unit_id
GROUP BY a.variant;
```

### SRM

```sql
SELECT variant, COUNT(DISTINCT unit_id) AS n,
       COUNT(DISTINCT unit_id) * 1.0 / SUM(COUNT(DISTINCT unit_id)) OVER () AS share
FROM exp_assignment
WHERE exp_id = '{{exp_id}}'
GROUP BY variant;
```

### Balance

```sql
SELECT variant,
       AVG(pre_gmv_30d) AS avg_pre_gmv,
       STDDEV_SAMP(pre_gmv_30d) AS sd_pre_gmv,
       AVG(pre_orders_30d) AS avg_pre_orders,
       AVG(CASE WHEN is_new THEN 1 ELSE 0 END) AS new_rate
FROM exp_assignment a
JOIN company_features f USING (company_id)
WHERE a.exp_id = '{{exp_id}}'
GROUP BY variant;
```

### Guardrail

```sql
SELECT variant,
       COUNT(DISTINCT order_id) AS orders,
       SUM(CASE WHEN cancelled THEN 1 ELSE 0 END) * 1.0 / COUNT(DISTINCT order_id) AS cancel_rate,
       SUM(CASE WHEN disputed THEN 1 ELSE 0 END) * 1.0 / COUNT(DISTINCT order_id) AS dispute_rate
FROM orders o
JOIN exp_assignment a USING (company_id)
WHERE a.exp_id = '{{exp_id}}'
  AND o.order_time >= '{{start}}' AND o.order_time < '{{end}}'
GROUP BY variant;
```

## 9. Amendment log

```markdown
| Date | Change | Reason | Before/after exposure | Approved by | Impact on confirmatory status |
|---|---|---|---|---|---|
```

## 10. Holdout plan

```markdown
- Holdout share: 5–10%
- Randomization: hash(company_id + salt)
- Duration: 60–90 days
- Metrics: primary, guardrails, cannibalization
- Analysis: holdout vs treated, same estimator
- Ethical/ops: service parity, exception process
- Decision date:
```
