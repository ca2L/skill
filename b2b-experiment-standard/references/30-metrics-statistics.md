# 30 · Metrics and statistics

Metrics define what “better” means; statistics define how much evidence supports it. Both must be fixed before exposure.

## 1. Metric tree

```text
North Star (long-term platform health)
└── Primary metric (one, tied to the hypothesis)
    ├── Secondary metrics (mechanism, 2–4)
    ├── Guardrails (must not degrade, 3–6)
    └── Counter-metric (gaming detection, 1–2)
```

Rules:
- One primary per experiment. Multiple primaries require multiplicity control and a clear decision rule.
- Secondary metrics explain *why* the primary moved; they do not become primary after the fact.
- Guardrails are constraints, not objectives; a guardrail breach can veto a positive primary.
- Counter-metrics catch “winning the metric, losing the business” (e.g., order count up, cancellation up).

## 2. Choosing metrics

A good primary metric is:
- **Aligned** with the decision and the long-term North Star.
- **Sensitive** to the lever within the experiment window.
- **Measurable** at the randomization unit with reliable lineage.
- **Hard to game** without a counter-metric.
- **Pre-registered** with a direction and an MDE.

Avoid:
- Vanity metrics (clicks, impressions) with no causal path to value.
- Metrics that move mechanically with exposure (e.g., “sessions per exposed user”).
- Metrics with a different unit than randomization without a cluster adjustment.
- Composite metrics that hide which component moved; if used, publish components.

## 3. Metric specification (口径)

Every metric needs all ten:

1. **Name and ID** (e.g., `D02 Q2O`).
2. **Plain-language definition**.
3. **Formula** (numerator/denominator) and unit of analysis.
4. **Numerator**: events/entities included, filters, dedupe.
5. **Denominator**: population, eligibility, exclusions.
6. **Window**: start/end, attribution, time zone.
7. **Value rules**: currency, tax, refunds, cancellations, discounts, returns.
8. **Entity rules**: company vs user vs order; multi-account; duplicates.
9. **Source and SQL**: tables, partition, version hash, owner.
10. **Direction and threshold**: higher/lower is better; guardrail limit.

If two people can compute different numbers from the spec, it is not a spec.

## 4. B2B metric formulas

| Metric | Formula | Notes |
|---|---|---|
| Q2O conversion | orders / quote requests | Same buyer, same window; exclude test orders |
| Quote acceptance | accepted quotes / sent quotes | Buyer accepts; not seller views |
| Quote latency | median/avg(sent_at − request_at) | Report median and p90 |
| RFQ response rate | RFQs with ≥1 quote / RFQs | Seller-side supply health |
| Net GMV | gross GMV − returns − cancellations − discounts | Currency-normalized; tax excluded |
| Order frequency | orders / active buyers | Window-specific |
| Buyer retention | active buyers in period / buyers in base | Cohort-based; define active |
| Seller retention | active sellers in period / sellers in base | Same cohort logic |
| On-time fulfillment | orders delivered by promise / orders | Exclude buyer-caused delays |
| Cancellation rate | cancelled orders / placed orders | By party: buyer/seller/platform |
| Dispute rate | disputes / orders | Include resolution time |
| Gross margin | (net revenue − COGS) / net revenue | Finance-defined COGS |
| Take rate | platform revenue / GMV | Marketplace mode |
| Price consistency | % orders within policy band | Guardrail for pricing tests |
| Time to first order | days from signup to first order | New buyer cohort |

Always pair a volume metric with a quality metric (GMV with margin, orders with cancellation, conversion with dispute).

## 5. SQL rules

- Start from the assignment table; left join exposure/outcomes. Never start from outcomes, or you drop non-converters.
- Filter to the pre-registered population and window; apply the same filters in both arms.
- Do not filter on post-treatment variables (e.g., “engaged users”) for the primary analysis.
- Dedupe at the unit level before aggregating; avoid fan-out joins.
- Use `COUNT(DISTINCT unit_id)` for units, not row counts, unless the metric is event-level.
- Keep currency, tax, and refund logic identical across arms.
- Version the SQL and record a hash; dashboards must reference the same version.
- Reconcile to a known total (finance/order system) before trusting the lift.

## 6. Pre-registration and amendment

Pre-register:
- primary metric and exact SQL/version
- secondary and guardrail metrics
- analysis population, windows, exclusions
- estimator, covariates, CUPED
- subgroups and multiplicity method
- decision thresholds and stop rules

Amendment rules:
- Before exposure: allowed, versioned, with reason.
- After exposure but before readout: allowed only for data-quality fixes; document and downgrade confirmatory status if the metric changes.
- After seeing outcome: exploratory only; cannot support a confirmatory claim.
- Never silently change the denominator, window, or exclusion.

## 7. Estimands

| Estimand | Question | Use |
|---|---|---|
| **ITT** | Effect of assignment/offer | Primary; preserves randomization |
| **TOT/LATE** | Effect of actually receiving treatment | Secondary; requires exclusion restriction |
| **CATE** | Effect for a subgroup | Pre-registered heterogeneity |
| **ATT** | Effect on treated | Descriptive; not a substitute for ITT |

Default: ITT. Report TOT only with a credible compliance model and clear assumptions.

## 8. Estimators

### Difference in means

```text
τ̂ = Ȳ_T − Ȳ_C
SE = sqrt(s_T²/n_T + s_C²/n_C)
CI = τ̂ ± z_{1−α/2} SE
```

Use Welch’s t-test for unequal variances; with large N, normal approximation is fine.

### Regression adjustment

```text
Y_i = α + τ T_i + β' X_i + ε_i
```

- Include pre-treatment covariates only.
- Report both adjusted and unadjusted; if they disagree materially, investigate.
- With cluster assignment, cluster the SE at the assignment unit.

### Cluster-robust SE

```text
Var(β̂) = (X'X)⁻¹ (Σ_g X_g' û_g û_g' X_g) (X'X)⁻¹
```

- Cluster at the randomization unit (company/seller/geo), not the outcome unit.
- Use `G/(G−1)` correction; with < 40 clusters, use CR2 or randomization inference.
- Few clusters → wide, unreliable CI; report and avoid strong claims.

### Ratio metrics: delta method

For `R = ΣY / ΣX`:

```text
Var(R) ≈ Var(Y − R X) / (n X̄²)
SE(R) = sqrt(Var(R))
```

Or bootstrap at the randomization unit. Never run a naive t-test on per-unit ratios without accounting for the denominator.

### CUPED

```text
θ = Cov(Y, X) / Var(X)
Y_adj = Y − θ (X − X̄)
```

- `X` must be pre-treatment.
- Variance reduction ≈ `ρ²`; residual variance ≈ `1 − ρ²`.
- Pre-register as primary if used; report unadjusted as sensitivity.

### Stratification

Analyze within strata and combine with weights, or include stratum fixed effects. Report the stratification variables and check balance within strata.

### Outliers and winsorization

- Pre-register the rule (e.g., winsorize at 1%/99% by arm).
- Do not trim outliers because they weaken the result.
- Report both winsorized and raw for GMV-type metrics.
- Investigate extreme accounts; a single whale can drive a B2B result.

## 9. Effect sizes and uncertainty

Always report:

| Quantity | Definition |
|---|---|
| Control mean | Baseline |
| Treatment mean | Observed |
| Absolute lift | `mean_T − mean_C` |
| Relative lift | `(mean_T − mean_C) / mean_C` |
| 95% CI | For absolute and relative |
| P-value | Two-sided, matching the pre-registered test |
| MDE | Minimum detectable effect at the achieved sample |
| Business value | Lift × volume × margin, with assumptions |

Rules:
- Relative lift without the baseline is uninterpretable.
- A CI that includes both “no effect” and “large effect” means the experiment is inconclusive, not negative.
- “Statistically significant” is not “business significant”; compare to MDE and value.
- Report the CI for the decision metric, not only the p-value.

## 10. Multiple testing

Use when you test more than one confirmatory hypothesis (multiple primaries, many subgroups, many guardrails).

| Method | Control | Rule |
|---|---|---|
| **Bonferroni** | FWER | `p_i ≤ α/m` |
| **Holm** | FWER | Sort p; reject `p_(i) ≤ α/(m−i+1)` |
| **Benjamini–Hochberg** | FDR | Sort p; reject `p_(i) ≤ i·q/m` |

Guidance:
- One primary: no correction needed for the primary; correct secondary/subgroup claims.
- Multiple primaries: Holm or BH; pre-register.
- Subgroups: interaction test first; do not compare p-values across arms.
- Guardrails: correct across guardrails, or use non-inferiority bounds.
- Exploratory analyses: label as exploratory; no correction can make them confirmatory.

## 11. Power and MDE

- Power depends on baseline, variance, sample, alpha, and design effect.
- For cluster designs, use `DEFF = 1 + (m−1) ICC`; small ICC still matters with large clusters.
- For ratio metrics, simulate or use delta-method variance; do not assume binomial.
- For CUPED, use the expected correlation, not the best-case.
- Report achieved power/MDE after the experiment; a non-significant result with low power is inconclusive.

## 12. Sequential and Bayesian

### Sequential

- Pre-register alpha spending (O’Brien–Fleming, Pocock) and the number/timing of looks.
- Do not peek continuously without adjustment.
- Use a group-sequential or always-valid method; report adjusted CIs.

### Bayesian

- Pre-register priors, likelihood, and decision rule (e.g., `P(τ > MDE) > 0.95` and expected loss < threshold).
- Report posterior median, 95% credible interval, and probability of harm.
- Bayesian does not license optional stopping by itself; the decision rule must be pre-registered.
- Do not mix Bayesian posterior with frequentist p-values in one claim.

## 13. Statistical pitfalls

| Pitfall | Why it misleads | Fix |
|---|---|---|
| Peeking | Inflates false positive rate | Sequential design |
| Optional stopping | Same | Pre-register horizon |
| Multiple metrics | p-hacking | One primary + correction |
| Subgroup fishing | False discoveries | Pre-register + interaction |
| Ignoring clusters | Too-narrow CI | Cluster-robust |
| Naive ratio test | Wrong variance | Delta/bootstrap |
| Post-treatment adjustment | Bias | Pre-treatment covariates only |
| Dropping outliers | Bias | Pre-register winsorization |
| “No effect” from p > .05 | Ignores CI/MDE | Report CI and MDE |
| Changing metric post hoc | HARKing | Freeze + amendment |
| Simpson’s paradox | Aggregation masks segments | Pre-registered strata |
| Regression to the mean | Extreme baseline | Randomization + pre-period |

## 14. Readout table

```markdown
| Metric | Control | Treatment | Abs lift | Rel lift | 95% CI (rel) | p | MDE | n |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| Primary | | | | | | | | |
| Secondary | | | | | | | | |
| Guardrail | | | | | | | | |
```

Add:
- data lock time, DQ status, estimator, covariates, cluster count
- guardrail owner sign-off
- subgroup results (pre-registered only)
- long-term window status
- limitations and sensitivity analyses
