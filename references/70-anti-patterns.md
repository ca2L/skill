# 70 · Anti-patterns and cases

Use this before design (pre-mortem), before readout (red team), and after archive (postmortem). The names are deliberately blunt; the fix matters more than the label.

## 1. The 20 anti-patterns

| # | Anti-pattern | What it looks like | Why it misleads | Fix |
|---:|---|---|---|---|
| 1 | **“Test and see”** | No hypothesis, no MDE, no decision rule | Any result becomes a story; no falsification | Write the four-part hypothesis and decision rules |
| 2 | **Wrong unit** | Users randomized, price/account changed | Control sees treatment; effect diluted or contaminated | Randomize at company/account or cluster |
| 3 | **Historical control** | “Last month was baseline” | Seasonality, macro, product changes confound | Concurrent control; quasi-experiment with assumptions |
| 4 | **Peeking** | Daily dashboard; stop when p<.05 | Inflated false positives | Fixed horizon or pre-registered sequential design |
| 5 | **Metric shopping** | Primary changes after readout | HARKing; p-hacking | Freeze metric + SQL hash; amendment log |
| 6 | **Many primaries** | “We’ll see which one moves” | Multiplicity; no clear decision | One primary; correct secondaries |
| 7 | **Underpowered pilot** | 300 accounts, expect +5% | Wide CI called “no effect” | Compute MDE; change design/metric/window |
| 8 | **SRM denial** | “It’s only a little off” | Assignment bug masquerades as effect | Block; trace assignment; rerun |
| 9 | **Exposure = assignment** | Treat assigned as treated | ITT diluted; mechanism unknown | Define reached/exposed; report funnel |
| 10 | **Sales contamination** | Reps apply treatment to control accounts | Cross-over; biased effect | Randomize by rep/territory; log CRM actions |
| 11 | **Duplicate entities** | One company, many accounts | Wrong denominator; double counting | Canonical company ID; entity resolution |
| 12 | **Definition drift** | Different SQL for dashboard vs readout | Numbers don’t reconcile | One metric spec + SQL hash; reconcile |
| 13 | **Naive ratio test** | t-test on GMV/order | Wrong variance; false significance | Delta method or bootstrap |
| 14 | **Ignoring clusters** | Company randomization, user-level SE | CI too narrow; false confidence | Cluster-robust at assignment unit |
| 15 | **Subgroup fishing** | “It works for SMBs” after the fact | False discovery; harmful targeting | Pre-register + interaction test + correction |
| 16 | **Guardrail without teeth** | “We’ll watch cancellations” | Harm ships | Named owner, threshold, circuit breaker |
| 17 | **Novelty win** | Week-1 spike declared success | Effect decays; wrong decision | 30-day primary; 60/90 check |
| 18 | **No holdout** | Full rollout immediately | Can’t measure long-term/cannibalization | 5–10% randomized holdout |
| 19 | **HiPPO decision** | “Leadership feels it worked” | Evidence ignored; no learning | Decision record + pre-registered rules |
| 20 | **Archive graveyard** | Screenshots in a folder | No reuse; repeat mistakes | Doc/SQL/dashboard/KB/lesson |

## 2. Three B2B cases

### Case 1 — Quote SLA: positive primary, guardrail veto

**Setup.** Mid-market buyers who requested a quote but had not ordered. Company-level randomized, 50/50, 6,200 companies per arm, 30-day window. Treatment: 4-hour seller quote SLA with escalation.

**Result.**
- Q2O: 8.4% → 9.2%, relative +9.4% [1.8%, 17.0%], p=0.012.
- Seller quote rate: −6.1pp (guardrail threshold −5pp) — **breach**.
- Cancellation: +1.2pp (threshold +2pp) — pass.
- New buyers: +15.1%; existing: +6.8%; interaction p=0.04.

**Diagnosis.** The SLA works for buyers, but sellers route quotes away or decline when the 4-hour promise is unrealistic. Scaling would improve Q2O while degrading supply health.

**Decision.** **Iterate**, not scale. Fix seller capacity/incentive, add a “promise feasibility” check, rerun with seller quote rate as a co-primary guardrail. Do not target new buyers while the seller-side harm persists.

**Lesson.** A positive primary metric does not override a guardrail breach. The guardrail is the business’s immune system.

### Case 2 — Seller fulfillment tool: two-sided marketplace trap

**Setup.** Seller-level cluster randomized (seller clusters by region/category), 1,800 sellers, 90-day window. Treatment: recommended packing sequence and carrier cut-off alerts.

**Result.**
- On-time fulfillment: +4.2pp [1.1, 7.3], p=0.008.
- Seller retention: +2.1pp [−0.4, 4.6], p=0.10.
- Buyer dispute rate: +0.8pp (threshold +0.5pp) — **breach**.
- Buyer NPS: −3 points in treated seller clusters.

**Diagnosis.** Sellers hit carrier cut-offs by shipping partial orders; on-time improves, but completeness and buyer experience degrade. Seller-level randomization was correct for seller behavior, but buyer outcomes are clustered within sellers and needed cluster-robust analysis.

**Decision.** **Stop** the current version; iterate with a “complete order” constraint and a dispute guardrail. Do not scale on on-time alone.

**Lesson.** In a two-sided marketplace, every seller-side win must be checked on the buyer side. Randomize at the seller, analyze both sides with the seller cluster.

### Case 3 — Tiered pricing: geo test with margin and fairness

**Setup.** 8 matched markets, 4 treatment / 4 control, 8-week geo test. Treatment: volume-tiered discount for mid-market buyers. Primary: net GMV; guardrails: gross margin, price consistency, dispute rate.

**Result.**
- Net GMV: +6.8% [−1.2, 15.1], p=0.09.
- Gross margin: −2.4pp (threshold −1.5pp) — **breach**.
- Price consistency violations: 3.1% vs 1.0% (threshold 2%) — **breach**.
- Contract accounts: +9.1%; spot buyers: +2.0%; interaction p=0.06 (not significant after correction).

**Diagnosis.** The point estimate is positive but uncertain; margin and price consistency are harmed. The apparent contract-account segment is not credible after multiplicity correction.

**Decision.** **Stop** the broad rollout; **retest** a narrower contract-account design with a margin floor and price governance. Do not target spot buyers on a non-significant interaction.

**Lesson.** A geo test with 8 markets has limited power; a positive point estimate is not a mandate. Margin and price consistency can veto GMV.

## 3. Red-team questions before readout

1. What would make this result a bug rather than an effect?
2. Which arm had more exposure, and why?
3. Did any human decide who got treatment after assignment?
4. Which metric definition changed since pre-registration?
5. How many subgroups were tested, and what is the adjusted p?
6. Is the CI wide enough to include both “no effect” and “large harm”?
7. What happens to the result if we winsorize the top 1% of accounts?
8. What does the 7-day curve look like vs the 30-day curve?
9. Who bears the cost if we scale, and did we measure their outcome?
10. If we scale, how will we know in 90 days whether it still works?

## 4. Postmortem template

```markdown
# Postmortem — EXP-{ID}

- Outcome: scale / target / iterate / stop / retest
- What we predicted:
- What happened (primary, CI, guardrails):
- Biggest surprise:
- Data-quality issue (if any):
- Decision quality: would we decide the same with the same evidence?
- Process fix (one change):
- Reusable lesson (pattern, boundary):
- Owner / due date:
```

## 5. When the experiment “failed”

A null or negative result is still an asset if it:
- rules out an effect larger than the MDE,
- falsifies a mechanism,
- reveals a guardrail cost,
- shows the population/segment is wrong,
- improves the next design.

Write it down. The most expensive experiment is the one nobody learns from.
