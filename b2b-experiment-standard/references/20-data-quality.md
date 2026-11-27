# 20 · Data quality gates

No readout is valid until the data pass. Data quality is not a dashboard; it is a set of blocking tests with owners and evidence.

## 1. Severity model

| Level | Meaning | Action |
|---|---|---|
| **S1 — blocking** | Invalidates assignment or outcome; effect cannot be trusted | Stop readout; fix or declare experiment invalid |
| **S2 — material** | Biases or inflates uncertainty; decision may change | Disclose; correct if possible; downgrade confidence |
| **S3 — cosmetic** | Documentation/coverage gap; unlikely to change decision | Note; fix before archive |

S1 examples: SRM p < 0.001, assignment not deterministic, exposure event missing for one arm, outcome table incomplete for a period, duplicate entities above threshold, treatment applied to control.

## 2. The sample funnel

Report four counts for every arm:

| Count | Definition |
|---|---|
| **Assigned** | Units in the assignment table at launch |
| **Eligible** | Assigned units passing pre-registered eligibility |
| **Exposed** | Eligible units with a valid exposure event |
| **Analyzed** | Exposed units with a non-missing primary outcome |

Funnel rules:
- Assignment is the ITT denominator; do not silently drop units.
- Eligibility filters must be pre-registered and applied symmetrically.
- Exposure rate = exposed / eligible; report by arm.
- Outcome missingness = 1 − analyzed / exposed; report by arm and segment.
- A large gap between assigned and eligible usually means targeting/logging is wrong, not that the population is “cleaner.”

## 3. SRM (sample ratio mismatch)

### Test

For `k` arms with observed counts `O_i` and expected proportions `p_i`:

```text
χ² = Σ (O_i − N p_i)² / (N p_i),  df = k − 1
```

For two equal arms, a simpler check:

```text
χ² = (O_T − O_C)² / (O_T + O_C)
```

Flag if `p < 0.001`. Do not use `p < 0.05` as a blocking rule; with large N, trivial imbalances become “significant.”

### Causes, in order of likelihood

1. Assignment logging or hash bug (non-deterministic, wrong salt, wrong unit).
2. Eligibility filter applied asymmetrically (e.g., treatment needs a feature flag).
3. Exposure redirect or bot filtering that differs by arm.
4. Delayed outcome/assignment partitions.
5. Genuine randomization failure (rare; check the assignment job).
6. Multiple testing across many SRM checks (use a stricter threshold or a global test).

### Response

- Stop. Do not “fix” by reweighting, trimming, or choosing a subsample that balances.
- Trace the assignment table back to the randomization job; compare counts at assignment, delivery, and exposure.
- If the cause is a logging bug and assignment is intact, analyze ITT on the assignment table and document the exposure issue.
- If assignment itself is broken, declare the experiment invalid; rerun with a fixed salt/job.
- Record the investigation and the decision in the experiment record.

## 4. Pre-period balance

### Standardized mean difference

```text
SMD = (mean_T − mean_C) / sqrt((s_T² + s_C²) / 2)
```

For binary variables, use the same formula with `p(1−p)`.

| Threshold | Interpretation |
|---|---|
| `abs(SMD) < 0.05` | Good balance |
| `0.05–0.10` | Acceptable; monitor |
| `> 0.10` | Investigate; adjust or disclose |

Rules:
- Check 10–20 pre-period covariates, including the pre-period primary metric.
- With many covariates, some will exceed 0.10 by chance; report the count and a joint test, not just the worst one.
- Do not drop covariates after seeing imbalance; pre-register the adjustment.
- If imbalance is material, use regression adjustment/CUPED with pre-period covariates and report unadjusted as sensitivity.
- Balance does not prove validity; SRM and exposure still matter.

## 5. Exposure completeness

Metrics:
- **Delivery rate** = units actually served treatment / assigned treatment units.
- **Consumption rate** = units with the changed element in their session / delivered units.
- **Arm difference** = treatment rate − control rate (for the same event).

Checks:
- Delivery rate should be near 100% for a server-side change; < 90% means a gating/rollout bug.
- Consumption differs legitimately if the treatment changes behavior; a large difference can be the effect, not a bug. Distinguish via a pre-treatment exposure proxy.
- Exposure timestamps must fall inside the experiment window and after assignment.
- Deduplicate exposure events by `(unit_id, variant, first_exposure)`; multiple exposures are fine, multiple units per event are not.
- Check exposure by day, channel, device, and segment for holes.

## 6. Contamination

Two types:

| Type | Definition | Detection |
|---|---|---|
| **Cross-over** | A unit receives the other arm’s experience | Join assignment to delivery/config logs |
| **Spillover** | A unit’s outcome is affected by another unit’s treatment | Shared seller/inventory/market; compare control outcomes near treated units |

Thresholds:
- Cross-over < 5%: ITT remains valid but diluted; report.
- Cross-over ≥ 5%: investigate; consider TOT/LATE with compliance assumptions, or invalidate.
- Spillover: cannot be fixed post hoc; change the unit (cluster/geo/switchback) and rerun.
- Sales/ops contamination: check CRM notes, manual overrides, and discount approvals by arm.

## 7. Duplicate users and accounts

B2B entities are messy: one company can have many user IDs, emails, domains, and ship-to addresses.

Checks:
- Exact duplicates on `company_id`, `account_id`, `tax_id`, normalized domain.
- Fuzzy duplicates on name + address + phone; review top matches manually.
- Multiple users per company: expected; randomize at company, not user.
- Duplicate outcome events: same order counted twice; dedupe on order ID.
- Duplicate exposure: same unit exposed in both arms; S1.

Thresholds:
- Duplicate company rate < 2% (after entity resolution) is acceptable with disclosure.
- Duplicate outcome rate should be 0 after dedupe; any remaining duplicates are S2.
- If duplicates are concentrated in one arm, treat as contamination/S1.

## 8. Data lineage and reconciliation

Every metric must have a traceable path:

```text
source event/table → cleaned table → metric aggregate → dashboard/readout
```

Checks:
- **Freshness**: latest partition is within SLA; no partial day in the readout.
- **Completeness**: row counts by day/arm match expectations; no missing partitions.
- **Reconciliation**: metric total matches finance/order system within a documented tolerance.
- **Nulls**: primary outcome null rate by arm; if differential, S1.
- **Schema**: column types, currency, tax, refund, and cancellation flags are consistent.
- **Version**: SQL/metric definition hash is recorded; dashboard uses the same version.
- **Time zone**: all windows use the same zone; DST and month boundaries handled.

## 9. DQ scorecard

| Dimension | Weight | Pass criterion |
|---|---:|---|
| Assignment integrity | 20 | Deterministic, logged, no SRM |
| Sample funnel | 15 | Counts reconcile; missingness < 10% and balanced |
| SRM | 15 | p ≥ 0.001 |
| Pre-period balance | 15 | Max abs(SMD) < 0.10 or adjusted |
| Exposure | 10 | Delivery ≥ 90%; no arm gap > 2pp unexplained |
| Contamination | 10 | Cross-over < 5%; no spillover |
| Duplicates | 5 | Company duplicates < 2%; outcome duplicates 0 |
| Lineage | 10 | Fresh, complete, reconciled, versioned |

Decision:
- Any S1 → **blocked**.
- Score ≥ 85 and no S1 → **pass**.
- 70–84 → **conditional**; disclose and adjust confidence.
- < 70 → **fail**; do not use for a scale decision.

## 10. SQL check patterns

```sql
-- SRM: observed vs expected by arm
SELECT variant,
       COUNT(DISTINCT unit_id) AS n,
       COUNT(DISTINCT unit_id) * 1.0 / SUM(COUNT(DISTINCT unit_id)) OVER () AS share
FROM exp_assignment
WHERE exp_id = '{{exp_id}}'
GROUP BY variant;

-- Exposure funnel by arm
SELECT a.variant,
       COUNT(DISTINCT a.unit_id) AS assigned,
       COUNT(DISTINCT e.unit_id) AS exposed,
       COUNT(DISTINCT o.unit_id) AS with_outcome
FROM exp_assignment a
LEFT JOIN exp_exposure e
  ON a.unit_id = e.unit_id AND a.variant = e.variant
LEFT JOIN exp_outcome o
  ON a.unit_id = o.unit_id
WHERE a.exp_id = '{{exp_id}}'
GROUP BY a.variant;

-- Duplicate company check
SELECT company_id, COUNT(*) AS n
FROM dim_company
GROUP BY company_id
HAVING COUNT(*) > 1;

-- Cross-over check
SELECT a.variant AS assigned_variant,
       d.variant AS delivered_variant,
       COUNT(DISTINCT a.unit_id) AS units
FROM exp_assignment a
JOIN exp_delivery d USING (unit_id)
WHERE a.exp_id = '{{exp_id}}'
GROUP BY 1, 2;
```

## 11. Gate decision

| Finding | Decision |
|---|---|
| SRM p < 0.001, assignment intact | Analyze ITT; disclose exposure; no scale without fix |
| SRM p < 0.001, assignment broken | Invalid; rerun |
| Primary outcome missing differentially | Blocked until fixed |
| Balance abs(SMD) > 0.10 | Adjust/CUPED; disclose |
| Cross-over 5–10% | ITT + TOT secondary; disclose |
| Cross-over > 10% | Invalid or quasi-experimental |
| Spillover detected | Change unit; rerun |
| Duplicate companies > 2% | Resolve entities; rerun checks |
| Lineage/reconciliation fail | Blocked |
| All pass | Proceed to readout |

## 12. Common traps

- “SRM is just a little off; the effect is huge.” A huge effect under SRM is more likely a bug than a breakthrough.
- “We’ll reweight to fix SRM.” Reweighting changes the estimand and hides the bug.
- “Balance is fine, so assignment is fine.” Balance can pass while exposure is broken.
- “Missing outcomes are random.” In B2B, high-value accounts are more likely to have complete data; missingness is rarely random.
- “We deduped users.” The unit is the company; deduping users does not fix account-level duplication.
- “The dashboard matches.” Check the metric SQL hash and the date range, not just the headline number.
