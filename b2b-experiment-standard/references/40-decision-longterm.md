# 40 · Heterogeneity, long-term effects, and decisions

An experiment answers “what happened, for whom, for how long, and what should we do.” This file covers the last three.

## 1. Heterogeneity: when a subgroup is real

Subgroup analysis is the most abused part of experimentation. A credible subgroup claim needs all five:

1. **Pre-registered** before exposure, with a stated hypothesis.
2. **Interaction test**, not two separate significance tests.
3. **Sufficient power** for the interaction (usually 2–4× the sample of a main effect).
4. **Multiplicity control** across the pre-registered subgroups.
5. **Operational relevance**: the business can actually target or treat the segment differently.

If any is missing, label the result exploratory.

### Interaction test

For a binary subgroup `Z`:

```text
Y_i = α + τ T_i + γ Z_i + δ (T_i × Z_i) + β' X_i + ε_i
```

`δ` is the differential treatment effect. Test `H0: δ = 0`.

For a continuous segment (e.g., baseline GMV), use:

```text
Y_i = α + τ T_i + γ Z_i + δ (T_i × Z_i) + β' X_i + ε_i
```

with `Z` centered/scaled; report the effect at meaningful values, not only the interaction coefficient.

Rules:
- Do not declare a subgroup effect because treatment is significant inside one subgroup and not the other.
- Do not compare p-values across subgroups.
- With many subgroups, use BH/Holm on the interaction p-values.
- Report subgroup estimates with CIs, not just stars.

### Effect measure

For each subgroup, report:

- control mean, treatment mean
- absolute and relative lift
- 95% CI
- interaction p-value (adjusted)
- sample and event count
- whether the subgroup was pre-registered

## 2. B2B heterogeneity dimensions

| Dimension | Why it may matter | Caution |
|---|---|---|
| New vs existing buyer | Learning, trust, baseline conversion | New buyers may be novelty-sensitive; existing buyers may have inertia |
| High vs low value | Elasticity, sales attention, risk tolerance | Value measured pre-treatment; avoid post-hoc tiers |
| High vs low frequency | Habit, procurement cycle | Frequency is endogenous to treatment; use pre-period |
| Channel (web/app/API/sales) | Different exposure and decision process | Channel mix may shift with treatment |
| Category/product | Margin, lead time, substitutability | Many categories → multiplicity; pre-register |
| Seller tier/segment | Fulfillment capability, incentives | Seller-side effects can spill to buyers |
| Region/market | Logistics, competition, regulation | Few markets → weak inference |
| Contract type (spot vs framework) | Buying process, price sensitivity | Contract data may be incomplete |
| Platform mode (自营/平台/混合) | Who controls price/fulfillment | Do not pool modes without testing |
| Sales rep/territory | Effort, relationship, compliance | Contamination and small N |

### Pre-registered subgroup set

Limit to 3–5. A practical default:

1. New vs existing buyer (or new vs established account).
2. High vs low baseline value (pre-period GMV/order count).
3. High vs low frequency (pre-period orders).
4. Channel or platform mode (only if operationally distinct).
5. One business-critical segment (category/seller tier/region).

Everything else is exploratory.

## 3. From heterogeneity to targeting

Target only when all are true:

- Interaction is credible (pre-registered, adjusted, sufficient power).
- The segment is large enough to matter and identifiable before treatment.
- Targeting is operationally feasible without leakage or unfairness.
- The untargeted segment is not harmed.
- The targeted rollout can be monitored and reversed.

If the interaction is not credible, do **not** target. A flat overall effect with a “great” post-hoc segment is usually noise.

Targeting policy options:

| Option | When |
|---|---|
| Full rollout | Overall positive, guardrails pass, no credible harm |
| Targeted rollout | Credible interaction + operational feasibility + no harm |
| Phased rollout | Overall positive but capacity/risk constraints |
| Iterate | Directional signal but CI includes meaningful harm or MBE not reached |
| Stop | Harm or guardrail breach or confidently below MBE |
| Retest | Inconclusive due to power/data; specify the design change |

## 4. Long-term effects

### Windows

| Window | Purpose | Interpretation |
|---|---|---|
| 7 days | Early signal / novelty check | Do not decide |
| 14 days | Learning and stabilization | Watch for decay |
| 30 days | Primary decision window (default) | Main readout |
| 60 days | Durability | Is the effect holding? |
| 90 days | Structural/seasonal | Repeat purchase, retention |
| Post-rollout | Full-population effect | Holdout/DID/ITS |

Why early and late differ:
- **Novelty/primacy**: early lift from attention, later from habit.
- **Learning**: users/sellers need time to adopt.
- **Selection**: early adopters differ from the population.
- **Seasonality**: a 7-day window can sit inside a peak.
- **Competitive response**: sellers/buyers adjust.
- **Stock vs flow**: one-time purchases vs recurring.

### Decay

Report the effect trajectory, not just the endpoint:

```text
effect_t = f(t), t = 7, 14, 30, 60, 90
```

Classify:
- **Sustained**: effect stable or growing.
- **Decaying**: effect shrinks; estimate half-life if roughly exponential.
- **Delayed**: effect appears after 14–30 days.
- **Reversed**: early positive, later negative (novelty or harm).

If decay is plausible, the decision must use the long-term estimate, not the 7-day peak.

### Side effects

Check beyond the primary metric:

- Cannibalization of other categories/channels.
- Seller/buyer fairness and price perception.
- Support ticket volume and resolution time.
- Cancellation, return, dispute, and chargeback rates.
- Sales team behavior and discount discipline.
- Reputation/reviews, especially in marketplace mode.
- Ecosystem health: seller count, assortment, fill rate.

## 5. Post-rollout measurement

Once everyone is treated, you lose the concurrent control. Options:

### Holdout

- Randomly hold out 5–10% of the rollout population for 30–90 days.
- Analyze holdout vs treated with the same estimator.
- Pre-register the holdout size and duration; do not shrink it after seeing results.
- Watch for ethical/competitive issues: held-out buyers may get worse service.

### Difference-in-differences (DID)

```text
τ = (Y_treat,post − Y_treat,pre) − (Y_control,post − Y_control,pre)
```

Requires parallel trends; test pre-trends and placebo periods. Use never-treated or late-treated units as controls.

### Synthetic control

- Build a weighted combination of untreated markets/accounts that matches the treated unit pre-period.
- Report pre-period fit, placebo tests, and leave-one-out sensitivity.
- Use for market-level rollouts with few treated units.

### Interrupted time series (ITS)

- Model the pre-period trend and level; estimate the break at rollout.
- Control for seasonality and autocorrelation.
- Requires enough pre-period points and no concurrent shock.

### Stepped-wedge

- Roll out in randomized waves; all units eventually treated.
- Analyze with time and unit fixed effects; account for within-unit correlation.

## 6. Decision framework

### Evidence first

Before the decision meeting, confirm:

- DQ gates passed or disclosed.
- Primary result with CI, p, MDE, and business value.
- Guardrails with owner sign-off.
- Pre-registered subgroups and multiplicity.
- Long-term/holdout status.
- Limitations and sensitivity analyses.

### Decision matrix

| Primary result | Guardrails | Action |
|---|---|---|
| CI lower bound > MBE | Pass | **Scale** (ramp + holdout) |
| CI lower bound > 0 but < MBE | Pass | **Iterate/scale narrowly** depending on value and cost |
| CI includes 0, wide | Pass | **Retest** or **iterate**; do not claim no effect |
| CI entirely below MBE | Pass | **Stop** (confidently below threshold) |
| Any | Breach | **Stop/remediate**; guardrail veto |
| Positive overall, credible subgroup | Pass | **Target**, with monitoring |
| Negative/harm | Any | **Stop**; investigate mechanism |

Thresholds:
- `MBE` = minimum business effect worth shipping, pre-registered.
- “Pass” guardrail = non-inferiority bound met or no material harm.
- “Wide” CI = upper bound above MBE and lower bound below 0.

### Decision rules

**Scale** when:
- Primary CI lower bound exceeds MBE.
- Guardrails non-inferior.
- No S1 data-quality issue.
- Operational capacity and rollback are ready.
- Long-term/holdout plan exists.

**Target** when:
- Credible interaction, not post-hoc.
- Segment identifiable and operable.
- No harm to the rest.
- Targeting does not create fairness/legal risk.

**Iterate** when:
- Direction is promising but CI includes meaningful harm or MBE is not reached.
- Mechanism is plausible and fixable.
- Do not scale on a hope; run a new experiment with a sharper lever or larger sample.

**Stop** when:
- Harm or guardrail breach.
- Confidently below MBE.
- Mechanism falsified.
- Cost/risk exceeds value.

**Retest** when:
- Inconclusive due to power, data quality, or contamination.
- Specify what changes: sample, unit, metric, window, or design.
- Do not simply rerun the same underpowered test and hope.

## 7. Decision record

```markdown
# Decision — EXP-{ID}

- Date / attendees:
- Evidence: primary, CI, p, MDE, guardrails, DQ status
- Options considered:
- Decision: scale / target / iterate / stop / retest
- Rationale:
- Dissent and unresolved questions:
- Owner and deadline:
- Rollout plan: ramp %, monitoring, rollback trigger
- Holdout/long-term plan:
- Follow-up experiment or review date:
```

The record is part of the experiment, not an afterthought. It should be readable by someone who was not in the room.

## 8. Rollout plan

- Ramp: 5% → 25% → 50% → 100%, with DQ and guardrail checks at each step.
- Monitoring: daily for the first week, then weekly; alert on guardrail breach and SRM-like anomalies.
- Rollback: named trigger, owner, and technical path; test it before launch.
- Holdout: 5–10% for 30–90 days if the effect is long-term or cannibalization is plausible.
- Communication: sales/support/sellers know what changed and what not to do.
- Archive: document, SQL, dashboard, decision record, reusable lesson.

## 9. Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Deciding on day 7 | Novelty/seasonality | Use 30-day primary |
| Post-hoc subgroup targeting | Harm/no effect at scale | Pre-register + interaction |
| “Flat” without CI | Missed real effect or harm | Report CI and MDE |
| Scaling on p < .05 only | Small, uneconomic effect | Require CI lower > MBE |
| Ignoring guardrails | Brand/seller harm | Veto + owner |
| No holdout | Can’t measure long-term | 5–10% holdout |
| Full rollout immediately | No comparison group | Ramp + holdout |
| Decision by HiPPO | Ego/ politics | Decision record + evidence |
| Not archiving | Repeat mistakes | Knowledge card + SQL |
| Treating “no effect” as failure | Learning lost | Record mechanism and null result |
